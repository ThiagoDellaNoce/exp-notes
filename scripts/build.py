#!/usr/bin/env python3
"""
Build script for EXP Notes GitHub Pages site.
Scans all .md files in the repo, copies them to _site/notes/,
and generates _site/index.json with the category tree.
"""
import json
import os
import shutil
from pathlib import Path

REPO_ROOT = Path(".")
SITE_DIR = Path("_site")
NOTES_DIR = SITE_DIR / "notes"

EXCLUDE_DIRS = {
    ".git", ".github", ".claude", "scripts", "site", "_site", "node_modules"
}

EXCLUDE_ROOT_FILES = {
    "blank.md", "blank2.md", "blank3.md",
    "cheatsheet.md", "markdown-cheat-sheet.md",
}


def build():
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir()
    NOTES_DIR.mkdir()

    (SITE_DIR / ".nojekyll").touch()
    shutil.copy("site/index.html", SITE_DIR / "index.html")

    categories = []
    root_files = []

    top_items = sorted(REPO_ROOT.iterdir(), key=lambda p: p.name.lower())

    for item in top_items:
        if item.is_dir() and item.name not in EXCLUDE_DIRS and not item.name.startswith("."):
            files = []
            for md_file in sorted(item.rglob("*.md"), key=lambda p: p.name.lower()):
                rel_path = str(md_file.relative_to(REPO_ROOT))
                rel_to_cat = md_file.relative_to(item)

                if len(rel_to_cat.parts) > 1:
                    prefix = " / ".join(rel_to_cat.parts[:-1])
                    display = f"{prefix} / {md_file.stem}"
                else:
                    display = md_file.stem

                files.append({"name": display, "path": rel_path})

                dest = NOTES_DIR / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(md_file, dest)

            if files:
                categories.append({"name": item.name, "files": files})

        elif (
            item.is_file()
            and item.suffix.lower() == ".md"
            and item.name not in EXCLUDE_ROOT_FILES
        ):
            root_files.append({"name": item.stem, "path": item.name})
            shutil.copy(item, NOTES_DIR / item.name)

    index = {"categories": categories, "root_files": root_files}

    with open(SITE_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    total = sum(len(c["files"]) for c in categories) + len(root_files)
    print(f"✓ {len(categories)} categorias, {total} notas → {SITE_DIR}/")


if __name__ == "__main__":
    build()
