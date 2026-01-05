#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys


OPEN_TO_CLOSE = {
    "(": ")",
    "[": "]",
}
CLOSE_TO_OPEN = {v: k for k, v in OPEN_TO_CLOSE.items()}


def iter_pine_files(args):
    if args:
        for path in args:
            yield Path(path)
        return
    yield from Path(".").rglob("*.pine")


def add_error(errors, path, line, col, message):
    errors.append(f"{path}:{line}:{col}: error: {message}")


def check_text(text, path):
    errors = []
    stack = []
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False

    line = 1
    col = 0
    i = 0
    text_len = len(text)
    while i < text_len:
        ch = text[i]
        if ch == "\n":
            if in_single or in_double:
                add_error(errors, path, line, col + 1, "Unterminated string literal")
                in_single = False
                in_double = False
            if in_line_comment:
                in_line_comment = False
            line += 1
            col = 0
            i += 1
            continue

        col += 1
        nxt = text[i + 1] if i + 1 < text_len else ""

        if in_line_comment:
            i += 1
            continue

        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
                col += 1
            else:
                i += 1
            continue

        if in_single:
            if ch == "\\" and i + 1 < text_len:
                i += 2
                col += 1
                continue
            if ch == "'":
                in_single = False
            i += 1
            continue

        if in_double:
            if ch == "\\" and i + 1 < text_len:
                i += 2
                col += 1
                continue
            if ch == '"':
                in_double = False
            i += 1
            continue

        if ch == "/" and nxt == "/":
            in_line_comment = True
            i += 2
            col += 1
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            col += 1
            continue

        if ch == "'":
            in_single = True
            i += 1
            continue
        if ch == '"':
            in_double = True
            i += 1
            continue

        if ch in OPEN_TO_CLOSE:
            stack.append((ch, line, col))
            i += 1
            continue
        if ch in CLOSE_TO_OPEN:
            if not stack:
                add_error(errors, path, line, col, f"Unmatched closing '{ch}'")
            else:
                open_ch, open_line, open_col = stack.pop()
                expected = OPEN_TO_CLOSE[open_ch]
                if ch != expected:
                    add_error(
                        errors,
                        path,
                        line,
                        col,
                        f"Mismatched closing '{ch}', expected '{expected}' for '{open_ch}' opened at {open_line}:{open_col}",
                    )
            i += 1
            continue

        i += 1

    if in_single or in_double:
        add_error(errors, path, line, max(col, 1), "Unterminated string literal at EOF")
    if in_block_comment:
        add_error(errors, path, line, max(col, 1), "Unterminated block comment at EOF")
    while stack:
        open_ch, open_line, open_col = stack.pop()
        expected = OPEN_TO_CLOSE[open_ch]
        add_error(
            errors,
            path,
            open_line,
            open_col,
            f"Unclosed '{open_ch}', expected '{expected}'",
        )

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Basic Pine Script pre-check: quotes, comments, and brackets."
    )
    parser.add_argument("paths", nargs="*", help="Files or directories to scan")
    args = parser.parse_args()

    errors = []
    paths = list(iter_pine_files(args.paths))
    if not paths:
        print("No .pine files found.", file=sys.stderr)
        return 1

    for path in paths:
        if path.is_dir():
            for sub in path.rglob("*.pine"):
                errors.extend(check_text(sub.read_text(encoding="utf-8"), sub))
        else:
            errors.extend(check_text(path.read_text(encoding="utf-8"), path))

    if errors:
        for err in errors:
            print(err)
        return 1

    print("Pine pre-check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
