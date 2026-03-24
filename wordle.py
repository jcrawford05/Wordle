#!/usr/bin/env python3
"""
Wordle - Terminal Edition
Guess the 5-letter word in 6 tries!
"""

import random
import sys

# ── Colour codes ────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"

# Background + foreground combos for filled boxes
BG_GREEN  = "\033[42m\033[97m"
BG_YELLOW = "\033[43m\033[30m"
BG_GRAY   = "\033[100m\033[97m"
BG_EMPTY  = "\033[40m\033[90m"   # dark box for unfilled rows

# Foreground-only for keyboard
FG_GREEN  = "\033[92m"
FG_YELLOW = "\033[93m"
FG_GRAY   = "\033[90m"

BOX_W = 5   # chars wide per tile
GAP   = " " # gap between tiles

# ── Word list (from NLTK) ────────────────────────────────────────────────────
def load_words() -> list[str]:
    try:
        from nltk.corpus import words as nltk_words
        import nltk
        try:
            word_list = nltk_words.words()
        except LookupError:
            print("  Downloading NLTK words corpus...")
            nltk.download("words", quiet=True)
            word_list = nltk_words.words()
        return sorted(set(w.lower() for w in word_list if len(w) == 5 and w.isalpha()))
    except ImportError:
        print("  ✗  nltk is not installed. Run: pip install nltk")
        sys.exit(1)

WORDS = load_words()

MAX_GUESSES = 6
WORD_LEN    = 5

# ── Helpers ──────────────────────────────────────────────────────────────────

def score_guess(guess: str, answer: str) -> list[str]:
    """Return a list of 'green'/'yellow'/'gray' for each position."""
    result = [None] * WORD_LEN
    answer_remaining = list(answer)

    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            result[i] = "green"
            answer_remaining[i] = None

    for i, g in enumerate(guess):
        if result[i]:
            continue
        if g in answer_remaining:
            result[i] = "yellow"
            answer_remaining[answer_remaining.index(g)] = None
        else:
            result[i] = "gray"

    return result


def render_tile(letter: str, state: str) -> str:
    """Return one coloured box tile."""
    colour = {
        "green":  BG_GREEN,
        "yellow": BG_YELLOW,
        "gray":   BG_GRAY,
        "empty":  BG_EMPTY,
    }[state]

    if state == "empty":
        return f"{colour}     {RESET}"

    return f"{colour}{BOLD}  {letter.upper()}  {RESET}"

def render_row(letters: list[str], states: list[str]) -> str:
    tiles = [render_tile(l, s) for l, s in zip(letters, states)]
    return "  " + GAP.join(tiles)


def print_board(guesses: list[str], answer: str) -> None:
    print()
    for i in range(MAX_GUESSES):
        if i < len(guesses):
            states  = score_guess(guesses[i], answer)
            letters = list(guesses[i])
        else:
            states  = ["empty"] * WORD_LEN
            letters = [" "] * WORD_LEN
        print(render_row(letters, states))
        print()


def build_keyboard(guesses: list[str], answer: str) -> str:
    """Show a mini keyboard with per-letter colour hints."""
    rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    letter_state: dict[str, str] = {}

    for guess in guesses:
        scores = score_guess(guess, answer)
        for ch, state in zip(guess, scores):
            if state == "green":
                letter_state[ch] = "green"
            elif state == "yellow" and letter_state.get(ch) != "green":
                letter_state[ch] = "yellow"
            elif ch not in letter_state:
                letter_state[ch] = "gray"

    lines = []
    for row in rows:
        parts = []
        for ch in row:
            state = letter_state.get(ch)
            if state == "green":
                parts.append(f"{FG_GREEN}{BOLD}{ch.upper()}{RESET}")
            elif state == "yellow":
                parts.append(f"{FG_YELLOW}{BOLD}{ch.upper()}{RESET}")
            elif state == "gray":
                parts.append(f"{FG_GRAY}{ch.upper()}{RESET}")
            else:
                parts.append(ch.upper())
        lines.append("  " + " ".join(parts))
    return "\n".join(lines)


def print_title() -> None:
    print(f"\n{BOLD}  ╔══════════════════╗")
    print(f"  ║  W O R D L E  🟩  ║")
    print(f"  ╚══════════════════╝{RESET}")
    print(f"  Guess the {WORD_LEN}-letter word in {MAX_GUESSES} tries.\n")
    print("  🟩 = right letter, right spot")
    print("  🟨 = right letter, wrong spot")
    print("  ⬛ = letter not in word\n")


# ── Main game loop ───────────────────────────────────────────────────────────

def play() -> bool:
    answer  = random.choice(WORDS)
    guesses = []
    won     = False

    print_title()

    while len(guesses) < MAX_GUESSES:
        print_board(guesses, answer)
        print(build_keyboard(guesses, answer))
        print()

        remaining = MAX_GUESSES - len(guesses)
        prompt = f"  Guess ({remaining} left): "

        try:
            raw = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Game interrupted. Goodbye!")
            return False

        # Validation
        if len(raw) != WORD_LEN:
            print(f"  ⚠  Please enter exactly {WORD_LEN} letters.\n")
            continue
        if not raw.isalpha():
            print("  ⚠  Letters only, no numbers or symbols.\n")
            continue
        if raw not in WORDS:
            print(f"  ⚠  '{raw.upper()}' is not in the word list. Try again.\n")
            continue

        guesses.append(raw)

        if raw == answer:
            won = True
            break

    # Final board
    print_board(guesses, answer)

    if won:
        labels = ["Genius!", "Magnificent!", "Impressive!", "Splendid!", "Great!", "Phew!"]
        print(f"  🎉  {labels[len(guesses) - 1]}  You got it in {len(guesses)}/{MAX_GUESSES}!\n")
    else:
        print(f"  😔  Hard luck! The word was {BOLD}{answer.upper()}{RESET}\n")

    return won


def main() -> None:
    while True:
        play()
        try:
            again = input("  Play again? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            again = "n"
        if again not in ("y", "yes"):
            print("\n  Thanks for playing! 👋\n")
            break
        print("\n" + "─" * 44)


if __name__ == "__main__":
    main()
