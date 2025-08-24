from collections import Counter

def letter_frequency(words):
    """
    Counts the frequency of letters in the given list of words.
    Each letter is counted at most once per word.
    Returns a list of (letter, count) tuples, sorted from most common to least common.
    """
    counter = Counter()
    for word in words:
        unique_letters = set(word)
        counter.update(unique_letters)
    return counter.most_common()

def top_letters(words, top=10):
    """
    Returns a list of the most common letters, limited to top N.
    """
    return letter_frequency(words)[:top]
