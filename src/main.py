from _filter import filter_words, filter_candidates_by_comparison
from _common import top_letters
from _score import score_words

ANSWER_LIST_PATH = 'src/wordlist.txt'
QUESS_LIST_PATH = 'src/wordlist2.txt'

with open(ANSWER_LIST_PATH, "r", encoding="utf-8") as f:
    all_possible_inputs = [w.strip().lower() for w in f if len(w.strip()) == 5]

with open(ANSWER_LIST_PATH, "r", encoding="utf-8") as f:
    answers = [w.strip().lower() for w in f if len(w.strip()) == 5]

# Previous guesses and their results
# g = green, y = yellow, b = gray
guesses = [
    # eg. ("irate", "bybbg")
]

comparing = [
]
contains = [
]

candidates = [ans for ans in answers if all(k in ans for k in contains)]
candidates = filter_words(candidates, guesses)
candidates = filter_candidates_by_comparison(candidates, all_possible_inputs, comparing)

print("Possible words:", len(candidates))
print(candidates[:30])

letter_freqs = top_letters(candidates, top=len(set(''.join(candidates))))
print("Letter frequencies:")
for letter, count in letter_freqs:
    print(f"{letter}: {count}")

scored = score_words(candidates)
print("\nTop scored words:")
for word, score in scored[:5]:
    print(f"{word}: {score}")
