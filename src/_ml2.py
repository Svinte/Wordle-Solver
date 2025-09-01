import torch
from collections import defaultdict

def match_pattern(candidate: str, pattern: str, target_word: str) -> bool:
    """
    Check if a candidate word can produce the given g/y/b pattern
    relative to a target_word.
    g = green, y = yellow, b = black
    """
    if len(candidate) != 5 or len(target_word) != 5 or len(pattern) != 5:
        return False

    # First pass: green
    for i in range(5):
        if pattern[i] == 'g' and candidate[i] != target_word[i]:
            return False

        if pattern[i] != 'g' and candidate[i] == target_word[i]:
            return False

    # Second pass: yellow and black
    for i in range(5):
        if pattern[i] == 'y':
            if candidate[i] == target_word[i] or candidate[i] not in target_word:
                return False

        if pattern[i] == 'b':
            if candidate[i] in target_word:
                return False

    return True


def compute_answer_probabilities(
    top_words,
    top_probs,
    answers,
    user_pattern,
    device='cuda'
):
    """
    Compute weighted answer probabilities based on a user's top words.
    Supports answers as a list (preloaded) instead of file path.

    Args:
        top_words: list of user's top words
        top_probs: tensor of probabilities corresponding to top_words
        answers: list of possible target words
        user_pattern: string of g/y/b from user's most recent guess
        device: torch device

    Returns:
        dict mapping answer_word -> probability
    """
    probs_dict = defaultdict(float)

    # Ensure tensor
    if not isinstance(top_probs, torch.Tensor):
        top_probs_tensor = torch.tensor(top_probs, dtype=torch.float32, device=device)

    else:
        top_probs_tensor = top_probs.to(dtype=torch.float32, device=device)

    for idx, candidate in enumerate(top_words):
        weight = top_probs_tensor[idx].item()

        for ans in answers:
            if match_pattern(candidate, user_pattern, ans):
                probs_dict[ans] += weight

    return probs_dict
