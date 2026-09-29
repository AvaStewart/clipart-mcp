# clipart-mcp

An MCP server that gives an AI hands-on access to a folder of clip art: it can search the collection, actually look at images, and tag them so future searches get smarter.

I built it to power a park website made from 1990s CD-ROM clip art. The original discs had DOS-style filenames (`ANI0042.PCX`), so the art was basically unsearchable. This server fixes that with a simple loop: the AI views an image, describes it, saves tags, and searches those tags later while building the site.

## How it works

```
CD-ROM clip art (PCX / TIF / BMP)
        |  batch convert to PNG (XnConvert)
        v
folder of PNGs  --build_manifest.py-->  manifest.json
        |                                    |
        +---------------  server.py  --------+
                              |
                    Claude (Claude Code, etc.)
                    search / view / tag / random
```

The server never modifies your images. The only file it writes is `manifest.json`, when you tag something.

## Setup

Requires Python 3.10+.

```
git clone https://github.com/YOUR-USERNAME/clipart-mcp.git
cd clipart-mcp
pip3 install -r requirements.txt
python3 build_manifest.py C:\path\to\png_folder
```

`build_manifest.py` scans the folder for PNGs and writes `manifest.json` into it. The first subfolder name becomes the category, and words from folder and file names become starter tags. Re-running it keeps any tags added earlier, so you can add images later without losing work.

## Connect to Claude Code

```
claude mcp add clipart --env CLIPART_DIR=C:\path\to\png_folder -- python C:\path\to\clipart-mcp\server.py
```

Run `claude mcp list` to confirm it is connected. On macOS/Linux, use forward-slash paths.

## Tools

| Tool | What it does |
| --- | --- |
| `list_categories` | Every category and how many images it has |
| `search_clipart` | Keyword search across tags, category, and filename |
| `random_clipart` | Random images, optionally within a category |
| `view_clipart` | Returns the image itself so the AI can look at it |
| `tag_clipart` | Saves descriptive tags to the manifest |

## Suggested workflow

1. Ask the AI to pick a category, call `view_clipart` on each image, and `tag_clipart` it with real descriptions ("squirrel, cartoon, holding acorn").
2. Ask it to build your site, using `search_clipart` to find art for each section.
3. Commit the PNGs and `manifest.json` to your site repo. The site can load `manifest.json` to choose images at runtime.

Tagging thousands of images uses a lot of AI usage, so start with a few categories.

## Notes

- Only PNG files are indexed. Convert PCX, TIF, and BMP first.
- `view_clipart` refuses paths outside the clip art folder.
- Check the license of your clip art before publishing it. This repo contains code only and no images.
