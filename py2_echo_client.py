import socket

#HOST = "localhost"
HOST = "199.87.127.48"
PORT = 8888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "Created socket"
s.connect((HOST, PORT))
print "Connected to " + HOST + " on port " + str(PORT)
while True:
	msg = raw_input("Type msg to send: ").strip()
	s.send(msg)
	data = s.recv(1024)
	print "Response from server:"
	print data