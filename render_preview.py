"""Render the housing, placed SG90, and roller to out/preview.png (run the generator first)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.colors import to_rgba
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT = Path(__file__).parent / "out"
VIEWS = [("front-right-top", 25, -60), ("back-right-top", 25, 50), ("from the roller side", 90, -90), ("from back", 0, 0)]


def add(ax, parts):
    # One collection for everything so faces depth-sort together instead of per model
    tris = np.concatenate([m.triangles for m, _ in parts])
    colors = np.concatenate([np.tile(to_rgba(c), (len(m.faces), 1)) for m, c in parts])
    ax.add_collection3d(Poly3DCollection(tris, facecolors=colors, linewidths=0, shade=True))


housing = trimesh.load(OUT / "eye_servo_housing.stl")
servo = trimesh.load(OUT / "sg90_placed.stl")
roller = trimesh.load(OUT / "roller_placed.stl")
both = trimesh.util.concatenate([housing, servo, roller])
lo, hi = both.bounds
span = (hi - lo).max() / 2
mid = (hi + lo) / 2

fig = plt.figure(figsize=(12, 10))
for i, (title, elev, azim) in enumerate(VIEWS, 1):
    ax = fig.add_subplot(2, 2, i, projection="3d")
    add(ax, [(housing, "#e8e4d8"), (servo, "#3b6fd6"), (roller, "#d9c38f")])
    for set_lim, m in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), mid):
        set_lim(m - span, m + span)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title)
    ax.set_xlabel("X front→back")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
fig.tight_layout()
fig.savefig(OUT / "preview.png", dpi=110)
print(f"Wrote {OUT / 'preview.png'}")
