#Juho Jääskeläinen 6.3.2022
import socket
import threading
import random
#https://www.youtube.com/watch?v=hBnOdIg0jAM series used for the whole project

#Setup variables
HOST='127.0.0.1'
PORT=1234
LISTENER_LIMIT=50
#Data structures to hold the connected clients
active_clients = [] ###Updates socket
active_clients_channel_1=[]#contains socket AND username
active_clients_channel_2=[]#contains socket AND username

def send_message_to_all(message,list_of_recievers):
    for user in list_of_recievers:
            #print(user)
            send_message_to_client(message,user[1])


def send_message_to_client(message,client):
    client.sendall(message.encode())

def send_private_message(sender_client,sender,message,list_of_recievers):# /w [Name] [message]
    target = message.strip('/w').split(' ')[1]
    message = message.strip('/w').split(target,1)[1]
    #print(target)
    #print(message)
    final_message = sender+' (private)'+':'+message
    found_target=False
    for user in list_of_recievers:
        if user[0] == target:
            found_target=True
            send_message_to_client(final_message,user[1])
            send_succesfull=sender+' to '+user[0]+':'+message
            send_message_to_client(send_succesfull,sender_client)
            break
    if not found_target:
        user_not_found=f'Server: {target} was not found from this channel'
        send_message_to_client(user_not_found,sender_client)

def listen_messages(client, username):#Lissens messages from give user. Runs on own thread
    while True:
        try:#This handles disconnections
            message = client.recv(2048).decode('utf-8')
            if message !='' :
                if message == '/q1':#If client closes chat window.
                     active_clients_channel_1.remove((username,client))
                     print(f'{username} has disconnected from channel 1')
                     send_message_to_all(f'Server: {username} has disconnected',active_clients_channel_1)
                     break
                elif message=='/q2':
                    active_clients_channel_2.remove((username,client))
                    print(f'{username} has disconnected from channel 2')
                    send_message_to_all(f'Server: {username} has disconnected',active_clients_channel_2)
                    break
                #if message starts /w
                print(message)
                channel=message.split(':')[0]
                message=message.split(':')[1]
                final_message = username + ': ' + message
                if int(channel)==1:
                    if(message.startswith('/w')):
                        print('sending private message')
                        send_private_message(client,username,message,active_clients_channel_1)
                    else:
                        send_message_to_all(final_message,active_clients_channel_1)
                elif int(channel)==2:
                    if(message.startswith('/w')):
                        print('sending private message')
                        send_private_message(client,username,message,active_clients_channel_2)
                    else:
                        send_message_to_all(final_message,active_clients_channel_2)
                #else:Send private message
            else:
                print(f'Empty message {username}')
                break
        except :##TODO to handle multiple channels.
            ##removes the connection from active clients
            if (client) in active_clients:
                active_clients.remove(client)
                if (username,client) in active_clients_channel_1:
                    active_clients_channel_1.remove((username,client))
                    send_message_to_all(f'Server: {username} has disconnected',active_clients_channel_1)

                if(username,client) in active_clients_channel_2:
                    active_clients_channel_2.remove((username,client))
                    send_message_to_all(f'Server: {username} has disconnected',active_clients_channel_2)

                #print(active_clients[0])
            print(f"Connection from {username} has been lost.")
            client.close()
            break
    print(f'closing message listening for user: {username}')
    threading.Thread(target=client_handler,args=(client, )).start()
    return 0

def client_handler(client):#Waits for the client to send username and channel it connected. Starts listen_messages() in new thread and closes this thread.
    active_clients.append(client)
    while True:##lissens messages containing username
        try: #if connection lost except
            channel_username = client.recv(2048).decode('utf-8')
            if channel_username!='':
                channel=channel_username.split(':')[0]
                username=channel_username.split(':')[1]
                #print(channel_username,channel,username)
                if username!='':
                    if int(channel)==1:
                        print(f'adding {username} to channel 1')
                        active_clients_channel_1.append((username,client))
                        send_message_to_all(f'Server: {username} joined the chat, say hello!',active_clients_channel_1)
                    elif int(channel)==2:
                        print(f'adding {username} to channel 2')
                        active_clients_channel_2.append((username,client))
                        send_message_to_all(f'Server: {username} joined the chat, say hello!',active_clients_channel_2)
                    threading.Thread(target=listen_messages,args=(client, username, )).start() #lissens messages from the channel
                    #print(active_clients)
                break
            else:
                print('here')
                connection_message= 'Connection succesfull waiting for username and channel'
                send_message_to_client(connection_message,client)
                break
        except:
            print('connection closed violently')
            break
    print('Closing client handler')
    return 0
#Main

def main():
    #Creates socket class object AF_NET uses IPv4 and TCP protocol
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        server.bind((HOST, PORT))
        print(f'Server running successfully {HOST} port: {PORT}')
        pass
    except:
        print(f'Unable to bind to host: {HOST} port: {PORT}')
        pass
    #Set server limit
    server.listen(LISTENER_LIMIT)

    #Main loop for connections
    while True:
        client,address = server.accept()
        print(f'Succesfully connected to client {address[0]} - {address[1]}')
        threading.Thread(target=client_handler,args=(client, )).start()
        #lisäis client listaan!

if __name__ == '__main__':
    main()
