from concurrent import futures
import logging
from collections import defaultdict
from uuid import uuid4
import binascii
import os
import re

from datetime import timezone
import datetime

import grpc
import chat_pb2
import chat_pb2_grpc


class ChatServer(chat_pb2_grpc.ChatServerServicer):
    def __init__(self) -> None:
        super().__init__()
        self.user_inbox = defaultdict(lambda: [])
        
        # format of metadata store
        # key - username (must be unique)
        # per value entry (password, name)
        self.user_metadata_store = {}
        self.token_length = 15
        
        # token hub keys are usernames and the values are token, timestamp pairs
        self.token_hub = {}
        
        # keeping track of time by standardizing to UTC
        self.utc_time_gen = datetime.datetime
        
    def ValidatePassword(self, password):
        if type(password) != str:
            return -1
        else:
            return 0
        
    def GenerateToken(self):
        token = os.urandom(self.token_length)
        return binascii.hexlify(token).decode()
    
    def ValidateToken(self, username, token):
        if username not in self.token_hub.keys():
            return -1
        
        stored_token, timestamp = self.token_hub[username]
        
        if stored_token != token:
            return -1
        
        duration = self.utc_time_gen.now().timestamp() - timestamp
        duration_in_hr = duration / 3600
        
        if duration_in_hr > 1.0:
            return -1
        
        return 0

    def SendMessage(self, request, context):
        print(request)
        token = request.auth_token
        username = request.username
        recipient = request.recipient_username
        if self.ValidateToken(username=username,
                              token=token) < 0:
            return chat_pb2.MessageReply(version=1,
                                         error_code="Invalid Token")
        
        message_string = request.message
        modified_string = f"[{username}]: {message_string}"
        if recipient not in self.user_inbox.keys():
            return chat_pb2.MessageReply(version=1,
                                         error_code="Invalid Recipient")
        self.user_inbox[recipient].append(modified_string)
        return chat_pb2.MessageReply(version=1, error_code="")

    def DeliverMessages(self, request, context):
        print(request)
        # every client will end up running this
        while True:
            token = request.auth_token
            username = request.username
            if self.ValidateToken(username=username,
                                token=token) < 0:
                return chat_pb2.RefreshReply(version=1,
                                             error_code="Invalid Token")
            # Check if there are any new messages
            while len(self.user_inbox[username]) > 0:
                msg = self.user_inbox[username].pop(0)
                yield chat_pb2.RefreshReply(version=1, 
                                            error_code="",
                                            message=msg)

    def Login(self, request, context):
        print(request)
        # get the given username and do basic error checking
        username = request.username
        if username not in self.user_metadata_store.keys():
            return chat_pb2.LoginReply(
                                error_code="ERROR Username Invalid",
                                auth_token="",
                                fullname="")
            
        # basic password match
        password = request.password
        if password != self.user_metadata_store[username][0]:
            return chat_pb2.LoginReply(
                                error_code="ERROR Password Invalid",
                                auth_token="",
                                fullname="")
        
        # generate new token
        token = self.GenerateToken()
        timestamp = self.utc_time_gen.now().timestamp()
        
        # register token in token hub
        self.token_hub[username] = (token, timestamp)
        return chat_pb2.LoginReply(version=1,
                                   error_code="",
                                   auth_token=token,
                                   fullname=self.user_metadata_store[username][1])

    def CreateAccount(self, request, context):
        print(request)
        # get the given username and do basic error checking
        username = request.username
        if username in self.user_metadata_store.keys():
            return chat_pb2.AccountCreateReply(version=1, 
                                error_code="ERROR Username Already Exists",
                                auth_token="",
                                fullname="")
        
        # get the password and do basic error checking
        password = request.password
        if self.ValidatePassword(password) < 0:
            return chat_pb2.AccountCreateReply(version=1, 
                                error_code="ERROR Invalid Passcode",
                                auth_token="",
                                fullname="")
        
        # prepare metadata
        fullname = request.fullname
        token = self.GenerateToken()
        timestamp = self.utc_time_gen.now().timestamp()
        
        # create user metadata
        self.user_metadata_store[username] = (password, fullname)
        # create user chat inbox
        self.user_inbox[username] = []
        # register user in token hub / stores last given token
        self.token_hub[username] = (token, timestamp)
        
        return chat_pb2.AccountCreateReply(version=1,
                                           error_code="",
                                           auth_token=token,
                                           fullname=fullname)
        

    def ListAccounts(self, request, context):
        print(request)
        token = request.auth_token
        username = request.username
        if self.ValidateToken(username=username,
                              token=token) < 0:
            return chat_pb2.ListAccountReply(version=1,
                                             error_code="Invalid token",
                                             account_names="")
        list_of_usernames = self.user_metadata_store.keys()
        
        filtered_list = list_of_usernames
        # search using filter
        regex = request.regex
        if len(regex) != 0:
            r = re.compile(f".*{regex}")
            # filter based on compiled regex
            filtered_list = list(filter(r.match, list_of_usernames))
        filtered_string = ", ".join(filtered_list[:100])
        
        return chat_pb2.ListAccountReply(version=1,
                                         error_code="",
                                         account_names=filtered_string)
        
    def DeleteAccount(self, request, context):
        token = request.auth_token
        username = request.username
        if self.ValidateToken(username=username,
                              token=token) < 0:
            return chat_pb2.DeleteAccountReply(version=1,
                                             error_code="Invalid token")
            
        # delete all relevant metadata
        self.token_hub.pop(username)
        self.user_inbox.pop(username)
        self.user_metadata_store.pop(username)
        
        return chat_pb2.DeleteAccountReply(version=1,
                                           error_code="")
        
        
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