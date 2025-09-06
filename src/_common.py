from typing import List, Tuple

def top_words(wordlist: List[Tuple[str, float]], min_prob: float = 0.01, max_gap: float = 0.1) -> List[Tuple[str, float]]:
    """
    Filter and split words based on probability.

    Parameters:
    - wordlist: list of (word, probability)
    - min_prob: minimum probability to include
    - max_gap: maximum allowed gap between consecutive probabilities

    Returns:
    - Filtered and possibly truncated list of (word, probability)
    """
    # Filter by minimum probability
    filtered = [(w, p) for w, p in wordlist if p >= min_prob]
    if not filtered:
        return []

    # Sort by probability descending
    filtered.sort(key=lambda x: x[1], reverse=True)

    # Split list if gap between consecutive probabilities exceeds max_gap
    result = [filtered[0]]
    for i in range(1, len(filtered)):
        prev_prob = filtered[i - 1][1]
        curr_prob = filtered[i][1]

        if prev_prob - curr_prob > max_gap:
            break

        result.append(filtered[i])

    return result

def normalize(wordlist: List[Tuple[str, float]], percent = False) -> List[Tuple[str, float]]:
    """
    Normalize probabilities so they sum to 1.

    Parameters:
    - wordlist: list of (word, probability)

    Returns:
    - list of (word, normalized_probability)
    """
    if percent:
        total = sum(p for _, p in wordlist)

    else:
        total = len(wordlist)

    if total == 0:
        return [(w, 0.0) for w, _ in wordlist]

    return [(w, p / total) for w, p in wordlist]
