import datetime
import time
from contextlib import contextmanager

import sb_pb2
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


engine = create_engine(f"sqlite:///db.sqlite")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def new_strand(strand: sb_pb2.Strand) -> sb_pb2.Strand:
    with session_scope(Session) as session:
        s = Strand(
            start_time=strand.start_time.ToDatetime(),
            end_time=strand.end_time.ToDatetime(),
            seeding_probability=strand.seeding_probability,
            infection_probability=strand.infection_probability,
            incubation_period_days=strand.incubation_period_days,
            infectious_period_days=strand.infectious_period_days
        )
        session.add(s)
        return sb_pb2.Strand(
            strand_id=s.strand_id,
            start_time=timestamp_from_datetime(s.start_time),
            end_time=timestamp_from_datetime(s.end_time),
            seeding_probability=s.seeding_probability,
            infection_probability=s.infection_probability,
            incubation_period_days=s.incubation_period_days,
            infectious_period_days=s.infectious_period_days,
        )

def new_report(report: sb_pb2.InfectionReport):
    with session_scope(Session) as session:
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

def get_update() -> sb_pb2.StrandUpdate:
    with session_scope(Session) as session:
        return sb_pb2.StrandUpdate(
            strands=[
                sb_pb2.Strand(
                    strand_id=s.strand_id,
                    start_time=timestamp_from_datetime(s.start_time),
                    end_time=timestamp_from_datetime(s.end_time),
                    seeding_probability=s.seeding_probability,
                    infection_probability=s.infection_probability,
                    incubation_period_days=s.incubation_period_days,
                    infectious_period_days=s.infectious_period_days,
                ) for s in session.query(Strand) \
                            .filter(Strand.start_time < datetime.datetime.now() - datetime.timedelta(days=2)) \
                            .filter(Strand.end_time > datetime.datetime.now()) \
                            .all()
            ]
        )

new_strand(sb_pb2.Strand(
    start_time=timestamp_from_datetime(datetime.datetime.now() - datetime.timedelta(days=2)),
    end_time=timestamp_from_datetime(datetime.datetime.now() + datetime.timedelta(days=2)),
    seeding_probability=0.1,
    infection_probability=0.5,
    incubation_period_days=2,
    infectious_period_days=5
))

new_strand(sb_pb2.Strand(
    start_time=timestamp_from_datetime(datetime.datetime.now() - datetime.timedelta(days=0)),
    end_time=timestamp_from_datetime(datetime.datetime.now() + datetime.timedelta(days=3)),
    seeding_probability=0.2,
    infection_probability=0.1,
    incubation_period_days=1,
    infectious_period_days=4
))

new_strand(sb_pb2.Strand(
    start_time=timestamp_from_datetime(datetime.datetime.now() - datetime.timedelta(days=5)),
    end_time=timestamp_from_datetime(datetime.datetime.now() - datetime.timedelta(days=1)),
    seeding_probability=0.2,
    infection_probability=0.1,
    incubation_period_days=1,
    infectious_period_days=4
))

new_report(sb_pb2.InfectionReport(
    client_id="test",
    current_incubating_strands=[1],
    current_infected_strands=[2],
    current_removed_strands=[3]
))

print(get_update())
