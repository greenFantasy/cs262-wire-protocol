# Wire Protocol & GRPC Design

## Overview

We implement a basic encoding sceme where every message has a corresponding OpCode - operation code that allows us to determine the type of operations requested by the user and a version number that allows us to support backwards compatibility in the future. 

As we are using a python implementation we encode the message as a unified string buffer and decode it on the receiving end by parsing the "||" deliminated fields. In order to ensure canary protection: we add a canary block to the end of the message to check for corruption. 

Each operation that requires the user to be logged in requires a 14 character long Authentication token which is validated by the server side token hub upon receiving a message. 

This requires us to provide a token for the user when they login and create an account. This also necessitates that the user be required to login again over a period of time. To this end, we add a expiration time of an hour for each API token given to a user after logging in. 

## Message Types

### V1. Create Acount via Wire Protocol

```python 
class AccountCreateRequest(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "username": str,
            "password": str,
            "fullname": str
        }
        super().__init__(fields, raw_bytes)    

class AccountCreateReply(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "error_code": str,
            "auth_token": str,
            "fullname": str
        }
        super().__init__(fields, raw_bytes)
```
### V2. Create Account via GRPC
```proto
message AccountCreateRequest {
  int32 version = 1;
  string username = 2;
  string password = 3;
  string fullname = 4;
}

message AccountCreateReply {
  int32 version = 1;
  string error_code = 2;
  string auth_token = 3;
  string fullname = 4;
}

rpc CreateAccount (AccountCreateRequest) returns (AccountCreateReply) {}
```

Our wire protocol and GRPC implementation match for the most part when it comes to the create account functionality for the chat server. Essentially, both implementations take in a username, password and full name to associate the user metadata with. Then the data is used to create a user inbox, token hub mapping and user profile for the associated client. If any of the information is invalid, the reply contains an error code message with the corresponding failure information from the server handler.

### V1. Login via Wire Protocol
```python
class LoginRequest(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "username": str,
            "password": str
        }
        super().__init__(fields, raw_bytes)

class LoginReply(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "error_code": str,
            "auth_token": str,
            "fullname": str
        }
        super().__init__(fields, raw_bytes)
```

### V2. Login via GRPC

```proto
message LoginRequest {
  int32 version = 1;
  string username = 2;
  string password = 3;
}

message LoginReply {
  int32 version = 1;
  string error_code = 2;
  string auth_token = 3;
  string fullname = 4;
}

rpc Login (LoginRequest) returns (LoginReply) {}
```

The login-in message takes in a username and a password which will be validated on the server side. In return we give back an `auth_token` for the user to validate their future queries. If there is anything wrong with the user provided information we pass back specific server related errors through the error code field which are then displayed on the user side. While the proto file is processed by the GPRC module, our manually designed wire protocol inherits a general socket message class that is used to encode and decode the struct information. 

### V1. Message Request via Wire Protocol
```python
class MessageRequest(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "auth_token": str,
            "username": str,
            "recipient_username": str,
            "message": str
        }
        super().__init__(fields, raw_bytes)

class MessageReply(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "error_code": str
        }
        super().__init__(fields, raw_bytes)
```

### V2. Message Sending via GRPC
```proto
message MessageRequest {
  int32 version = 1;
  string auth_token = 2;
  string username = 3;
  string recipient_username = 4;
  string message = 5;
}

message MessageReply {
  int32 version = 1;
  string error_code = 2;
}

rpc SendMessage (MessageRequest) returns (MessageReply) {}
```

With message request, we take in a version number to understand the type of client the user using for backwards compatibility and the authorization token from their last login into the server. After the user request is validated: we then use the recipient field which contains the username for the user which the client is trying to message and validate that it is an existing account. After this validation, we drop the message into the user's inbox for pick up by a refresh query. 


### V1. List Account via Wire Protocol
```python
class ListAccountRequest(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "auth_token": str,
            "username": str,
            "number_of_accounts": int,
            "regex": str
        }
        super().__init__(fields, raw_bytes)

class ListAccountReply(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "error_code": str,
            "account_names": str
        }
        super().__init__(fields, raw_bytes)
```

### V2. List Account via GRPC

```proto
message ListAccountRequest {
  int32 version = 1;
  string auth_token = 2;
  string username = 3;
  int32 number_of_accounts = 4;
  string regex = 5;
}

message ListAccountReply {
  int32 version = 1;
  string error_code = 2;
  string account_names = 3;
}

rpc ListAccounts (ListAccountRequest) returns (ListAccountReply) {}
```

The user has to be validated for them to be able to make a query in order to see the other users on the system. From a design perspective this is a safer alternative as we do not want the user to be spammed by outisde sources that could use the list option to accquire account information. The user essentially passes in a regular expression which we then compile in order to search the existing database for names. We can then translate this into a response query that will give back as many names as possible. We have limited this to 25. If the query is incorrect or the regular expression is faulty, we return back an error code to be displayed in the user side client.  


### V1. Delete Account via Wire Protocol 
```python
class DeleteAccountRequest(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "auth_token": str,
            "username": str
        }
        super().__init__(fields, raw_bytes)

class DeleteAccountReply(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "error_code": str
        }
        super().__init__(fields, raw_bytes)
```

### V2. Delete Account via GRPC
```proto
message DeleteAccountRequest {
  int32 version = 1;
  string auth_token = 2;
  string username = 3;
}

message DeleteAccountReply {
  int32 version = 1;
  string error_code = 2;
}

rpc DeleteAccount (DeleteAccountRequest) returns (DeleteAccountReply) {}
```

We ensure that the user has the proper credentials for deleting their own account. We do not let the user terminate another's account, and they have to have an updated login token. If a user logs into their account and intializes the client application, the listening thread will spin up before the interface. This means that before a user deletes their account, all remaining messages will delivered. If they are logged in, then consistency on the metadata locking would ensure that the inbox was cleared before the deleting server thread could eliminate the account. 

### V1. Refreshing via Wire Protocol 
```python 
class RefreshRequest(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "auth_token": str,
            "username": str
        }
        super().__init__(fields, raw_bytes)

class RefreshReply(SocketMessage):
    def __init__(self, raw_bytes):
        fields = {
            "version": int,
            "message": str,
            "error_code": str
        }
        super().__init__(fields, raw_bytes)
```

### V2. Refreshing via GRPC

```proto
message RefreshRequest {
  int32 version = 1;
  string auth_token = 2;
  string username = 3;
}

message RefreshReply {
  int32 version = 1;
  string message = 2;
  string error_code = 3;
}

rpc DeliverMessages (RefreshRequest) returns (stream RefreshReply) {}
```

When it comes to refreshing the implementations of the wire protocol and the GRPC diverge. Here we see that for the GRPC implementation, we opt to return a stream object which essentially returns to the client thread an iterable message object which blocks the queue of messages popped is empty for a specific user inbox. On the wire-protocol side the refresh system takes and validates the user credentials the same way as GRPC but returns a batch of messages all together in whatever it can fit on the packet side. This is accomplished by fitting all of the un-delivered messages into the packet and then in a one time response, sending ti to the client. The wire protocol implementation does not gaurantee that all remanining messages will be delivered with a single refresh request on the client listening thread, while for the GRPC implementation this is a given. 