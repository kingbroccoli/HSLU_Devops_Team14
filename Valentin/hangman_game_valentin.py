import random

# Step 1: Select a word
word_list = ["house", "tree", "superman", "worldwideweb", "banane"]
chosen_word = random.choice(word_list)
display = ["_" for _ in chosen_word]  # Creates a list of underscores for each letter
attempts = 6  # Number of allowed incorrect attempts
guessed_letters = []  # To keep track of guessed letters

print("Welcome to Hangman!")
print("Try to guess the word letter by letter.")

# Game loop
while attempts > 0:
    print("\nCurrent word:", " ".join(display))  # Show the current state of the word
    print(f"Remaining attempts: {attempts}")
    print("Guessed letters:", " ".join(guessed_letters))

    # Step 2: Get the player's guess
    guess = input("Guess a letter: ").lower()

    # Check if the letter was already guessed
    if guess in guessed_letters:
        print("You already guessed that letter. Try again.")
        continue

    guessed_letters.append(guess)  # Add the guess to the list of guessed letters

    # Step 3: Check if the guess is in the word
    if guess in chosen_word:
        print(f"Good job! {guess} is in the word.")
        # Reveal the correct guessed letters in the display
        for index, letter in enumerate(chosen_word):
            if letter == guess:
                display[index] = guess
    else:
        print(f"Sorry, {guess} is not in the word.")
        attempts -= 1  # Decrease attempts if guess is incorrect

    # Step 4: Check if the player has guessed the whole word
    if "_" not in display:
        print("\nCongratulations! You've guessed the word:", chosen_word)
        break

# Step 5: End game if out of attempts
if attempts == 0:
    print("\nSorry, you've run out of attempts. The word was:", chosen_word)
