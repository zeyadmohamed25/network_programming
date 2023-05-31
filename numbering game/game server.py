import tkinter as tk
import socket
import threading
import random

# Server configuration
host = 'localhost'
port = 7001

# Generate a random number
number = random.randint(1, 100)

# List to store connected clients
clients = []
guesses = {}

# Locks for thread safety
lock = threading.Lock()
guess_lock = threading.Lock()


class NumberGuessGameServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(2)
        print('Server started. Waiting for connections...')

        self.root = tk.Tk()
        self.root.title("Number Guessing Game - Server")

        self.label = tk.Label(self.root, text="Waiting for players...")
        self.label.pack(pady=10)

        threading.Thread(target=self.accept_clients).start()
        self.root.mainloop()

    def accept_clients(self):
        while len(clients) < 2:
            client_socket, address = self.server_socket.accept()
            print('Connected to', address)
            clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

        self.start_game()

    def start_game(self):
        self.label.configure(text="Game started. Guess a number between 1 and 100.")

    def handle_client(self, client_socket):
        while True:
            try:
                guess = int(client_socket.recv(1024).decode())
                with guess_lock:
                    guesses[client_socket] = guess
                self.check_guess(client_socket, guess)
            except ValueError:
                self.send_message(client_socket, 'Invalid guess! Try again.')

    def check_guess(self, client_socket, guess):
        if guess == number:
            self.send_message(client_socket, 'Correct guess! You win!')
            self.end_game()
        elif guess < number:
            self.send_message(client_socket, 'Too low! Guess higher.')
        else:
            self.send_message(client_socket, 'Too high! Guess lower.')

    def end_game(self):
        winner = None
        for client_socket, guess in guesses.items():
            if guess == number:
                winner = client_socket
                client_socket.send('You win! Congratulations!'.encode())
            else:
                client_socket.send('You lose! Better luck next time.'.encode())
            client_socket.close()
        clients.clear()
        guesses.clear()
        self.label.configure(text="Game over. The correct number was " + str(number) + ".")
        self.server_socket.close()

    def send_message(self, client_socket, message):
        client_socket.send(message.encode())


if __name__ == '__main__':
    NumberGuessGameServer()
