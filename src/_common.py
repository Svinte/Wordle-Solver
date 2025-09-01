from collections import Counter
import torch

# =====================
# 1. Top words helper
# =====================
def top_words(words, probs, top_n=10, min_prob=1e-6, max_gap=None):
    """
    Return the top words and their probabilities using Torch tensors with optional filtering.

    Args:
        words (list[str]): List of words.
        probs (torch.Tensor): 1D tensor of probabilities.
        top_n (int): Maximum number of top words to return.
        min_prob (float): Minimum probability to consider.
        max_gap (float or None): Maximum allowed gap between consecutive probabilities.

    Returns:
        tuple: (top_words_list, top_probs_tensor)
    """
    # filter min_prob
    mask = probs >= min_prob
    filtered_probs = probs[mask]
    filtered_words = [w for w, m in zip(words, mask) if m]

    if filtered_probs.numel() == 0:
        return [], torch.tensor([], device=probs.device)

    # Sort
    sorted_probs, idx = torch.sort(filtered_probs, descending=True)
    sorted_words = [filtered_words[i] for i in idx]

    # Cut
    if max_gap is not None and sorted_probs.numel() > 1:
        for i in range(1, sorted_probs.numel()):
            if (sorted_probs[i-1] - sorted_probs[i]) > max_gap:
                sorted_probs = sorted_probs[:i]
                sorted_words = sorted_words[:i]
                break

    return sorted_words[:top_n], sorted_probs[:top_n]



# =====================
# 2. Letter frequencies
# =====================
def top_letters(word_list, top=None):
    """
    Count letter frequencies in a list of words.

    Args:
        word_list (list[str]): List of words.
        top (int or None): Maximum number of letters to return.

    Returns:
        list[tuple]: List of (letter, count) sorted descending.
    """
    letters = "".join(word_list)
    counts = Counter(letters)

    return counts.most_common(top)


# =====================
# 3. Visual bar
# =====================
def make_bar(value, scale=20, char="█"):
    """
    Create a visual bar for a given value.

    Args:
        value (float): Value between 0 and 1.
        scale (int): Maximum bar length.
        char (str): Character to use for the bar.

    Returns:
        str: Visual bar.
    """
    length = int(value * scale)

    return char * length


# =====================
# 4. Probability normalization
# =====================
def normalize_probs(probs):
    """
    Normalize probabilities to sum to 1 (Torch tensor only).

    Args:
        probs (torch.Tensor): Probability tensor.

    Returns:
        torch.Tensor: Normalized probabilities.
    """
    if not isinstance(probs, torch.Tensor):
        raise TypeError("normalize_probs expects a torch.Tensor")

    total = probs.sum(dim=-1, keepdim=True)

    return probs / total


# =====================
# 5. Filter words from guesses
# =====================
def filter_words_from_guesses(word_list, guesses):
    """
    Filter words based on previous guesses and their patterns.

    Args:
        word_list (list[str]): List of words.
        guesses (list[tuple]): Each tuple is (word, pattern) where pattern is 'g', 'y', 'b'.

    Returns:
        list[str]: Filtered words.
    """
    def match(word, guess, pattern):
        word = list(word)

        for i, (g, p) in enumerate(zip(guess, pattern)):
            if p == 'g' and word[i] != g:
                return False

            elif p == 'y' and (g not in word or word[i] == g):
                return False

            elif p == 'b' and g in word:
                return False

        return True

    return [w for w in word_list if all(match(w, g, p) for g, p in guesses)]


# =====================
# 6. Word scoring
# =====================
def score_words(word_list):
    """
    Score words based on letter frequency and uniqueness.

    Args:
        word_list (list[str]): List of words.

    Returns:
        list[tuple]: List of (word, score) sorted descending.
    """
    letter_counts = dict(top_letters(word_list))
    scored = []

    for w in word_list:
        score = sum(letter_counts.get(c, 0) for c in set(w))
        scored.append((w, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    return scored
