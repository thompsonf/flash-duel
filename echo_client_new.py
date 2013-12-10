import socket

def strip_tag(msg):
	print(msg)
	if msg[:2] == "b'" and msg[-1] == "'":
		return msg[2:-1]
	else:
		#This shouldn't happen!
		return False

#HOST = "localhost"
HOST = "199.87.127.48"
PORT = 8888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Created socket")
s.connect((HOST, PORT))
print("Connected to", HOST, "on port", PORT)
while True:
	msg = input("Type msg to send: ").strip()
	s.send(str.encode(msg))
	print("Sent:", str(msg), len(str(msg)))
	data = s.recv(1024)
	print(len(data))
	print(data.decode())