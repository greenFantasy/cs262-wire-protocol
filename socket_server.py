import socket

host = "127.0.0.1"

# reserve a port on your computer
# in our case it is 12345 but it
# can be anything
port = 2048

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))

print("socket binded to port", port)

# put the socket into listening mode
s.listen(5)
print("socket is listening")

# establish connection with client
c, addr = s.accept()      
print('Connected to :', addr[0], ':', addr[1])

# Start a new thread and return its identifier

# TODO: Protect against crashing if client violently disconnects
print(c.recv(1024).decode("UTF-8"))

c.close()