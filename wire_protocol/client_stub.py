import socket
from . import socket_types

class ChatServerStub:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sck.connect((host,port))

    def CreateAccount(self, create_account_request):
        self.sck.send(create_account_request)
        create_account_bytes = self.sck.recv(1024)
        return socket_types.AccountCreateReply(create_account_bytes)
    
    def Login(self, login_request):
        self.sck.send(login_request)
        login_reply_bytes = self.sck.recv(1024)
        return socket_types.LoginReply(login_reply_bytes)
    
    def SendMessage(self, message_request):
        self.sck.send(message_request)
        message_reply_bytes = self.sck.recv(1024)
        return socket_types.MessageReply(message_reply_bytes)
    
    def ListAccounts(self, list_account_request):
        self.sck.send(list_account_request)
        list_account_reply_bytes = self.sck.recv(1024)
        return socket_types.ListAccountReply(list_account_reply_bytes)
    
    def DeleteAccount(self, delete_account_request):
        self.sck.send(delete_account_request)
        delete_account_reply_bytes = self.sck.recv(1024)
        return socket_types.DeleteAccountReply(delete_account_reply_bytes)

    def DeliverMessages(self, refresh_request):
        self.sck.send(refresh_request)
        refresh_reply_bytes = self.sck.recv(1024)
        return socket_types.RefreshReply(refresh_reply_bytes)