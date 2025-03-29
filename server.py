import socket, threading, pickle, mysql.connector
from game_functions import *
import uuid

# tokens for server to select from
token = ["images/dog.png", "images/hat.png", "images/car.png", "images/ship.png"]

def initalise_game(game_id, token, player_class, socket_add):
    return {"game_id":game_id, "clients_turn":0, "players":[player_class], "token":token, "all_bought":[], "bought":[], "message":[], "all_messages":[], "clients":[[player_class.client_id, socket_add]], "currently_playing":0}

lobby = []
games = [{"game_id":"0", "clients_turn":0, "players":[], "token":token, "all_bought":[], "bought":[], "message":[], "all_messages":[], "clients":[], "currently_playing":0}]

# run each client in this class
class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket):
        # start threading process
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.client_number = str(uuid.uuid4())
        self.game_id = str(uuid.uuid4())[:6]
        self.current_game_location = None
        print ("New connection added: ", clientAddress)

    def run(self):
        global lobby, games

        # send client number
        self.csocket.sendall(pickle.dumps(self.client_number))

        # recieve client details
        details = pickle.loads(self.csocket.recv(1024*5))
        lobby.append(Player(details[0], details[1]))

        game_create_completed = False

        while True:
            if game_create_completed == False:
                #load data from client
                try:
                    data_in = pickle.loads(self.csocket.recv(1024*5))
                except:
                    counter = 0
                    found = False
                    while counter < len(lobby) and found == False:
                        if lobby[counter].client_id == self.client_number:
                            lobby.pop(counter)
                            found = True
                    break

                # the revieved data is asking for a new game to be created
                if data_in[0] == 0:
                    found = False
                    counter = 0
                    found_empty_game = False

                    # find client in lobby server
                    while found == False and counter < len(lobby):
                        if lobby[counter].client_id == self.client_number:
                            found = True
                            game_create_completed = True
                            found_empty_game_counter = 0

                            # check for empty game containers
                            while found_empty_game_counter < len(games) and found_empty_game == False:
                                if games[found_empty_game_counter] == {}:
                                    games[found_empty_game_counter] = initalise_game(self.game_id, token, lobby[counter], self.csocket)
                                    self.current_game_location = found_empty_game_counter
                                    found_empty_game = True
                                else:
                                    found_empty_game_counter += 1
                            
                            # need to create a new game container as all are being used
                            if found_empty_game == False:
                                games.append(initalise_game(self.game_id, token, lobby[counter], self.csocket))
                                self.current_game_location = len(games)-1
                            else:
                                found_empty_game = False

                            # adds the players attributes into the new game server
                            games[self.current_game_location]["players"][0].token_location = games[self.current_game_location]["token"][len(games[self.current_game_location]["token"])-1]
                            games[self.current_game_location]["token"].pop(len(games[self.current_game_location]["token"])-1)

                            # remove player from lobby otherwise duplicate account
                            lobby.pop(counter)
                        else:
                            counter += 1

                    self.csocket.sendall(pickle.dumps({"game_create_completed":game_create_completed}))

                # the recieved data is asking to join a game using a game_id
                elif data_in[0] == 1:
                    client_game_id = data_in[1]
                    client_game_location = False

                    for i in range(0, len(games)):
                        try:
                            if games[i]["game_id"] == client_game_id:
                                client_game_location = str(i)
                        except:
                            pass

                    # client location has been found in the servers
                    if client_game_location != False:
                        client_game_location = int(client_game_location)
                        found = False
                        counter = 0
                        while found == False and counter < len(lobby):
                            if lobby[counter].client_id == self.client_number:
                                found = True
                                game_create_completed = True

                                # add the player and client attribute to the new server from the lobby
                                games[client_game_location]["players"].append(lobby[counter])
                                games[client_game_location]["clients"].append([lobby[counter].client_id, self.csocket])

                                lobby.pop(counter)
                                self.current_game_location = client_game_location
                                self.game_id = games[client_game_location]["game_id"]
                            else:
                                counter += 1
                        
                        games[self.current_game_location]["players"][len(games[self.current_game_location]["players"])-1].token_location = games[self.current_game_location]["token"][len(games[self.current_game_location]["token"])-1]
                        games[self.current_game_location]["token"].pop(len(games[self.current_game_location]["token"])-1)
                
                    self.csocket.sendall(pickle.dumps({"game_create_completed":game_create_completed}))
            else:
                try:
                    data_in = pickle.loads(self.csocket.recv(1024*5))
                except:
                    # remove game lobby from list of games if no recieved data
                    counter = 0
                    found = False
                    while counter < len(games[self.current_game_location]["clients"]) and found == False:
                        if games[self.current_game_location]["clients"][counter][0] == self.client_number:
                            games[self.current_game_location]["clients"].pop(counter)
                            found = True

                    # if no clients remain in game lobby
                    if games[self.current_game_location]["clients"] == []:
                        games[self.current_game_location] = {}
                    else:
                        counter = 0
                        found = False

                        # loop through the games and find the client
                        while counter < len(games[self.current_game_location]["players"]) and found == False:
                            if games[self.current_game_location]["players"][counter].client_id == self.client_number:
                                # once found remove player
                                games[self.current_game_location]["players"].pop(counter)

                                try:
                                    games[self.current_game_location]["players"][counter]
                                except:
                                    games[self.current_game_location]["clients_turn"] = 0
                                
                                found = True
                        
                        # add bought assets to the player who owns it
                        bought_assets = []
                        for i in range(0, len(games[self.current_game_location]["bought"])):
                            if games[self.current_game_location]["bought"][i][1] == self.client_number:
                                bought_assets.append(i)
                        
                        # remove the last bought asset
                        for i in range(len(bought_assets)-1, -1, -1):
                            games[self.current_game_location]["bought"].pop(i)

                        games[self.current_game_location]["currently_playing"] -= 1

                        # data to send back to client
                        data_out = {"players":games[self.current_game_location]["players"], "clients_turn":games[self.current_game_location]["clients_turn"], "bought":games[self.current_game_location]["bought"], "currently_playing":games[self.current_game_location]["currently_playing"]}

                        for i in range(0, len(games[self.current_game_location]["clients"])):
                            try:
                                games[self.current_game_location]["clients"][i][1].sendall(pickle.dumps(data_out))
                            except:
                                break
                    break

                # recieve and send data from client back to them
                try:
                    sent_client_number = data_in["client_number"]
                except:
                    pass

                try:
                    message = data_in["message"]
                    games[self.current_game_location]["message"] = [message[0], message[2], message[1]]
                    games[self.current_game_location]["all_messages"].append([games[self.current_game_location]["message"], sent_client_number, message[1]])
                except:
                    pass

                try:
                    players = data_in["players"]
                    games[self.current_game_location]["players"] = players
                except:
                    pass

                try:
                    bought = data_in["bought"]
                    games[self.current_game_location]["bought"].append(bought)
                    games[self.current_game_location]["all_bought"].append(bought)
                except:
                    pass

                try:
                    currently_playing = data_in["currently_playing"]
                    games[self.current_game_location]["currently_playing"] = currently_playing
                except:
                    pass

                try:
                    clients_turn = data_in["clients_turn"]
                    games[self.current_game_location]["clients_turn"] = clients_turn
                except:
                    pass

                # data to send back to client
                data_out = {"message":games[self.current_game_location]["message"], "players":games[self.current_game_location]["players"], "clients_turn":games[self.current_game_location]["clients_turn"], "bought":games[self.current_game_location]["bought"], "currently_playing":games[self.current_game_location]["currently_playing"], "game_id":self.game_id}

                games[self.current_game_location]["message"] = []
                games[self.current_game_location]["bought"] = []
                for i in range(0, len(games[self.current_game_location]["clients"])):
                    try:
                        games[self.current_game_location]["clients"][i][1].sendall(pickle.dumps(data_out))
                    except:
                        break
            
        print ("Client at ", clientAddress , " disconnected...")

LOCALHOST = socket.gethostbyname(socket.gethostname())
PORT = 8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))

# maximum amount of clients
while True:
    server.listen()
    clientsock, clientAddress = server.accept()

    # create new thread for client
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()