from client import ClientApplication
from server import ChatServer
from concurrent import futures
import signal
import os
from colorama import Fore, Style
import grpc
import chat_pb2
import chat_pb2_grpc
import time

import multiprocessing as mp
from tkinter import *

# def handle_sigterm():
#     done_event = server.stop(30)
#     done_event.wait(30)
#     print('Stop complete.')

PORT = '50051'



def run_client_thread(username, password, fullname, account_status="no"):
    root = Tk()  # I just used a very simple Tk window for the chat UI, this can be replaced by anything
    frame = Frame(root, width=300, height=300)
    frame.pack()
    root.withdraw()
    root.deiconify() 
    
    app = None
    
    try:
        app = ClientApplication(
                        use_grpc="yes",
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
    except Exception as e:
        print(Fore.RED + "CREATE ACCOUNT TEST FAILED: " 
              + "Client Application could not be intialized"
              + Style.RESET_ALL)
        
        return -1

    app.interface_setup()
    app.start_listening()
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
        
    msg_packet = app.message_creator.MessageRequest(version=1,
                                                 auth_token=app.token,
                                                 message=f"{app.username}",
                                                 username=app.username,
                                                 recipient_username=app.password)
    ret_val = app.client_stub.SendMessage(msg_packet)
    
    if len(ret_val.error_code) > 0:
        print(Fore.RED + "CONCURRENT MESSAGE SEND FAILED: " 
              + str(check) 
              + " error_code: " 
              + ret_val.error_code
              + Style.RESET_ALL)
    
    time.sleep(0.5)
    
    print(app.messages[END])
        


def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServerServicer_to_server(ChatServer(), server)
    server.add_insecure_port('[::]:' + PORT)
    server.start()
    print("Server started, listening on " + PORT)

    proc1 = mp.Process(target=run_client_thread, args=('a', 'b', 'a', 'no'))
    proc2 = mp.Process(target=run_client_thread, args=('b', 'c', 'b', 'no'))
    proc3 = mp.Process(target=run_client_thread, args=('c', 'd', 'c', 'no'))
    proc4 = mp.Process(target=run_client_thread, args=('d', 'a', 'd', 'no'))

    proc1.start()
    proc2.start()
    proc3.start()
    proc4.start()

    server.wait_for_termination()

if __name__ == '__main__':
    run()