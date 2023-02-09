from concurrent import futures
import logging

import grpc
import chat_pb2
import chat_pb2_grpc


class ChatServer(chat_pb2_grpc.ChatServerServicer):

    def SayHello(self, request, context):
        return chat_pb2.MessageReply(message='Hello, %s!' % request.name)


def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServerServicer_to_server(ChatServer(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()