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

        # token hub keys are usernames and the values are token, timestamp
        # pairs
        self.token_hub = {}

        # keeping track of time by standardizing to UTC
        self.utc_time_gen = datetime.datetime

        # user metadata lock
        self.metadata_lock = mp.Lock()

        # inbox lock
        self.inbox_lock = mp.Lock()

    def GenerateToken(self) -> str:
        """
        Generates a token for authenticating user requests to a chat server.

        Returns:
            str: A token that can be used to authenticate user requests.
        """

        token = os.urandom(self.token_length)
        return binascii.hexlify(token).decode()

    def ValidatePassword(self, password: str) -> int:
        """
        Validates a password to ensure that it is a string.

        Args:
            password (str): The password to validate.

        Returns:
            int: Returns 0 if the password is a string, or -1 if it is not.
        """

        if not isinstance(password, str):
            return -1
        else:
            return 0

    def ValidateToken(self, username: str, token: str) -> int:
        """
        Validates a user token and checks if it has expired.

        Args:
            username (str): The username associated with the token.
            token (str): The token to validate.

        Returns:
            int: Returns 0 if the token is valid and has not expired,
            or -1 if it is invalid or has expired.
        """
        with self.metadata_lock:
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

    def CreateAccount(self, raw_bytes: str) -> wp.encode.AccountCreateReply:
        """
        Validates the buffer and registers a new user with relevant metadata structures.

        Args:
            raw_bytes (str): The raw bytes containing the user account information.

        Returns:
            wp.encode.AccountCreateReply: Returns an `AccountCreateReply`
            object that contains the version, error code,
            authentication token, and full name of the new user.
        """
        request = wp.socket_types.AccountCreateRequest(raw_bytes)
        if request.generated_error_code:
            return wp.encode.AccountCreateReply(
                version=1,
                error_code=request.generated_error_code,
                auth_token="",
                fullname="")

        username = request.username
        with self.metadata_lock:
            if username in self.user_metadata_store.keys():
                return wp.encode.AccountCreateReply(
                    version=1,
                    error_code="ERROR Username Already Exists",
                    auth_token="",
                    fullname="")

            # get the password and do basic error checking
            password = request.password
            if self.ValidatePassword(password) < 0:
                return wp.encode.AccountCreateReply(
                    version=1, error_code="ERROR Invalid Passcode", auth_token="", fullname="")

            # prepare metadata
            fullname = request.fullname
            token = self.GenerateToken()
            timestamp = self.utc_time_gen.now().timestamp()

            # create user metadata
            self.user_metadata_store[username] = (password, fullname)
            # register user in token hub / stores last given token
            self.token_hub[username] = (token, timestamp)

            with self.inbox_lock:
                # create user chat inbox
                self.user_inbox[username] = []

                return wp.encode.AccountCreateReply(version=1,
                                                    error_code="",
                                                    auth_token=token,
                                                    fullname=fullname)

    def Login(self, raw_bytes: str) -> wp.socket_types.LoginReply:
        """
        Authenticate a user and generate a token for them to access the chat server.

        Args:
            raw_bytes (str): A string containing the serialized LoginRequest message.

        Returns:
            LoginReply: A message containing the authentication token
            and user information, or an error message if the login failed.

        The function validates the given username
        and password against the user metadata store,
        and generates a new token for
        the user if the login is successful.
        The token is stored in the token hub,
        and returned to the user in the LoginReply message.
        If the username or password is invalid,
        an error message is returned instead.
        Note that the LoginRequest message is
        deserialized from the `raw_bytes` string before processing,
        and the LoginReply message is serialized before being returned.
        """

        request = wp.socket_types.LoginRequest(raw_bytes)
        if request.generated_error_code:
            return wp.encode.LoginReply(
                version=1,
                error_code=request.generated_error_code,
                auth_token="",
                fullname="")

        # get the given username and do basic error checking
        username = request.username

        with self.metadata_lock:
            if username not in self.user_metadata_store.keys():
                return wp.encode.LoginReply(
                    version=1,
                    error_code="ERROR Username Invalid",
                    auth_token="",
                    fullname="")

            # basic password match
            password = request.password
            if password != self.user_metadata_store[username][0]:
                return wp.encode.LoginReply(
                    version=1,
                    error_code="ERROR Password Invalid",
                    auth_token="",
                    fullname="")

            # generate new token
            token = self.GenerateToken()
            timestamp = self.utc_time_gen.now().timestamp()

            # register token in token hub
            self.token_hub[username] = (token, timestamp)
            return wp.encode.LoginReply(
                version=1,
                error_code="",
                auth_token=token,
                fullname=self.user_metadata_store[username][1])

    def ReceiveMessage(self, raw_bytes: str) -> wp.encode.MessageReply:
        """
        Receives a raw string buffer from the user
        and stores the message in the correct recipient's inbox.

        Args:
            raw_bytes (str): A string buffer representing a message sent by a user,
            containing the message content,
            recipient username, and authentication token.

        Returns:
            wp.encode.MessageReply: A message reply object containing
            a version number and error code, if applicable.

        The function first parses the request message from the raw string buffer
        using the `MessageRequest` object. It then validates the authentication token
        and recipient username using the `ValidateToken` function. If the validation
        fails, the function returns a `MessageReply` object with an appropriate error code.

        If the authentication token and recipient username are valid,
        the function appends the message to the recipient's
        inbox and returns a `MessageReply` object with a success code.

        The function uses the `inbox_lock` to protect access
        to the inbox dictionaries and ensures that the inbox for the
        recipient exists before attempting to append the message.
        If the recipient does not exist, the function returns a
        `MessageReply` object with an error code indicating an invalid recipient.
        """

        request = wp.socket_types.MessageRequest(raw_bytes)
        if request.generated_error_code:
            return wp.encode.MessageReply(
                version=1, error_code=request.generated_error_code, )

        token = request.auth_token
        username = request.username
        recipient = request.recipient_username

        # note that validate token is protected by the metadata lock
        if self.ValidateToken(username=username,
                              token=token) < 0:
            return wp.encode.MessageReply(version=1,
                                          error_code="Invalid Token")

        message_string = request.message
        modified_string = f"[{username}]: {message_string}"

        # protect inbox access with lock
        with self.inbox_lock:

            if recipient not in self.user_inbox.keys():
                return wp.encode.MessageReply(version=1,
                                              error_code="Invalid Recipient")

            self.user_inbox[recipient].append(modified_string)
            return wp.encode.MessageReply(version=1, error_code="")

    def ListAccounts(self, raw_bytes: str) -> wp.encode.ListAccountReply:
        """
        Validate the user's token, and return a list of usernames
        filtered by a regular expression.
        The list is limited to a maximum of 100 usernames.

        Args:
            raw_bytes (str): The raw string buffer containing the user request.

        Returns:
            wp.socket_types.ListAccountReply: A socket type object containing the version,
            error code and a comma-separated list of filtered usernames.
        """
        request = wp.socket_types.ListAccountRequest(raw_bytes)
        if request.generated_error_code:
            return wp.encode.ListAccountReply(
                version=1, error_code=request.generated_error_code, account_names="")

        token = request.auth_token
        username = request.username
        if self.ValidateToken(username=username,
                              token=token) < 0:
            return wp.encode.ListAccountReply(version=1,
                                              error_code="Invalid token",
                                              account_names="")

        with self.metadata_lock:
            list_of_usernames = self.user_metadata_store.keys()

        filtered_list = list_of_usernames
        # search using filter
        regex = request.regex
        if len(regex) != 0:
            r = None
            try:
                r = re.compile(f"{regex}")
            except Exception as e:
                return wp.encode.ListAccountReply(version=1,
                                                  error_code=str(e),
                                                  account_names="")
            # filter based on compiled regex
            filtered_list = list(filter(r.match, list_of_usernames))
        filtered_string = ", ".join(filtered_list[:25])

        return wp.encode.ListAccountReply(version=1,
                                          error_code="",
                                          account_names=filtered_string)

    def DeleteAccount(self, raw_bytes: str) -> wp.encode.DeleteAccountReply:
        """
        Deletes the user account and associated metadata,
        including the user's inbox, based on a raw string buffer received from the user.

        Args:
            raw_bytes (str): The raw string buffer to validate and process.

        Returns:
            wp.encode.DeleteAccountReply: A reply message that
            indicates the success or failure of the operation.
            The message contains a version number, an error code (if any),
            and an empty string as a payload.
        """
        request = wp.socket_types.DeleteAccountRequest(raw_bytes)
        if request.generated_error_code:
            return wp.encode.DeleteAccountReply(
                version=1, error_code=request.generated_error_code)

        token = request.auth_token
        username = request.username
        if self.ValidateToken(username=username,
                              token=token) < 0:
            return wp.encode.DeleteAccountReply(version=1,
                                                error_code="Invalid token")

        # delete all relevant metadata
        with self.metadata_lock:
            self.token_hub.pop(username)
            self.user_metadata_store.pop(username)

            with self.inbox_lock:
                self.user_inbox.pop(username)

                return wp.encode.DeleteAccountReply(version=1,
                                                    error_code="")

    def DeliverMessages(self, raw_bytes: str) -> wp.encode.RefreshReply:
        """
        Given a raw string buffer user request,
        validate the request and deliver a set of messages to the user.

        Args:
            raw_bytes (str): A raw string buffer user request.

        Returns:
            wp.encode.RefreshReply: A RefreshReply object containing
            the messages and/or error code.

        This function validates the user request,
        and if the request is valid,
        it checks the user inbox for any new messages.
        If there are new messages, it returns a RefreshReply object
        with the messages and an empty inbox.
        If there are no new messages, it returns a
        RefreshReply object with an empty message and an error code.
        """

        request = wp.socket_types.RefreshRequest(raw_bytes)
        if request.generated_error_code:
            return wp.encode.RefreshReply(
                version=1, message="", error_code=request.generated_error_code)

        token = request.auth_token
        username = request.username
        if self.ValidateToken(username=username,
                              token=token) < 0:
            return wp.encode.RefreshReply(version=1,
                                          message="",
                                          error_code="Invalid Token"
                                          )
        # Check if there are any new messages
        with self.inbox_lock:
            if len(self.user_inbox[username]) > 0:
                msg = "\n".join(self.user_inbox[username])
                self.user_inbox[username] = []
                return wp.encode.RefreshReply(version=1,
                                              message=msg,
                                              error_code=""
                                              )
            else:
                return wp.encode.RefreshReply(version=1,
                                              message="",
                                              error_code="No new message"
                                              )

    def HandleNewConnection(self, c: socket.socket, addr: tuple) -> None:
        """
        This method handles incoming connections and spins off new threads to handle requests.

        Args:
            c (socket.socket): The socket object used for communication with the client.
            addr (tuple): The IP address and port number of the client.

        Returns:
            None
        """

        while True:
            data = c.recv(2048)
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
                0: self.CreateAccount,
                1: self.Login,
                2: self.ReceiveMessage,
                3: self.ListAccounts,
                4: self.DeleteAccount,
                5: self.DeliverMessages
            }

            if opcode in opcode_map.keys():
                result = opcode_map[opcode](data)
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
    port = 50051

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
        mp.Thread(target=chatServer.HandleNewConnection,
                  daemon=False, args=(c, addr)).start()
