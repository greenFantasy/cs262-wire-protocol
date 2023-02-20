import socket
from collections import defaultdict
import datetime
import threading as mp
import os
import binascii
import re

import wire_protocol as wp
socket.setdefaulttimeout(60 * 60)

class ChatServer:
    def __init__(self):
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
    
    def generate_token(self):
        token = os.urandom(self.token_length)
        return binascii.hexlify(token).decode()
    
    def validate_password(self, password):
        if type(password) != str:
            return -1
        else:
            return 0
    
    def validate_token(self, username, token):
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

    def create_account(self, raw_bytes):
        request = wp.socket_types.AccountCreateRequest(raw_bytes)
        if request.generated_error_code:
            return wp.encode.AccountCreateReply(version=1,
                                error_code=request.generated_error_code,
                                auth_token="",
                                fullname="")

        username = request.username
        if username in self.user_metadata_store.keys():
            return wp.encode.AccountCreateReply(version=1,
                                error_code="ERROR Username Already Exists",
                                auth_token="",
                                fullname="")
        
        # get the password and do basic error checking
        password = request.password
        if self.validate_password(password) < 0:
            return wp.encode.AccountCreateReply(version=1,
                                error_code="ERROR Invalid Passcode",
                                auth_token="",
                                fullname="")
        
        # prepare metadata
        fullname = request.fullname
        token = self.generate_token()
        timestamp = self.utc_time_gen.now().timestamp()
        
        # create user metadata
        self.user_metadata_store[username] = (password, fullname)
        # create user chat inbox
        self.user_inbox[username] = []
        # register user in token hub / stores last given token
        self.token_hub[username] = (token, timestamp)
        
        return wp.encode.AccountCreateReply(version=1,
                                           error_code="",
                                           auth_token=token,
                                           fullname=fullname)
    
    def login(self, raw_bytes):
        request = wp.socket_types.LoginRequest(raw_bytes)

        # get the given username and do basic error checking
        username = request.username
        if username not in self.user_metadata_store.keys():
            return wp.encode.LoginReply(version=1,
                                error_code="ERROR Username Invalid",
                                auth_token="",
                                fullname="")
            
        # basic password match
        password = request.password
        if password != self.user_metadata_store[username][0]:
            return wp.encode.LoginReply(version=1,
                                error_code="ERROR Password Invalid",
                                auth_token="",
                                fullname="")
        
        # generate new token
        token = self.generate_token()
        timestamp = self.utc_time_gen.now().timestamp()
        
        # register token in token hub
        self.token_hub[username] = (token, timestamp)
        return wp.encode.LoginReply(version=1,
                                   error_code="",
                                   auth_token=token,
                                   fullname=self.user_metadata_store[username][1])

    def receive_message(self, raw_bytes):
        request = wp.socket_types.MessageRequest(raw_bytes)

        token = request.auth_token
        username = request.username
        recipient = request.recipient_username
        if self.validate_token(username=username,
                              token=token) < 0:
            return wp.encode.MessageReply(version=1,
                                         error_code="Invalid Token")
        
        message_string = request.message
        modified_string = f"[{username}]: {message_string}"
        if recipient not in self.user_inbox.keys():
            return wp.encode.MessageReply(version=1,
                                         error_code="Invalid Recipient")
        self.user_inbox[recipient].append(modified_string)
        return wp.encode.MessageReply(version=1, error_code="")

    def list_accounts(self, raw_bytes):
        request = wp.socket_types.ListAccountRequest(raw_bytes)

        token = request.auth_token
        username = request.username
        if self.validate_token(username=username,
                              token=token) < 0:
            return wp.encode.ListAccountReply(version=1,
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
        
        return wp.encode.ListAccountReply(version=1,
                                          error_code="",
                                          account_names=filtered_string)
    
    def delete_account(self, raw_bytes):
        request = wp.socket_types.DeleteAccountRequest(raw_bytes)

        token = request.auth_token
        username = request.username
        if self.validate_token(username=username,
                              token=token) < 0:
            return wp.encode.DeleteAccountReply(version=1,
                                                error_code="Invalid token")
            
        # delete all relevant metadata
        self.token_hub.pop(username)
        self.user_inbox.pop(username)
        self.user_metadata_store.pop(username)
        
        return wp.encode.DeleteAccountReply(version=1, 
                                            error_code="")
    
    def deliver_messages(self, raw_bytes):
        request = wp.socket_types.RefreshRequest(raw_bytes)

        while True:
            token = request.auth_token
            username = request.username
            if self.validate_token(username=username,
                                token=token) < 0:
                return wp.encode.RefreshReply(version=1,
                                              message="",
                                              error_code="Invalid Token"
                                             )
            # Check if there are any new messages
            while len(self.user_inbox[username]) > 0:
                msg = self.user_inbox[username].pop(0)
                yield wp.encode.RefreshReply(version=1, 
                                            message=msg,
                                            error_code="",
                                            )


    def handle_new_connection(self, c : socket.socket, addr):

        # TODO: Protect against crashing if client violently disconnects
        while True:
            data = c.recv(1024)
            decoded = ""
            try:
                decoded = data.decode("UTF-8")
            except UnicodeDecodeError:
                print("Unable to decode the message")
                c.close()

            args = decoded.split("||")
            if len(args) == 0:
                c.close()
                return 

            try:
                opcode = int(args[0])
            except ValueError:
                opcode = -1

            opcode_map = {
                0: self.create_account,
                1: self.login,
                2: self.receive_message,
                3: self.list_accounts,
                4: self.delete_account
            }

            if opcode in opcode_map.keys():
                result = opcode_map[opcode](data)
                print(f"Sending status message to {addr}")
                c.send(result)
            else:
                # Invalid opcodes are dropped immediately, invalid opcodes
                #  occur when a connection is being closed by the client,
                #  or when a malicious / corrupted message is being sent
                c.close()
                return
                
if __name__ == "__main__":

    chatServer = ChatServer()

    host = "0.0.0.0"
    port = 2048

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))

    print("socket binded to port", port)

    # put the socket into listening mode
    s.listen(10)
    print("socket is listening")

    while True:
        # establish connection with client
        c, addr = s.accept()      
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        mp.Thread(target=chatServer.handle_new_connection, daemon=False, args=(c,addr)).start()