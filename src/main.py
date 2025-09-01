import json
import torch
from rich.console import Console
from rich.table import Table
from _ml1 import compute_user_first_guesses
from _ml2 import compute_answer_probabilities
from _ml3 import aggregate_ml2_results
from _common import top_words, make_bar, normalize_probs, filter_words_from_guesses, score_words

# =====================
# Guesses
# =====================
guesses = [
    # Example: ("irate", "bybbg"),
    # ("world", "bbbbb"),
]

# =====================
# Paths
# =====================
WORDLIST_PATH = "data/wordlist.txt"
ANSWERS_PATH = "data/answers.txt"
TRAIN_JSON_PATH = "data/train.json"
INPUT_JSON_PATH = "data/input.json"

# =====================
# Torch device
# =====================
console = Console()
device = "cuda" if torch.cuda.is_available() else "cpu"
console.print(f"[bold cyan]Using device:[/bold cyan] {device}\n")

# =====================
# Load answers & filter impossible based on guesses
# =====================
with open(ANSWERS_PATH, 'r', encoding='utf-8') as f:
    all_answers = [w.strip().lower() for w in f if len(w.strip()) == 5]

filtered_answers = filter_words_from_guesses(all_answers, guesses)

# =====================
# 1. ML1: User first guesses
# =====================
with open(TRAIN_JSON_PATH, "r", encoding="utf-8") as f:
    train_data = json.load(f)

for entry in train_data:
    entry["weight"] = len(entry.get("guesses", []))

tmp_train_path = "data/train_with_weights.json"
with open(tmp_train_path, "w", encoding="utf-8") as f:
    json.dump(train_data, f, ensure_ascii=False, indent=2)

users, words, probs = compute_user_first_guesses(tmp_train_path, WORDLIST_PATH, device=device)

MIN_PROB = 0.001
MAX_GAP = 0.0001

console.print("[bold green]ML1: Top words per user[/bold green]")
user_top_words_dict = {}

for i, user in enumerate(users):
    user_history_count = sum(1 for e in train_data if e["user_id"] == user)
    user_probs_weighted = probs[i] * max(user_history_count, 1)

    top_w, top_p = top_words(words, user_probs_weighted, top_n=10, min_prob=MIN_PROB, max_gap=MAX_GAP)
    top_p = normalize_probs(top_p)

    user_top_words_dict[user] = (top_w, top_p)

    table = Table(title=f"Top words for {user}")
    table.add_column("Word", style="cyan", justify="center")
    table.add_column("Probability", style="magenta", justify="center")
    table.add_column("Bar", style="green")

    for w, p in zip(top_w[:5], top_p[:5]):
        table.add_row(w, f"{p:.4f}", make_bar(p.item()))

    console.print(table)

# =====================
# 2. ML2: Answer probabilities
# =====================
with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
    user_patterns_list = json.load(f)

user_patterns = {entry["user_id"]: entry["pattern"] for entry in user_patterns_list}

all_user_probs = {}
for user in users:
    if user not in user_patterns:
        continue

    top_w, top_p = user_top_words_dict[user]
    if not top_w:
        continue

    probs_dict = compute_answer_probabilities(
        top_w,
        top_p,
        filtered_answers,  # lista, ei tiedostopolkua
        user_patterns[user],
        device=device
    )

    final_words = list(probs_dict.keys())
    final_probs = torch.zeros(len(final_words), device=device)

    for idx, w in enumerate(final_words):
        ml1_prob = top_p[top_w.index(w)] if w in top_w else 0.0
        ml2_prob = probs_dict[w]
        final_probs[idx] = ml1_prob + ml2_prob

    final_probs = normalize_probs(final_probs)
    all_user_probs[user] = dict(zip(final_words, final_probs))

# =====================
# 3. ML3: Aggregate results
# =====================
if all_user_probs:
    final_words, final_probs = aggregate_ml2_results(all_user_probs, top_n=10, device=device)
    table = Table(title="ML3: Top candidate words")
    table.add_column("Word", style="cyan", justify="center")
    table.add_column("Probability", style="magenta", justify="center")
    table.add_column("Bar", style="green")

    for w, p in zip(final_words, final_probs):
        table.add_row(w, f"{p:.4f}", make_bar(p.item()))

    console.print(table)

# =====================
# 4. Filter & score words
# =====================
with open(WORDLIST_PATH, "r", encoding="utf-8") as f:
    all_words = [w.strip().lower() for w in f if len(w.strip()) == 5]

candidates = filter_words_from_guesses(all_words, guesses)

scored = score_words(candidates)
table = Table(title="Top scored words")
table.add_column("Word", style="cyan", justify="center")
table.add_column("Score", style="magenta", justify="center")
table.add_column("Bar", style="green")
max_score = max(s for _, s in scored) if scored else 1

for word, score in scored[:5]:
    table.add_row(word, str(score), make_bar(score / max_score))

console.print(table)

# =====================
# 5. Analytics: ML3 vs basic score
# =====================
console.print("\n[bold blue]ML3 vs Basic Score Analysis[/bold blue]")
analytics_table = Table(title="Word | ML3 Prob | Basic Score | Combined")
analytics_table.add_column("Word", style="cyan", justify="center")
analytics_table.add_column("ML3 Prob", style="magenta", justify="center")
analytics_table.add_column("Basic Score", style="yellow", justify="center")
analytics_table.add_column("Combined", style="green", justify="center")

basic_scores_dict = {w: s for w, s in scored}

if all_user_probs:
    for w, p in zip(final_words, final_probs):
        ml3_prob = p.item()
        basic_score = basic_scores_dict.get(w, 0)
        combined = ml3_prob + (basic_score / max_score)
        analytics_table.add_row(w, f"{ml3_prob:.4f}", f"{basic_score}", f"{combined:.4f}")

console.print(analytics_table)
