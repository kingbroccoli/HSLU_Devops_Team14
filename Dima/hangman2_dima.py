import random

# Initialize game data
words = ['test', 'cat', 'dog', 'lamp']
all_letters = list('abcdefghijklmnopqrstuvwxyz')  # All possible letters
guessed_letters = []  # Store guessed letters
word = random.choice(words)
shown_word = ['_'] * len(word)

# Functions
def open_letter(letter, word, shown_word):
    """Update the shown word with the guessed letter."""
    for idx, char in enumerate(word):
        if char == letter:
            shown_word[idx] = letter
    return shown_word

def draw_next(state):
    """Draw the Hangman based on the current state."""
    hangman_stages = [
        '''
          -----
              |
              |
              | 
              |
              |
        =========''',
        '''
          -----
              |
          O   |
              |
              |
              |
        =========''',
        '''
          -----
              |
          O   |
          |   |
              |
              |
        =========''',
        '''
          -----
              |
          O   |
         /|   |
              |
              |
        =========''',
        '''
          -----
              |
          O   |
         /|\\  |
              |
              |
        =========''',
        '''
          -----
              |
          O   |
         /|\\  |
         /    |
              |
        =========''',
        '''
          -----
              |
          O   |
         /|\\  |
         / \\  |
              |
        =========''',
        '''
          -----
          |   |
          O   |
         /|\\  |
         / \\  |
              |
        ========='''
    ]
    print(hangman_stages[state])

# Game loop
state = 0
# max_mistakes = len(all_letters) - len(word)
while state < 8:
    print("\nWord:", ' '.join(shown_word))
    print("Guessed letters:", ' '.join(guessed_letters))
    print("Remaining letters:", ' '.join(all_letters))

    guess = input("Guess a letter: ").lower()

    if len(guess) != 1 or not guess.isalpha():
        print("Please enter a single valid letter.")
        continue

    if guess in guessed_letters:
        print("You already guessed that letter!")
        continue

    guessed_letters.append(guess)
    all_letters.remove(guess)  # Remove the guessed letter from the pool

    if guess in word:
        shown_word = open_letter(guess, word, shown_word)
        if '_' not in shown_word:
            print("Congrats! You guessed the word:", ''.join(shown_word))
            break
    else:
        state += 1
        print(f"Nope! You made {state} mistakes.")
        draw_next(state-1)

if state == 8:
    print(f"Game over! The word was: {word}")
