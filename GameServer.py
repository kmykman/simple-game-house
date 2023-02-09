#!/usr/bin/python3

import socket
import sys
import os.path
import threading
import random
import copy
import time

room_status = []
room_choice = []
room_result = []
room_discon = []
room_player = []

for i in range(10):
	room_status.append([])                                      # name of people in the room in form of [[John], [Peter, Alice], [], ...]
	room_choice.append([])                                      # choice of player in the room in form of [[], [0, 1], [], ...]
	room_result.append([])                                      # random result of each room if not tie
	room_discon.append([])                                      # number of people disconnected in each room in form of [[dis], [], [], ...]
	room_player.append([])                                      # copy of room_status[], but change when one of the player complete the game

lock = threading.Lock()

def thread_func(client, user_file):
	while True:
		try:
			conn, addr = client
			print("Connection established. Here is the remote peer info:", addr)
			login(user_file, conn)
			conn.close()
		except socket.error as emsg:
			print("Socket error : ", emsg)
			sys.exit(0)
		except Exception:                                # if client disconnects in login stage
			print(addr[1], ": client disconnected unexpectedly")
			sys.exit(0)
		except KeyboardInterrupt:
			print("Keyboard Interrupt")
			sys.exit(1)
def login(user_file, conn):
	login_s = 0
	while (login_s == 0):
		try:
			login_detail = conn.recv(1024).decode()
			name_password = login_detail.split()
			comb = name_password[1] + ":" + name_password[2] + "\n"
			with open(user_file) as fd:                                       # open UserInfo.txt for checking
				if comb in fd.read():
					succ = "1001 Authentication successful"
					conn.sendall(succ.encode('ascii'))
					login_s = 1
					fd.close()
					print(name_password[1], "login")
					game_hall(name_password[1], conn)                   # enter game hall after successful login
					break
				else:
					succ = "1002 Authentication failed"
					conn.sendall(succ.encode('ascii'))
					fd.close()
					continue
		except os.error as msg:
			print("File error: ", msg)
			sys.exit(1)
		except socket.error as emsg:
			print("Socket error : ", emsg)
			sys.exit(0)
		except Exception:
			print(name_password[1], "disconnected unexpectedly")
			sys.exit(0)
		except KeyboardInterrupt:
			print("Keyboard Interrupt")
			sys.exit(1)
	
def game_hall(name, conn):
	global room_status
	hall = 0
	while (hall == 0):
		try:
			re_in = conn.recv(1024).decode()
			request = re_in.split()
			if request[0] == "HERE":                             # may have missending from playing game stage, so need to skip it
				continue
			print(name, re_in)
			if (len(request) == 1 and request[0] != "/list" and request[0] != "/exit") or (len(request) > 2) or (len(request) == 2 and (request[0] != "/enter"  or request[1].isdigit() == False or (int(request[1]) < 1 or int(request[1]) > 10))):
				reply = "4002 Unrecognized message"
				conn.sendall(reply.encode('ascii'))
				continue
			if request[0] == "/exit":
				reply = "4001 Bye bye"
				conn.sendall(reply.encode('ascii'))
				conn.close()                                 # close client connection if user /exit
				sys.exit(0)
			elif request[0] == "/list":
				reply = "3001 10"                            # 10 game rooms in total
				lock.acquire()
				for x in room_status:
					reply = reply + " " + str(len(x))
				lock.release()
				conn.sendall(reply.encode('ascii'))
				continue
			elif request[0] == "/enter":                                        # int(request[1]) - 1 is room number - 1, to be used in searching list later
				if len(room_status[int(request[1]) - 1]) == 0:              # when required enter room is empty
					lock.acquire()
					room_status[int(request[1]) - 1].append(name)
					lock.release()
					wait_rm(int(request[1]) - 1, conn, name)
					break
				elif len(room_status[int(request[1]) - 1]) == 1:              # when required enter room already have one person waiting
					lock.acquire()
					room_status[int(request[1]) - 1].append(name)
					lock.release()
					playing(int(request[1]) - 1, conn, name)
					break
				elif len(room_status[int(request[1]) - 1]) >= 2:              # when required enter room is full
					reply = "3013 The room is full"
					conn.sendall(reply.encode('ascii'))
					continue
		except socket.error as emsg:
			print("Socket error : ", emsg)
			sys.exit(0)
		except Exception as m:
			print("Error : ", m)
			print(name, "disconnected unexpectedly")
			sys.exit(0)
		except KeyboardInterrupt:
			print("Keyboard Interrupt")
			sys.exit(1)
def wait_rm(room, conn, name):
	global room_status
	wait = 0
	reply = "3011 Wait"
	conn.sendall(reply.encode('ascii'))
	while (wait == 0):
		try:
			while 1:
				deadline = time.time() + 0.5                    # if no message sends from client constantly, it means client disconnects
				while not conn.recv(50):
					if time.time() >= deadline:
						raise Exception()
				conn.sendall("OK".encode('ascii'))
				if len(room_status[room]) == 2:
					wait = 1
					playing(room, conn, name)
					break
		except socket.error as emsg:
			print("Socket error : ", emsg)
			print(name, "disconnected unexpectedly")
			lock.acquire()
			room_status[room].clear()
			lock.release()
			sys.exit(0)
		except Exception as m:
			print("Error : ", m)
			print(name, "disconnected unexpectedly")
			lock.acquire()
			room_status[room].clear()                              # remove waiting player from list
			lock.release()
			sys.exit(0)
		except KeyboardInterrupt:
			print("Keyboard Interrupt")
			sys.exit(1)
def playing(room, conn, name):
	global room_choice, room_result, room_discon, room_player
	room_player = copy.deepcopy(room_status)
	play = 0
	reply = "3012 Game started. Please guess true or false"
	conn.sendall(reply.encode('ascii'))
	while (play == 0):
		try:
			choice = conn.recv(1024).decode()
			if choice == "HERE":                                         # may have missending from waiting stage, so need to skip it
				continue;
			choice = choice.replace("HERE", "")
			s_choice = choice.split()
			if len(s_choice) != 2 or s_choice[0] != "/guess" or (s_choice[1] != "true" and s_choice[1] != "True" and s_choice[1] != "false" and s_choice[1] != "False"):
				reply = "4002 Unrecognized message"
				conn.sendall(reply.encode('ascii'))
				continue
			if len(room_status[room]) == 0:                               # for a waiting player disconnects and another player enter the room at the same time
				lock.acquire()
				room_discon[room]. append("dis")
				lock.release()
			if s_choice[1] == "true" or s_choice[1] == "True":            # changing player choice from string to bool
				bc = True
			elif s_choice[1] == "false" or s_choice[1] == "False":
				bc = False
			lock.acquire()
			room_choice[room].append(bc)
			lock.release()
			while len(room_choice[room]) < 2:                              # when only one player enters the choice
				while 1:
					deadline = time.time() + 0.5                    # if no message sends from client constantly, it means client disconnects
					conn.sendall("OK".encode('ascii'))
					while not conn.recv(50):
						if len(room_choice[room]) == 2 or "dis" in room_discon[room]:
							break
						if time.time() >= deadline:
							raise socket.error()
					if len(room_choice[room]) == 2 or "dis" in room_discon[room]:
						break
				if len(room_choice[room]) == 2 or "dis" in room_discon[room]:
					break
				continue
			if "dis" in room_discon[room]:                                  # decide another player as winner when one of them disconnects
				reply = "3021 You are the winner"
			elif room_choice[room][0] == room_choice[room][1]:
				reply = "3023 The result is a tie"
			else:
				r = None
				lock.acquire()
				if len(room_result[room]) == 0:
					r = random.choice([True, False])                # random generate result
					room_result[room] = [r]
					if bc == r:
						reply = "3021 You are the winner"
					elif bc != r:
						reply = "3022 You lost this game"
				else:
					if bc in room_result[room]:
						reply = "3021 You are the winner"
					elif bc not in room_result[room]:
						reply = "3022 You lost this game"
				lock.release()
			conn.sendall(reply.encode('ascii'))
			room_player[room].remove(name)
			while len(room_player[room]) == 1:
				if len(room_player[room]) == 0 or len(room_status[room]) == 0:
					break
				continue
			lock.acquire()
			room_status[room].clear()                                    # both players leaving the room so need to clear corresponding list
			room_result[room].clear()
			room_discon[room].clear()
			room_choice[room].clear()
			room_player[room].clear()
			lock.release()
			game_hall(name, conn)
		except socket.error as emsg:
			print("Socket error : ", emsg)
			print(name, "disconnected unexpectedly")
			lock.acquire()
			room_discon[room]. append("dis")
			room_player[room].remove(name)
			if len(room_discon[room]) == 2:                            # clear corresponding list when both players disconnect
				room_status[room].clear()
				room_result[room].clear()
				room_discon[room].clear()
				room_choice[room].clear()
				room_player[room].clear()
			lock.release()
			sys.exit(0)
		except KeyboardInterrupt:
			print("Keyboard Interrupt")
			sys.exit(1)

def main(argv):
	serverPort = int(argv[1])
	sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockfd.bind( ("", serverPort) )
	
	sockfd.listen(5)
    
	print("The server is ready to receive")
	
	while True:
		client = sockfd.accept()
		new_thread = threading.Thread(target=thread_func, args=(client, argv[2],))
		new_thread.start()
	sockfd.close()

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Usage: python3 GameServer.py <Server_port> <path_to_UserInfo.txt>")
		sys.exit(1)
	if os.path.isfile(sys.argv[2]) == False:                                # when the entered path does not exist
		print("path :", sys.argv[2], "does not exist")
		sys.exit(1)
	main(sys.argv)
