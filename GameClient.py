#!/usr/bin/python3

import socket
import os.path
import sys

def main(argv):
	try:
		sockfd = socket.socket()
		sockfd.connect((argv[1], int(argv[2])))
	except socket.error as emsg:
		print("Socket error: ", emsg)
		sys.exit(1)
	login(sockfd)
	
def login(sockfd):
	authen = 0
	while (authen == 0):
		try:
			name = input("Please input your user name:\n")
			if not name:                                               # require user to enter again if enter empty
				continue
			password = input("Please input your password:\n")
			while not password:
				password = input("Please input your password:\n")
			login = " ".join(['/login', name, password])
			sockfd.sendall(login.encode('ascii'))
			reply = sockfd.recv(50).decode()
			if reply == '':                                            # reply is '' if server disconnects
				raise Exception()
			print(reply)
			s_reply = reply.split()
			if s_reply[0] == "1001":
				authen = 1
				game_hall(sockfd)                                  # go to game hall stage
				break
			elif s_reply[0] == "1002":                                 # incorrect user login info
				continue
		except socket.error as emsg:
			print("Socket sendall error: ", emsg)
			sys.exit(1)
		except Exception as m:
			print("Error : ", m)
			print("Server disconnected unexpectedly")
			sys.exit(0)
		except KeyboardInterrupt:
			print("Keyboard Interrupt")
			sys.exit(1)


def game_hall(sockfd):
	hall = 0
	while (hall == 0):
		try:
			hall_request = input()
			if not hall_request:
				continue
			sockfd.sendall(hall_request.encode('ascii'))
			reply = sockfd.recv(50).decode()
			print(reply)
			s_reply = reply.split()
			if s_reply[0] == "3011":                  # enter empty room
				hall = 1
				wait_rm(sockfd)
				break
			elif s_reply[0] == "3001" or s_reply[0] == "3013" or s_reply[0] == "4002":           # when input is /list or room is full or invalid input
				continue
			elif s_reply[0] == "3012":                # start the game
				hall = 1
				playing(sockfd)
				break
			elif s_reply[0] == "4001":
				print("Client ends")
				sockfd.close()
				sys.exit(1)
		except socket.error as emsg:
			print("Socket sendall error: ", emsg)
			sys.exit(1)
		except KeyboardInterrupt:
			print("Keyboard Interrupt")
			sys.exit(1)

def wait_rm(sockfd):
	wait = 0
	while (wait == 0):
		try:
			while 1:                                  # keep on communicating with server while waiting to know if server is still connected
				sockfd.sendall(b"HERE")
				reply = sockfd.recv(50).decode()
				if "OK" not in reply:
					break
			if "OK" in reply:
				continue
			print(reply)
			s_reply = reply.split()
			if s_reply[0] == "3012":                 # start the game
				wait = 1
				playing(sockfd)
				break
		except socket.error as emsg:
			print("Socket sendall error: ", emsg)
			print("Server disconnected unexpectedly")
			sys.exit(1)
		except KeyboardInterrupt:
			print("Keyboard Interrupt")
			sys.exit(1)

def playing(sockfd):
	game = 0
	while (game == 0):
		try:
			choice = input()                          # t/f
			if not choice:
				continue
			choice = choice
			sockfd.sendall(choice.encode('ascii'))
			while 1:                                       # keep on communicating with server while waiting to know if server is still connected
				sockfd.sendall(b"HERE")
				result = sockfd.recv(50).decode()
				r = result.replace("OK", "")
				if r == '':
					continue
				if result != "OK":
					break
				if "3" in result or "4" in result:      # when real game result comes
					break
			result = result.replace("OK", "")               # received message may mixed with "OK" in checking stage, so need to remove "OK"
			if result == "":
				continue
			print(result)                          # tie/win/lost
			s_result = result.split()
			if s_result[0] == "3023" or s_result[0] == "3021" or s_result[0] == "3022":
				game_hall(sockfd)                       # go back to game hall
				break
			elif s_result[0] == "4002":
				continue
		except socket.error as emsg:
			print("Socket sendall error: ", emsg)
			print("Server disconnected unexpectedly")
			sys.exit(1)
		except Exception as m:
			print("Error : ", m)
			print("Server disconnected unexpectedly")
			sys.exit(0)
		except KeyboardInterrupt:
			print("Keyboard Interrupt")
			sys.exit(1)

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Usage: python3 GameClient.py <Server_addr> <Server_port>")
		sys.exit(1)
	main(sys.argv)
