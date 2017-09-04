#-*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# CSC 412-Networking
# Expanding A Protocol 
# Authors: Jose Zindia
#------------------------------------------------------------------------------

import base64
import uuid
import string
import random
class MessageServer():
    def __init__(self):
        self.IMQ = []  # incoming_message_queue
        self.MBX = {}  # user_mailboxes
        self.login = {} #registered accounts and passwords
        self.ID = {}  #session ids and usernames
        self.assigned_cookies=[] #to check which session cookies has already been assigned

    def assign_cookie(self, username, conn):
        session_id=base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        if username not in self.ID and session_id not in self.assigned_cookies: #checking if username doesn't already have a cookie and if cookie is not assigned
            self.ID[username]=session_id
            self.assigned_cookies.append(session_id)
            conn.sendall(session_id)
        else:
            print "Username has session cookie already."
            return False


    def register(self, message, connection):
          '''Register with password.Only username is parsed.Password must be direct'''
          username = message.split(" ")[1]   #splitting username from message
          password= message.split(" ")[2]   #splitting password from message
          if username not in self.login:    #if user is not already registered
              self.login[username]=password #register him/her
              self.assign_cookie(username, connection)
              if username not in self.MBX:   #if user does not have a mailbox
                  self.MBX[username]=[]     #create mailbox
              return True
          else:
              connection.send("KO. You are registered. You should login now.")
              return False

    def log_out(self, message, connection):
        username = message.split(" ")[1]  # splitting username from message
        password = message.split(" ")[2]  # splitting password from message
        if username in self.login:      #if user is already registered
            if self.login[username]==password:      #if his accound and password match
                for i in self.assigned_cookies:
                    if i == self.ID[username]:
                        self.assigned_cookies.remove(i)     #delete user session from assigned session list
                del self.ID[username]           #delete user from [account_name:session]
                print "Removed session id of user:", username




    def login(self,message,connection):
        username = message.split(" ")[1]  # splitting username from message
        password = message.split(" ")[2]  # splitting password from message
        if username in self.login:          #if user is registered
            if self.login[username]==password:  #if user account match user password
                print "Success.", username, "is logged in."
                self.assign_cookie(username, connection)    #assign cookie to logged in user
            else:
                print "Failure. Wrong password."
        else:
            print "You should register first."


    def add_message(self, content, connection):

        message = content.split(" ")[1:]
        self.IMQ.append(message)
        connection.send("OK. You message was added.")
        return True


    def store(self, message, connection):

        user = message.split(" ")[1]
        if user in self.MBX:
            recent_message= self.IMQ.pop()
            self.MBX[user].append(recent_message)
            connection.send(b"OK. Your recent message has been stored in user's mailbox")
            return True
        else:
            connection.send("KO. Your message has not been stored")
            return False


    def count(self, username, connection):
        user = username.split(" ")[1]
        if user in self.MBX:
            count=len(self.MBX[user])
            connection.send("Your total messages COUNTED:", "<", count,">")
            return True
        else:
            connection.send("KO. did not count error")
            return False

    def delete_message(self, username, connection):
        user = username.split(" ")[1]
        if user in self.MBX:
            self.MBX[user].pop(0)
            connection.send("OK. You first message was deleted from MBX.")
            return True
        else:
            connection.send("KO. was not deleted")
            return False

    def get_client_message(self, username, connection):
        user = username.split(" ")[1]
        if user in self.MBX:
            connection.send("Your message:",self.MBX[user].pop())
            return True
        else:
            connection.send("KO. did not get client message")
            return False

        #return the first message from the user's mailbox queue
        #return KO if no message or user not registered


    def dump(self, msg, conn):
        if "DUMP" in msg:
            print self.MBX
            print self.IMQ
            conn.sendall(b"OK\0")
            return True
        else:
            print("NO HANDLER FOR CLIENT MESSAGE: [{0}]".format(msg))
            conn.sendall(b"KO\0")
            return False

'''
        When the server receives a DUMP command, it should print the contents of the IMQ and MBX to its terminal.
        This is a debugging command; it allows the client to ask the server to print its contents,
        which is useful to the server author. It should always return OK. '''
