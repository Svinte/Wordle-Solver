import json
from _user_analyze import UserWordleAnalyzer
from _answer_analyze import AnswerAnalyzer
from _summary import SummaryAnalyzer
from _filter import filter_words


# ==============================
# Limits
# ==============================

MIN_PROB_1 = 1
MIN_PROB_2 = 0.001
MAX_GAP = 0.0003

# ==============================
# Paths
# ==============================

TARGETS_PATH="storage/public/targets.jsonl"
WORDLIST_PATH="storage/public/wordlist.txt"
ANSWERS_PATH="storage/public/answers.txt"
TRAIN_PATH="storage/local/train.jsonl"
INPUT_PATH="storage/local/input.jsonl"

# ==============================
# Load data
# ==============================

with open(WORDLIST_PATH, "r", encoding="utf-8") as f:
    WORDLIST = [w.strip() for w in f if len(w.strip()) == 5]

with open(TARGETS_PATH, "r", encoding="utf-8") as f:
    targets = {json.loads(line)["game_id"]: json.loads(line)["target"] for line in f}

with open(TRAIN_PATH, "r", encoding="utf-8") as f:
    train_data = [json.loads(line) for line in f]

with open(ANSWERS_PATH, "r", encoding="utf-8") as f:
    ANSWERS = [w.strip() for w in f if len(w.strip()) == 5]

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    input_data = [json.loads(line) for line in f]

# ==============================
# Compute start_words once per user
# ==============================

start_words_dict = {}

for user in train_data:
    user_id = user.get("user_id", "unknown_user")
    guesses = user.get("guesses", [])

    analyzer = UserWordleAnalyzer(
        user_id=user_id,
        guesses=guesses,
        targets=targets,
        wordlist=WORDLIST
    )

    sw = analyzer.top_start_words(min_prob=MIN_PROB_1, max_gap=MAX_GAP, normalize_probs=False)
    analyzer.print_top_words()
    start_words_dict[user_id] = sw

# ==============================
# Optional filter
# ==============================

guesses = [
    ("audio", "bgbbb"),
    ("norma", "bbbbb"),
    ("minor", "bbbbb"),
    ("plant", "bybbb"),
    ("-l---", "bybbb"),
    ("-e---", "bybbb"),
]

ANSWERS = filter_words(ANSWERS, guesses)

# ==============================
# Analyze answers
# ==============================

answer_analyzer = AnswerAnalyzer(
    wordlist=WORDLIST,
    answers=ANSWERS,
    input_data=input_data,
    start_words_dict=start_words_dict
)

results = answer_analyzer.analyze()

# ==============================
# Combine all users' results into summary
# ==============================

summary_analyzer = SummaryAnalyzer(results)
summary_analyzer.print_summary(top_n=10, min_prob=MIN_PROB_2, max_gap=MAX_GAP)
