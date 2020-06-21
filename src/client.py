import datetime

import grpc
import sb_pb2
import sb_pb2_grpc
from utils import timestamp_from_datetime

with grpc.insecure_channel("localhost:5858") as channel:
    client_stub = sb_pb2_grpc.SafeBluesStub(channel)
    admin_client_stub = sb_pb2_grpc.SafeBluesAdminStub(channel)

    admin_client_stub.NewStrand(sb_pb2.Strand(
        start_time=timestamp_from_datetime(datetime.datetime.now() - datetime.timedelta(days=2)),
        end_time=timestamp_from_datetime(datetime.datetime.now() + datetime.timedelta(days=2)),
        seeding_probability=0.1,
        infection_probability=0.5,
        incubation_period_days=2,
        infectious_period_days=5
    ))

    admin_client_stub.NewStrand(sb_pb2.Strand(
        start_time=timestamp_from_datetime(datetime.datetime.now() - datetime.timedelta(days=0)),
        end_time=timestamp_from_datetime(datetime.datetime.now() + datetime.timedelta(days=3)),
        seeding_probability=0.2,
        infection_probability=0.1,
        incubation_period_days=1,
        infectious_period_days=4
    ))

    admin_client_stub.NewStrand(sb_pb2.Strand(
        start_time=timestamp_from_datetime(datetime.datetime.now() - datetime.timedelta(days=5)),
        end_time=timestamp_from_datetime(datetime.datetime.now() - datetime.timedelta(days=1)),
        seeding_probability=0.2,
        infection_probability=0.1,
        incubation_period_days=1,
        infectious_period_days=4
    ))

    client_stub.Report(sb_pb2.InfectionReport(
        client_id="test",
        current_incubating_strands=[1],
        current_infected_strands=[2],
        current_removed_strands=[3]
    ))

    print(client_stub.Pull(sb_pb2.Empty()))