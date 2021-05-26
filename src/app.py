import datetime
import functools
import logging
import os
import time
from concurrent import futures
from contextlib import contextmanager
from os import environ

import grpc
from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session

import sb_pb2
import sb_pb2_grpc
from models import Base, Report, Strand, StrandInReport, StrandSocialDistancing, StrandStatus
from utils import timestamp_from_datetime

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


def _get_strand_update():
    with session_scope() as session:
        strands = [s.to_pb() for s in session.query(Strand).all()]
        sds = [s.to_pb() for s in session.query(StrandSocialDistancing).all()]
        return sb_pb2.StrandUpdate(
            strands=strands,
            sds=sds,
            latest_app_version=max([strand.minimum_app_version or 0 for strand in strands]),
        )


class SafeBluesAdminServicer(sb_pb2_grpc.SafeBluesAdminServicer):
    def NewStrand(self, request, context):
        with session_scope() as session:
            s = Strand.from_pb(request)
            session.add(s)
            session.commit()
            return s.to_pb()

    def ListStrands(self, request, context):
        return _get_strand_update()


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
        _get_strand_update()


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


Base.metadata.create_all(get_engine())

server = grpc.server(futures.ThreadPoolExecutor(1))
server.add_insecure_port("[::]:5858")
logging.info(f"Added insecure port on 5858")

sb_pb2_grpc.add_SafeBluesAdminServicer_to_server(SafeBluesAdminServicer(), server)
sb_pb2_grpc.add_SafeBluesServicer_to_server(SafeBluesServicer(), server)
sb_pb2_grpc.add_SafeBluesStatsServicer_to_server(SafeBluesStatsServicer(), server)
server.start()
server.wait_for_termination()
