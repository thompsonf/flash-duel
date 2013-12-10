import socket

HOST_dflt = "199.87.127.48"
PORT_dflt = 8888

HOST = input("Connect to which IP? (leave empty for default): ")
PORT = input("Connect to which port? (leave empty for default): ")

if not HOST:
	HOST = HOST_dflt
if PORT:
	PORT = int(PORT)
else:
	PORT = PORT_dflt

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Connected to", HOST, "on port", PORT)
while True:

	msgstr = s.recv(1024).decode()
	if msgstr == "":
		print("Disconnected from server")
		exit()
	print("Received msg:", msgstr)
	msglist = msgstr.split()
	msgtype = msglist[0]
	msgdata = msglist[1:]

	#process the msg
	if msgtype == "name-rqst":
		name = input("Please type your name: ")
		s.send(name.encode())
	elif msgtype == "dspl-txt":
		print(" ".join(msgdata))
	elif msgtype == "get-move":
		print("What is your next move?")
		print("Valid moves are movetoward, moveaway, push, attack, dashingstrike.")
		print("Your hand is: " + " ".join(msgdata))
		move = input()
		s.send(move.encode())
	elif msgtype == "dspl-board":
		p1pos, p1name, p2pos, p2name, numcards = msgdata
		p1pos = int(p1pos)
		p2pos = int(p2pos)
		numcards = int(numcards)
		print("------------------------------------------------------")
		print("   " * p1pos + "  " + p1name[0] + "   " * (p2pos - p1pos - 1) + "  " + p2name[0])
		print("  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18")
		print("------------------------------------------------------")
		print("Deck has", numcards, "cards.")
