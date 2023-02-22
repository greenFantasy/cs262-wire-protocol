import multiprocessing as mp
import os
import socket
import threading as th
import time
from tkinter import *

from colorama import Fore, Style

from client import ClientApplication
from socket_server import ChatServer

PORT = 8000


def RunClientThread(
        username: str,
        password: str,
        fullname: str,
        account_status: str = "no") -> int:
    """
    Runs a set of integrations tests given init parameters.

    Args:
        username (str): username for client
        password (str): password for client
        fullname (str): full name of client
        account_status (str): create account or not

    Returns:
        (int) success or not.
    """
    # Create a Tk root window.
    root = Tk()
    # Create a frame and set its dimensions.
    frame = Frame(root, width=300, height=300)
    # Pack the frame.
    frame.pack()
    # Hide the root window.
    root.withdraw()
    # Show the root window.
    root.deiconify()

    # Initialize app to None.
    app = None

    # Try creating a ClientApplication object.
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
        # If the app object has a token, print a success message.
        if len(app.token) > 0:
            print(Fore.GREEN + "CREATE ACCOUNT TEST PASSED: "
                  + str(app)
                  + Style.RESET_ALL)
        # If the app object does not have a token, print a failure message and
        # raise an assertion error.
        else:
            print(Fore.RED + "CREATE ACCOUNT TEST FAILED: token-invalid:"
                  + str(app.token)
                  + Style.RESET_ALL)
            assert False
    # If an exception is raised, print a failure message and raise an
    # assertion error.
    except Exception as e:
        print(Fore.RED + "CREATE ACCOUNT TEST FAILED: "
              + "Client Application could not be intialized"
              + Style.RESET_ALL)
        assert False

    # Print the process information and wait for 1 second.
    print('Application Started || parent process:',
          os.getppid(), '|| process id:', os.getpid())
    time.sleep(1)

    # Create a ListAccountRequest packet.
    list_packet = app.message_creator.ListAccountRequest(
        version=1,
        auth_token=app.token,
        username=app.username,
        number_of_accounts=100,  # TODO currently not used
        regex=".*"
    )

    # Call the ListAccounts method and store the response in resp.
    resp = app.client_stub.ListAccounts(list_packet)
    # Split the account names in the response by ", " and sort them.
    response_list = sorted(resp.account_names.split(", "))
    # Create a ground_truth list.
    ground_truth = sorted(['a', 'b', 'c', 'd'])

    # Check if the response list and ground truth list match.
    check = (response_list == ground_truth)

    # If check is True, print a success message.
    if check:
        print(Fore.GREEN + "LIST ACCOUNTS PASSED: "
              + str(check) + " values: "
              + resp.account_names
              + Style.RESET_ALL)
    # If check is False, print a failure message and raise an assertion error.
    else:
        print(Fore.RED + "LIST ACCOUNTS FAILED: "
              + str(check)
              + " values: "
              + resp.account_names
              + " expected: "
              + ", ".join(ground_truth)
              + Style.RESET_ALL)
        assert False

    # Create a MessageRequest packet.
    msg_packet = app.message_creator.MessageRequest(
        version=1,
        auth_token=app.token,
        message=app.username,
        username=app.username,
        recipient_username=app.password)
    # Call the SendMessage method and store the response in ret_val.
    ret_val = app.client_stub.SendMessage(msg_packet)

    # Check if there is an error code in the return value
    if len(ret_val.error_code) > 0:
        # Print an error message with the error code
        print(Fore.RED + "CONCURRENT MESSAGE SEND FAILED: "
              + str(check)
              + " error_code: "
              + ret_val.error_code
              + Style.RESET_ALL)
        # Raise an assertion error to stop the program
        assert False

    # Pause execution for 2 seconds
    time.sleep(2)

    def Listen(app):
        # Create a request for a message refresh
        auth_msg_request = app.message_creator.RefreshRequest(
            version=1, auth_token=app.token, username=app.username)
        # Calculate an expected value for the message
        expected_value = chr(((ord(app.username) - 97) + 3) % 4 + 97)
        while True:
            auth_msg_request = app.message_creator.RefreshRequest(
                version=1, auth_token=app.token, username=app.username)

            msg = app.client_stub.DeliverMessages(auth_msg_request)

            if msg.message and len(msg.message) > 0:
                found = msg.message.split(": ")[-1]
                if found:
                    # Print a message with the found value in green text
                    print(Fore.GREEN + "CONCURRENT MESSAGE RECEIVED: "
                          + " Nodes: "
                          + f"[{found}] -> [{app.username}]"
                          + Style.RESET_ALL)
                else:
                    # Print an error message with the expected and actual values in
                    # red text
                    print(Fore.RED + "CONCURRENT MESSAGE FAILED: "
                          + str(check)
                          + " values: "
                          + found
                          + " expected: "
                          + ", ".join(expected_value)
                          + Style.RESET_ALL)
            time.sleep(1)

    # Create a thread to listen for messages
    listen_th = th.Thread(target=Listen, args=(app,), daemon=True)
    # Start the thread
    listen_th.start()

    # Print a message indicating the process is sleeping
    print(f"Process {app.username} Sleeping")
    # Pause execution for 2 seconds
    time.sleep(2)

    if app.username == "c":
        # Print a message indicating the concurrent delete test is starting
        print("STARTING CONCURRENT DELETE TEST")
        # Create a request to delete the account
        del_packet = app.message_creator.DeleteAccountRequest(
            version=1, auth_token=app.token, username=app.username)
        # Send the delete request and store the response
        resp = app.client_stub.DeleteAccount(del_packet)
        # Check if there is an error code in the response
        if resp.error_code and len(resp.error_code) > 0:
            # Print an error message with the error code
            print(Fore.RED + "ACCOUNT DELETION FAILED: "
                  + str(check)
                  + " error_code: "
                  + resp.error_code
                  + Style.RESET_ALL)
            # Raise an assertion error to stop the program
            assert False
        else:
            # Print a success message with the deleted username
            print(Fore.GREEN + "ACCOUNT DELETION SUCCESSFUL: "
                  + str(check)
                  + f" DELETED username: {app.username}"
                  + Style.RESET_ALL)
        # Print a message indicating the process is exiting
        print(f"Process {app.username} exiting")
        # Return 0 to indicate successful completion
        return 0
    else:
        # Print a message indicating the concurrent message during delete test
        # is starting
        print(
            f"STARTING CONCURRENT MESSAGE DURING DELETE TEST: {app.username}")

        # Create a request to send a message
        msg_packet = app.message_creator.MessageRequest(version=1,
                                                        auth_token=app.token,
                                                        message=app.username,
                                                        username=app.username,
                                                        recipient_username="a")
        ret_val = app.client_stub.SendMessage(msg_packet)

        if ret_val.error_code and len(ret_val.error_code) > 0:
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


def RunServer():
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
        th.Thread(target=chatServer.HandleNewConnection,
                  daemon=False, args=(c, addr)).start()


def Run():

    server_thread = mp.Process(target=RunServer)
    server_thread.start()

    proc1 = mp.Process(target=RunClientThread, args=('a', 'b', 'a', 'no'))
    proc2 = mp.Process(target=RunClientThread, args=('b', 'c', 'b', 'no'))
    proc3 = mp.Process(target=RunClientThread, args=('c', 'd', 'c', 'no'))
    proc4 = mp.Process(target=RunClientThread, args=('d', 'a', 'd', 'no'))

    proc1.start()
    proc2.start()
    proc3.start()
    proc4.start()


if __name__ == '__main__':
    Run()
