from typing import List, Tuple
from _common import top_words, normalize

class AnswerAnalyzer:
    def __init__(
        self,
        wordlist: List[str],
        answers: List[str],
        input_data: List[dict],
        start_words_dict: dict
    ):
        self.wordlist = wordlist
        self.answers = answers
        self.input_data = input_data
        self.start_words_dict = start_words_dict

    def analyze(self) -> dict:
        results = {}

        for entry in self.input_data:
            user_id = entry["user_id"]
            pattern = entry["pattern"]

            # Use precomputed start_words from main.py
            start_words = self.start_words_dict.get(user_id, [])

            if not start_words:
                continue

            start_words = top_words(start_words)

            # Whole-word scoring
            scored_answers: List[Tuple[str, float]] = []

            for answer in self.answers:
                total_score = 0.0

                for w, prob in start_words:
                    match_score = 0.0

                    for c1, c2, p in zip(w, answer, pattern):
                        if p == "g" and c1 == c2:
                            match_score += 1.0

                        elif p == "y" and c1 in answer and c1 != c2:
                            match_score += 1.0

                    match_score /= 5.0  # normalize by word length
                    total_score += match_score * prob

                if total_score > 0:
                    scored_answers.append((answer, total_score))

            results[user_id] = scored_answers

        return results
