from django.core.files import File
from django.conf import settings
from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from cairosvg import svg2png
import svgwrite



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


# --- PDF generator ---
def generate_order_pdf(order):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()

    # Header
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.5*inch, height=0.75*inch)
    else:
        logo = Paragraph("<b>Company Logo</b>", ParagraphStyle('logo', fontSize=16))
    company_info = Paragraph(
        "Your Company Name<br/>123 Main St, City<br/>Phone: XXX-XXX-XXXX<br/>Email: info@example.com",
        ParagraphStyle('company', fontSize=10, leading=12)
    )
    header_table = Table([[logo, company_info]], colWidths=[2*inch, 4*inch])
    story.append(header_table)
    story.append(Spacer(1, 12))

    # Order title
    story.append(Paragraph(f"<b>Order #{order.order_code}</b>", ParagraphStyle('title', fontSize=16, leading=20, spaceAfter=12)))

    # Customer info
    customer_table = Table([
        ["Customer:", order.customer.name],
        ["Phone:", order.customer.phone],
        ["Address:", order.customer.address]
    ], colWidths=[1.5*inch, 4*inch])
    customer_table.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 12))

    # Order info
    order_table = Table([
        ["Order Date:", order.receive_order_at.strftime("%d %b %Y")],
        ["Completion Date:", order.completed_order_at.strftime("%d %b %Y") if order.completed_order_at else "-"],
        ["Total Price:", f"${float(order.total_price):.2f}"],
        ["Remaining Payment:", f"${float(order.remaining_payment):.2f}"]
    ], colWidths=[1.5*inch, 4*inch])
    order_table.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    story.append(order_table)
    story.append(Spacer(1, 12))

    # Material info
    material = order.mejlis_materials.first()
    if material:
        material_table = Table([
            ["Type", material.material_type],
            ["Design", material.design_type],
            ["Room Size", f"{material.room_size} sqm"],
            ["Shape", material.room_shape.upper()],
            ["Price/Meter", f"${float(material.price_per_meter):.2f}"]
        ], colWidths=[2*inch, 4*inch])
        material_table.setStyle(TableStyle([
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        story.append(material_table)
        story.append(Spacer(1, 12))

        # Room diagram
        try:
            svg_content = generate_room_svg(
                material.room_shape,
                {s.side_name: s.values for s in material.segments.all()}
            )
            png_buffer = BytesIO()
            # High-resolution conversion
            svg2png(bytestring=svg_content.encode('utf-8'), write_to=png_buffer, output_width=1000, output_height=1000)
            png_buffer.seek(0)
            story.append(Image(png_buffer, width=5*inch, height=5*inch))
            story.append(Spacer(1, 12))
        except Exception:
            story.append(Paragraph("Room layout diagram not available", ParagraphStyle('body', fontSize=10)))

    # Footer
    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "Thank you for your business! | © 2025 Your Company | www.example.com",
        ParagraphStyle('footer', fontSize=9, alignment=1, textColor=colors.grey)
    ))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    filename = f"order_{order.order_code}.pdf"
    if order.document_path:
        if os.path.exists(order.document_path.path):
            os.remove(order.document_path.path)
    order.document_path.save(filename, File(buffer))
    return order.document_path.url
