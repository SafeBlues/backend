import enum

from sqlalchemy import (Column, DateTime, Enum, Float, ForeignKey, Integer,
                        String, Table)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

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

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True)

    client_id = Column(String)

    time_received = Column(DateTime, nullable=False, default=func.now())

    strands = relationship("StrandInReport")
