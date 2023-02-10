## Entry 1/9/2023 11:00 am

Worked on looking at documentation of the the python GrPC protocol online and worked through the demo example provided regarding latitude and longitude coordinate transfer. 
Talked about how we do not have to stream things messages, because each message can be treated as its own operation rather than a streaming operation.

We then used the HelloWorld proto base template to get started with our application. We notice that routines are delineated with the rpc function and respective service declaration. Meanwhile the types that the services use are declared under the message declaration. 

We can recreate the stub files using the proto: 

`python -m grpc_tools.protoc -I protos --python_out=. --pyi_out=. --grpc_python_out=. protos/chat.proto`

We now see that it is good form to have the protos file inside of a protos directory. 

## Entry 1/9/2023 9:04 pm 

In order to create an account, we have a username Unique Id, Name, password. To send messages the user has to login. We want to avoid a situation where two people request to make a username account and both will not be assigned the same id (whoever's request is sent first). My basic take is that the login token recieved should just expire after an hour and not take user activity into account. I (AM) would prefer if we implement most basic working implementation first before adding bells and whistles. 

50 characters max for every field. You can see at max 100 users. 100*50 characters passed in the list accounts operation. Regex matching for search to query relevant names. 

We have to mantain a list of the tokens that are valid, deliver to chat user either right away, or as they login. As the user logs in, we have to return a message stream. In regards, to deleting an account and generally - you have to be logged in order to to any operation such as deleting an account. Seeing that the user has to be logged in order to delete an account, they will recieve all of their undelivereed messages first. 

For the future, we want to mantain message histories, delivery confirmation and auth extension based on activity. For now we are starting with individual messages to get the server to work in the future we might add message streams.  

