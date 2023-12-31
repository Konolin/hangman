import socket
import random


def generate_random_word():
    words = ["python", "hangman", "network", "programming"]
    return random.choice(words)


def initialize_game():
    word = generate_random_word()
    guessed_letters = []
    attempts = 6
    return word, guessed_letters, attempts


def update_game_state(word, guessed_letters):
    display_word = ""
    # replaces all '_' with the letters that were correctly guessed
    for letter in word:
        if letter in guessed_letters:
            display_word += letter + " "
        else:
            display_word += "_ "
    return display_word.strip()


def handle_guess(guess, word, guessed_letters, attempts):
    if guess in guessed_letters:  # the letter was already guessed
        return "already_guessed", attempts
    elif guess in word:  # the guess was correct
        guessed_letters.append(guess)
        return update_game_state(word, guessed_letters), attempts
    else:  # the guess was wrong
        attempts -= 1
        return "wrong_guess", attempts


def main():
    # create server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 8888))
    server.listen(2)

    # the first player is connecting, send the welcome message
    print("Waiting for the first player to connect...")
    client1, addr1 = server.accept()
    client1.send("Welcome! You are Player 1.".encode('utf-8'))
    print(f"Player 1 connected from: {addr1}")

    # the second player is connecting, send the welcome message
    print("Waiting for the second player to connect...")
    client2, addr2 = server.accept()
    client2.send("Welcome! You are Player 2.".encode('utf-8'))
    print(f"Player 2 connected from: {addr2}")

    # initialize the game
    word, guessed_letters, attempts = initialize_game()

    # repeat until there are no attempts left
    while attempts > 0:
        # alternate between the two players
        for client, addr in [(client1, addr1), (client2, addr2)]:
            game_state = update_game_state(word, guessed_letters)
            client.send(game_state.encode('utf-8'))
            client.send(f"Lives remaining: {attempts}".encode('utf-8'))

            # stop the game if the word was guessed
            if "_" not in game_state:
                client.send("You win!".encode('utf-8'))
                break

            # get the guessed char from the client
            guess = client.recv(1024).decode('utf-8')
            response, attempts = handle_guess(guess, word, guessed_letters, attempts)

            # send the corresponding answer to the client
            if response == "already_guessed":
                client.send("You already guessed that letter.".encode('utf-8'))
            elif response == "wrong_guess":
                client.send("Wrong guess.".encode('utf-8'))
            else:
                client.send(response.encode('utf-8'))

        # the clients lose
        if attempts == 0:
            client1.send(f"You lose! The word was {word}".encode('utf-8'))
            client2.send(f"You lose! The word was {word}".encode('utf-8'))
            break

    client1.close()
    client2.close()


if __name__ == "__main__":
    main()
