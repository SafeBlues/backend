import enum

import sb_pb2
from sqlalchemy import (Column, DateTime, Enum, Float, ForeignKey, Integer,
                        String, Table)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from utils import timestamp_from_datetime

Base = declarative_base()

class StrandStatus(enum.Enum):
    incubating = 1
    infected = 2
    removed = 3

class StrandInReport(Base):
    __tablename__ = "strands_in_report"
    id = Column(Integer, primary_key=True)

    state = Column(Enum(StrandStatus), nullable=False)
    report_id = Column(ForeignKey("reports.report_id"), nullable=False)
    strand_id = Column(ForeignKey("strands.strand_id"), nullable=False)

class Strand(Base):
    __tablename__ = "strands"

    strand_id = Column(Integer, primary_key=True)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    seeding_probability = Column(Float, nullable=False)
    infection_probability = Column(Float, nullable=False)

    incubation_period_days = Column(Float, nullable=False)
    infectious_period_days = Column(Float, nullable=False)

    def to_pb(self) -> sb_pb2.Strand:
        return sb_pb2.Strand(
            strand_id=self.strand_id,
            start_time=timestamp_from_datetime(self.start_time),
            end_time=timestamp_from_datetime(self.end_time),
            seeding_probability=self.seeding_probability,
            infection_probability=self.infection_probability,
            incubation_period_days=self.incubation_period_days,
            infectious_period_days=self.infectious_period_days,
        )

    @classmethod
    def from_pb(cls, strand: sb_pb2.Strand):
        return cls(
            # NOTE: strand_id == 0 => None
            strand_id=strand.strand_id if strand.strand_id != 0 else None,
            start_time=strand.start_time.ToDatetime(),
            end_time=strand.end_time.ToDatetime(),
            seeding_probability=strand.seeding_probability,
            infection_probability=strand.infection_probability,
            incubation_period_days=strand.incubation_period_days,
            infectious_period_days=strand.infectious_period_days
        )

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True)

    client_id = Column(String)

    time_received = Column(DateTime, nullable=False, default=func.now())

    strands = relationship("StrandInReport")
