import datetime
from os import environ

import grpc
import sb_pb2
import sb_pb2_grpc
from utils import timestamp_from_datetime

if environ.get("SB_SECURE_CLIENT", None):
    channel = grpc.secure_channel("api.safeblues.org:8443", grpc.ssl_channel_credentials())
else:
    channel = grpc.insecure_channel("localhost:5858")

client_stub = sb_pb2_grpc.SafeBluesStub(channel)
admin_client_stub = sb_pb2_grpc.SafeBluesAdminStub(channel)

print(client_stub.PingServer(sb_pb2.Ping(nonce=12345)))

admin_client_stub.NewStrand(sb_pb2.Strand(
    start_time=timestamp_from_datetime(datetime.datetime.utcnow() - datetime.timedelta(days=2)),
    end_time=timestamp_from_datetime(datetime.datetime.utcnow() + datetime.timedelta(days=2)),
    seeding_probability=0.1,
    infection_probability=0.5,
    incubation_period_days=2,
    infectious_period_days=5
))

admin_client_stub.NewStrand(sb_pb2.Strand(
    start_time=timestamp_from_datetime(datetime.datetime.utcnow() - datetime.timedelta(days=0)),
    end_time=timestamp_from_datetime(datetime.datetime.utcnow() + datetime.timedelta(days=3)),
    seeding_probability=0.2,
    infection_probability=0.1,
    incubation_period_days=1,
    infectious_period_days=4
))

admin_client_stub.NewStrand(sb_pb2.Strand(
    start_time=timestamp_from_datetime(datetime.datetime.utcnow() - datetime.timedelta(days=5)),
    end_time=timestamp_from_datetime(datetime.datetime.utcnow() - datetime.timedelta(days=1)),
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
