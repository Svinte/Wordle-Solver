# _contains.py
import re
from typing import List

class ContainsSyntaxError(ValueError):
    """Raised when the contains list has invalid duplicate letters in exact-count rules."""
    pass

def match_contains(word: str, contains_list: List[str]) -> bool:
    """
    Checks if the word satisfies all conditions in the contains_list.

    Conditions can be:
      - single letter: "a"
      - multiple letters (OR): "a|b|c"
      - multiple letters with minimum count: "a|b|c*2" -> at least 2 letters present
      - multiple letters with exact count: "a|b|c**2" -> exactly 2 letters present (duplicates not allowed)
    """
    word = word.lower()

    for cond in contains_list:
        match_exact = re.match(r'^(.*)\*\*(\d+)$', cond)
        if match_exact:
            letters_part, exact_count = match_exact.groups()
            exact_count = int(exact_count)
            letters = letters_part.split("|")

            if len(letters) != len(set(letters)):
                raise ContainsSyntaxError(
                    f"Duplicate letters in exact-count rule are not allowed: {cond}"
                )

            letters = list(dict.fromkeys(letters))

            if sum(1 for l in letters if l in word) != exact_count:
                return False

            continue

        match_min = re.match(r'^(.*)\*(\d+)$', cond)
        if match_min:
            letters_part, min_count = match_min.groups()
            min_count = int(min_count)
            letters = letters_part.split("|")

            letters = list(dict.fromkeys(letters))

            if sum(1 for l in letters if l in word) < min_count:
                return False

            continue

        letters = cond.split("|")
        letters = list(dict.fromkeys(letters))

        if not any(l in word for l in letters):
            return False

    return True

def filter_contains(candidates: List[str], contains_list: List[str]) -> List[str]:
    """
    Filters a list of candidate words based on contains_list conditions.
    """
    if not contains_list:
        return candidates

    return [word for word in candidates if match_contains(word, contains_list)]
