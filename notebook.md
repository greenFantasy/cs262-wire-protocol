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

## Entry 1/12/2023 4:37 pm 

In order to create a user account we have to keep track of metadata. We opt for the twitter type inbox system where messages are just queues waiting for the user like emails. We also enable a user metadata store that keeps track of all usernames, passwords and full names. Lastly, we have a token hub which in turn provides the much needed token to timestamp mapping so we can tell when a token has expired. 


```
Traceback (most recent call last):
  File "/Users/amishra/cs262-wire-protocol/client.py", line 184, in <module>
    run()
  File "/Users/amishra/cs262-wire-protocol/client.py", line 180, in run
    app.start()
  File "/Users/amishra/cs262-wire-protocol/client.py", line 70, in start
    mp.Process(target=self.listen_loop, daemon=True).start()
  File "/Users/amishra/miniconda3/envs/262-dev/lib/python3.9/multiprocessing/process.py", line 121, in start
    self._popen = self._Popen(self)
  File "/Users/amishra/miniconda3/envs/262-dev/lib/python3.9/multiprocessing/context.py", line 224, in _Popen
    return _default_context.get_context().Process._Popen(process_obj)
  File "/Users/amishra/miniconda3/envs/262-dev/lib/python3.9/multiprocessing/context.py", line 284, in _Popen
    return Popen(process_obj)
  File "/Users/amishra/miniconda3/envs/262-dev/lib/python3.9/multiprocessing/popen_spawn_posix.py", line 32, in __init__
    super().__init__(process_obj)
  File "/Users/amishra/miniconda3/envs/262-dev/lib/python3.9/multiprocessing/popen_fork.py", line 19, in __init__
    self._launch(process_obj)
  File "/Users/amishra/miniconda3/envs/262-dev/lib/python3.9/multiprocessing/popen_spawn_posix.py", line 47, in _launch
    reduction.dump(process_obj, fp)
  File "/Users/amishra/miniconda3/envs/262-dev/lib/python3.9/multiprocessing/reduction.py", line 60, in dump
    ForkingPickler(file, protocol).dump(obj)
TypeError: cannot pickle '_tkinter.tkapp' object
```


```
Exception in thread Thread-1:
Traceback (most recent call last):
  File "/Users/amishra/miniconda3/envs/262-dev/lib/python3.9/threading.py", line 980, in _bootstrap_inner
    self.run()
  File "/Users/amishra/miniconda3/envs/262-dev/lib/python3.9/threading.py", line 917, in run
    self._target(*self._args, **self._kwargs)
  File "/Users/amishra/cs262-wire-protocol/client.py", line 80, in listen_loop
    for note in self.client_stub.DeliverMessages(auth_msg_request):
  File "/Users/amishra/miniconda3/envs/262-dev/lib/python3.9/site-packages/grpc/_channel.py", line 426, in __next__
    return self._next()
  File "/Users/amishra/miniconda3/envs/262-dev/lib/python3.9/site-packages/grpc/_channel.py", line 826, in _next
    raise self
grpc._channel._MultiThreadedRendezvous: <_MultiThreadedRendezvous of RPC that terminated with:
        status = StatusCode.UNKNOWN
        details = "Exception iterating responses: 'float' object has no attribute 'total_seconds'"
        debug_error_string = "UNKNOWN:Error received from peer ipv6:%5B::1%5D:50051 {created_time:"2023-02-13T02:18:43.129338-05:00", grpc_status:2, grpc_message:"Exception iterating responses: \'float\' object has no attribute \'total_seconds\'"}"
```



