from __future__ import print_function

import logging

import grpc
import chat_pb2
import chat_pb2_grpc
import time

# use python-mp for true concurrency: this calls fork()
import threading as mp
from tkinter import *
from tkinter import simpledialog

import wire_protocol as wp

ADDRESS =  "localhost" # "10.250.240.43"
PORT = 50051

class ClientApplication:
    def __init__(self, 
                 use_grpc, # If True, use grpc, if False, use sockets
                 username, 
                 password, 
                 fullname,
                 address, 
                 port,
                 application_window,
                 token=None,
                 account_status="yes"):
        
        self.use_grpc = use_grpc
        # save user metadata
        self.username = username
        self.password = password
        self.fullname = fullname
        
        # store application window object
        self.application_window = application_window
        self.messages = []
        
        # save server address
        self.address = address
        self.port = port
        
        # create channel
        if self.use_grpc:
            self.channel = grpc.insecure_channel(f"{self.address}:{self.port}")
            self.client_stub = chat_pb2_grpc.ChatServerStub(self.channel)
            self.message_creator = chat_pb2
        else:
            self.message_creator = wp.encode
            self.client_stub = wp.client_stub.ChatServerStub(self.address, self.port)
        
        # get token if there is none
        self.token = token
        if self.token == None:
            resp = None
            if account_status == "no":
                create_msg = self.message_creator.AccountCreateRequest(
                    version=1,
                    username=self.username,
                    password=self.password,
                    fullname=self.fullname
                )
                resp = self.client_stub.CreateAccount(create_msg)
            else:
                login_msg = self.message_creator.LoginRequest(version=1,
                                                username=self.username,
                                                password=self.password)
                resp = self.client_stub.Login(login_msg)
            
            if len(resp.error_code) > 0:
                print(resp.error_code)
                raise ValueError("Invalid Credentials, Please Restart")

            else:
                self.token = resp.auth_token
        
    def start(self):
        # TODO: Implement this!!!
        mp.Thread(target=self.listen_loop, daemon=True).start()
        self.interface_setup()
        self.application_window.mainloop()
        
    
    def listen_loop(self):
        if self.use_grpc:
            auth_msg_request = self.message_creator.RefreshRequest(version=1, 
                                                    auth_token=self.token,
                                                    username=self.username)
            
            for msg in self.client_stub.DeliverMessages(auth_msg_request):
                self.messages.insert(END, msg.message)
        else:
            while True:
                auth_msg_request = self.message_creator.RefreshRequest(version=1, 
                                                        auth_token=self.token,
                                                        username=self.username)
                
                msg = self.client_stub.DeliverMessages(auth_msg_request)
                print(msg, msg.message)
                if not msg.error_code:
                    self.messages.insert(END, msg.message)
                time.sleep(1)

            
    def interface_setup(self):
        
        # setup up the UI for the specific chat inbox
        self.messages = Text()
        self.messages.pack(side=TOP)
        
        # display the username for the current applicant
        self.display_username = Label(self.application_window, text=self.username)
        self.display_username.pack(side=LEFT)
        
        # Recipient input
        self.recp_input = Entry(self.application_window, bd=2)
        self.recp_input.insert(0, "Recipient Input.")
        self.recp_input.focus()
        self.recp_input.pack(side=LEFT)
        
        # input for entering messages
        self.message_input = Entry(self.application_window, bd=7)
        self.message_input.insert(0, "Sample Message")
        self.message_input.bind('<Return>', self.enter_command)
        self.message_input.focus()
        self.message_input.pack(side=BOTTOM)
        
        # type input
        self.type_input = Entry(self.application_window, bd=2)
        self.type_input.focus()
        self.type_input.insert(0, "LIST, MSG, DELETE")
        self.type_input.pack(side=RIGHT)
        self.type_input.bind('<Return>', self.enter_command)
        
    def enter_command(self, event):
        """
        This method is called when user enters something into the textbox
        """
        cmd_type = self.type_input.get()
        
        if cmd_type == "MSG":
            msg = self.message_input.get()
            recp = self.recp_input.get()
            # TODO put checking of size of message here
            msg_packet = self.message_creator.MessageRequest(version=1,
                                                 auth_token=self.token,
                                                 message=msg,
                                                 username=self.username,
                                                 recipient_username=recp)
            gui_msg_string = f"[me -> {recp}] {msg}\n"
            self.messages.insert(END, gui_msg_string)
            self.client_stub.SendMessage(msg_packet)
        
        if cmd_type == "LIST":
            recp = self.recp_input.get()
            list_packet = self.message_creator.ListAccountRequest(
                version=1,
                auth_token=self.token,
                username=self.username,
                number_of_accounts=100, # TODO currently not used
                regex=recp
            )
            
            resp = self.client_stub.ListAccounts(list_packet)
            self.messages.insert(END, resp.account_names + "\n")
            
        if cmd_type == "DELETE":
            del_packet = self.message_creator.DeleteAccountRequest(version=1,
                                                       auth_token=self.token,
                                                       username=self.username)
            resp = self.client_stub.DeleteAccount(del_packet)
            
            if len(resp.error_code) == 0:
                self.messages.insert(END, "Account Deleted")
            else:
                self.messages.insert(END, resp.error_code)
            
        # TODO as of now, no error checking is occruing on whether the packet is even being returned correctly
        
        
def run():
    use_grpc = None
    while not (use_grpc == "y" or use_grpc == "n"):
        use_grpc = input("Use grpc? (y/n): ")
    use_grpc = (use_grpc == "y")
    print(f"use_grpc: {use_grpc}")

    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    root = Tk()  # I just used a very simple Tk window for the chat UI, this can be replaced by anything
    frame = Frame(root, width=300, height=300)
    frame.pack()
    root.withdraw()
    
    account_status = None
    username = None
    password = None
    fullname = None
    while account_status is None:
        account_status = simpledialog.askstring("Returning User?", "Do you have an account? (yes/no)", parent=root)
    
    while username is None and password is None and fullname is None:
        username = simpledialog.askstring("Username", "Choose your username", parent=root)
        password = simpledialog.askstring("Password", "Type in a Password.", parent=root)
        fullname = simpledialog.askstring("Full Name", "Type Full Name.", parent=root)

    root.deiconify() 
    
    app = ClientApplication(
                      use_grpc=use_grpc,
                      username=username,
                      password=password,
                      fullname=fullname,
                      account_status=account_status,
                      address=ADDRESS,
                      port=PORT,
                      application_window=frame) 

    app.start()

if __name__ == '__main__':
    logging.basicConfig()
    run()