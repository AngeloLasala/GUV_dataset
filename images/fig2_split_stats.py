"""
Panel B — grouped bar chart: image count and GUV count per split.

Produces three variants:
  fig2a — all Leica merged into one bar
  fig2b — Leica train (L1+L2) and Leica val (L1+L2) as two bars
  fig2c — Leica 1 train, Leica 1 val, Leica 2 train, Leica 2 val as four bars

Saves: images/fig2a_split_stats.png, fig2b_split_stats.png, fig2c_split_stats.png
"""

import pathlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

DATASET_ROOT = pathlib.Path(__file__).parent.parent / "rgb"

FIGSIZE      = (9, 5)
FS_LABEL     = 14
FS_TICK      = 13
FS_ANNOT     = 12
FS_LEGEND    = 12
GUV_COLOR    = "#c0392b"   # right y-axis colour


def count_folders(folders):
    n_imgs, n_guvs = 0, 0
    for folder in folders:
        split_dir = DATASET_ROOT / folder
        n_imgs += len(list((split_dir / "images").glob("*.jpg")))
        for lf in (split_dir / "labels").glob("*.txt"):
            n_guvs += len([l for l in lf.read_text().splitlines() if l.strip()])
    return n_imgs, n_guvs


def draw_chart(ax1, groups):
    """Draw bar chart on ax1 (creates twinx internally). Returns (ax1, ax2)."""
    names, colors, img_counts, guv_counts = [], [], [], []
    for label, folders, color in groups:
        n_imgs, n_guvs = count_folders(folders)
        names.append(label)
        colors.append(color)
        img_counts.append(n_imgs)
        guv_counts.append(n_guvs)

    ax2 = ax1.twinx()
    x = np.arange(len(names))
    bar_w = 0.35

    bars1 = ax1.bar(x - bar_w / 2, img_counts, bar_w, color=colors, alpha=0.9,
                    edgecolor="white", linewidth=0.5)
    bars2 = ax2.bar(x + bar_w / 2, guv_counts, bar_w, color=colors, alpha=0.5,
                    edgecolor="white", linewidth=0.5, hatch="//")

    for bar, v in zip(bars1, img_counts):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 4,
                 str(v), ha="center", va="bottom", fontsize=FS_ANNOT, fontweight="bold")

    for bar, v in zip(bars2, guv_counts):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                 str(v), ha="center", va="bottom", fontsize=FS_ANNOT,
                 color=GUV_COLOR, fontweight="bold")

    ax1.set_xticks(x)
    ax1.set_xticklabels(names, fontsize=FS_TICK)
    ax1.set_ylabel("Number of images", fontsize=FS_LABEL)
    ax2.set_ylabel("Number of GUVs",   fontsize=FS_LABEL, color=GUV_COLOR)
    ax1.set_ylim(0, max(img_counts) * 1.35)
    ax2.set_ylim(0, max(guv_counts) * 1.35)
    ax1.tick_params(axis="y", labelsize=FS_TICK)
    ax2.tick_params(axis="y", labelsize=FS_TICK, colors=GUV_COLOR)
    ax2.spines["right"].set_edgecolor(GUV_COLOR)
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax1.yaxis.grid(True, linestyle=":", linewidth=0.8, color="#bbbbbb", zorder=0)
    ax1.set_axisbelow(True)
    ax2.yaxis.grid(True, linestyle=":", linewidth=0.8, color=GUV_COLOR, alpha=0.35, zorder=0)
    ax2.set_axisbelow(True)

    legend_elements = [
        Patch(facecolor="grey", alpha=0.9,             label="Images"),
        Patch(facecolor="grey", alpha=0.5, hatch="//", label="GUVs"),
    ]
    ax1.legend(handles=legend_elements, fontsize=FS_LEGEND, loc="upper right")

    return ax1, ax2


def save_fig(fig, stem):
    for ext, kw in [(".png", {"dpi": 300}), (".pdf", {"dpi": 300})]:
        p = pathlib.Path(__file__).parent / (stem + ext)
        fig.savefig(p, bbox_inches="tight", **kw)
        print(f"Saved: {p}")


def make_chart(groups, stem):
    fig, ax1 = plt.subplots(figsize=FIGSIZE)
    draw_chart(ax1, groups)
    plt.tight_layout()
    save_fig(fig, stem)
    plt.close(fig)


# ── group definitions ──────────────────────────────────────────────────────

GROUPS_A = [
    ("Nikon\ntrain", ["train"],                                                    "#2166ac"),
    ("Nikon\nval",   ["val"],                                                      "#4dac26"),
    ("Nikon\ntest",  ["test"],                                                     "#1b7837"),
    ("Leica",        ["train_Leica_1", "val_Leica_1",
                      "train_Leica_2", "val_Leica_2"],                             "#7b2d8b"),
]

GROUPS_B = [
    ("Nikon\ntrain",  ["train"],                                   "#2166ac"),
    ("Nikon\nval",    ["val"],                                     "#4dac26"),
    ("Nikon\ntest",   ["test"],                                    "#1b7837"),
    ("Leica\ntrain",  ["train_Leica_1", "train_Leica_2"],          "#7b2d8b"),
    ("Leica\nval",    ["val_Leica_1",   "val_Leica_2"],            "#c77ddb"),
]

GROUPS_C = [
    ("Nikon\ntrain",    ["train"],          "#2166ac"),
    ("Nikon\nval",      ["val"],            "#4dac26"),
    ("Nikon\ntest",     ["test"],           "#1b7837"),
    ("Leica 1\ntrain",  ["train_Leica_1"],  "#7b2d8b"),
    ("Leica 1\nval",    ["val_Leica_1"],    "#c77ddb"),
    ("Leica 2\ntrain",  ["train_Leica_2"],  "#5c1a6b"),
    ("Leica 2\nval",    ["val_Leica_2"],    "#a64dcc"),
]

if __name__ == "__main__":
    out_dir = pathlib.Path(__file__).parent
    make_chart(GROUPS_A, "fig2a_split_stats")
    make_chart(GROUPS_B, "fig2b_split_stats")
    make_chart(GROUPS_C, "fig2c_split_stats")
