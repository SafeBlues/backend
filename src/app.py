import datetime
import logging
import time
from concurrent import futures
from contextlib import contextmanager
from os import environ

import grpc
import sb_pb2
import sb_pb2_grpc
from models import Base, Report, Strand, StrandInReport, StrandStatus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import timestamp_from_datetime

logging.basicConfig(format="%(asctime)s.%(msecs)03d: %(process)d: %(message)s", datefmt="%F %T", level=logging.INFO)

@contextmanager
def session_scope(Session):
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class SafeBluesAdminServicer(sb_pb2_grpc.SafeBluesAdminServicer):
    def __init__(self, Session):
        self._Session = Session

    def NewStrand(self, request, context):
        with session_scope(self._Session) as session:
            s = Strand.from_pb(request)
            session.add(s)
            session.commit()
            return s.to_pb()

    def ListStrands(self, request, context):
        with session_scope(self._Session) as session:
            return sb_pb2.StrandUpdate(
                strands=[
                    s.to_pb() for s in session.query(Strand) \
                        .all()
                ]
            )


class SafeBluesServicer(sb_pb2_grpc.SafeBluesServicer):
    def __init__(self, Session):
        self._Session = Session

    def PingServer(self, request, context):
        logging.info(f"Got PingServer with nonce={request.nonce}")
        return sb_pb2.Ping(nonce=request.nonce)

    def Report(self, request, context):
        report = request
        with session_scope(self._Session) as session:
            incubating_strands = [
                StrandInReport(
                    state=StrandStatus.incubating,
                    strand_id=strand_id
                ) for strand_id in report.current_incubating_strands]
            for strand in incubating_strands:
                session.add(strand)

            infected_strands = [
                StrandInReport(
                    state=StrandStatus.infected,
                    strand_id=strand_id
                ) for strand_id in report.current_infected_strands]
            for strand in infected_strands:
                session.add(strand)

            removed_strands = [
                StrandInReport(
                    state=StrandStatus.removed,
                    strand_id=strand_id
                ) for strand_id in report.current_removed_strands]
            for strand in removed_strands:
                session.add(strand)

            session.add(Report(
                client_id=report.client_id,
                strands=incubating_strands + infected_strands + removed_strands
            ))
        return sb_pb2.Empty()

    def Pull(self, request, context):
        with session_scope(self._Session) as session:
            return sb_pb2.StrandUpdate(
                strands=[
                    s.to_pb() for s in session.query(Strand) \
                        .filter(Strand.start_time < datetime.datetime.utcnow() - datetime.timedelta(days=2)) \
                        .filter(Strand.end_time > datetime.datetime.utcnow()) \
                        .all()
                ]
            )


class SafeBluesStatsServicer(sb_pb2_grpc.SafeBluesStatsServicer):
    def __init__(self, Session):
        self._Session = Session

    def AllStats(self, request, context):
        with session_scope(self._Session) as session:
            raise NotImplementedError("NI")
            return sb_pb2.AllStatsRes(
                stats=[sb_pb2.StatsRes(
                    strand_id=1,
                    times=[timestamp_from_datetime(datetime.datetime.now())],
                    total_incubating_strands=[5],
                    total_infected_strands=[3],
                    total_removed_strands=[2],
                )]
            )

    def Stats(self, request, context):
        with session_scope(self._Session) as session:
            date_ = func.date_trunc("day", Report.time_received)

            stats = (session.query(date_, func.sum(StrandInReport.state))
                .join(StrandInReport, StrandInReport.report_id == Report.report_id)
                .filter(StrandInReport.strand_id == request.strand_id)
                .group_by(date_)
                .all())

            return sb_pb2.StatsRes(
                strand_id=1,
                times=[timestamp_from_datetime(datetime.datetime.now())],
                total_incubating_strands=[6],
                total_infected_strands=[3],
                total_removed_strands=[2],
            )



engine = create_engine(f"sqlite:///db.sqlite")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

server = grpc.server(futures.ThreadPoolExecutor(1))
server.add_insecure_port("[::]:5858")
logging.info(f"Added insecure port on 5858")

sb_pb2_grpc.add_SafeBluesAdminServicer_to_server(SafeBluesAdminServicer(Session), server)
sb_pb2_grpc.add_SafeBluesServicer_to_server(SafeBluesServicer(Session), server)
sb_pb2_grpc.add_SafeBluesStatsServicer_to_server(SafeBluesStatsServicer(Session), server)
server.start()
server.wait_for_termination()
