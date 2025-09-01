import json
import torch
from collections import defaultdict, Counter

def triplet_from_guess(candidate: str, target: str) -> str:
    """
    Compute g/y/b pattern for a candidate word vs target word.
    g = green (same letter, same position)
    y = yellow (same letter, different position)
    b = black (letter not in target)
    Returns a string of 5 characters: 'g', 'y', 'b'
    """
    pattern = ['b'] * 5
    target_counts = Counter(target)

    # Green letters
    for i in range(5):
        if candidate[i] == target[i]:
            pattern[i] = 'g'
            target_counts[candidate[i]] -= 1

    # Yellow letters
    for i in range(5):
        if pattern[i] == 'b' and candidate[i] in target_counts and target_counts[candidate[i]] > 0:
            pattern[i] = 'y'
            target_counts[candidate[i]] -= 1

    return ''.join(pattern)


def compute_user_first_guesses(train_json_path: str, wordlist_path: str = 'data/wordlist.txt', device: str = 'cuda'):
    """
    Compute per-user first guess probabilities using historical games.
    Uses 'weight' field from JSON to scale user contribution.
    Returns:
        - users: list of user_ids
        - words: list of words from wordlist.txt
        - probs: tensor (num_users x num_words) with weighted counts (not normalized)
    """
    # Load wordlist
    with open(wordlist_path, 'r', encoding='utf-8') as f:
        wordlist = [w.strip().lower() for w in f if len(w.strip()) == 5]

    # Load training data
    with open(train_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Unique users and their indices
    users = sorted({entry['user_id'] for entry in data})
    user_index = {u: i for i, u in enumerate(users)}

    num_users = len(users)
    num_words = len(wordlist)
    probs = torch.zeros((num_users, num_words), dtype=torch.float32, device=device)

    # Initialize per-user counts
    user_counts = defaultdict(lambda: torch.zeros(num_words, device=device))

    # Process each user's guesses
    for entry in data:
        user = entry['user_id']
        guesses = entry.get('guesses', [])
        weight = float(entry.get('weight', len(guesses)))

        if not guesses or weight <= 0:
            continue

        for g in guesses:
            target = g['target']
            result = g['result']

            for j, candidate in enumerate(wordlist):
                predicted = triplet_from_guess(candidate, target)

                if predicted == result:
                    user_counts[user][j] += weight

    # Transfer counts to probs tensor
    for user, counts in user_counts.items():
        probs[user_index[user]] = counts

    return users, wordlist, probs
