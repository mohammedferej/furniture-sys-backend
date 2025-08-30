

import svgwrite
from cairosvg import svg2pdf
from io import BytesIO

# Example colors and corner color
COLORS = ["#FF6B6B", "#6BCB77", "#4D96FF", "#FFD93D", "#A66DD4", "#00C9A7"]
CORNER_COLOR = "#888"
RECT_HEIGHT = 40
SPACING = 4
SCALE = 50
CORNER_LENGTH = 1

def generate_room_svg(room_shape, segments: dict, scale=SCALE):
    dwg = svgwrite.Drawing(size=("100%", "100%"), profile='tiny')

    x, y = 200, 200
    dir = 0  # 0: right, 1: down, 2: left, 3: up

    min_x = max_x = x
    min_y = max_y = y

    def move(length):
        nonlocal x, y
        if dir == 0: x += (length * scale + SPACING)
        elif dir == 1: y += (length * scale + SPACING)
        elif dir == 2: x -= (length * scale + SPACING)
        elif dir == 3: y -= (length * scale + SPACING)

    def draw_segment(length, is_corner=False, side_idx=None, seg_idx=None):
        nonlocal x, y, min_x, min_y, max_x, max_y
        horiz = dir % 2 == 0
        px = length * scale
        w = px if horiz else RECT_HEIGHT
        h = RECT_HEIGHT if horiz else px
        draw_x = x - px if dir == 2 else x
        draw_y = y - px if dir == 3 else y

        min_x, max_x = min(min_x, draw_x), max(max_x, draw_x + w)
        min_y, max_y = min(min_y, draw_y), max(max_y, draw_y + h)

        color = CORNER_COLOR if is_corner else COLORS[(side_idx + seg_idx) % len(COLORS)]
        dwg.add(dwg.rect(insert=(draw_x, draw_y), size=(w, h), rx=4, fill=color, stroke='black'))
        dwg.add(dwg.text(f"{length}m", insert=(draw_x + w / 2, draw_y + h / 2 + 4),
                         text_anchor="middle", font_size=12, fill="white", font_weight="bold"))

    side_keys = list(segments.keys())
    corner_between = [0] if room_shape == "L" else [0, 1] if room_shape == "U" else []

    for side_idx, side_key in enumerate(side_keys):
        segs = segments.get(side_key, [])

        if (side_idx - 1) in corner_between:
            draw_segment(CORNER_LENGTH, is_corner=True)
            move(CORNER_LENGTH)

        for seg_idx, seg in enumerate(segs):
            draw_segment(seg, is_corner=False, side_idx=side_idx, seg_idx=seg_idx)
            move(seg)

        if side_idx in corner_between:
            draw_segment(CORNER_LENGTH, is_corner=True)
            move(CORNER_LENGTH)

        if room_shape != "Straight":
            dir = (dir + 1) % 4

    dwg.viewbox(min_x - 30, min_y - 30, (max_x - min_x) + 60, (max_y - min_y) + 60)
    return dwg.tostring()
