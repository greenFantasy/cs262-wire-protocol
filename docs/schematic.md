# Server - Client Multithreading Design Schematic

For the gRPC setup, we have a global pool of threads that we can use to handle incomimg connections for each request. We use a RPC stream response for a client's refresh thread. This returns a blocking iterator object that in turn takes the messages that the user has not gotten and forwards them to the user. On the other hand, we have the socket implementation that does not run as a dameon thread because it is essentially polling the inbox server with a timed loop that constantly asks for refreshed messages in return for a message update per refresh. 

![schematic](design_schema.png)