import socket

HOST = ""
PORT = 8888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(10)
conn, addr = s.accept()
print('Connected with ' + addr[0] + ':' + str(addr[1]))
data = conn.recv(1024)
while data:
	reply = str.encode('You sent: ') + data
	print(str(data))
	conn.send(reply)
	print(str(reply))
	data = conn.recv(1024)
conn.close()