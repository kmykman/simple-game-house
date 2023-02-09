# Simple Game House

A python scoket program for multiple players connecting to server to play random guessing game using TCP protocol.

## Author

Man Yuet Ki Kimmy

## Description
There are 10 game rooms in total.  Players need to input correct username and password to enter game rooms.  Each game room can accept a maximum of 2 players.  When there is 2 players in the game room, the game starts and each player need to guess *True* or *False*.  The server randomly generate *True* or *False* and inform the game result to players.  The result is *win* or *lose* or *tie*.

## Features
- path of UserInfo.txt accept absolute path or relative path or directly input file name
- when server disconnects while waiting for client input, once client inputs something, error showing disconnection pops up and exit
- when client disconnects, server shows client disconnection message and client name
- if disconnected client A is in playing game stage, server treats another client B as winner and display winning result after that client B sends valid `/guess`
- if client A initially in waiting stage, client A disconnects and client B enters that room at the same time, server will let client B enters and start the game, but it treats client B as winner because client A disconnects
- in playing game stage, client can input `/guess true` or `/guess True` (both capital letter or small letter of `true` and `false` is accepted)
## Usage
- Prepare `UserInfo.txt` to store the login information of players
- Open GameServer before opening GameClient

#### GameServer
```
python3 GameServer.py <server's listening port> <path to login information UserInfo.txt>
```
For example
```
python3 GameServer.py 12345 /home/Documents/Prog_Assignment/UserInfo
```
or
```
python3 GameServer.py 12345 ./UserInfo
```
or
```
python3 GameServer.py 12345 UserInfo
```
#### GameClient
```
python3 GameClient.py <hostname / IP address of the server> <server's listening port>
```
For example
```
python3 GameClient.py localhost 12345
```
After `1001 Authentication successful` is shown, player can enter
`/list`: to show number of player in each room
Output
```
3001 <no. of room> <no. of player in each room>
```
For example
```
3001 10 1 0 0 0 0 0 0 0 0 2
```
means in 10 game rooms, room 1 has 1 player and room 10 has 2 players

`/enter <room number (1-10)>`: to enter game room

## Input assumptions
- User does not enter name with space when login
- User does not input when in wait stage and when waiting for another user input in playing stage

## Server output
when player connects to server successfully
```
Connection established. Here is the remote peer info: ('127.0.0.1', 34628)
```
when user login successfully
```
Bob login
```
when player disconnects
```
Error : <socket error or exception message>
Bob disconnected unexpectedly
```
when player inputs in game hall
```
Jacky /enter 1
Bob /list
```
## Client output
- basic ouputs are same as assignment document
when `Ctrl-C` is pressed to terminate client
```
Keyboard Interrupt
```
when server disconnected
```
Error : <socket error or exception message>
Server disconnected unexpectedly
```

Copyright 2022 Man Yuet Ki Kimmy
