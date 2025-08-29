from collections import Counter

def yellow_frequency(words):
    """
    Counts how many words contain each letter, ignoring green positions.
    Each letter is counted once per word.
    """
    counter = Counter()
    for word in words:
        counter.update(set(word))

    return counter

def green_frequency(words):
    """
    Optimized: counts letters that esiintyy samoilla paikoilla muiden sanojen kanssa.
    Returns dict {word: score}.
    """
    word_len = len(words[0])
    scores = {w: 0 for w in words}

    for i in range(word_len):
        column_counts = Counter(word[i] for word in words)
        for word in words:
            scores[word] += column_counts[word[i]] - 1

    return scores


def score_words(words, green_weight=1.0, yellow_weight=1.0):
    """
    Scores each word based on yellow and green frequencies.
    Yellow score counts letters ignoring green matches.
    """
    freqs_green = green_frequency(words)
    freqs_yellow = yellow_frequency(words)

    scored = []

    for word in words:
        unique_letters = set(word)
        yellow_score = sum(freqs_yellow[l] for l in unique_letters)
        green_score = freqs_green[word]
        total_score = yellow_score * yellow_weight + green_score * green_weight
        scored.append((word, total_score))

    scored.sort(key=lambda x: x[1], reverse=True)

    return scored
