import socket
import wire_protocol as wp

host = "localhost"
port = 2048

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((host,port))

ans = wp.encode.AccountCreateRequest(
    version=1,
    username='rajat', 
    password='raj',
    fullname="Rajat Mittal"
    )

s.send(ans)
data = s.recv(1024)

reply = wp.socket_types.AccountCreateReply(data)
print(reply.auth_token)

import time
time.sleep(2)

ans = wp.encode.ListAccountRequest(
    version=1,
    auth_token=reply.auth_token, 
    username='rajat',
    number_of_accounts=10,
    regex="r*"
    )

s.send(ans)
data = s.recv(1024)
reply = wp.socket_types.ListAccountReply(data)
print(reply.error_code, reply.account_names)

s.close()
