def match(word, guess, result):
from collections import Counter
    """
    Check if the word matches the guess with the given result.
    """
    for i in range(5):
        if result[i] == "g" and word[i] != guess[i]:
            return False
        if result[i] == "y" and (guess[i] not in word or word[i] == guess[i]):
            return False
        if result[i] == "b" and guess[i] in word:
            return False

    return True

def filter_words(words, guesses):
    """
    Filter the list of words based on the guesses and their results.
    """
    for guess, result in guesses:
        words = [w for w in words if match(w, guess, result)]

    return words
