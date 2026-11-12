"""Render out/eye_servo_housing.stl with the placed SG90 to out/preview.png (run the generator first)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT = Path(__file__).parent / "out"
VIEWS = [("front-right-top", 25, -60), ("back-left-top", 30, 130), ("from right (shaft side)", 0, 90), ("top", 90, -90)]


def add(ax, mesh, color, alpha):
    ax.add_collection3d(Poly3DCollection(mesh.triangles, facecolors=color, linewidths=0, alpha=alpha, shade=True))


housing = trimesh.load(OUT / "eye_servo_housing.stl")
servo = trimesh.load(OUT / "sg90_placed.stl")
both = trimesh.util.concatenate([housing, servo])
lo, hi = both.bounds
span = (hi - lo).max() / 2
mid = (hi + lo) / 2

fig = plt.figure(figsize=(12, 10))
for i, (title, elev, azim) in enumerate(VIEWS, 1):
    ax = fig.add_subplot(2, 2, i, projection="3d")
    add(ax, housing, "#e8e4d8", 1.0)
    add(ax, servo, "#3b6fd6", 0.55)
    for set_lim, m in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), mid):
        set_lim(m - span, m + span)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title)
    ax.set_xlabel("X front→back")
    ax.set_ylabel("Y left→right")
    ax.set_zlabel("Z")
fig.tight_layout()
fig.savefig(OUT / "preview.png", dpi=110)
print(f"Wrote {OUT / 'preview.png'}")
