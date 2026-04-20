"""
Composite panel figure for paper/repo:

  (A) top row    — 4 representative tiles with bbox overlays (Nikon ×2, Leica ×2)
  (B) bottom-left  — dataset split statistics (fig2a)
  (C) bottom-right — GUV size distribution with log-normal fit in µm (fig3d)

Saves: images/fig_panel.png
"""

import sys
import pathlib
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fig2_split_stats import draw_chart, GROUPS_A as FIG2_GROUPS
from fig3_bbox_sizes  import draw_chart_with_fit, GROUPS_D as FIG3_GROUPS

random.seed(42)

DATASET_ROOT = pathlib.Path(__file__).parent.parent / "rgb"

BOX_COLOR = "#d6604d"
TARGET_W, TARGET_H = 900, 600

FIG1_SPLITS = [
    ("Nikon", DATASET_ROOT / "train"),
    ("Nikon", DATASET_ROOT / "val"),
    ("Leica", DATASET_ROOT / "train_Leica_1"),
    ("Leica", DATASET_ROOT / "train_Leica_2"),
]

PANEL_LABEL_KW = dict(fontsize=14, fontweight="bold", va="top", ha="left")


# ── fig1 helpers ─────────────────────────────────────────────────────────────

def load_labels(path):
    boxes = []
    if path.exists():
        for line in path.read_text().splitlines():
            parts = line.strip().split()
            if len(parts) == 5:
                _, cx, cy, w, h = map(float, parts)
                boxes.append((cx, cy, w, h))
    return boxes


def letterbox(img, boxes):
    orig_H, orig_W = img.shape[:2]
    scale  = min(TARGET_W / orig_W, TARGET_H / orig_H)
    new_w  = round(orig_W * scale)
    new_h  = round(orig_H * scale)
    canvas = np.full((TARGET_H, TARGET_W, 3), 255, dtype=np.uint8)
    pad_x  = (TARGET_W - new_w) // 2
    pad_y  = (TARGET_H - new_h) // 2
    canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = np.array(
        Image.fromarray(img).resize((new_w, new_h), Image.LANCZOS)
    )
    new_boxes = [
        ((cx * orig_W * scale + pad_x) / TARGET_W,
         (cy * orig_H * scale + pad_y) / TARGET_H,
         w  * orig_W * scale           / TARGET_W,
         h  * orig_H * scale           / TARGET_H)
        for cx, cy, w, h in boxes
    ]
    return canvas, new_boxes


def draw_sample_images(axes):
    for ax, (title, split_dir) in zip(axes, FIG1_SPLITS):
        img_files  = sorted((split_dir / "images").glob("*.jpg"))
        chosen     = random.choice(img_files)
        label_file = split_dir / "labels" / (chosen.stem + ".txt")
        raw        = np.array(Image.open(chosen).convert("RGB"))
        boxes      = load_labels(label_file)
        img, boxes = letterbox(raw, boxes)

        H, W = img.shape[:2]
        ax.imshow(img)
        for cx, cy, w, h in boxes:
            ax.add_patch(mpatches.Rectangle(
                ((cx - w / 2) * W, (cy - h / 2) * H), w * W, h * H,
                linewidth=1.4, edgecolor=BOX_COLOR, facecolor="none"
            ))
        ax.axis("off")
        ax.set_title(title, fontsize=10, fontweight="bold", pad=4)
        n = len(boxes)
        ax.text(0.03, 0.03, f"{n} GUVs",
                transform=ax.transAxes, fontsize=11, color="white",
                fontweight="bold",
                bbox=dict(facecolor="black", alpha=0.55, pad=4, edgecolor="none"),
                va="bottom")


# ── build panel ──────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(15, 11))

outer = gridspec.GridSpec(2, 1, figure=fig,
                          height_ratios=[2, 1],
                          hspace=0.10)

# ── row A: sample images ──
top_gs = gridspec.GridSpecFromSubplotSpec(1, 4, subplot_spec=outer[0], wspace=0.04)
img_axes = [fig.add_subplot(top_gs[0, i]) for i in range(4)]
draw_sample_images(img_axes)

# panel label A
img_axes[0].text(-0.06, 1.12, "A", transform=img_axes[0].transAxes, **PANEL_LABEL_KW)

# ── row B/C: stats and distribution ──
bot_gs = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer[1], wspace=0.45)

ax_bar  = fig.add_subplot(bot_gs[0, 0])
ax_hist = fig.add_subplot(bot_gs[0, 1])

draw_chart(ax_bar, FIG2_GROUPS)
draw_chart_with_fit(ax_hist, FIG3_GROUPS)

ax_bar.text( -0.22, 1.12, "B", transform=ax_bar.transAxes,  **PANEL_LABEL_KW)
ax_hist.text(-0.15, 1.12, "C", transform=ax_hist.transAxes, **PANEL_LABEL_KW)

for ext, kw in [(".png", {"dpi": 300}), (".pdf", {"dpi": 300})]:
    p = pathlib.Path(__file__).parent / ("fig_panel" + ext)
    fig.savefig(p, bbox_inches="tight", **kw)
    print(f"Saved: {p}")
