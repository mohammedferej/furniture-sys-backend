from typing import Dict, List

COLORS       = ["#FF6B6B", "#6BCB77", "#4D96FF", "#FFD93D", "#A66DD4", "#00C9A7"]
CORNER_COLOR = "#888"

def generate_room_svg(
    room_shape: str,
    segments: Dict[str, List[int]],
    scale: int = 50,        # 1 m → 50 px
    rect_h: int = 40,
    corner_len: int = 1,
    margin: int = 30,
) -> str:
    def draw_rect(x, y, w, h, fill, text=""):
        rect = (
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{fill}" stroke="black" stroke-width="1" rx="4"/>'
        )
        if text:
            tx = x + w / 2
            ty = y + h / 2 + 4
            label = (
                f'<text x="{tx}" y="{ty}" text-anchor="middle" '
                f'font-size="12" fill="#fff" font-weight="bold">{text}</text>'
            )
            return rect + label
        return rect

    # ── Shape rules ───────────────────────────────
    corner_between = {"L": [0], "U": [0, 1], "Straight": []}.get(room_shape, [])

    # ── State tracking ────────────────────────────
    state = {
        "x": 200,
        "y": 200,
        "dir": 0,  # 0→right, 1→down, 2→left, 3→up
        "min_x": 200,
        "max_x": 200,
        "min_y": 200,
        "max_y": 200,
    }
    svg_elems = []

    def move(length_px):
        spacing = 4
        d = state["dir"]
        if d == 0: state["x"] += length_px + spacing
        elif d == 1: state["y"] += length_px + spacing
        elif d == 2: state["x"] -= length_px + spacing
        else: state["y"] -= length_px + spacing

    def add_seg(length_m, is_corner, side_i, seg_i):
        horiz = state["dir"] % 2 == 0
        px = length_m * scale
        w = px if horiz else rect_h
        h = rect_h if horiz else px
        dx = state["x"] - px if state["dir"] == 2 else state["x"]
        dy = state["y"] - px if state["dir"] == 3 else state["y"]

        state["min_x"] = min(state["min_x"], dx)
        state["min_y"] = min(state["min_y"], dy)
        state["max_x"] = max(state["max_x"], dx + w)
        state["max_y"] = max(state["max_y"], dy + h)

        color = CORNER_COLOR if is_corner else COLORS[(side_i + seg_i) % len(COLORS)]
        label = "" if is_corner else f"{length_m}m"
        svg_elems.append(draw_rect(dx, dy, w, h, color, label))

    def add_corner(side_i, seg_i):
        px = corner_len * scale

        # 1st leg (same direction)
        horiz = state["dir"] % 2 == 0
        w1, h1 = (px, rect_h) if horiz else (rect_h, px)
        dx1 = state["x"] - px if state["dir"] == 2 else state["x"]
        dy1 = state["y"] - px if state["dir"] == 3 else state["y"]
        svg_elems.append(draw_rect(dx1, dy1, w1, h1, CORNER_COLOR))
        move(corner_len * scale)

        # turn direction (90° right)
        state["dir"] = (state["dir"] + 1) % 4

        # 2nd leg (new direction)
        horiz2 = state["dir"] % 2 == 0
        w2, h2 = (px, rect_h) if horiz2 else (rect_h, px)
        dx2 = state["x"] - px if state["dir"] == 2 else state["x"]
        dy2 = state["y"] - px if state["dir"] == 3 else state["y"]
        svg_elems.append(draw_rect(dx2, dy2, w2, h2, CORNER_COLOR))
        move(corner_len * scale)

    # ── Traverse room layout ──────────────────────
    side_keys = list(segments.keys())
    for side_i, key in enumerate(side_keys):
        segs = segments[key]

        if (side_i - 1) in corner_between:
            add_corner(side_i, -1)

        for seg_i, length in enumerate(segs):
            add_seg(length, False, side_i, seg_i)
            move(length * scale)

        if side_i in corner_between:
            add_corner(side_i, len(segs))

        if room_shape != "Straight":
            state["dir"] = (state["dir"] + 1) % 4

    # ── SVG wrap-up ───────────────────────────────
    width = state["max_x"] - state["min_x"] + 2 * margin
    height = state["max_y"] - state["min_y"] + 2 * margin
    view = f'{state["min_x"] - margin} {state["min_y"] - margin} {width} {height}'

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="{view}">\n'
        f'{"".join(svg_elems)}\n</svg>'
    )
