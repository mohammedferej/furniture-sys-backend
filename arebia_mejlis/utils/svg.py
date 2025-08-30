import svgwrite
from pathlib import Path
from django.conf import settings

SCALE = 100  # 1 m = 100 SVG units

def build_points(shape: str, sides: list[int]):
    pts = [(0, 0)]
    if shape == "Straight":
        pts.append((sides[0] * SCALE, 0))
    elif shape == "L":
        a, b = sides
        pts += [
            (a * SCALE, 0),
            (a * SCALE, SCALE),
            (a * SCALE, b * SCALE + SCALE),
        ]
    elif shape == "U":
        a, b, c = sides
        pts += [
            (a * SCALE, 0),
            (a * SCALE, SCALE),
            (a * SCALE, b * SCALE + SCALE),
            (a * SCALE - c * SCALE, b * SCALE + SCALE),
            (a * SCALE - c * SCALE, SCALE),
        ]
    return pts

def create_room_svg(room) -> Path:
    pts = build_points(room.shape, room.sides)
    dwg = svgwrite.Drawing(size=("1000mm", "1000mm"))
    dwg.add(dwg.polyline(points=pts, stroke="black",
                         fill="none", stroke_width=2))
    # output path
    out_path = Path(settings.MEDIA_ROOT) / f"room_detail/{room.id}.svg"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    dwg.saveas(out_path)
    return out_path
