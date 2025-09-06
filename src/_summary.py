# _summary.py
from typing import Dict, List, Tuple
from _common import normalize, top_words

class SummaryAnalyzer:
    def __init__(self, user_results: Dict[str, List[Tuple[str, float]]]):
        """
        user_results: dictionary mapping user_id -> [(word, score), ...]
        """
        self.user_results = user_results

    def summarize(self) -> List[Tuple[str, float]]:
        combined_scores: Dict[str, float] = {}

        # Combine scores from all users
        for word_list in self.user_results.values():
            for word, score in word_list:
                if word in combined_scores:
                    combined_scores[word] += score

                else:
                    combined_scores[word] = score

        # Convert to list of tuples
        combined_list: List[Tuple[str, float]] = list(combined_scores.items())

        # Normalize to get percentages
        combined_list = normalize(combined_list)

        # Sort descending by score
        combined_list.sort(key=lambda x: x[1], reverse=True)

        return combined_list

    def print_summary(self, top_n: int = 20, min_prob: int = 0.001, max_gap=0.001):
        summary = self.summarize()
        summary_top = top_words(summary, min_prob, max_gap)
        summary_top = normalize(summary_top, True)

        print("\n=== Combined Summary of Words ===")
        for word, score in summary_top[:top_n]:
            print(f"{word}: {score:.0%}")
