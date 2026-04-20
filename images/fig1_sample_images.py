"""
Panel A — sample tiles with bounding-box overlays.
Picks 2 Nikon images and 1 Leica_1 + 1 Leica_2 image (random but seeded).
All images are letterboxed (resize + black padding) to the same rectangular
size, preserving each source's aspect ratio.
Single bbox colour for all panels.
Saves: images/fig1_sample_images.png
"""

import random
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

random.seed(42)

DATASET_ROOT = pathlib.Path(__file__).parent.parent / "rgb"

SPLITS = [
    ("Nikon", DATASET_ROOT / "train"),
    ("Nikon", DATASET_ROOT / "val"),
    ("Leica", DATASET_ROOT / "train_Leica_1"),
    ("Leica", DATASET_ROOT / "train_Leica_2"),
]

BOX_COLOR = "#d6604d"


def load_labels(label_path: pathlib.Path):
    boxes = []
    if label_path.exists():
        for line in label_path.read_text().splitlines():
            parts = line.strip().split()
            if len(parts) == 5:
                _, cx, cy, w, h = map(float, parts)
                boxes.append((cx, cy, w, h))
    return boxes


# Target canvas: 900×600 is a good compromise between Nikon (16:9) and Leica (4:3)
TARGET_W, TARGET_H = 900, 600


def letterbox(img: np.ndarray, boxes):
    """Resize img to fit inside TARGET_W×TARGET_H keeping aspect ratio,
    pad remainder with black. Returns (canvas_array, remapped_boxes)."""
    orig_H, orig_W = img.shape[:2]
    scale = min(TARGET_W / orig_W, TARGET_H / orig_H)
    new_w = round(orig_W * scale)
    new_h = round(orig_H * scale)

    resized = np.array(Image.fromarray(img).resize((new_w, new_h), Image.LANCZOS))

    canvas = np.full((TARGET_H, TARGET_W, 3), 255, dtype=np.uint8)
    pad_x = (TARGET_W - new_w) // 2
    pad_y = (TARGET_H - new_h) // 2
    canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized

    # remap normalised box coords to canvas space
    new_boxes = []
    for cx, cy, w, h in boxes:
        new_cx = (cx * orig_W * scale + pad_x) / TARGET_W
        new_cy = (cy * orig_H * scale + pad_y) / TARGET_H
        new_w_ = w * orig_W * scale / TARGET_W
        new_h_ = h * orig_H * scale / TARGET_H
        new_boxes.append((new_cx, new_cy, new_w_, new_h_))

    return canvas, new_boxes


def draw_boxes(ax, img: np.ndarray, boxes):
    H, W = img.shape[:2]
    ax.imshow(img)
    for cx, cy, w, h in boxes:
        x0 = (cx - w / 2) * W
        y0 = (cy - h / 2) * H
        rect = patches.Rectangle(
            (x0, y0), w * W, h * H,
            linewidth=1.4, edgecolor=BOX_COLOR, facecolor="none",
        )
        ax.add_patch(rect)
    ax.axis("off")


fig, axes = plt.subplots(1, 4, figsize=(14, 4))

for ax, (title, split_dir) in zip(axes, SPLITS):
    images_dir = split_dir / "images"
    labels_dir = split_dir / "labels"
    img_files = sorted(images_dir.glob("*.jpg"))
    chosen = random.choice(img_files)
    label_file = labels_dir / (chosen.stem + ".txt")

    raw = np.array(Image.open(chosen).convert("RGB"))
    boxes = load_labels(label_file)
    img, boxes = letterbox(raw, boxes)

    draw_boxes(ax, img, boxes)
    # ax.set_title(title, fontsize=10, fontweight="bold", pad=5)

    n_guv = len(boxes)
    ax.text(
        0.03, 0.03, f"{n_guv} GUVs",
        transform=ax.transAxes, fontsize=13, color="white", fontweight="bold",
        bbox=dict(facecolor="black", alpha=0.55, pad=5, edgecolor="none"),
        va="bottom",
    )

# fig.suptitle("Representative tiles with ground-truth annotations", fontsize=11)
fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.01, wspace=0.04)

def save_fig(fig, stem):
    for ext, kw in [(".png", {"dpi": 300}), (".pdf", {"dpi": 300})]:
        p = pathlib.Path(__file__).parent / (stem + ext)
        fig.savefig(p, bbox_inches="tight", **kw)
        print(f"Saved: {p}")

save_fig(fig, "fig1_sample_images")
