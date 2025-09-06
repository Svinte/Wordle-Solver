import json
from collections import defaultdict
from typing import List, Dict, Tuple
from _common import top_words, normalize

class UserWordleAnalyzer:
    def __init__(self, user_id: str, guesses: List[Dict], targets: Dict[str, str], wordlist: List[str]):
        self.user_id = user_id
        self.guesses = guesses
        self.targets = targets
        self.wordlist = wordlist
        self.word_counts = defaultdict(int)

    def simulate_result(self, guess_word: str, target_word: str) -> str:
        """Simulate Wordle feedback for a guess against a target."""
        result = ["b"] * 5
        target_chars = list(target_word)
        for i, c in enumerate(guess_word):
            if c == target_chars[i]:
                result[i] = "g"
                target_chars[i] = None

        for i, c in enumerate(guess_word):
            if result[i] == "b" and c in target_chars:
                result[i] = "y"
                target_chars[target_chars.index(c)] = None

        return "".join(result)

    def analyze(self) -> List[Tuple[str, float]]:
        """Compute raw probabilities for all words based on user guesses."""
        if not self.guesses:
            return []

        total_games = len(self.guesses)
        for g in self.guesses:
            game_id = g.get("game_id")
            user_result = g.get("result", "")
            target_word = self.targets.get(game_id)

            if not target_word:
                continue

            for word in self.wordlist:
                if self.simulate_result(word, target_word) == user_result:
                    self.word_counts[word] += 1

        word_probs = [(w, count / total_games) for w, count in self.word_counts.items()]
        word_probs.sort(key=lambda x: x[1], reverse=True)
        return word_probs

    def filter_word(self, word: str, guess: str, pattern: str) -> bool:
        """Return True if the word satisfies green, yellow, and black constraints."""
        for w_c, g_c, p in zip(word, guess, pattern):
            if p == "g" and w_c != g_c:
                return False

            if p == "y":
                if w_c == g_c or g_c not in word:
                    return False

            if p == "b" and g_c in word:
                return False

        return True

    def filter_all_words(self, wordlist: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Apply green/yellow/black constraints from all guesses."""
        filtered = []
        for word, prob in wordlist:
            valid = True

            for g in self.guesses:
                guess_word = g.get("guess", "")
                pattern = g.get("result", "")

                if not self.filter_word(word, guess_word, pattern):
                    valid = False
                    break

            if valid:
                filtered.append((word, prob))

        return filtered

    def top_start_words(self, min_prob: float = 0.01, max_gap: float = 0.1, normalize_probs: bool = True) -> List[Tuple[str, float]]:
        """Return top starting words after filtering by pattern constraints."""
        probs = self.analyze()
        probs = self.filter_all_words(probs)
        filtered = top_words(probs, min_prob=min_prob, max_gap=max_gap)

        if normalize_probs:
            filtered = normalize(filtered)

        return filtered

    def print_top_words(self, top_n: int = 10, min_prob: float = 0.01, max_gap: float = 0.1):
        filtered = self.top_start_words(min_prob=min_prob, max_gap=max_gap)
        print(f"\nUser: {self.user_id}")
        print(f"Top {top_n} possible starting words:")
        for word, prob in filtered[:top_n]:
            print(f"{word}: {prob:.4f}")
