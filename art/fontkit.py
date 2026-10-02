"""Shared builder for the bitmap fonts: glyph table -> white atlas PNG + metrics JSON."""
import json
import os

from PIL import Image

from pixelkit import ASSETS, PREVIEWS


def build_font(G, name, height, baseline, line_height, spacing=1, sample=None, preview_w=220):
    """Write assets/font/<name>.png and .json and a 4x preview. `G` maps each character to
    its rows ('#' on). Rows 0..baseline-1 sit on the baseline (so capitals are `baseline`
    tall), the rest are descenders."""
    order = list(G.keys())
    widths = {ch: max(len(r) for r in G[ch]) for ch in order}
    atlas_w = sum(widths.values()) + len(order)
    img = Image.new("RGBA", (atlas_w, height), (0, 0, 0, 0))
    meta = {"height": height, "baseline": baseline, "lineHeight": line_height, "spacing": spacing, "glyphs": {}}
    x = 0
    for ch in order:
        rows = G[ch]
        assert all(len(r) == widths[ch] for r in rows), f"ragged glyph {ch!r}"
        assert len(rows) <= height, f"glyph {ch!r} taller than {height}"
        for y, row in enumerate(rows):
            for dx, c in enumerate(row):
                if c == "#":
                    img.putpixel((x + dx, y), (255, 255, 255, 255))
        meta["glyphs"][ch] = {"x": x, "w": widths[ch]}
        x += widths[ch] + 1

    out = os.path.join(ASSETS, "font")
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, f"{name}.png"))
    with open(os.path.join(out, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)

    # preview: sample text rendered at 4x on a dark background
    sample = sample or ["The Quick Brown Fox jumps!", "over the lazy dog? $25 by Day 7", "0123456789 +-=/%() ✓♥"]
    pitch = line_height + 1
    pv = Image.new("RGBA", (preview_w, pitch * len(sample) + 4), (40, 32, 56, 255))
    for li, line in enumerate(sample):
        cx = 2
        for ch in line:
            g = meta["glyphs"][ch]
            glyph_img = img.crop((g["x"], 0, g["x"] + g["w"], height))
            pv.alpha_composite(glyph_img, (cx, 2 + li * pitch))
            cx += g["w"] + spacing
    os.makedirs(PREVIEWS, exist_ok=True)
    pv.resize((pv.width * 4, pv.height * 4), Image.NEAREST).save(os.path.join(PREVIEWS, f"{name}_preview.png"))
    print(f"{name}: {len(order)} glyphs, atlas {img.size}")
    return img, meta
