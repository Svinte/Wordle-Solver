from collections import Counter

def match_scheme_old(word, guess, result):
    """
    Filter words based on a simple match scheme.
    Safe to use in non official games but may effect performance.
    """
    for i in range(5):
        if result[i] == "g" and word[i] != guess[i]:
            return False
        if result[i] == "y":
            if guess[i] == word[i] or guess[i] not in word:
                return False
        if result[i] == "b" and guess[i] in word:
            return False

    return True

def match_scheme_performance(word, guess, result):
    """
    Filter words based on a more complex match scheme.
    Best performance. Safe for official Wordle.
    """
    for i in range(5):
        if result[i] == "g" and word[i] != guess[i]:
            return False

    remaining = Counter()
    for i in range(5):
        if result[i] != "g":
            remaining[word[i]] += 1

    for i in range(5):
        if result[i] == "y":
            if guess[i] == word[i] or remaining[guess[i]] <= 0:
                return False
            remaining[guess[i]] -= 1

    for i in range(5):
        if result[i] == "b" and remaining[guess[i]] > 0:
            return False

    return True

def match(word, guess, result, scheme='performance'):
    """
    Check word using chosen scheme.

    Params:
    - word: candidate (str)
    - guess: guessed word (str)
    - result: 'g','y','b' string
    - scheme: 'old' or 'performance'

    Returns:
    - True if it fits
    """
    if scheme == 'old':
        return match_scheme_old(word, guess, result)

    elif scheme == 'performance':
        return match_scheme_performance(word, guess, result)

    else:
        raise ValueError("scheme must be 1 or 2")

def filter_words(words, guesses, scheme='performance'):
    """
    Filter words by guesses using selected scheme.

    Params:
    - words: list of words
    - guesses: list of (guess, result)
    - scheme: 'scheme1' or 'scheme2' (default 'scheme2')

    Returns:
    - List of matching words
    """
    for guess, result in guesses:
        words = [w for w in words if match(w, guess, result, scheme)]

    return words
