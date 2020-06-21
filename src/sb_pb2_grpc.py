# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import sb_pb2 as sb__pb2


class SafeBluesAdminStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.NewStrand = channel.unary_unary(
                '/sb.SafeBluesAdmin/NewStrand',
                request_serializer=sb__pb2.Strand.SerializeToString,
                response_deserializer=sb__pb2.Strand.FromString,
                )


class SafeBluesAdminServicer(object):
    """Missing associated documentation comment in .proto file"""

    def NewStrand(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SafeBluesAdminServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'NewStrand': grpc.unary_unary_rpc_method_handler(
                    servicer.NewStrand,
                    request_deserializer=sb__pb2.Strand.FromString,
                    response_serializer=sb__pb2.Strand.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'sb.SafeBluesAdmin', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SafeBluesAdmin(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def NewStrand(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sb.SafeBluesAdmin/NewStrand',
            sb__pb2.Strand.SerializeToString,
            sb__pb2.Strand.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)


class SafeBluesStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.PingServer = channel.unary_unary(
                '/sb.SafeBlues/PingServer',
                request_serializer=sb__pb2.Ping.SerializeToString,
                response_deserializer=sb__pb2.Ping.FromString,
                )
        self.Report = channel.unary_unary(
                '/sb.SafeBlues/Report',
                request_serializer=sb__pb2.InfectionReport.SerializeToString,
                response_deserializer=sb__pb2.Empty.FromString,
                )
        self.Pull = channel.unary_unary(
                '/sb.SafeBlues/Pull',
                request_serializer=sb__pb2.Empty.SerializeToString,
                response_deserializer=sb__pb2.StrandUpdate.FromString,
                )


class SafeBluesServicer(object):
    """Missing associated documentation comment in .proto file"""

    def PingServer(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Report(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Pull(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SafeBluesServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'PingServer': grpc.unary_unary_rpc_method_handler(
                    servicer.PingServer,
                    request_deserializer=sb__pb2.Ping.FromString,
                    response_serializer=sb__pb2.Ping.SerializeToString,
            ),
            'Report': grpc.unary_unary_rpc_method_handler(
                    servicer.Report,
                    request_deserializer=sb__pb2.InfectionReport.FromString,
                    response_serializer=sb__pb2.Empty.SerializeToString,
            ),
            'Pull': grpc.unary_unary_rpc_method_handler(
                    servicer.Pull,
                    request_deserializer=sb__pb2.Empty.FromString,
                    response_serializer=sb__pb2.StrandUpdate.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'sb.SafeBlues', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SafeBlues(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def PingServer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sb.SafeBlues/PingServer',
            sb__pb2.Ping.SerializeToString,
            sb__pb2.Ping.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Report(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sb.SafeBlues/Report',
            sb__pb2.InfectionReport.SerializeToString,
            sb__pb2.Empty.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Pull(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sb.SafeBlues/Pull',
            sb__pb2.Empty.SerializeToString,
            sb__pb2.StrandUpdate.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)
