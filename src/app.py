import datetime
import functools
import logging
import os
import time
from concurrent import futures
from contextlib import contextmanager
from os import environ
from secrets import compare_digest

import grpc
from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import func

import sb_pb2
import sb_pb2_grpc
from models import Base, DebugData, Report, Strand, StrandInReport, StrandSocialDistancing, StrandStatus
from utils import timestamp_from_datetime, to_aware_datetime
from google.api import httpbody_pb2

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d: %(process)d: %(message)s",
    datefmt="%F %T",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@functools.cache
def get_engine():
    return create_engine(os.getenv("DATABASE_CONNECTION_STRING"))


@contextmanager
def session_scope():
    session = Session(get_engine())
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


secret_key = os.environ["SECRET_KEY"]


def _get_strand_update():
    with session_scope() as session:
        strands = [s.to_pb() for s in session.query(Strand).all()]
        subq = (
            session.query(func.max(StrandSocialDistancing.id).label("id"))
            .group_by(StrandSocialDistancing.strand_id)
            .subquery()
        )
        sds = [
            s.to_pb()
            for s in session.query(StrandSocialDistancing).join(subq, subq.c.id == StrandSocialDistancing.id).all()
        ]
        return sb_pb2.StrandUpdate(
            strands=strands,
            sds=sds,
            latest_app_version=max([strand.minimum_app_version or 0 for strand in strands]),
        )


def _check_key(context):
    metadata = dict(context.invocation_metadata())

    if "authorization" not in metadata:
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authorization header")

    authorization = metadata["authorization"]
    if not authorization.startswith("Bearer "):
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "Wrong format auth header")

    if not compare_digest(secret_key, authorization[7:]):
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "Wrong key")


class SafeBluesAdminServicer(sb_pb2_grpc.SafeBluesAdminServicer):
    def NewStrand(self, request, context):
        _check_key(context)
        with session_scope() as session:
            s = Strand.from_pb(request)
            session.add(s)
            session.commit()
            return s.to_pb()

    def ListStrands(self, request, context):
        return _get_strand_update()

    def SetSD(self, request, context):
        _check_key(context)
        with session_scope() as session:
            sd = StrandSocialDistancing.from_pb(request)
            session.add(sd)
            session.commit()
            return sd.to_pb()


class SafeBluesServicer(sb_pb2_grpc.SafeBluesServicer):
    def PingServer(self, request, context):
        logging.info(f"Got PingServer with nonce={request.nonce}")
        return sb_pb2.Ping(nonce=request.nonce)

    def Report(self, request, context):
        logger.info(f"Processing Report from client_id={request.client_id}, version={request.version_code}")
        report = request
        with session_scope() as session:
            incubating_strands = [
                StrandInReport(state=StrandStatus.incubating, strand_id=strand_id)
                for strand_id in report.current_incubating_strands
            ]
            for strand in incubating_strands:
                session.add(strand)

            infected_strands = [
                StrandInReport(state=StrandStatus.infected, strand_id=strand_id)
                for strand_id in report.current_infected_strands
            ]
            for strand in infected_strands:
                session.add(strand)

            removed_strands = [
                StrandInReport(state=StrandStatus.removed, strand_id=strand_id)
                for strand_id in report.current_removed_strands
            ]
            for strand in removed_strands:
                session.add(strand)

            session.add(
                Report(
                    client_id=report.client_id,
                    version_code=report.version_code,
                    strands=incubating_strands + infected_strands + removed_strands,
                )
            )

        logger.info(
            f"Report received from client_id={request.client_id}: {len(incubating_strands)} incubating, {len(infected_strands)} infected, {len(removed_strands)} removed"
        )
        return sb_pb2.Empty()

    def Pull(self, request, context):
        logger.info(f"Processing Pull")
        return _get_strand_update()

    def PushDebugData(self, request, context):
        logger.info(f"PushDebugData with {len(request.data)} data points")
        with session_scope() as session:
            for datum in request.data:
                session.add(
                    DebugData(
                        experiment_id=datum.experiment_id,
                        participant_id=datum.participant_id,
                        now=to_aware_datetime(datum.now),
                        first_seen=to_aware_datetime(datum.first_seen),
                        last_seen=to_aware_datetime(datum.last_seen),
                        tx_powers=",".join(map(str, datum.tx_powers)),
                        rssis=",".join(map(str, datum.rssis)),
                        duration=datum.duration,
                        distance=datum.distance,
                        temporary_id=datum.temporary_id,
                        strand_ids=",".join(map(str, datum.strand_ids)),
                    )
                )
        return sb_pb2.Empty()


class SafeBluesStatsServicer(sb_pb2_grpc.SafeBluesStatsServicer):
    def AllStats(self, request, context):
        with session_scope() as session:
            raise NotImplementedError("NI")
            return sb_pb2.AllStatsRes(
                stats=[
                    sb_pb2.StatsRes(
                        strand_id=1,
                        times=[timestamp_from_datetime(datetime.datetime.now())],
                        total_incubating_strands=[5],
                        total_infected_strands=[3],
                        total_removed_strands=[2],
                    )
                ]
            )

    def Stats(self, request, context):
        with session_scope() as session:
            date_ = func.date_trunc("day", Report.time_received)

            stats = (
                session.query(date_, func.sum(StrandInReport.state))
                .join(StrandInReport, StrandInReport.report_id == Report.report_id)
                .filter(StrandInReport.strand_id == request.strand_id)
                .group_by(date_)
                .all()
            )

            return sb_pb2.StatsRes(
                strand_id=1,
                times=[timestamp_from_datetime(datetime.datetime.now())],
                total_incubating_strands=[6],
                total_infected_strands=[3],
                total_removed_strands=[2],
            )

    def DebugInfo(self, request, context):
        with session_scope() as session:
            output = "experiment_id,participant_id,now,first_seen,last_seen,tx_powers,rssis,duration,distance,temporary_id,strand_ids\n"
            for d in session.query(DebugData).all():
                output += f"\"{d.experiment_id}\",\"{d.participant_id}\",\"{d.now}\",\"{d.first_seen}\",\"{d.last_seen}\",\"{d.tx_powers}\",\"{d.rssis}\",\"{d.duration}\",\"{d.distance}\",\"{d.temporary_id.strip()}\",\"{d.strand_ids}\"\n"
        return httpbody_pb2.HttpBody(
            content_type="text/plain",
            data=output.encode("utf8"),
        )


Base.metadata.create_all(get_engine())

server = grpc.server(futures.ThreadPoolExecutor(1))
server.add_insecure_port("[::]:5858")
logging.info(f"Added insecure port on 5858")

sb_pb2_grpc.add_SafeBluesAdminServicer_to_server(SafeBluesAdminServicer(), server)
sb_pb2_grpc.add_SafeBluesServicer_to_server(SafeBluesServicer(), server)
sb_pb2_grpc.add_SafeBluesStatsServicer_to_server(SafeBluesStatsServicer(), server)
server.start()
server.wait_for_termination()
