# Design Documentation - Table of Contents

This document contains links to all of our relevant design documentation.

## (1) gRPC and Wire Protocol Message and Protocol Structure

### Overview

This documentation describes the design of the wire protocol and gRPC implementation for a chat server. The wire protocol encoding scheme uses an opcode and version number to determine the type of operation and support backwards compatibility. The message is encoded as a unified string buffer and decoded by parsing deliminated fields. An authentication token is required for every operation that requires the user to be logged in, which is validated by the server-side token hub upon receiving a message. The documentation also provides the message types for create account, login, message request, and list account functionalities in both wire protocol and gRPC implementation, with slight variations between the two. The documentation provides the code structure for both the wire protocol and gRPC implementation for each message type.

[Full Wire Protocol and gRPC Documentation Here](wire_design.md)

## (2) Locking Structure and Hierarchy

### Overview

The "Locking Overview" documentation outlines the access protection mechanism of a chat server for server-wide user metadata. Three structures require access protection: user metadata store, token hub, and user inbox. The user metadata store and token hub use the `app.metadata_lock`, while the user inbox has its own lock called `app.inbox_lock`. The locking is implemented using the with pythonic syntax to ensure that the lock is not held after a function returns or a scope is unexpectedly terminated. The locking hierarchy is strictly maintained to prevent deadlocks, where the metadata lock is held first, followed by the inbox lock, and the reverse order is used to release them. Overall, the fine-grained locking approach aims to reduce contention and increase efficiency in handling concurrent requests in the chat server.

[Full Locking Documentation Here](locking_design.md)

## (3) Multi-threading Server / Client Structure

### Overview

For the gRPC setup, we have a global pool of threads that we can use to handle incomimg connections for each request. We use a RPC stream response for a client's refresh thread. This returns a blocking iterator object that in turn takes the messages that the user has not gotten and forwards them to the user. On the other hand, we have the socket implementation that does not run as a dameon thread because it is essentially polling the inbox server with a timed loop that constantly asks for refreshed messages in return for a message update per refresh. 

[Full Design Schematic](schematic.md)






