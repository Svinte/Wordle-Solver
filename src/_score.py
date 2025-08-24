from collections import Counter

def letter_frequency(words):
    """
    Counts the frequency of letters in the given list of words.
    Each letter is counted at most once per word.
    """
    counter = Counter()
    for word in words:
        counter.update(set(word))
    return counter

def score_words(words):
    """
    Scores each word based on letter frequency.
    Each word gets points equal to the sum of its letters' frequencies in the candidate list.
    Returns a list of tuples (word, score), sorted by score descending.
    """
    freqs = letter_frequency(words)
    scored = []
    for word in words:
        unique_letters = set(word)
        score = sum(freqs[l] for l in unique_letters)
        scored.append((word, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
