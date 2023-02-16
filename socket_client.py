import socket

host = "10.250.240.43"
port = 2048


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((host,port))

ans = "Aakash you suck."
s.send(ans.encode('ascii'))
data = s.recv(1024)

s.close()