# from typing import Dict, List

# COLORS       = ["#FF6B6B", "#6BCB77", "#4D96FF", "#FFD93D", "#A66DD4", "#00C9A7"]
# CORNER_COLOR = "#888"

# def generate_room_svg(
#     room_shape: str,
#     segments: Dict[str, List[int]],
#     scale: int = 50,        # 1 m → 50 px
#     rect_h: int = 40,
#     corner_len: int = 1,
#     margin: int = 30,
# ) -> str:
#     def draw_rect(x, y, w, h, fill, text=""):
#         print("draw_rect", "x  :",x," y  :",y," w  +",w,"  h :",h,"  fill",fill)
#         rect = (
#             f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
#             f'fill="{fill}" stroke="black" stroke-width="1" rx="4"/>'
#         )
#         if text:
#             tx = x + w / 2
#             ty = y + h / 2 + 4
#             label = (
#                 f'<text x="{tx}" y="{ty}" text-anchor="middle" '
#                 f'font-size="12" fill="#fff" font-weight="bold">{text}</text>'
#             )
#             return rect + label
#         print("rect  "+rect)
#         return rect

#     # ── Room shape → corner logic ──────────────
#     corner_between = {"L": [0], "U": [0, 1], "Straight": []}.get(room_shape, [])

#     # ── Positioning state ──────────────────────
#     dir_ = 0
#     x = y = 200
#     min_x = max_x = x
#     min_y = max_y = y
#     svg_elems = []

#     def move_dir(dx, dy):
#         nonlocal x, y
#         print("move_dit  :",dx,"  ",dy)
#         x += dx
#         y += dy

#     def move(length_px):
#         print("move :",move)
#         spacing = 4
#         if dir_ == 0: move_dir(length_px + spacing, 0)
#         elif dir_ == 1: move_dir(0, length_px + spacing)
#         elif dir_ == 2: move_dir(-length_px - spacing, 0)
#         else: move_dir(0, -length_px - spacing)

#     def add_seg(length_m, is_corner, side_index, seg_index):
#         print("add_seg :",length_m)
#         horiz = dir_ % 2 == 0
#         print("horiz  ",horiz)
#         px  = length_m * scale
#         print("px :",px)
#         w   = px if horiz else rect_h
#         print("px :",w)
#         h   = rect_h if horiz else px
#         print("px :",h)
#         dx  = x - px if dir_ == 2 else x
#         print("px :",dx)
#         dy  = y - px if dir_ == 3 else y
#         print("px :",dy)

#         nonlocal min_x, min_y, max_x, max_y
#         min_x, min_y = min(min_x, dx), min(min_y, dy)
#         max_x, max_y = max(max_x, dx + w), max(max_y, dy + h)

#         print("min_x, min_y :",min_x,"  ",min_y)

#         color = CORNER_COLOR if is_corner else COLORS[(side_index + seg_index) % len(COLORS)]
#         print("color :"+color)
#         label = "" if is_corner else f"{length_m}m"
#         svg_elems.append(draw_rect(dx, dy, w, h, color, label))

#     def add_corner(side_index, seg_index):
#         print("add_corner", side_index,"   ",seg_index)
#         px = corner_len * scale
#         print("px :",px)
#         dx = dy = 0
#         if dir_ == 2: 
#             dx = -px
#             print("px :",px)
#         elif dir_ == 3: 
#             dy = -px
#             print("px :",px)
#         # Otherwise (right/down), dx and dy remain 0

#         svg_elems.append(draw_rect(x + dx, y + dy, px, px, CORNER_COLOR))
#         move(corner_len * scale)

#     # ── Iterate all sides ──────────────────────
#     side_keys = list(segments.keys())
#     print(side_keys)
#     for side_index, key in enumerate(side_keys):
#         segs = segments[key]
#         print("segs",segs)
#         print("side_index",side_index)
#         print("corner_between",corner_between)

#         # corner BEFORE this side
#         if (side_index - 1) in corner_between:
#             add_corner(side_index, -1)

#         # draw each segment
#         for seg_index, length in enumerate(segs):
#             print("seg_index :",seg_index,"  length :",length, " side_index :",side_index)
#             add_seg(length, False, side_index, seg_index)
#             move(length * scale)

#         # corner AFTER this side
#         if side_index in corner_between:
#             print("side_index",side_index)
#             add_corner(side_index, len(segs))


#         # rotate direction if shape needs turning
#         if room_shape != "Straight":
#             dir_ = (dir_ + 1) % 4

#     # ── SVG boundaries and wrap-up ─────────────
#     width  = max_x - min_x + 2 * margin
#     height = max_y - min_y + 2 * margin
#     view   = f"{min_x - margin} {min_y - margin} {width} {height}"

#     return (
#         '<?xml version="1.0" encoding="UTF-8"?>\n'
#         f'<svg xmlns="http://www.w3.org/2000/svg" '
#         f'width="{width}" height="{height}" viewBox="{view}">\n'
#         f'{"".join(svg_elems)}\n</svg>'
#     )


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
