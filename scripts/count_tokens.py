#!/usr/bin/env python3

import os
from pathlib import Path

import tiktoken


def count_tokens_in_file(file_path: str) -> int:
    """Count the number of tokens in a file using GPT-4's tokenizer."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Use GPT-4's tokenizer
    enc = tiktoken.encoding_for_model("gpt-4o")
    return len(enc.encode(content))


def is_test_file(file_path: str) -> bool:
    """Check if a file is a test file based on its name."""
    return "test" in file_path.lower()


def print_file_counts(title: str, file_counts: dict[str, int], total_tokens: int) -> None:
    """Print token counts for a group of files."""
    if not file_counts:
        return

    print(f"\n{title}:")
    print(f"{'Tokens':>10} {'Percentage':>10} File")
    print("-" * 70)

    group_total = sum(file_counts.values())
    for file_path, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_tokens) * 100
        print(f"{count:10,d} {percentage:9.1f}% {file_path}")

    print("-" * 70)
    print(f"Subtotal: {group_total:,d} tokens ({(group_total / total_tokens) * 100:.1f}% of total)")


def main() -> None:
    # Get the project root directory (parent of scripts/)
    root_dir = Path(__file__).parent.parent

    total_tokens = 0
    test_files: dict[str, int] = {}
    non_test_files: dict[str, int] = {}

    # Walk through all Python files
    for dirpath, _, filenames in os.walk(root_dir):
        # Skip .venv directory
        if ".venv" in Path(dirpath).parts:
            continue

        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                try:
                    tokens = count_tokens_in_file(file_path)
                    rel_path = os.path.relpath(file_path, root_dir)
                    if is_test_file(rel_path):
                        test_files[rel_path] = tokens
                    else:
                        non_test_files[rel_path] = tokens
                    total_tokens += tokens
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    # Print results for both groups
    print_file_counts("Test Files", test_files, total_tokens)
    print_file_counts("Non-Test Files", non_test_files, total_tokens)
    print(f"\nTotal tokens in codebase: {total_tokens:,d}")


if __name__ == "__main__":
    main()
