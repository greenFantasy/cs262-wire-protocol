from client import ClientApplication
from socket_server import ChatServer
from concurrent import futures
import signal
import os
import sys
from colorama import Fore, Style
import grpc
import chat_pb2
import chat_pb2_grpc
import time
import socket

import threading as th
import multiprocessing as mp
from tkinter import *


PORT = 50051



def run_client_thread(username, password, fullname, account_status="no"):
    root = Tk()
    frame = Frame(root, width=300, height=300)
    frame.pack()
    root.withdraw()
    root.deiconify() 
    
    app = None
    
    try:
        app = ClientApplication(
                        use_grpc=False,
                        username=username,
                        password=password,
                        fullname=fullname,
                        account_status=account_status,
                        address="localhost",
                        port=PORT,
                        application_window=frame)
        if len(app.token) > 0:
            print(Fore.GREEN + "CREATE ACCOUNT TEST PASSED: " 
                + str(app)
                + Style.RESET_ALL)
        else:
            print(Fore.RED + "CREATE ACCOUNT TEST FAILED: token-invalid:" 
              + str(app.token)
              + Style.RESET_ALL)
            assert False
    except Exception as e:
        print(Fore.RED + "CREATE ACCOUNT TEST FAILED: " 
              + "Client Application could not be intialized"
              + Style.RESET_ALL)
        
        assert False

    print('Application Started || parent process:', os.getppid(), '|| process id:', os.getpid())
    time.sleep(1)
    list_packet = app.message_creator.ListAccountRequest(
                version=1,
                auth_token=app.token,
                username=app.username,
                number_of_accounts=100, # TODO currently not used
                regex=".*"
            )
            
    resp = app.client_stub.ListAccounts(list_packet)
    response_list = sorted(resp.account_names.split(", "))
    ground_truth = sorted(['a','b','c','d'])
    
    check = (response_list == ground_truth)
    
    if check:
        print(Fore.GREEN + "LIST ACCOUNTS PASSED: " 
              + str(check) + " values: " 
              + resp.account_names 
              + Style.RESET_ALL)
    else:
        print(Fore.RED + "LIST ACCOUNTS FAILED: " 
              + str(check) 
              + " values: " 
              + resp.account_names 
              + " expected: "
              + ", ".join(ground_truth)
              + Style.RESET_ALL)
        assert False
        
    msg_packet = app.message_creator.MessageRequest(version=1,
                                                 auth_token=app.token,
                                                 message=app.username,
                                                 username=app.username,
                                                 recipient_username=app.password)
    ret_val = app.client_stub.SendMessage(msg_packet)
    
    if len(ret_val.error_code) > 0:
        print(Fore.RED + "CONCURRENT MESSAGE SEND FAILED: " 
              + str(check) 
              + " error_code: " 
              + ret_val.error_code
              + Style.RESET_ALL)
        assert False
    
    time.sleep(2)
    
    def listen(app):
        auth_msg_request = app.message_creator.RefreshRequest(version=1, 
                                                        auth_token=app.token,
                                                        username=app.username)
        
        expected_value = chr(((ord(app.username) - 97)+3)%4 + 97)
        while True:
            auth_msg_request = app.message_creator.RefreshRequest(version=1, 
                                                    auth_token=app.token,
                                                    username=app.username)
            
            msg = app.client_stub.DeliverMessages(auth_msg_request)
            if len(msg.message) > 0:
                found = msg.message.split(": ")[-1]
                if found:
                    print(Fore.GREEN + "CONCURRENT MESSAGE RECIEVED: " 
                        + " Nodes: " 
                        + f"[{found}] -> [{app.username}]" 
                        + Style.RESET_ALL)
                else:
                    print(Fore.RED + "CONCURRENT MESSAGE FAILED: " 
                        + str(check) 
                        + " values: " 
                        + found
                        + " expected: "
                        + ", ".join(expected_value)
                    + Style.RESET_ALL)
            time.sleep(1)
            
            
    
    listen_th = th.Thread(target=listen, args=(app,), daemon=True)
    listen_th.start()
    
    print(f"Process {app.username} Sleeping")
    time.sleep(2)
    
    if app.username == "c":
        print("STARTING CONCURRENT DELETE TEST")
        
        del_packet = app.message_creator.DeleteAccountRequest(version=1,
                                                       auth_token=app.token,
                                                       username=app.username)
        resp = app.client_stub.DeleteAccount(del_packet)
        
        if len(resp.error_code) > 0:
            print(Fore.RED + "ACCOUNT DELETION FAILED: " 
              + str(check) 
              + " error_code: " 
              + resp.error_code
              + Style.RESET_ALL)
            assert False
        else:
            print(Fore.GREEN + "ACCOUNT DELETION SUCCESSFUL: " 
              + str(check) 
              + f" DELETED username: {app.username}" 
              + Style.RESET_ALL)
            
        print(f"Process {app.username} exiting")
        return 0
    else:
        print(f"STARTING CONCURRENT MESSAGE DURING DELETE TEST: {app.username}")
        msg_packet = app.message_creator.MessageRequest(version=1,
                                                auth_token=app.token,
                                                message=app.username,
                                                username=app.username,
                                                recipient_username="a")
        ret_val = app.client_stub.SendMessage(msg_packet)

        if len(ret_val.error_code) > 0:
            print(Fore.RED + "CONCURRENT MESSAGE SEND FAILED: " 
                + " error_code: " 
                + ret_val.error_code
                + Style.RESET_ALL)
            assert False
        else:
            print(Fore.GREEN + "CONCURRENT MESSAGE SENT: " 
                + f"[{app.username}] -> [{app.password}]"
                + Style.RESET_ALL)
                    
        if app.username == 'a':
            time.sleep(4)
            print("Tests Passed! Press [CTRL-C] to Exit Test")

        print(f"Process {app.username} exiting")


def run_server():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", PORT))

        print("socket binded to port", PORT)

        # put the socket into listening mode
        s.listen(10)
        print("socket is listening")
        
        chatServer = ChatServer()
        
        while True:
            # establish connection with client
            c, addr = s.accept()      
            print('Connected to :', addr[0], ':', addr[1])

            # Start a new thread and return its identifier
            th.Thread(target=chatServer.HandleNewConnection, daemon=False, args=(c,addr)).start()
            
def run():


    server_thread = mp.Process(target=run_server)
    server_thread.start()

    proc1 = mp.Process(target=run_client_thread, args=('a', 'b', 'a', 'no'))
    proc2 = mp.Process(target=run_client_thread, args=('b', 'c', 'b', 'no'))
    proc3 = mp.Process(target=run_client_thread, args=('c', 'd', 'c', 'no'))
    proc4 = mp.Process(target=run_client_thread, args=('d', 'a', 'd', 'no'))

    proc1.start()
    proc2.start()
    proc3.start()
    proc4.start()

if __name__ == '__main__':
    run()