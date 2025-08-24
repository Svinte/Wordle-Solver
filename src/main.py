import sys
from _filter import filter_words
from _common import top_letters
from _score import score_words

if len(sys.argv) < 2:
    print("Usage: python main.py wordlist.txt")
    sys.exit(1)

with open(sys.argv[1], "r", encoding="utf-8") as f:
    words = [w.strip().lower() for w in f if len(w.strip()) == 5]

# Previous guesses and their results
# g = green, y = yellow, b = gray
guesses = [
    # eg. ("irate", "bybbg")
]

candidates = filter_words(words, guesses)

print("Possible words:", len(candidates))
print(candidates[:5])

letter_freqs = top_letters(candidates, top=len(set(''.join(candidates))))
print("Letter frequencies:")
for letter, count in letter_freqs:
    print(f"{letter}: {count}")

scored = score_words(candidates)
print("\nTop scored words:")
for word, score in scored[:5]:
    print(f"{word}: {score}")
