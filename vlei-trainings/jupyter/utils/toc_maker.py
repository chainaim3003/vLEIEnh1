#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote
from collections import defaultdict

def generate_anchor(heading_text, existing_anchors):
    """
    Generates a GitHub-style anchor for a heading, handling duplicates.
    Keeps original case, replaces spaces with hyphens, removes most punctuation.

    Args:
        heading_text (str): The text of the heading.
        existing_anchors (defaultdict): A dict tracking counts of generated anchors
                                         within the current notebook file.

    Returns:
        str: The generated unique anchor string.
    """
    # Keep alphanumeric, replace space with hyphen, remove others
    # Allows hyphens within the heading text to persist
    anchor = re.sub(r'[^\w\s:-]', '', heading_text).strip()
    anchor = re.sub(r'\s+', '-', anchor)
    # Do not lowercase - keep original case as requested

    # Handle duplicates by appending -1, -2, etc.
    base_anchor = anchor
    count = existing_anchors[base_anchor]
    if count > 0:
        anchor = f"{base_anchor}-{count}"
    existing_anchors[base_anchor] += 1
    return anchor

def extract_headings(notebook_path, max_level):
    """
    Extracts Markdown headings and their levels from a Jupyter notebook.

    Args:
        notebook_path (Path): The path to the .ipynb file.
        max_level (int): The maximum heading level to include (e.g., 2 for # and ##).

    Returns:
        list: A list of tuples, where each tuple is (level, text, anchor).
              Returns an empty list if the file cannot be parsed or has no headings.
    """
    headings = []
    try:
        # Ensure UTF-8 encoding is used
        with open(notebook_path, 'r', encoding='utf-8') as f:
            try:
                notebook = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {notebook_path}", file=sys.stderr)
                return [] # Skip malformed files

        # Track anchors generated within this specific notebook
        notebook_anchors = defaultdict(int)

        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'markdown':
                source = cell.get('source', [])
                # Source can be a string or list of strings
                if isinstance(source, str):
                    source_lines = source.splitlines()
                else:
                    source_lines = source

                for line in source_lines:
                    line = line.strip()
                    # Match lines starting with 1 to max_level '#'
                    match = re.match(r'^(#{{1,{max_level}}})\s+(.*)'.format(max_level=max_level), line)
                    if match:
                        level = len(match.group(1))
                        text = match.group(2).strip()
                        # Remove potential markdown links within the heading text itself for cleaner TOC
                        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
                        # Remove potential markdown formatting like bold/italics
                        text = re.sub(r'[*_`]', '', text)
                        if text: # Ensure heading text is not empty
                            anchor = generate_anchor(text, notebook_anchors)
                            headings.append((level, text, anchor))
    except FileNotFoundError:
        print(f"Warning: File not found {notebook_path}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Warning: Error processing {notebook_path}: {e}", file=sys.stderr)
        return []
    return headings

def find_notebooks(folder_path, recursive):
    """
    Finds all .ipynb files in a folder, optionally recursively.

    Args:
        folder_path (Path): The path to the folder to search.
        recursive (bool): Whether to search subdirectories.

    Returns:
        list: A sorted list of Path objects for found .ipynb files.
    """
    notebook_files = []
    if recursive:
        # Walk through directory
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.ipynb'):
                    # Create full path and add to list
                    notebook_files.append(Path(root) / file)
    else:
        # Iterate through items in the directory
        for item in folder_path.iterdir():
            # Check if it's a file and ends with .ipynb
            if item.is_file() and item.name.lower().endswith('.ipynb'):
                notebook_files.append(item)

    # Sort alphabetically by the full path for consistent order
    notebook_files.sort()
    return notebook_files

def generate_toc(notebook_files, include_filenames, use_bullets, max_level, base_folder):
    """
    Generates the Markdown Table of Contents.

    Args:
        notebook_files (list): List of Path objects for the notebooks.
        include_filenames (bool): Whether to include filenames in the TOC.
        use_bullets (bool): True to use bullets (*), False for numbered lists (1.).
        max_level (int): Maximum heading level to include.
        base_folder (Path): The root folder from which paths should be relative.

    Returns:
        str: The generated Markdown TOC.
    """
    toc_lines = ["# Table of Contents"]
    unique_headings = set() # To avoid adding the exact same heading text consecutively

    for notebook_path in notebook_files:
        # Get path relative to the initial folder_path for cleaner links
        try:
            relative_path = notebook_path.relative_to(base_folder)
        except ValueError:
            # Fallback if relative path fails (shouldn't happen with current logic)
            relative_path = notebook_path.name

        # URL-encode the path components for the link, ensuring forward slashes
        encoded_path = '/'.join(quote(part) for part in relative_path.parts)

        headings = extract_headings(notebook_path, max_level)

        if headings:
            file_header_added = False
            if include_filenames:
                # Add filename as a non-linked item or a higher-level heading
                # Using bold text here for separation
                toc_lines.append(f"\n**{relative_path.name}**\n")
                file_header_added = True

            last_heading_text = None
            for level, text, anchor in headings:
                # Basic check to avoid immediate duplicates of the exact same text
                if text == last_heading_text:
                    continue
                last_heading_text = text

                # Indentation based on heading level (level 1 has 0 indentation)
                # Use 4 spaces per indent level for better compatibility
                indent = "    " * (level - 1) # Changed from "  " to "    "
                marker = "*" if use_bullets else "1." # Standard Markdown uses 1. for all ordered items
                link = f"[{text}]({encoded_path}#{anchor})"
                toc_lines.append(f"{indent}{marker} {link}")

    return "\n".join(toc_lines)

def main():
    parser = argparse.ArgumentParser(
        description="Generate a Markdown Table of Contents (TOC) from Jupyter notebooks (.ipynb) in a folder.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "folder_path",
        type=str,
        help="Path to the folder containing .ipynb files."
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Search for .ipynb files recursively in subfolders."
    )
    parser.add_argument(
        "-f", "--include-filenames",
        action="store_true",
        help="Include notebook filenames in the TOC."
    )
    parser.add_argument(
        "-b", "--use-bullets",
        action="store_true",
        help="Use bullet points (*) instead of numbered lists (1.) for TOC items."
    )
    parser.add_argument(
        "-l", "--max-level",
        type=int,
        default=2,
        help="Maximum heading level to include in the TOC (e.g., 1 for #, 2 for # and ##, etc.). Default is 2."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Optional path to an output Markdown file. If not specified, prints to standard output."
    )

    args = parser.parse_args()

    folder_path = Path(args.folder_path)
    if not folder_path.is_dir():
        print(f"Error: Folder not found or is not a directory: {args.folder_path}", file=sys.stderr)
        sys.exit(1)

    if args.max_level < 1:
        print(f"Error: Max level must be at least 1.", file=sys.stderr)
        sys.exit(1)

    # Find notebooks
    notebook_files = find_notebooks(folder_path, args.recursive)

    if not notebook_files:
        print(f"No .ipynb files found in {args.folder_path}"
              f"{' recursively' if args.recursive else ''}.", file=sys.stderr)
        sys.exit(0)

    # Generate TOC
    toc_markdown = generate_toc(
        notebook_files,
        args.include_filenames,
        args.use_bullets,
        args.max_level,
        folder_path # Pass base folder for relative path calculation
    )

    # Output TOC
    if args.output:
        try:
            output_path = Path(args.output)
            # Create parent directories if they don't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(toc_markdown + "\n") # Add trailing newline
            print(f"TOC successfully written to {output_path}")
        except Exception as e:
            print(f"Error writing to output file {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Print to standard output
        print(toc_markdown)

if __name__ == "__main__":
    main()
