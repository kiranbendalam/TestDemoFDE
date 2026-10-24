"""Helpers so every L1 step shows what it runs: the call chain and the real code lines, with line numbers."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def chain(text):
    print("HOW THIS STEP RUNS\n" + text.rstrip() + "\n")


def code(rel, start, end=None, label="", notes=None):
    """Print lines of ROOT/rel from the line containing `start` to the line containing `end`.
    notes: {snippet: "annotation"} printed at the right of the matching line."""
    lines = (ROOT / rel).read_text().splitlines()
    a = next(i for i, l in enumerate(lines, 1) if start in l)
    b = next(i for i, l in enumerate(lines, 1) if i >= a and end in l) if end else a
    print(f"  {label}  ({rel}, lines {a}-{b}):" if label else f"  {rel}, lines {a}-{b}:")
    for n in range(a, b + 1):
        l = lines[n - 1]
        note = next((v for k, v in (notes or {}).items() if k in l), "")
        print(f"    {n:>3} | {l:<62}{('  ← ' + note) if note else ''}")
    print()
