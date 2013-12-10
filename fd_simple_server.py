import socket
import random
import sys
import os

class Deck(object):
	cards = []

	def __init__(self):
		self.cards = [1,2,3,4,5] * 5
		self.shuffle()

	def shuffle(self):
		random.shuffle(self.cards)

	def draw(self, numCards):
		cardsDrawn = []
		for i in range(numCards):
			cardsDrawn.append(self.cards.pop())
		return cardsDrawn

	def empty(self):
		return len(self.cards) == 0
	
	def view(self):
		print("Deck:")
		print(self.cards)

class Discard(object):
	cards = []

	def __init__(self):
		self.cards = []

	def add(discardedCards):
		self.cards += discardedCards
		self.cards.sort()

	def view(self):
		print("Discard:")
		print(self.cards)

class Player(object):
	pos = 0
	hand = []
	towardDir = 1
	name = ""
	stunned = False
	conn = None

	def __init__(self, startPos, towardDir, name, pconn):
		self.pos = startPos
		self.hand = []
		self.towardDir = towardDir
		self.name = name
		self.stunned = False
		self.conn = pconn

	def draw(self, numCards, deck):
		self.hand += deck.draw(numCards)
		self.hand.sort()

	def drawUpTo(self, numCards, deck):
		self.draw(numCards - len(self.hand), deck)

	def viewHand(self):
		print("%s's Hand:" % self.name)
		print(self.hand)

	def takeTurn(self, other, deck, discard):
		if self.stunned:
			stun_str = "dspl-txt " + self.name + " is stunned! " + self.name + " draws up to 5 and ends turn."
			self.conn.send(stun_str.encode())
			other.conn.send(stun_str.encode())
			self.stunned = False
			self.drawUpTo(5, deck)
			return True
		moverqststr = "get-move " + " ".join(str(card) for card in self.hand)
		self.conn.send(moverqststr.encode())
		moveString = self.conn.recv(1024).decode()
		move, cards = splitMove(moveString)
		if move in ["movetoward", "moveaway", "push", "attack", "dashingstrike"]:
			self.playCards(cards)
			if move == "movetoward":
				self.moveToward(other, cards[0])
			elif move == "moveaway":
				self.moveAway(cards[0])
			elif move == "push":
				self.push(other, cards[0])
			elif move == "attack":
				self.attack(other, cards[0], len(cards))
			elif move == "dashingstrike":
				self.dashingStrike(other, cards[0], cards[1], len(cards) - 1)
			else:
				#bad!
				exit()
		else:
			#bad!
			exit()
		self.drawUpTo(5, deck)
		return True

	def lose(self):
		print(self.name + " loses!")
		exit()

	def playCards(self, cards):
		oldHand = self.hand
		for card in cards:
			if card in self.hand:
				self.hand.remove(card)
			else:
				self.hand = oldHand
				return False
		return True

	#testing whether desired cards are in the hand should be done before
	#these moves are called!
	def moveToward(self, other, dist):
		if self.towardDir == 1:
			self.pos = min(other.pos - 1, self.pos + dist)
		else:
			self.pos = max(other.pos + 1, self.pos - dist)
		print(self.name, "moved forward by %d" % dist)
		return True

	def moveAway(self, dist):
		if self.towardDir == 1:
			self.pos = max(0, self.pos - dist)
		else:
			self.pos = min(17, self.pos + dist)
		print(self.name, "moved away by %d" % dist)
		return True

	def push(self, other, dist):
		if abs(self.pos - other.pos) != 1:
			return False
		other.moveAway(dist)
		return True

	def attack(self, other, dist, strength):
		if abs(self.pos - other.pos) != dist:
			print("Invalid attack distance!")
			return False
		other.respondAttack(dist, strength)
		return True

	def dashingStrike(self, other, dashDist, attackDist, strength):
		originalPos = self.pos
		self.moveToward(other, dashDist)
		if abs(self.pos - other.pos) != attackDist:
			self.pos = originalPos
			return False
		other.respondDashingStrike(attackDist, strength)
		return True

	def respondAttack(self, dist, strength):
		if self.hand.count(dist) < strength:
			self.lose()
		else:
			print(self.name, " defends with %d %ds" % (strength, dist))
			for i in range(strength):
				self.hand.remove(dist)
		return True

	#this should definitely be simplified
	def respondDashingStrike(self, dist, strength):
		print(self.name + ", you must defend or retreat a dashing strike from dist %d with strength %d." % (dist, strength))
		print("Your hand is:", self.hand)
		moveString = input("Give your response: ")
		move, cards = splitMove(moveString)
		if move in ["defend", "retreat"]:
			if move == "defend":
				return self.respondAttack(dist, strength)
			elif move == "retreat":
				self.playCards(cards)
				#only one card should have been played
				self.moveAway(cards[0])
				self.stunned = True
				print(self.name, "retreats %d" % cards[0], "and is now stunned!")
				return True
			else:
				#how did you get here?!
				exit()
		else:
			#not a valid move!
			exit()



def splitMove(moveWithCards):
	allSymbols = moveWithCards.split()
	move = allSymbols.pop(0)
	cards = [int(x) for x in allSymbols]
	#Now allSymbols is just a list of cards played with the move
	return move, cards

def printGameState(p1, p2, deck, discard):
	print("------------------------------------------------------")
	print("   " * p1.pos + "  " + p1.name[0] + "   " * (p2.pos - p1.pos - 1) + "  " + p2.name[0])
	print("  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18")
	print("------------------------------------------------------")
	print("Deck has", len(deck.cards), "cards.")

def getGameStateMsgStr(p1, p2, deck, discard):
	return "dspl-board %d %s %d %s %d" % (p1.pos, p1.name, p2.pos, p2.name, len(deck.cards))

def start():
	HOST = ""
	PORT = 8888
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(10)

	p1conn, p1addr = s.accept()
	print('Connected with p1 at ' + p1addr[0] + ':' + str(p1addr[1]))
	p2conn, p2addr = s.accept()
	print('Connected with p2 at ' + p2addr[0] + ':' + str(p2addr[1]))

	#Get player names
	p1conn.send("name-rqst".encode())
	p1name = p1conn.recv(1024).decode()
	p2conn.send("name-rqst".encode())
	p2name = p2conn.recv(1024).decode()
	playingstr = "dspl-txt " + p1name + " is playing against " + p2name

	deck = Deck()
	discard = Discard()
	deck.shuffle()

	p1 = Player(0, 1, p1name, p1conn)
	p2 = Player(17, -1, p2name, p2conn)

	p1.drawUpTo(5, deck)
	p2.drawUpTo(5, deck)

	while(not deck.empty()):
		p1.conn.send(getGameStateMsgStr(p1, p2, deck, discard).encode())
		p1.takeTurn(p2, deck, discard)
		p1.conn.send(getGameStateMsgStr(p1, p2, deck, discard).encode())
		p2.conn.send(getGameStateMsgStr(p1, p2, deck, discard).encode())
		p2.takeTurn(p1, deck, discard)
		p2.conn.send(getGameStateMsgStr(p1, p2, deck, discard).encode())

if __name__ == '__main__':
    start()