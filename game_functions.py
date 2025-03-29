import random, pygame, sys, mysql.connector
from pygame.locals import *

class DB():
    def __init__(self, connection):
        self.db = connection.MySQLConnection(user='root', password='root', host='localhost', database='monopoly', port=3306)
    
    # login
    def login(self, username):

        sql = f"SELECT * FROM users WHERE username='{username}'"
        
        cursor = self.db.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()

        for i in records:
            return i
    
    # create account
    def create_account(self, username, password):
        sql = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"

        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()

    # landed on asset id
    def asset_id(self, pos):
        sql = f"SELECT id FROM assets WHERE position={pos}"

        cursor = self.db.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()

        for i in records:
            return i

    # landed on asset buyable
    def asset_buyable(self, pos):
        sql = f"SELECT buyable FROM assets WHERE position={pos}"

        cursor = self.db.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()

        for i in records:
            return i

    # landed on asset name
    def asset_name(self, pos):
        sql = f"SELECT name FROM assets WHERE position={pos}"

        cursor = self.db.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()

        for i in records:
            return i

    # landed on asset buy price
    def asset_buy_price(self, pos):
        sql = f"SELECT price FROM assets WHERE position={pos}"

        cursor = self.db.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()

        for i in records:
            return i

    # landed on asset rent price
    def asset_rent_price(self, pos):
        sql = f"SELECT price FROM assets WHERE position={pos}"

        cursor = self.db.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()

        for i in records:
            return (int(i[0])*0.10)

# class for player attributes
class Player():
    def __init__(self, name, client_id):
        self.name = name
        # the identifier of client
        self.client_id = client_id
        self.token_location = None
        self.jail = True
        self.bankrupt = False
        self.money = 1500
        self.assets = 0
        self.assetsValue = 0
        #position on board
        self.pos = 0
        self.turnDone = False

    def stats(self):
        return [f"Position: {self.pos}", f"Jail: {self.jail}", f"Money: {self.money}", f"Assets: {self.assets}"]

    def add_pos(self, value):
        if (self.pos + value) >= 40:
            self.pos = (self.pos + value) - 40
            self.money += 200
        else:
            self.pos += value

class Dice():
    def __init__(self):
        self.d1 = random.randint(1,6)
        self.d2 = random.randint(1,6)
    
    def roll(self):
        return [self.d1, self.d2]
    
    def double(self):
        if self.d1 == self.d2:
            return True
        else:
            return False
    
    def roll_value(self):
        return self.d1 + self.d2