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

        pattern, required_count = m.groups()
        required_count = int(required_count) if required_count else 1

        match_count = 0

        for word in word_list:
            word = word.lower()
            feedback = ["b"] * 5
            answer_counts = Counter(candidate)

            for i in range(5):
                if word[i] == candidate[i]:
                    feedback[i] = "g"
                    answer_counts[word[i]] -= 1

            for i in range(5):
                if feedback[i] == "b" and word[i] in answer_counts and answer_counts[word[i]] > 0:
                    feedback[i] = "y"
                    answer_counts[word[i]] -= 1

            if "".join(feedback) == pattern:
                match_count += 1

        if match_count < required_count:
            return False

    return True

# -------------------------------
# Rule filtering helpers
# -------------------------------

def consolidate_rules(rules: list[str]) -> list[str]:
    counter = Counter()

    for rule in rules:
        m = re.match(r"([gyb]{5})(?:\*(\d+))?", rule.lower())

        if not m:
            raise ValueError(f"Invalid rule: {rule}")

        pattern, count = m.groups()
        count = int(count) if count else 1
        counter[pattern] += count

    consolidated = []
    for pattern, count in counter.items():
        if count > 1:
            consolidated.append(f"{pattern}*{count}")

        else:
            consolidated.append(pattern)

    return consolidated

# -------------------------------
# Generic match function
# -------------------------------

def match(word, guess, result, scheme='performance'):
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
    """
    Finds the largest rule subset that yields at least one valid candidate.
    Gradually weakens rules if no results are found.
    """
    consolidated_rules = consolidate_rules(rules)
    best_result = []
    best_rule_count = 0

    n = len(consolidated_rules)

    if n == 0:
        return candidates

    for size in range(n, 0, -1):
        local_best = []
        local_rules = []

        for i in range(0, n - size + 1):
            subset = consolidated_rules[i:i+size]
            try:
                subset_results = [
                    cand for cand in candidates
                    if match_scheme_comparison(cand, word_list, subset)
                ]

            except IndexError:
                continue

            if subset_results:
                if len(subset) > best_rule_count:
                    best_result = subset_results
                    best_rule_count = len(subset)
                    local_best = subset_results
                    local_rules = subset

        if local_best:
            print(f"Optimized: used {len(local_rules)} rules, produced {len(local_best)} results.")
            return sorted(local_best)

    fallback = []
    for rule in consolidated_rules:
        try:
            matched = [
                cand for cand in candidates
                if match_scheme_comparison(cand, word_list, [rule])
            ]

            if matched:
                fallback.extend(matched)

        except IndexError:
            continue

    if fallback:
        print("Fallback: results found using single rules.")
        return sorted(set(fallback))

    raise ValueError("No valid candidates found for any rule combination.")

def filter_words(words, guesses, scheme='performance'):
    """
    Standard Wordle filtering.
    """
    for guess, result in guesses:
        words = [w for w in words if match(w, guess, result, scheme)]

    return words
