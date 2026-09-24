"""Generate architecture/architecture.svg without third-party packages."""
from pathlib import Path
from xml.sax.saxutils import escape

OUTPUT = Path(__file__).resolve().parent / "architecture.svg"
W, H = 1600, 1180

BG = "#F7F8FA"
INK = "#182230"
MUTED = "#52606D"
BORDER = "#C8D0D9"
ORANGE = "#FF9900"
DARK = "#232F3E"
BLUE = "#EAF3FF"
PURPLE = "#F3ECFF"
GREEN = "#EAF8EF"
AMBER = "#FFF4D6"
RED = "#FDECEC"
WHITE = "#FFFFFF"
LINE = "#65758B"


def text(x, y, value, size=16, weight=400, fill=INK, anchor="start"):
    return (
        f'<text x="{x}" y="{y}" '
        'font-family="Inter,Segoe UI,Arial,sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}">{escape(value)}</text>'
    )


def multi(x, y, lines, size=13.5, fill=MUTED):
    output = [
        f'<text x="{x}" y="{y}" '
        'font-family="Inter,Segoe UI,Arial,sans-serif" '
        f'font-size="{size}" fill="{fill}">'
    ]
    for index, value in enumerate(lines):
        output.append(
            f'<tspan x="{x}" dy="{0 if index == 0 else 21}">'
            f'{escape(value)}</tspan>'
        )
    output.append("</text>")
    return "".join(output)


def box(x, y, w, h, title, lines=(), fill=WHITE, accent=ORANGE):
    return "".join(
        [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" '
            f'fill="{fill}" stroke="{BORDER}" stroke-width="1.5"/>',
            f'<rect x="{x}" y="{y}" width="7" height="{h}" rx="3.5" '
            f'fill="{accent}"/>',
            text(x + 24, y + 32, title, 17, 700),
            multi(x + 24, y + 59, lines) if lines else "",
        ]
    )


def section(x, y, w, h, label):
    return "".join(
        [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" '
            f'fill="none" stroke="{BORDER}" stroke-width="1.4" '
            'stroke-dasharray="7 6"/>',
            text(x + 18, y + 28, label.upper(), 12, 700, MUTED),
        ]
    )


def arrow(x1, y1, x2, y2, label="", dashed=False, label_offset=0):
    dash = ' stroke-dasharray="7 6"' if dashed else ""
    output = [
        f'<path d="M {x1} {y1} L {x2} {y2}" fill="none" '
        f'stroke="{LINE}" stroke-width="2.2"{dash} '
        'marker-end="url(#arrowhead)"/>'
    ]
    if label:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2 + label_offset
        width = max(82, len(label) * 7.2)
        output.extend(
            [
                f'<rect x="{mx - width / 2}" y="{my - 13}" '
                f'width="{width}" height="25" rx="12" fill="{BG}"/>',
                text(mx, my + 5, label, 12, 600, MUTED, "middle"),
            ]
        )
    return "".join(output)


def pill(x, y, label, fill=DARK):
    width = len(label) * 7.4 + 28
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="29" '
        f'rx="14.5" fill="{fill}"/>'
        + text(x + width / 2, y + 20, label, 12, 700, WHITE, "middle")
    )


s = []
s.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}">'
)
s.append(
    '<defs>'
    '<marker id="arrowhead" markerWidth="10" markerHeight="10" '
    'refX="8" refY="3" orient="auto">'
    f'<path d="M0,0 L0,6 L9,3 z" fill="{LINE}"/>'
    '</marker>'
    '</defs>'
)
s.append(f'<rect width="100%" height="100%" fill="{BG}"/>')

s += [
    text(70, 65, "SAP GenAI Incident Assistant", 34, 750, DARK),
    text(
        70,
        96,
        "Grounded SAP MM support analysis · AWS POC architecture",
        16,
        400,
        MUTED,
    ),
    pill(1320, 52, "READ-ONLY SAP"),
    pill(1320, 88, "HITL ENFORCED", ORANGE),

    section(60, 135, 1480, 115, "Experience"),
    box(100, 170, 270, 58, "SAP Support User", (), WHITE, DARK),
    box(
        640,
        160,
        320,
        76,
        "Streamlit UI · Amazon EC2",
        ("Ticket input · Evidence · Confidence",),
        BLUE,
        ORANGE,
    ),
    box(1180, 170, 290, 58, "SAP Specialist", (), WHITE, DARK),

    section(60, 285, 1480, 250, "Application & Control Layer · Amazon EC2"),
    box(
        85,
        340,
        215,
        135,
        "Scope Guard",
        ("SAP MM boundary", "Out-of-scope routing", "Missing-context control"),
        BLUE,
        "#3B82F6",
    ),
    box(
        325,
        340,
        215,
        135,
        "Classification",
        ("Process + intent", "PR · PO · GR · MIRO", "Authorization · MM/FI"),
        BLUE,
        "#3B82F6",
    ),
    box(
        565,
        340,
        215,
        135,
        "Evidence Gate",
        ("Score threshold", "Sufficiency", "Conflict detection"),
        AMBER,
        ORANGE,
    ),
    box(
        805,
        340,
        215,
        135,
        "Confidence",
        ("Retrieval 35%", "Completeness 20%", "Coverage 30% · Agreement 15%"),
        PURPLE,
        "#8B5CF6",
    ),
    box(
        1045,
        340,
        215,
        135,
        "Policy Engine",
        ("AI Scope", "HITL Policy", "Escalation Rules"),
        GREEN,
        "#2E8B57",
    ),
    box(
        1285,
        340,
        215,
        135,
        "HITL Gate",
        ("Action risk", "Authorization cases", "No autonomous writes"),
        RED,
        "#D14343",
    ),

    section(60, 575, 950, 350, "GenAI & Grounding"),
    box(
        90,
        635,
        250,
        165,
        "Amazon Bedrock",
        (
            "Claude Sonnet 4.6",
            "Converse API",
            "Grounded reasoning",
            "Structured JSON",
        ),
        PURPLE,
        "#8B5CF6",
    ),
    box(
        380,
        635,
        250,
        165,
        "Titan Embeddings V2",
        (
            "amazon.titan-embed-text-v2:0",
            "1024 dimensions",
            "Query + corpus embeddings",
            "Normalized vectors",
        ),
        PURPLE,
        "#8B5CF6",
    ),
    box(
        670,
        635,
        250,
        165,
        "FAISS · Amazon EC2",
        (
            "Local vector index",
            "Ranked SAP MM evidence",
            "Inner-product similarity",
            "Grounding threshold 0.50",
        ),
        GREEN,
        "#2E8B57",
    ),
    box(
        380,
        835,
        250,
        62,
        "Amazon S3",
        ("Curated SAP MM source documents",),
        GREEN,
        "#2E8B57",
    ),

    section(1050, 575, 490, 350, "Enterprise Data Boundary"),
    box(
        1090,
        635,
        200,
        165,
        "SAP Client",
        (
            "Normalized contract",
            "Read operations only",
            "Case-specific state",
            "Mutation denied",
        ),
        BLUE,
        "#3B82F6",
    ),
    box(
        1335,
        635,
        165,
        165,
        "SAP Mock",
        ("PO · PR · GR", "Invoice · Vendor", "Users · Release", "Read-only data"),
        WHITE,
        DARK,
    ),

    section(60, 965, 1480, 130, "Audit & Traceability"),
    box(
        430,
        1000,
        740,
        70,
        "Amazon DynamoDB · Audit Records",
        (
            "Request · Response · Sources · Model · Tokens · Latency · Confidence · Evidence Gate · HITL",
        ),
        WHITE,
        ORANGE,
    ),

    arrow(370, 199, 640, 199, "submits ticket"),
    arrow(960, 199, 1180, 199, "returns analysis"),
    arrow(800, 236, 192, 340, "request"),
    arrow(300, 407, 325, 407, "in scope"),
    arrow(540, 407, 565, 407, "classify"),
    arrow(780, 407, 805, 407, "validate"),
    arrow(1020, 407, 1045, 407, "score"),
    arrow(1260, 407, 1285, 407, "policy"),

    arrow(432, 475, 505, 635, "embed query"),
    arrow(630, 717, 670, 717, "vector"),
    arrow(795, 635, 505, 475, "ranked evidence"),
    arrow(505, 800, 505, 835, "source docs"),
    arrow(505, 835, 505, 800, "build index", dashed=True, label_offset=18),

    arrow(672, 475, 215, 635, "grounded prompt"),
    arrow(340, 717, 565, 475, "analysis"),

    arrow(432, 475, 1190, 635, "read context"),
    arrow(1290, 717, 1335, 717, "queries"),
    arrow(1392, 340, 1325, 228, "escalates"),

    arrow(800, 535, 800, 1000, "audit", True, 90),

    text(
        800,
        1140,
        "AI analyzes and recommends · Authorized humans retain control of SAP state-changing actions",
        15,
        650,
        DARK,
        "middle",
    ),
]

s.append("</svg>")
OUTPUT.write_text("".join(s), encoding="utf-8")
print(f"Generated: {OUTPUT}")