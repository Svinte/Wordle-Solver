from collections import Counter
import re

# -------------------------------
# Old and performance schemes
# -------------------------------

def match_scheme_old(word, guess, result):
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

# -------------------------------
# Comparison scheme
# -------------------------------

from collections import Counter

def match_scheme_comparison(candidate: str, word_list: list[str], rules: list[str]) -> bool:
    candidate = candidate.lower()

    for raw_rule in rules:
        m = re.match(r"([gyb]{5})(?:\*(\d+))?", raw_rule.lower())
        if not m:
            raise ValueError(f"Invalid rule: {raw_rule}")

        rule, required_count = m.groups()
        required_count = int(required_count) if required_count else 1

        match_count = 0

        for word in word_list:
            word = word.lower()

            g_match = all(word[i] == candidate[i] for i, r in enumerate(rule) if r == 'g')

            if not g_match:
                continue

            y_counts = Counter()
            for i, r in enumerate(rule):
                if r == 'y':
                    y_counts[word[i]] += 1

            candidate_counts = Counter(candidate)
            y_match = all(candidate_counts[char] == count for char, count in y_counts.items())

            if not y_match:
                continue

            match_count += 1

        if match_count < required_count:
            return False

    return True


# -------------------------------
# Generic match function
# -------------------------------

def match(word, guess, result, scheme='performance', wordlist=None):
    if scheme == 'old':
        return match_scheme_old(word, guess, result)

    elif scheme == 'performance':
        return match_scheme_performance(word, guess, result)

    else:
        raise ValueError("Invalid scheme")

# -------------------------------
# Filter functions
# -------------------------------

def filter_candidates_by_comparison(candidates: list[str], word_list: list[str], rules: list[str]) -> list[str]:
    filtered = []

    for candidate in candidates:
        if match_scheme_comparison(candidate, word_list, rules):
            filtered.append(candidate)

    return filtered

def filter_words(words, guesses, scheme='performance'):
    """
    Standard Wordle filtering.
    """
    for guess, result in guesses:
        words = [w for w in words if match(w, guess, result, scheme)]

    return words
