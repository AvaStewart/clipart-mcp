"""Walk a folder of PNG clip art and write manifest.json into it.

Usage:
    python build_manifest.py path/to/png_folder

Category = first subfolder name. Starter tags = words from the folder and
file names. Re-running keeps any tags you (or the AI) added earlier.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

EXTS = {".png"}


def main(root_arg: str) -> None:
    root = Path(root_arg).resolve()
    manifest_path = root / "manifest.json"

    old_tags = {}
    if manifest_path.exists():
        for item in json.loads(manifest_path.read_text(encoding="utf-8")):
            old_tags[item["path"]] = item.get("tags", [])

    items = []
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() not in EXTS:
            continue
        rel = p.relative_to(root)
        parts = rel.parts
        category = parts[0] if len(parts) > 1 else "uncategorized"
        try:
            with Image.open(p) as im:
                width, height = im.size
        except Exception as e:
            print(f"skipping {rel}: {e}")
            continue

        path = rel.as_posix()
        words = re.findall(r"[a-z]{3,}", " ".join(parts[:-1] + (p.stem,)).lower())
        tags = sorted(set(words) | set(old_tags.get(path, [])))
        items.append(
            {
                "path": path,
                "category": category,
                "width": width,
                "height": height,
                "tags": tags,
            }
        )

    manifest_path.write_text(json.dumps(items, indent=1), encoding="utf-8")
    print(f"Wrote {len(items)} entries to {manifest_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python build_manifest.py path/to/png_folder")
    main(sys.argv[1])
