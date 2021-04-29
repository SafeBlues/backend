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

    name = Column(String, unique=True, nullable=True)
    minimum_app_version = Column(Integer, nullable=True)

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    seeding_probability = Column(Float, nullable=False)

    infection_probability_map_p = Column(Float, nullable=False)
    infection_probability_map_l = Column(Float, nullable=False)
    infection_probability_map_k = Column(Float, nullable=False)

    incubation_period_mean_sec = Column(Float, nullable=False)
    incubation_period_shape = Column(Float, nullable=False)
    infectious_period_mean_sec = Column(Float, nullable=False)
    infectious_period_shape = Column(Float, nullable=False)

    def to_pb(self) -> sb_pb2.Strand:
        return sb_pb2.Strand(
            name=self.name,
            minimum_app_version=self.minimum_app_version,
            strand_id=self.strand_id,
            start_time=timestamp_from_datetime(self.start_time),
            end_time=timestamp_from_datetime(self.end_time),
            seeding_probability=self.seeding_probability,
            infection_probability_map_p=self.infection_probability_map_p,
            infection_probability_map_k=self.infection_probability_map_k,
            infection_probability_map_l=self.infection_probability_map_l,
            incubation_period_mean_sec=self.incubation_period_mean_sec,
            incubation_period_shape=self.incubation_period_shape,
            infectious_period_mean_sec=self.infectious_period_mean_sec,
            infectious_period_shape=self.infectious_period_shape,
        )

    @classmethod
    def from_pb(cls, strand: sb_pb2.Strand):
        return cls(
            # NOTE: strand_id == 0 => None
            name=strand.name if strand.name else None,
            minimum_app_version=strand.minimum_app_version if strand.minimum_app_version != 0 else None,
            strand_id=strand.strand_id if strand.strand_id != 0 else None,
            start_time=strand.start_time.ToDatetime(),
            end_time=strand.end_time.ToDatetime(),
            seeding_probability=strand.seeding_probability,
            infection_probability_map_p=strand.infection_probability_map_p,
            infection_probability_map_k=strand.infection_probability_map_k,
            infection_probability_map_l=strand.infection_probability_map_l,
            incubation_period_mean_sec=strand.incubation_period_mean_sec,
            incubation_period_shape=strand.incubation_period_shape,
            infectious_period_mean_sec=strand.infectious_period_mean_sec,
            infectious_period_shape=strand.infectious_period_shape,
        )

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True)

    client_id = Column(String)

    time_received = Column(DateTime(timezone=True), nullable=False, default=func.now())

    strands = relationship("StrandInReport")

    version_code = Column(Integer)
