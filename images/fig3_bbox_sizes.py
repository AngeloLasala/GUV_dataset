"""
Panel C — GUV size distribution.

Size formula:  dim = sqrt(max_dim² + min_dim²) / sqrt(2)
Bboxes where min_dim <= 0.5 * max_dim (edge/partial GUVs) are excluded.

Produces:
  fig3a-c — normalised to image diagonal (dimensionless)
  fig3d   — real size in µm with log-normal fit (same groups as fig3a)

Saves: images/fig3[a-d]_bbox_sizes.png
"""

import pathlib
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.stats import lognorm

DATASET_ROOT = pathlib.Path(__file__).parent.parent / "rgb"

FIGSIZE   = (9, 5)
FS_LABEL  = 14
FS_TICK   = 13
FS_LEGEND = 12

MU_PER_PX = {"nikon": 0.339, "leica": 0.45}


def compute_dims(folders, calibrated=False):
    """GUV sizes across splits. calibrated=True → µm, else normalised to image diagonal."""
    dims = []
    for folder in folders:
        mu = MU_PER_PX["leica" if "leica" in folder.lower() else "nikon"] if calibrated else None
        split_dir  = DATASET_ROOT / folder
        labels_dir = split_dir / "labels"
        images_dir = split_dir / "images"
        for lf in labels_dir.glob("*.txt"):
            img_path = images_dir / (lf.stem + ".jpg")
            if not img_path.exists():
                continue
            W, H = Image.open(img_path).size
            for line in lf.read_text().splitlines():
                parts = line.strip().split()
                if len(parts) == 5:
                    w_px = float(parts[3]) * W
                    h_px = float(parts[4]) * H
                    max_dim = max(w_px, h_px)
                    min_dim = min(w_px, h_px)
                    if min_dim <= 0.5 * max_dim:
                        continue
                    dim = np.sqrt(max_dim**2 + min_dim**2) / np.sqrt(2)
                    dims.append(dim * mu if calibrated else dim / np.sqrt(W**2 + H**2))
    return dims


def draw_chart(ax, groups):
    """Plain histogram (density=False, normalised dims). groups: (label, folders, color, alpha)."""
    for label, folders, color, alpha in groups:
        dims = compute_dims(folders)
        ax.hist(dims, bins="auto", alpha=alpha, color=color,
                label=label, density=False, edgecolor="none")

    ax.set_xlabel("GUV size (normalised to image diagonal)", fontsize=FS_LABEL)
    ax.set_ylabel("Count", fontsize=FS_LABEL)
    ax.tick_params(labelsize=FS_TICK)
    ax.legend(fontsize=FS_LEGEND)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle=":", linewidth=0.8, color="#bbbbbb", zorder=0)
    ax.set_axisbelow(True)
    return ax


def draw_chart_with_fit(ax, groups):
    """Calibrated histogram (density=True) + log-normal fit curves. groups: (label, folders, color, alpha)."""
    fit_lines = []
    x_max = 0

    for label, folders, color, alpha in groups:
        dims = np.array(compute_dims(folders, calibrated=True))
        if len(dims) == 0:
            continue
        x_max = max(x_max, dims.max())
        ax.hist(dims, bins="auto", alpha=alpha, color=color,
                density=True, edgecolor="none")
        try:
            shape, loc, scale = lognorm.fit(dims, floc=0)
            mu_ln    = float(np.log(scale))
            sigma_ln = float(shape)
        except Exception:
            shape = loc = scale = None
            mu_ln = sigma_ln = float("nan")
        fit_lines.append((label, color, shape, loc, scale, mu_ln, sigma_ln))

    x = np.linspace(0, x_max * 1.05, 1000)
    for label, color, shape, loc, scale, mu_ln, sigma_ln in fit_lines:
        if shape is not None:
            ax.plot(x, lognorm.pdf(x, shape, loc=loc, scale=scale),
                    color=color, linewidth=2, linestyle="-",
                    label=f"{label}:  µ={mu_ln:.2f}, σ={sigma_ln:.2f}")

    ax.set_xlabel("GUV size (µm)", fontsize=FS_LABEL)
    ax.set_ylabel("Density", fontsize=FS_LABEL)
    ax.tick_params(labelsize=FS_TICK)
    ax.legend(fontsize=FS_LEGEND)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle=":", linewidth=0.8, color="#bbbbbb", zorder=0)
    ax.set_axisbelow(True)
    return ax


def save_fig(fig, stem):
    for ext, kw in [(".png", {"dpi": 300}), (".pdf", {"dpi": 300})]:
        p = pathlib.Path(__file__).parent / (stem + ext)
        fig.savefig(p, bbox_inches="tight", **kw)
        print(f"Saved: {p}")


def make_chart(groups, stem):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    draw_chart(ax, groups)
    plt.tight_layout()
    save_fig(fig, stem)
    plt.close(fig)


def make_chart_with_fit(groups, stem):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    draw_chart_with_fit(ax, groups)
    plt.tight_layout()
    save_fig(fig, stem)
    plt.close(fig)


# ── group definitions ──────────────────────────────────────────────────────

GROUPS_A = [
    ("Nikon train",  ["train"],                                                   "#2166ac", 0.4),
    ("Nikon val",    ["val"],                                                      "#4dac26", 0.5),
    ("Nikon test",   ["test"],                                                     "#1b7837", 0.5),
    ("Leica",        ["train_Leica_1", "val_Leica_1",
                      "train_Leica_2", "val_Leica_2"],                             "#7b2d8b", 0.6),
]

GROUPS_B = [
    ("Nikon train",  ["train"],                                    "#2166ac", 0.55),
    ("Nikon val",    ["val"],                                      "#4dac26", 0.55),
    ("Nikon test",   ["test"],                                     "#1b7837", 0.55),
    ("Leica train",  ["train_Leica_1", "train_Leica_2"],           "#7b2d8b", 0.55),
    ("Leica val",    ["val_Leica_1",   "val_Leica_2"],             "#c77ddb", 0.55),
]

GROUPS_C = [
    ("Nikon train",   ["train"],           "#2166ac", 0.55),
    ("Nikon val",     ["val"],             "#4dac26", 0.55),
    ("Nikon test",    ["test"],            "#1b7837", 0.55),
    ("Leica 1 train", ["train_Leica_1"],   "#7b2d8b", 0.55),
    ("Leica 1 val",   ["val_Leica_1"],     "#c77ddb", 0.55),
    ("Leica 2 train", ["train_Leica_2"],   "#5c1a6b", 0.55),
    ("Leica 2 val",   ["val_Leica_2"],     "#a64dcc", 0.55),
]

GROUPS_D = [
    ("Nikon train",  ["train"],                                                   "#2166ac", 0.3),
    ("Nikon val",    ["val"],                                                      "#4dac26", 0.3),
    ("Nikon test",   ["test"],                                                     "#1b7837", 0.3),
    ("Leica",        ["train_Leica_1", "val_Leica_1",
                      "train_Leica_2", "val_Leica_2"],                             "#7b2d8b", 0.3),
]

if __name__ == "__main__":
    out_dir = pathlib.Path(__file__).parent
    make_chart(GROUPS_A, "fig3a_bbox_sizes")
    make_chart(GROUPS_B, "fig3b_bbox_sizes")
    make_chart(GROUPS_C, "fig3c_bbox_sizes")
    make_chart_with_fit(GROUPS_D, "fig3d_bbox_sizes_um")
