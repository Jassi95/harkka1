#Juho Jääskeläinen 6.3.2022
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

HOST='127.0.0.1'
PORT=1234

###FOR THE GUI
DARK_GREY = '#121212'
MEDIUM_GREY = '#1F1B24'
OCEAN_BLUE = '#464EB8'

LIGHT_GRAY='#ECE5DD'
TEAL_GREEN='#128C7E'
TEA_GREEN='#DCF8C6'
WA_BLUE='#34B7F1'

BLACK = "black"
WHITE='white'
FONT = ("Helvetica", 17)
BUTTON_FONT = ("Helvetica", 15)
SMALL_FONT = ("Helvetica", 13)

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)#global
connect=None #For connection usages



class ChatWindow: ##Handles the chat window GUI and all methods relative to it.
    username=''
    message=''
    ip=''
    channel=''


    listening_thread=None
    chat_window=None
    top_frame=None
    middle_frame=None
    bottom_frame=None
    username_label=None
    username_textbox=None
    username_button=None
    message_textbox=None
    message_button=None
    message_box =None

    def __init__(self,channel,client,connectObj): #Iniates the GUI and other paremeters
        self.channel=channel
        self.client=client

        self.chat_window =tk.Toplevel()
        self.chat_window.geometry("600x600")
        self.chat_window.title("Messenger Client")
        self.chat_window.resizable(False, False)
        self.connectObj=connectObj

        self.chat_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.chat_window.grid_rowconfigure(0, weight=1)
        self.chat_window.grid_rowconfigure(1, weight=4)
        self.chat_window.grid_rowconfigure(2, weight=1)

        self.top_frame = tk.Frame(self.chat_window, width=600, height=100, bg=TEAL_GREEN)
        self.top_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.middle_frame = tk.Frame(self.chat_window, width=600, height=400, bg=LIGHT_GRAY)
        self.middle_frame.grid(row=1, column=0, sticky=tk.NSEW)

        self.bottom_frame = tk.Frame(self.chat_window, width=600, height=100, bg=TEA_GREEN)
        self.bottom_frame.grid(row=2, column=0, sticky=tk.NSEW)

        self.username_label = tk.Label(self.top_frame, text="Enter username:", font=FONT, bg=TEAL_GREEN, fg=BLACK)
        self.username_label.pack(side=tk.LEFT, padx=10)

        self.username_textbox = tk.Entry(self.top_frame, font=FONT, bg=LIGHT_GRAY, fg=BLACK, width=23)
        self.username_textbox.pack(side=tk.LEFT)

        self.username_button = tk.Button(self.top_frame, text="Join", font=BUTTON_FONT, bg=WA_BLUE, fg=WHITE, command=self.connect_to_chat)
        self.username_button.pack(side=tk.LEFT, padx=15)

        self.message_textbox = tk.Entry(self.bottom_frame, font=FONT, bg=LIGHT_GRAY, fg=BLACK, width=38)
        self.message_textbox.pack(side=tk.LEFT, padx=10)

        self.message_button = tk.Button(self.bottom_frame, text="Send", font=BUTTON_FONT, bg=WA_BLUE, fg=WHITE, command=self.send_message)
        self.message_button.config(state=tk.DISABLED)
        self.message_button.pack(side=tk.LEFT, padx=10)

        self.message_box = scrolledtext.ScrolledText(self.middle_frame, font=SMALL_FONT, bg=LIGHT_GRAY, fg=BLACK, width=67, height=26.5)
        self.message_box.config(state=tk.DISABLED)
        self.message_box.pack(side=tk.TOP)


        print('Chat window iniated')

    def connection_succesfull(self):#Disables username from GUI
        self.username_textbox.config(state=tk.DISABLED)
        self.username_button.config(state=tk.DISABLED)
        self.message_button.config(state=tk.NORMAL)

    def add_message(self,message):#Adds recived messages to GUI
        #print(message)
        self.message_box.config(state=tk.NORMAL)
        self.message_box.insert(tk.END, message + '\n')
        self.message_box.config(state=tk.DISABLED)

    def connect_to_chat(self):#Connects to chat and starts thread to lissen to incomming messages
        username=self.username_textbox.get()
        channel_username= str(self.channel)+':'+username
        if (username !='' )and (':' not in username) and (' ' not in username):
            #print(channel_username)
            self.client.sendall(channel_username.encode())
            threading.Thread(target=self.connectObj.listen_messages_from_server,).start()#starts a thread to lissen messages

            self.connection_succesfull()

        else:
            self.add_message("username can't be empty or contain : or whitespace")



    def send_message(self):
        message = self.message_textbox.get()
        if message !='':
            message=str(self.channel)+':'+message
            self.client.sendall(message.encode())
            self.message_textbox.delete(0,len(message))
        else:
            self.message_box.showerror("Empty message", "Message cannot be empty")

    def disconnect(self):
        #print('enabling buttons1')
        quit_message = f'/q{self.channel}'
        try:
            self.client.sendall(quit_message.encode())
        except: print('server closed')


        self.connectObj.enable_channels()


    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to disconnect from the channel?"):
            self.disconnect()
            self.chat_window.destroy()



class connect_GUI: ##Handles the connection to the server and threads the lissening method.
    ip_address=None
    client=None
    CW=None
    def __init__(self,master):
        self.master=master
        self.frame=tk.Frame(self.master)

        self.label_text = tk.StringVar()
        self.label_text.set('Enter IP address: ')
        self.label=tk.Label(self.frame,textvariable=self.label_text)
        self.label.pack()

        self.ip_address=tk.Entry(self.frame)
        self.ip_address.pack(padx=10)

        self.button=tk.Button(self.frame, text='Connect to server',command=self.connect_channel)
        self.button.pack(padx=10)

        self.frame.pack()

    def connect_channel(self): ##Transforms the GUI to choose channel.
        self.client=self.connect_server(self.ip_address.get())

        if self.client!=None:
            self.ip_address.destroy()
            self.button.destroy()
            self.label_text.set('Choose channel:')
            #Starts chat window with channel 1
            self.button1=tk.Button(self.frame, text='Channel 1',command=lambda: self.start_ChatWindow(1))
            self.button1.pack()

            self.button2=tk.Button(self.frame, text='Channel 2',command=lambda: self.start_ChatWindow(2))
            self.button2.pack()
            self.frame.pack()


    def connect_server(self,host): #sets connection to server returs the socket.
        print(f'trying to connect to: {host}')
        #Connect to server
        try:
            client.connect((host, PORT))
            print('connection succesfull')
            return client
        except :
            print('Cannot connect to server')

    def listen_messages_from_server(self):#Handless the messages from the server
        while True:
            try:
                message=self.client.recv(2048).decode('utf-8')
                if message !='':
                    sender=message.split(':',1)[0]
                    message_body=message.split(':',1)[1]
                    self.CW.add_message(f'[{sender}]: {message_body}')
            except :
                print('Error listen_messages_from_server')
        #print('closing thread2')
        return 0


    def start_ChatWindow(self,channel):#starts chat window and disables channels
        self.CW = ChatWindow(channel,self.client,self)
        self.button1.config(state=tk.DISABLED)
        self.button2.config(state=tk.DISABLED)

    def enable_channels(self):
        #print('enabling buttons2')
        self.button1.config(state=tk.NORMAL)
        self.button2.config(state=tk.NORMAL)
        self.CW=None


def main():
    root = tk.Tk()
    connect = connect_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
