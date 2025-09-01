from _common import top_words
from collections import defaultdict
import torch

def aggregate_ml2_results(all_user_probs: dict, top_n: int = 10, device: str = 'cuda', neighbor_bonus: float = 0.1):
    """
    Aggregate ML2 results from all users, optionally adding a bonus if a word appears
    in other users' top-n lists.

    Args:
        all_user_probs: dict of {user_id: {word: prob}}
        top_n: number of top results to return
        device: 'cuda' or 'cpu'
        neighbor_bonus: extra weight for words appearing in other users' top-n

    Returns:
        final_words: list of top_n words
        final_probs: list of corresponding probabilities
    """
    combined = defaultdict(float)
    user_top_sets = dict()

    # Create top-n sets for each user
    for user, user_dict in all_user_probs.items():
        sorted_items = sorted(user_dict.items(), key=lambda x: x[1], reverse=True)
        top_words_user = [w for w, _ in sorted_items[:top_n]]
        user_top_sets[user] = set(top_words_user)

    # Sum user probabilities and add neighbor_bonus for other users' top-n words
    for user, user_dict in all_user_probs.items():
        for word, p in user_dict.items():
            combined[word] += p

            for other_user, other_set in user_top_sets.items():
                if other_user != user and word in other_set:
                    combined[word] += neighbor_bonus

    # Convert to tensor
    words_list = list(combined.keys())
    probs_list = torch.tensor([combined[w] for w in words_list], dtype=torch.float32, device=device)

    # Use top_words filter
    filtered_words, filtered_probs = top_words(words_list, probs_list, min_prob=0.0, max_gap=1e6)

    # Return top_n results
    return top_words(filtered_words[:top_n], filtered_probs[:top_n])
