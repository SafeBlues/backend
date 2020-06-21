import datetime
import time
from concurrent import futures
from contextlib import contextmanager

import grpc
import sb_pb2
import sb_pb2_grpc
from models import Base, Report, Strand, StrandInReport, StrandStatus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import timestamp_from_datetime


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
            return s.to_pb()


class SafeBluesServicer(sb_pb2_grpc.SafeBluesServicer):
    def __init__(self, Session):
        self._Session = Session

    def Report(self, request, context):
        report = request
        with session_scope(self._Session) as session:
            r = Report(
                client_id=report.client_id,
                strands=[
                    StrandInReport(
                        state=StrandStatus.incubating,
                        strand_id=strand_id
                    ) for strand_id in report.current_incubating_strands
                ] + [
                    StrandInReport(
                        state=StrandStatus.infected,
                        strand_id=strand_id
                    ) for strand_id in report.current_infected_strands
                ] + [
                    StrandInReport(
                        state=StrandStatus.removed,
                        strand_id=strand_id
                    ) for strand_id in report.current_removed_strands
                ]
            )
            session.add(r)
        return sb_pb2.Empty()

    def Pull(self, request, context):
        with session_scope(self._Session) as session:
            return sb_pb2.StrandUpdate(
                strands=[
                    s.to_pb() for s in session.query(Strand) \
                        .filter(Strand.start_time < datetime.datetime.now() - datetime.timedelta(days=2)) \
                        .filter(Strand.end_time > datetime.datetime.now()) \
                        .all()
                ]
            )


engine = create_engine(f"sqlite:///db.sqlite")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

server = grpc.server(futures.ThreadPoolExecutor(1))
server.add_insecure_port("[::]:5858")
sb_pb2_grpc.add_SafeBluesAdminServicer_to_server(SafeBluesAdminServicer(Session), server)
sb_pb2_grpc.add_SafeBluesServicer_to_server(SafeBluesServicer(Session), server)
server.start()
print(f"Serving on 5858")
server.wait_for_termination()