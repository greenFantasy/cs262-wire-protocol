from client import ClientApplication
from grpc_server import ChatServer
from concurrent import futures
import signal
import os
import sys
from colorama import Fore, Style
import grpc
import chat_pb2
import chat_pb2_grpc
import time

import threading as th
import multiprocessing as mp
from tkinter import *


PORT = '50051'

def RunClientThread(username, password, fullname, account_status="no"):
    root = Tk()
    frame = Frame(root, width=300, height=300)
    frame.pack()
    root.withdraw()
    root.deiconify() 
    
    app = None
    
    try:
        app = ClientApplication(
                        use_grpc=True,
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
    
    def Listen(app):
        auth_msg_request = app.message_creator.RefreshRequest(version=1, 
                                                        auth_token=app.token,
                                                        username=app.username)
        
        expected_value = chr(((ord(app.username) - 97)+3)%4 + 97)
        for msg in app.client_stub.DeliverMessages(auth_msg_request):
            found = msg.message.split(": ")[-1]
            check = found == expected_value
            if check:
                print(Fore.GREEN + "CONCURRENT MESSAGE RECIEVED: " 
                    + str(check) + " Nodes: " 
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
            
            
    
    listen_th = th.Thread(target=Listen, args=(app,), daemon=True)
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
        print("STARTING CONCURRENT LIST DURING DELETE TEST")
        time.sleep(2)
        list_packet = app.message_creator.ListAccountRequest(
                version=1,
                auth_token=app.token,
                username=app.username,
                number_of_accounts=100, # TODO currently not used
                regex=".*"
            )
            
        resp = app.client_stub.ListAccounts(list_packet)
        response_list = sorted(resp.account_names.split(", "))
        
        ground_truth = sorted(['a','b','d'])
    
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
        
        print("Valid Accounts: ", response_list)
        print(f"STARTING CONCURRENT MESSAGE DURING DELETE TEST: {app.username}")
        if app.password in response_list:
            msg_packet = app.message_creator.MessageRequest(version=1,
                                                    auth_token=app.token,
                                                    message=app.username,
                                                    username=app.username,
                                                    recipient_username=app.password)
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
                    
        if app.username in ['a', 'b']:
            time.sleep(4)
            if app.username == 'a': print("Tests Passed! Press [CTRL-C] to Exit Test")

        print(f"Process {app.username} exiting")


def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServerServicer_to_server(ChatServer(), server)
    server.add_insecure_port('[::]:' + PORT)
    server.start()
    print("Server started, Listening on " + PORT)

    proc1 = mp.Process(target=RunClientThread, args=('a', 'b', 'a', 'no'))
    proc2 = mp.Process(target=RunClientThread, args=('b', 'c', 'b', 'no'))
    proc3 = mp.Process(target=RunClientThread, args=('c', 'd', 'c', 'no'))
    proc4 = mp.Process(target=RunClientThread, args=('d', 'a', 'd', 'no'))

    proc1.start()
    proc2.start()
    proc3.start()
    proc4.start()

    server.wait_for_termination()

if __name__ == '__main__':
    run()