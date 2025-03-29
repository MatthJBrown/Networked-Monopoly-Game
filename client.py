import socket, pickle, pygame, threading, mysql.connector, sys, hashlib, time
from pygame.locals import *
from game_functions import *

# sending data to server template
# out_data = {"message":"", "players":[], "client_number":our_client_number, "bought":[]}

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 8080

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

# connect to databases
connect_database = DB(mysql.connector)

# client_id is sent from server
our_client_number = pickle.loads(client.recv(1024*5))

# initiate pygame
pygame.init()
screen = pygame.display.set_mode((1500,1000))
pygame.display.set_caption("Monopoly | Play with friends!")

# fonts
main_title_font = pygame.font.Font('freesansbold.ttf', 170)
secondary_title_font = pygame.font.Font('freesansbold.ttf', 32)
options_font = pygame.font.Font('freesansbold.ttf', 50)
asset_font = pygame.font.Font('freesansbold.ttf', 35)
main_font = pygame.font.Font('freesansbold.ttf', 17)

# main colours
title_color = (255, 17, 0)
button_color = (40, 224, 215)
text_color = (0,0,0)
white_color = (255,255,255)

# main background
background = pygame.image.load("images/start_menu_background.jpg")
background = pygame.transform.scale(background, (1500, 1000))

players = []
all_messages = []
players_turn = 0
bought = []
currently_playing_players = 0
client_name = ""
game_id = ""

# current active page
login_menu_page = True
menu_page = False
login_page = False
register_page = False
create_game_page = False
waiting_page = False
main_game_page = False
option_page = False
help_page = False

# login_menu_page assets
login_menu_login = pygame.Rect(550,500,400,100)
login_menu_login_text = options_font.render("Login", True, text_color)

login_menu_register = pygame.Rect(550,610,400,100)
login_menu_register_text  = options_font.render("Register", True, text_color)

login_menu_login_active = False
login_menu_register_active = False

# login_page assets
login_page_username_input = ""
login_page_password_input = ""

login_page_username_clicked = False
login_page_password_clicked = False
login_page_submit_clicked = False

login_page_username = pygame.Rect(550,500,400,100)
login_page_username_text = secondary_title_font.render("Username:", True, text_color)

login_page_password = pygame.Rect(550,610,400,100)
login_page_password_text = secondary_title_font.render("Password:", True, text_color)

login_page_submit = pygame.Rect(650,720,200,50)
login_page_submit_text = secondary_title_font.render("Login", True, text_color)

# register_page assets
reg_page_username_input = ""
reg_page_password_input = ""

reg_page_username_clicked = False
reg_page_password_clicked = False
reg_page_submit_clicked = False

reg_page_username = pygame.Rect(550,500,400,100)
reg_page_username_text = secondary_title_font.render("Username:", True, text_color)

reg_page_password = pygame.Rect(550,610,400,100)
reg_page_password_text = secondary_title_font.render("Password:", True, text_color)

reg_page_submit = pygame.Rect(650,720,200,50)
reg_page_submit_text = secondary_title_font.render("Register", True, text_color)

# menu_page assets
menu_page_title_text = main_title_font.render("Monopoly", True, title_color)
menu_page_title = pygame.Rect(350, 200, 500, 100)

menu_page_play = pygame.Rect(500,500,500,100)
menu_page_play_text = options_font.render("PLAY GAME!", True, text_color)

menu_page_options = pygame.Rect(550,620,400,100)
menu_page_options_text = options_font.render("OPTIONS", True, text_color)

menu_page_help = pygame.Rect(600,740,300,100)
menu_page_help_text = options_font.render("HELP", True, text_color)

# option_page assets
# help_page assets

# create_game_page assets
create_game_page_pin_clicked = False
create_game_page_submit_clicked = False
create_game_page_new_clicked = False
create_game_page_submit_completed = False

create_game_page_pin_input = ""

create_game_page_new = pygame.Rect(325,450,400,100)
create_game_page_new_text = asset_font.render("Create new game", True, text_color)

create_game_page_pin = pygame.Rect(775,450,400,100)
create_game_page_pin_text = asset_font.render("Enter game pin:", True, text_color)

create_game_page_submit = pygame.Rect(775,560,250,50)
create_game_page_submit_text = asset_font.render("Submit", True, text_color)

# waiting_page assets
waiting_page_player_list = pygame.Rect(110, 110, 280, 780)

waiting_page_all_messages = pygame.Rect(410, 110, 990, 670)

waiting_page_chat_input = ""
waiting_page_chat_clicked = False
waiting_page_chat = pygame.Rect(410, 790, 990, 100)
waiting_page_chat_text = main_font.render("Enter message:", True, text_color)

waiting_page_ready_clicked = False
waiting_page_ready = pygame.Rect(180, 740, 140, 50)
waiting_page_ready_text = secondary_title_font.render("Click to begin", True, text_color)

# main_game_page assets
main_game_page_board = pygame.Rect(0,0,1000,1000)
main_game_page_board_image = pygame.image.load("images/monopoly_board.jpg")

main_game_page_stats = pygame.Rect(1010,10,480,400)

main_game_page_all_messages = pygame.Rect(1010,420,480,370)

main_game_page_chat_input = ""
main_game_page_chat_clicked = False
main_game_page_chat = pygame.Rect(1010,790,480,100)
main_game_page_chat_text = main_font.render("Enter message:", True, text_color)

main_game_page_roll_dice = pygame.Rect(350, 450, 300, 100)
main_game_page_roll_dice_text = main_title_font.render("ROLL", True, text_color)
main_game_page_roll_dice_clicked = False
main_game_page_roll_dice_rolled = False
main_game_page_roll_dice_no = 0

main_game_page_buy_out_jail = pygame.Rect(350, 450, 300, 100)
main_game_page_buy_out_jail_text = options_font.render("Buy out of jail", True, button_color)
main_game_page_buy_out_jail_clicked = False

main_game_page_roll_out_jail = pygame.Rect(350, 560, 300, 100)
main_game_page_roll_out_jail_text = options_font.render("Roll out of jail", True, button_color)
main_game_page_roll_out_jail_clicked = False

main_game_page_buy_asset = pygame.Rect(250, 250, 500, 500)

main_game_page_buy_asset_purchase = pygame.Rect(275, 650, 200, 50)
main_game_page_buy_asset_purchase_text = main_font.render("Purchase", True, text_color)
main_game_page_buy_asset_purchase_clicked = False

main_game_page_buy_asset_cancel = pygame.Rect(525, 650, 200, 50)
main_game_page_buy_asset_cancel_text = main_font.render("Cancel", True, text_color)
main_game_page_buy_asset_cancel_clicked = False

main_game_page_finished_turn = pygame.Rect(1010, 965, 480, 30)
main_game_page_finished_turn_text = main_font.render("Finished Turn", True, text_color)
main_game_page_finished_turn_clicked = False

# update players turn
def update_players_turn(players_turn, players):
    if players_turn < len(players)-1:
        players_turn += 1
    else:
        players_turn = 0
    
    return players_turn

#create process for recieving
def thread_recieve():
    global players, all_messages, players_turn, bought, create_game_page_submit_completed, currently_playing_players, game_id

    # continious loop inside the thread -> constant running
    while True:
        try:
            # the data recieved from server.
            in_data = pickle.loads(client.recv(1024*5))
        except:
            break

        # new message
        try:
            if in_data["message"] != []:
                all_messages.append(in_data["message"])
        except:
            pass

        # all updated players
        try:
            players = in_data["players"]
        except:
            pass

        # whose turn it is
        try:
            players_turn = in_data["clients_turn"]
        except:
            pass
        
        # new bought assets
        try:
            if in_data["bought"] != []:
                bought.append(in_data["bought"])
        except:
            pass

        try:
            create_game_page_submit_completed = in_data["game_create_completed"]
        except:
            pass
        
        # all curently playing players
        try:
            currently_playing_players = in_data["currently_playing"]
        except:
            pass

        # the game id
        try:
            game_id = in_data["game_id"]
        except:
            pass

# start thread_recieve()
r = threading.Thread(target=thread_recieve)
r.daemon = True
r.start()

running = True
while running:
    screen.blit(background, (0,0))

    # login menu
    if login_menu_page == True:
        pygame.draw.rect(screen, button_color, login_menu_login) 
        screen.blit(login_menu_login_text, login_menu_login)

        pygame.draw.rect(screen, button_color, login_menu_register)
        screen.blit(login_menu_register_text, login_menu_register)

        # update screen
        pygame.display.flip()
    
    # login page display to user
    elif login_page == True:
        # if username button
        if login_page_username_clicked == True:
            login_page_username_text = secondary_title_font.render(login_page_username_input, True, text_color)
        elif login_page_username_input == "":
            login_page_username_text = secondary_title_font.render("Username:", True, text_color)
        # if password button
        if login_page_password_clicked == True:
            login_page_password_text = secondary_title_font.render(login_page_password_input, True, text_color)
        elif login_page_password_input == "":
            login_page_password_text = secondary_title_font.render("Password:", True, text_color)
        # if submit button
        if login_page_submit_clicked == True:
            login_page_hashed_password = hashlib.sha224(login_page_password_input.encode('utf-8')).hexdigest()
            login_page_client_details = connect_database.login(login_page_username_input)
            # account validation
            if login_page_client_details != None:
                # if password equals the password stored
                if login_page_client_details[2] == login_page_hashed_password:
                    # send client username back to server
                    client_details = [login_page_username_input, our_client_number]
                    client.sendall(pickle.dumps(client_details))

                    client_name = login_page_username_input

                    login_page = False
                    menu_page = True
            
            login_page_submit_clicked = False

        pygame.draw.rect(screen, button_color, login_page_username)
        screen.blit(login_page_username_text, login_page_username)

        pygame.draw.rect(screen, button_color, login_page_password)
        screen.blit(login_page_password_text, login_page_password)

        pygame.draw.rect(screen, button_color, login_page_submit)
        screen.blit(login_page_submit_text, login_page_submit)

        # update screen overall
        pygame.display.flip()
    
    # register page
    elif register_page == True:
        # if username clicked
        if reg_page_username_clicked == True:
            reg_page_username_text = secondary_title_font.render(reg_page_username_input, True, text_color)
        elif reg_page_username_input == "":
            reg_page_username_text = secondary_title_font.render("Username:", True, text_color)

        # if password clicked
        if reg_page_password_clicked == True:
            reg_page_password_text = secondary_title_font.render(reg_page_password_input, True, text_color)
        elif reg_page_password_input == "":
            reg_page_password_text = secondary_title_font.render("Password:", True, text_color)

        # if submit button clicked
        if reg_page_submit_clicked == True:
            reg_page_hashed_password = hashlib.sha224(reg_page_password_input.encode('utf-8')).hexdigest()
            reg_page_client_details = connect_database.create_account(reg_page_username_input, reg_page_hashed_password)

            client_name = reg_page_username_input

            register_page = False
            login_page = False
            menu_page = True
            
            reg_page_submit_clicked = False

        pygame.draw.rect(screen, button_color, reg_page_username)
        screen.blit(reg_page_username_text, reg_page_username)

        pygame.draw.rect(screen, button_color, reg_page_password)
        screen.blit(reg_page_password_text, reg_page_password)

        pygame.draw.rect(screen, button_color, reg_page_submit)
        screen.blit(reg_page_submit_text, reg_page_submit)

        # update sceeen overall
        pygame.display.flip()

    # menu page
    elif menu_page == True:
        screen.blit(menu_page_title_text, menu_page_title)

        # draw on screen the main buttons; help play options
        pygame.draw.rect(screen, button_color, menu_page_play)
        screen.blit(menu_page_play_text, menu_page_play)

        pygame.draw.rect(screen, button_color, menu_page_options)
        screen.blit(menu_page_options_text, menu_page_options)

        pygame.draw.rect(screen, button_color, menu_page_help)
        screen.blit(menu_page_help_text, menu_page_help)

        # update screen
        pygame.display.flip()
    
    # create game page
    elif create_game_page == True:
        if create_game_page_submit_completed == True:
            create_game_page = False
            waiting_page = True
        else:
            out_data = [2]
            client.sendall(pickle.dumps(out_data))

            # show enter pin box
            if create_game_page_pin_clicked == True:
                create_game_page_pin_text = asset_font.render(create_game_page_pin_input, True, text_color)
            elif create_game_page_pin_input == "":
                create_game_page_pin_text = asset_font.render("Enter game pin:", True, text_color)

            # create a new game box
            if create_game_page_submit_clicked == True:
                client.sendall(pickle.dumps([1, create_game_page_pin_input]))
                create_game_page_submit_clicked = False
            elif create_game_page_new_clicked == True:
                client.sendall(pickle.dumps([0]))
                create_game_page_new_clicked = False

                create_game_page = False
                waiting_page = True

            pygame.draw.rect(screen, button_color, create_game_page_new) 
            screen.blit(create_game_page_new_text, create_game_page_new)
            
            pygame.draw.rect(screen, button_color, create_game_page_pin) 
            screen.blit(create_game_page_pin_text, create_game_page_pin)

            pygame.draw.rect(screen, button_color, create_game_page_submit) 
            screen.blit(create_game_page_submit_text, create_game_page_submit)

        # update screen overall
        pygame.display.flip()

    # once in game, waiting for it to begin page
    elif waiting_page == True:
        # send server data to receive new information
        out_data = {}
        client.sendall(pickle.dumps(out_data))

        if currently_playing_players >= 1 and currently_playing_players == len(players):
            waiting_page = False
            main_game_page = True
        else:
            # display game pin
            game_id_text = main_font.render(f"Game Pin: {game_id}", True, text_color)
            screen.blit(game_id_text, (20,20))

            pygame.draw.rect(screen, button_color, waiting_page_player_list)

            # loop through all players
            for i in range(0, len(players)):
                waiting_page_player_list_text = main_font.render(players[i].name, True, text_color)
                screen.blit(waiting_page_player_list_text, (waiting_page_player_list.x + 20, waiting_page_player_list.y + 20*i + 20))
            
            pygame.draw.rect(screen, white_color, waiting_page_all_messages)

            # display messages at the top of chat + move down as more messages
            if len(all_messages) <= 30 and len(all_messages) > 0:
                for i in range(0, len(all_messages)):
                    waiting_page_display_messages = main_font.render(f"From {all_messages[i][2]}: {all_messages[i][0]}", True, text_color)
                    screen.blit(waiting_page_display_messages, (waiting_page_all_messages.x + 20, waiting_page_all_messages.y + 20*i + 20))
            elif len(all_messages) > 0:
                for i in range(len(all_messages)-30, len(all_messages)):
                    waiting_page_display_messages = main_font.render(f"From {all_messages[i][2]}: {all_messages[i][0]}", True, text_color)
                    screen.blit(waiting_page_display_messages, (waiting_page_all_messages.x + 20, waiting_page_all_messages.y + 20*(i+30-len(all_messages)) + 20))

            pygame.draw.rect(screen, button_color, waiting_page_chat)
            
            # chat option box
            if waiting_page_chat_clicked == True:
                waiting_page_chat_text = main_font.render(waiting_page_chat_input, True, text_color)
            elif waiting_page_chat_input == "":
                waiting_page_chat_text = main_font.render("Enter message:", True, text_color)

            # display all chats to players
            screen.blit(waiting_page_chat_text, waiting_page_chat)

            if waiting_page_ready_clicked == True:
                waiting_page_ready_text = asset_font.render("READY", True, text_color)
            else:
                waiting_page_ready_text = asset_font.render("Click to begin", True, text_color)

            pygame.draw.rect(screen, button_color, waiting_page_ready)
            screen.blit(waiting_page_ready_text, waiting_page_ready)

        # update screen overall
        pygame.display.flip()
    
    elif main_game_page == True:
        client.sendall(pickle.dumps({}))

        screen.blit(main_game_page_board_image, main_game_page_board)
        pygame.draw.rect(screen, button_color, main_game_page_stats)

        # user stats
        for i in range(0, len(players)):
            main_game_page_stats_text = main_font.render(f"{players[i].name} : {players[i].stats()}", True, text_color)
            screen.blit(main_game_page_stats_text, (main_game_page_stats.x + 20, main_game_page_stats.y + 17*i))

        pygame.draw.rect(screen, white_color, main_game_page_all_messages)
        
        # display messages at the top of chat + move down as more messages
        if len(all_messages) <= 15 and len(all_messages) > 0:
            for i in range(0, len(all_messages)):
                main_game_page_display_messages = main_font.render(f"From {all_messages[i][2]}: {all_messages[i][0]}", True, text_color)
                screen.blit(main_game_page_display_messages, (main_game_page_all_messages.x + 20, main_game_page_all_messages.y + 20*i + 20))
        elif len(all_messages) > 0:
            for i in range(len(all_messages)-15, len(all_messages)):
                main_game_page_display_messages = main_font.render(f"From {all_messages[i][2]}: {all_messages[i][0]}", True, text_color)
                screen.blit(main_game_page_display_messages, (main_game_page_all_messages.x + 20, main_game_page_all_messages.y + 20*(i+15-len(all_messages)) + 20))
        
        pygame.draw.rect(screen, button_color, main_game_page_chat)

        if main_game_page_chat_clicked == True:
            main_game_page_chat_text = main_font.render(main_game_page_chat_input, True, text_color)
        elif main_game_page_chat_input == "":
            main_game_page_chat_text = main_font.render("Enter message:", True, text_color)
        
        screen.blit(main_game_page_chat_text, main_game_page_chat)

        # position of player turned into coordinates
        for i in range(0, len(players)):
            if players[i].pos == 0:
                main_game_page_player_sprite = pygame.Rect(897.5,897.5,50,50)
            elif players[i].pos > 0 and players[i].pos < 10:
                main_game_page_player_sprite_pos = players[i].pos
                main_game_page_player_sprite = pygame.Rect(897.5,855 - (main_game_page_player_sprite_pos*80) + 15,50,50)
            elif players[i].pos == 10:
                main_game_page_player_sprite = pygame.Rect(897.5,42.5,50,50)
            elif players[i].pos > 10 and players[i].pos < 20:
                main_game_page_player_sprite_pos = (players[i].pos)-10
                main_game_page_player_sprite = pygame.Rect(855 - (main_game_page_player_sprite_pos*80) + 15,42.5,50,50)
            elif players[i].pos == 20:
                main_game_page_player_sprite = pygame.Rect(42.5,42.5,50,50)
            elif players[i].pos > 20 and players[i].pos < 30:
                main_game_page_player_sprite_pos = (players[i].pos)-20
                main_game_page_player_sprite = pygame.Rect(42.5,60 + (main_game_page_player_sprite_pos*80) + 15,50,50)
            elif players[i].pos == 30:
                main_game_page_player_sprite = pygame.Rect(42.5,897.5,50,50)
            elif players[i].pos > 30 and players[i].pos < 40:
                main_game_page_player_sprite_pos = (players[i].pos)-30
                main_game_page_player_sprite = pygame.Rect(135 + (main_game_page_player_sprite_pos*80) - 65,897.5,50,50)
        
            main_game_page_player_sprite_image = pygame.image.load(players[i].token_location)
            screen.blit(main_game_page_player_sprite_image, main_game_page_player_sprite)

        # displays player's sprite on bought assets
        for i in range(0, len(bought)):
            main_game_page_asset_bought_pos = (bought[i][0][0])-1
            main_game_page_asset_bought_token = bought[i][0][2]
            
            if main_game_page_asset_bought_pos > 0 and main_game_page_asset_bought_pos < 10:
                main_game_page_player_sprite_pos = main_game_page_asset_bought_pos
                main_game_page_player_sprite = pygame.Rect(807.5,855 - (main_game_page_player_sprite_pos*80) + 15,50,50)
            elif main_game_page_asset_bought_pos > 10 and main_game_page_asset_bought_pos < 20:
                main_game_page_player_sprite_pos = (main_game_page_asset_bought_pos)-10
                main_game_page_player_sprite = pygame.Rect(855 - (main_game_page_player_sprite_pos*80) + 15,132.5,50,50)
            elif main_game_page_asset_bought_pos > 20 and main_game_page_asset_bought_pos < 30:
                main_game_page_player_sprite_pos = (main_game_page_asset_bought_pos)-20
                main_game_page_player_sprite = pygame.Rect(132.5,60 + (main_game_page_player_sprite_pos*80) + 15,50,50)
            elif main_game_page_asset_bought_pos > 30 and main_game_page_asset_bought_pos < 40:
                main_game_page_player_sprite_pos = (main_game_page_asset_bought_pos)-30
                main_game_page_player_sprite = pygame.Rect(135 + (main_game_page_player_sprite_pos*80) - 65,807.5,50,50)
        
            main_game_page_player_sprite_image = pygame.image.load(main_game_page_asset_bought_token)
            screen.blit(main_game_page_player_sprite_image, main_game_page_player_sprite)

        # decide which player's turn it is
        if players[players_turn].client_id == our_client_number:
            if players[players_turn].jail == True:
                
                # check if player in jail or not before go
                if main_game_page_buy_out_jail_clicked == False and main_game_page_roll_out_jail_clicked == False:
                    pygame.draw.rect(screen, white_color, main_game_page_buy_out_jail)
                    screen.blit(main_game_page_buy_out_jail_text, main_game_page_buy_out_jail)

                    pygame.draw.rect(screen, white_color, main_game_page_roll_out_jail)
                    screen.blit(main_game_page_roll_out_jail_text, main_game_page_roll_out_jail)

                if main_game_page_buy_out_jail_clicked == True:
                    if players[players_turn].money >= 250:
                        players[players_turn].jail = False
                        players[players_turn].money -= 250

                        players_turn = update_players_turn(players_turn, players)
                        main_game_page_buy_out_jail_clicked = False
                    else:
                        pass
                elif main_game_page_roll_out_jail_clicked == True:
                    if Dice().double():
                        players[players_turn].jail = False

                    players_turn = update_players_turn(players_turn, players)
                    main_game_page_roll_out_jail_clicked = False

                # return data back to server
                out_data = {"players":players, "clients_turn":players_turn}
                client.sendall(pickle.dumps(out_data))

                main_game_page_buy_out_jail_clicked = False
                main_game_page_roll_out_jail_clicked = False

            # not in jail
            else:
                if main_game_page_roll_dice_rolled == False:
                    if main_game_page_roll_dice_clicked == False:
                        pygame.draw.rect(screen, white_color, main_game_page_roll_dice)
                        screen.blit(main_game_page_roll_dice_text, main_game_page_roll_dice)

                    else: # if dice button now been clicked
                        main_game_page_roll_dice_value = 0
                        while main_game_page_roll_dice_no < 3:
                            main_game_page_roll_dice_die = Dice()

                            main_game_page_roll_dice_value += main_game_page_roll_dice_die.roll_value()

                            if main_game_page_roll_dice_die.double() == False:
                                break
                            else:
                                main_game_page_roll_dice_no += 1
                        
                        players[players_turn].add_pos(main_game_page_roll_dice_value)

                        # return updated player information back to the server
                        out_data = {"players":players}
                        client.sendall(pickle.dumps(out_data))

                        main_game_page_roll_dice_no = 0
                        main_game_page_roll_dice_value = 0

                        main_game_page_roll_dice_clicked = False
                        main_game_page_roll_dice_rolled = True
                else:
                    main_game_page_asset_buyable = connect_database.asset_buyable(players[players_turn].pos)

                    # means asset is buyable (property)
                    if main_game_page_asset_buyable[0] == 1:
                        main_game_page_asset_id = connect_database.asset_id(players[players_turn].pos)[0]
                        main_game_page_asset_rent = int(connect_database.asset_rent_price(players[players_turn].pos))

                        main_game_page_asset_owned = False

                        # find which asset we have landed on
                        counter = 0
                        found = False
                        while counter < len(bought) and found == False:
                            if bought[counter][0] == main_game_page_asset_id:
                                main_game_page_asset_owned = True
                                
                                # if someone owns property
                                if bought[counter][1] != our_client_number:
                                    for i in range(0, len(players)):
                                        if players[i].client_id == bought[counter][1]:
                                            players[i].money += main_game_page_asset_rent
                                    
                                    # take money from clients account for rent
                                    players[players_turn].money -= main_game_page_asset_rent
                                    found = True
                            counter += 1
                        
                        # if not been bought
                        if main_game_page_asset_owned == False and (main_game_page_buy_asset_purchase_clicked == False and main_game_page_buy_asset_cancel_clicked == False):
                            pygame.draw.rect(screen, white_color, main_game_page_buy_asset)

                            pygame.draw.rect(screen, button_color, main_game_page_buy_asset_purchase)
                            screen.blit(main_game_page_buy_asset_purchase_text, main_game_page_buy_asset_purchase)

                            pygame.draw.rect(screen, button_color, main_game_page_buy_asset_cancel)
                            screen.blit(main_game_page_buy_asset_cancel_text, main_game_page_buy_asset_cancel)
                            
                    elif main_game_page_asset_buyable[0] == 2:
                        # jail
                        pass
                    elif main_game_page_asset_buyable[0] == 3:
                        # community chest
                        pass
                    elif main_game_page_asset_buyable[0] == 4:
                        # chance
                        pass
                    elif main_game_page_asset_buyable[0] == 5:
                        players[players_turn].money -= 200

                    if (main_game_page_buy_asset_purchase_clicked == True or main_game_page_buy_asset_cancel_clicked == True) or main_game_page_asset_buyable[0] != 1:
                        pygame.draw.rect(screen, button_color, main_game_page_finished_turn)
                        screen.blit(main_game_page_finished_turn_text, main_game_page_finished_turn)

                    if main_game_page_finished_turn_clicked == True:
                        players_turn = update_players_turn(players_turn, players)

                        out_data = {"players":players, "clients_turn":players_turn}
                        client.sendall(pickle.dumps(out_data))

                        main_game_page_roll_dice_rolled = False
                        main_game_page_buy_asset_purchase_clicked = False
                        main_game_page_buy_asset_cancel_clicked = False
                        main_game_page_finished_turn_clicked = False

        pygame.display.flip()

    for event in pygame.event.get():
        if event.type == QUIT:
            main_running = False
            pygame.QUIT
            sys.exit()

        elif event.type == MOUSEBUTTONDOWN:
            # if login menu page button
            if login_menu_page == True:
                if login_menu_login.collidepoint(pygame.mouse.get_pos()):
                    login_page = True
                    register_page = False
                    login_menu_page = False
                elif login_menu_register.collidepoint(pygame.mouse.get_pos()):
                    login_page = False
                    register_page = True
                    login_menu_page = False
            # login page
            elif login_page == True:
                if login_page_username.collidepoint(pygame.mouse.get_pos()):
                    login_page_username_clicked = True
                else:
                    login_page_username_clicked = False
                    
                if login_page_password.collidepoint(pygame.mouse.get_pos()):
                    login_page_password_clicked = True
                else:
                    login_page_password_clicked = False
                
                if login_page_submit.collidepoint(pygame.mouse.get_pos()):
                    login_page_submit_clicked = True
                else:
                    login_page_submit_clicked = False
            # register page
            elif register_page == True:
                if reg_page_username.collidepoint(pygame.mouse.get_pos()):
                    reg_page_username_clicked = True
                else:
                    reg_page_username_clicked = False
                    
                if reg_page_password.collidepoint(pygame.mouse.get_pos()):
                    reg_page_password_clicked = True
                else:
                    reg_page_password_clicked = False
                
                if reg_page_submit.collidepoint(pygame.mouse.get_pos()):
                    reg_page_submit_clicked = True
                else:
                    reg_page_submit_clicked = False
            # menu page
            elif menu_page == True:
                if menu_page_play.collidepoint(pygame.mouse.get_pos()):
                    create_game_page = True
                    menu_page = False
            # create game page
            elif create_game_page == True:
                if create_game_page_pin.collidepoint(pygame.mouse.get_pos()):
                    create_game_page_pin_clicked = True
                else:
                    create_game_page_pin_clicked = False
                
                if create_game_page_submit.collidepoint(pygame.mouse.get_pos()):
                    create_game_page_submit_clicked = True
                else:
                    create_game_page_submit_clicked = False

                if create_game_page_new.collidepoint(pygame.mouse.get_pos()):
                    create_game_page_new_clicked = True
                else:
                    create_game_page_new_clicked = False
            # waiting page
            elif waiting_page == True:
                if waiting_page_chat.collidepoint(pygame.mouse.get_pos()):
                    waiting_page_chat_clicked = True
                else:
                    waiting_page_chat_clicked = False
                
                if waiting_page_ready.collidepoint(pygame.mouse.get_pos()):
                    if waiting_page_ready_clicked == True:
                        waiting_page_ready_clicked = False
                        currently_playing_players -= 1
                    else:
                        waiting_page_ready_clicked = True
                        currently_playing_players += 1
                    # send data back to server
                    out_data = {"currently_playing":currently_playing_players}
                    client.sendall(pickle.dumps(out_data))
            # main game page
            elif main_game_page == True:
                if main_game_page_chat.collidepoint(pygame.mouse.get_pos()):
                    main_game_page_chat_clicked = True
                else:
                    main_game_page_chat_clicked = False
                
                if players[players_turn].client_id == our_client_number:
                    if players[players_turn].jail == True:
                        if main_game_page_buy_out_jail.collidepoint(pygame.mouse.get_pos()):
                            main_game_page_buy_out_jail_clicked = True
                        
                        if main_game_page_roll_out_jail.collidepoint(pygame.mouse.get_pos()):
                            main_game_page_roll_out_jail_clicked = True
                    else:
                        if main_game_page_roll_dice_rolled == False:
                            if main_game_page_roll_dice_clicked == False:
                                if main_game_page_roll_dice.collidepoint(pygame.mouse.get_pos()):
                                    main_game_page_roll_dice_clicked = True
                        else:
                            if main_game_page_buy_asset_purchase.collidepoint(pygame.mouse.get_pos()):
                                main_game_page_buy_asset_purchase_clicked = True
                                players[players_turn].assets += 1
                                out_data = {"bought":[main_game_page_asset_id, our_client_number, players[players_turn].token_location], "players":players}
                                # send data back to server
                                client.sendall(pickle.dumps(out_data))
                            elif main_game_page_buy_asset_cancel.collidepoint(pygame.mouse.get_pos()):
                                main_game_page_buy_asset_cancel_clicked = True

                            if main_game_page_finished_turn.collidepoint(pygame.mouse.get_pos()):
                                main_game_page_finished_turn_clicked = True

        elif event.type == KEYDOWN:
            # username clicked
            if login_page_username_clicked == True:
                if event.key == pygame.K_BACKSPACE:
                    login_page_username_input = login_page_username_input[:-1]
                else:
                    login_page_username_input += event.unicode
            # password clicked
            elif login_page_password_clicked == True:
                if event.key == pygame.K_BACKSPACE:
                    login_page_password_input = login_page_password_input[:-1]
                else:
                    login_page_password_input += event.unicode
            elif reg_page_username_clicked == True:
                if event.key == pygame.K_BACKSPACE:
                    reg_page_username_input = reg_page_username_input[:-1]
                else:
                    reg_page_username_input += event.unicode
            elif reg_page_password_clicked == True:
                if event.key == pygame.K_BACKSPACE:
                    reg_page_password_input = reg_page_password_input[:-1]
                else:
                    reg_page_password_input += event.unicode
            elif create_game_page_pin_clicked == True:
                if event.key == pygame.K_BACKSPACE:
                    create_game_page_pin_input = create_game_page_pin_input[:-1]
                else:
                    create_game_page_pin_input += event.unicode
            elif waiting_page_chat_clicked == True:
                if event.key == pygame.K_BACKSPACE:
                    waiting_page_chat_input = waiting_page_chat_input[:-1]
                elif event.key == pygame.K_RETURN:
                    out_data = {"message":[waiting_page_chat_input, client_name, our_client_number]}
                    client.sendall(pickle.dumps(out_data))
                    waiting_page_chat_input = ""
                else:
                    waiting_page_chat_input += event.unicode
            elif main_game_page_chat_clicked == True:
                if event.key == pygame.K_BACKSPACE:
                    main_game_page_chat_input = main_game_page_chat_input[:-1]
                elif event.key == pygame.K_RETURN:
                    out_data = {"message":[main_game_page_chat_input, client_name, our_client_number]}
                    client.sendall(pickle.dumps(out_data))
                    main_game_page_chat_input = ""
                else:
                    main_game_page_chat_input += event.unicode
                    