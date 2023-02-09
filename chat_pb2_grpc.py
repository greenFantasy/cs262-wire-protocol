# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chat_pb2 as chat__pb2


class ChatServerStub(object):
    """The greeting service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SayHello = channel.unary_unary(
                '/helloworld.ChatServer/SayHello',
                request_serializer=chat__pb2.MessageRequest.SerializeToString,
                response_deserializer=chat__pb2.MessageReply.FromString,
                )
        self.SayHelloStreamReply = channel.unary_stream(
                '/helloworld.ChatServer/SayHelloStreamReply',
                request_serializer=chat__pb2.MessageRequest.SerializeToString,
                response_deserializer=chat__pb2.MessageReply.FromString,
                )


class ChatServerServicer(object):
    """The greeting service definition.
    """

    def SayHello(self, request, context):
        """Sends a greeting
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SayHelloStreamReply(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SayHello': grpc.unary_unary_rpc_method_handler(
                    servicer.SayHello,
                    request_deserializer=chat__pb2.MessageRequest.FromString,
                    response_serializer=chat__pb2.MessageReply.SerializeToString,
            ),
            'SayHelloStreamReply': grpc.unary_stream_rpc_method_handler(
                    servicer.SayHelloStreamReply,
                    request_deserializer=chat__pb2.MessageRequest.FromString,
                    response_serializer=chat__pb2.MessageReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'helloworld.ChatServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatServer(object):
    """The greeting service definition.
    """

    @staticmethod
    def SayHello(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/helloworld.ChatServer/SayHello',
            chat__pb2.MessageRequest.SerializeToString,
            chat__pb2.MessageReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SayHelloStreamReply(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/helloworld.ChatServer/SayHelloStreamReply',
            chat__pb2.MessageRequest.SerializeToString,
            chat__pb2.MessageReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)