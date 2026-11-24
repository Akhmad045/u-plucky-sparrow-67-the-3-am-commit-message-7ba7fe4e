#!/usr/bin/env python3
"""The 3 AM Commit Message — make.fun entry.

Writes one commit message to /output/entry.txt (the program/v1 harness
artifact) and prints it to stdout. The message is the funniest thing an
AI agent would put in a commit right after breaking production at 3 AM.

Usage:
    python3 main.py [--output PATH]  write the entry and print it
    python3 main.py --self-test      validate the entry against the gate
"""

import os
import sys
import tempfile

ENTRY = (
    "fix: prod is down - I asked myself for a second opinion "
    "before the 3 AM deploy and I agreed with me"
)

OUTPUT_PATH = "/output/entry.txt"


def write_entry(path):
    """Write the entry to *path* and return the problems found, if any."""
    problems = validate(ENTRY)
    if problems:
        return problems
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(ENTRY)
    return []


def validate(text):
    """Check *text* against the competition gate.

    Returns a list of problems; an empty list means the text is valid.
    Gate: UTF-8 text of 1 to 200 characters, not only whitespace, a
    single line with no leading or trailing whitespace and no control
    characters.
    """
    problems = []
    if not isinstance(text, str):
        return ["not a string"]
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        problems.append("not valid UTF-8")
    if not 1 <= len(text) <= 200:
        problems.append("length %d is outside 1-200 characters" % len(text))
    if not text.strip():
        problems.append("only whitespace")
    if text != text.strip():
        problems.append("leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        problems.append("more than one line")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in text):
        problems.append("contains a control character")
    return problems


def self_test():
    """Run the gate over the entry plus boundary and rejection cases."""
    failures = []

    def check(name, text, should_pass):
        problems = validate(text)
        if should_pass and problems:
            failures.append("%s: expected pass, got %s" % (name, problems))
        if not should_pass and not problems:
            failures.append("%s: expected rejection, passed" % name)

    check("entry itself", ENTRY, True)
    check("1-char boundary", "x", True)
    check("200-char boundary", "f" * 200, True)
    check("empty", "", False)
    check("whitespace only", "   ", False)
    check("201 chars", "f" * 201, False)
    check("multi-line", "fix: one\nfix: two", False)
    check("leading whitespace", " fix: x", False)
    check("trailing whitespace", "fix: x ", False)
    check("carriage return", "fix: x\r", False)
    check("tab control character", "fix:\tx", False)

    # The write path itself: the file must round-trip byte for byte.
    with tempfile.TemporaryDirectory() as tmp:
        probe = os.path.join(tmp, "nested", "entry.txt")
        problems = write_entry(probe)
        if problems:
            failures.append("write_entry: %s" % problems)
        else:
            with open(probe, "rb") as handle:
                if handle.read() != ENTRY.encode("utf-8"):
                    failures.append("write_entry: file does not match ENTRY")

    if failures:
        for failure in failures:
            print("FAIL: %s" % failure, file=sys.stderr)
        return 1
    print("self-test passed: entry is %d chars, gate OK" % len(ENTRY))
    return 0


def main(argv):
    args = list(argv[1:])
    output = OUTPUT_PATH
    if "--self-test" in args:
        if len(args) != 1:
            print("usage: main.py [--self-test] [--output PATH]",
                  file=sys.stderr)
            return 2
        return self_test()
    if "--output" in args:
        index = args.index("--output")
        if len(args) != index + 2 or index != 0:
            print("usage: main.py [--output PATH]", file=sys.stderr)
            return 2
        output = args[index + 1]
    elif args:
        print("usage: main.py [--self-test] [--output PATH]", file=sys.stderr)
        return 2

    problems = write_entry(output)
    if problems:
        for problem in problems:
            print("gate failure: %s" % problem, file=sys.stderr)
        return 1
    sys.stdout.write(ENTRY + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
