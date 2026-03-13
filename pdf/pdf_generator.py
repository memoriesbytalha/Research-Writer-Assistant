"""
pdf/pdf_generator.py  —  Professional Academic PDF Generator  v3
═══════════════════════════════════════════════════════════════════
Fixes vs the original:
  1. Cover page has NO page number or header/footer
  2. Bold-wrapped Roman-numeral headings (**III. Methodology**) → H1, not H2
  3. Image captions derived from the surrounding section heading
  4. Images inserted only at section boundaries (never mid-paragraph)
  5. Full-bleed navy cover with card metadata block
  6. Proper hanging-indent bullets (firstLineIndent trick)
  7. APA-style hanging-indent for References section
"""

import re
import requests
from io import BytesIO
from datetime import datetime

from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    NextPageTemplate, PageBreak,
    Paragraph, Spacer, HRFlowable, KeepTogether,
    Image as RLImage,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT

try:
    from my_decorators.decorators import step_logger
except ImportError:
    def step_logger(fn):
        return fn


# ═══ Geometry ═════════════════════════════════════════════════════════════════
PW, PH   = A4
M_LR     = 1.05 * inch
M_TOP    = 1.00 * inch
M_BOT    = 0.85 * inch
TEXT_W   = PW - 2 * M_LR
TEXT_H   = PH - M_TOP - M_BOT

# ═══ Palette ══════════════════════════════════════════════════════════════════
NAVY   = colors.HexColor("#0f1d3a")
BLUE   = colors.HexColor("#1e4db7")
ACCENT = colors.HexColor("#3a86ff")
GREY   = colors.HexColor("#4a5568")
LGREY  = colors.HexColor("#c8d3e0")
TEXT_C = colors.HexColor("#1a202c")
MUTED  = colors.HexColor("#718096")
CARD   = colors.HexColor("#f4f7fb")
WHITE  = colors.white


# ═══ Styles ═══════════════════════════════════════════════════════════════════
def _make_styles() -> dict:
    HB  = "Helvetica-Bold"
    H   = "Helvetica"
    HI  = "Helvetica-Oblique"
    HBI = "Helvetica-BoldOblique"
    return {
        "h1": ParagraphStyle("h1",
            fontName=HB, fontSize=14, leading=19, textColor=NAVY,
            spaceBefore=20, spaceAfter=4, keepWithNext=1),

        "h2": ParagraphStyle("h2",
            fontName=HB, fontSize=11.5, leading=16, textColor=BLUE,
            spaceBefore=14, spaceAfter=4, keepWithNext=1),

        "h3": ParagraphStyle("h3",
            fontName=HBI, fontSize=10.5, leading=14, textColor=GREY,
            spaceBefore=10, spaceAfter=3, keepWithNext=1),

        "body": ParagraphStyle("body",
            fontName=H, fontSize=10.5, leading=16,
            alignment=TA_JUSTIFY, textColor=TEXT_C, spaceAfter=7),

        # Hanging-indent bullet: text wraps indented, bullet pulled left
        "bullet": ParagraphStyle("bullet",
            fontName=H, fontSize=10.5, leading=15, textColor=TEXT_C,
            leftIndent=20, firstLineIndent=-13, spaceAfter=4),

        # APA-style hanging indent for references
        "ref": ParagraphStyle("ref",
            fontName=H, fontSize=10, leading=15, textColor=TEXT_C,
            leftIndent=22, firstLineIndent=-22,
            spaceAfter=8, alignment=TA_LEFT),

        "caption": ParagraphStyle("caption",
            fontName=HI, fontSize=9, leading=12, textColor=MUTED,
            alignment=TA_CENTER, spaceBefore=3, spaceAfter=12),
    }


# ═══ Page decorators ══════════════════════════════════════════════════════════
def _cover_draw(canv, doc):
    """Full-bleed cover — drawn entirely via canvas, no platypus elements."""
    w, h = PW, PH
    query    = doc._cover_query
    date_str = doc._cover_date

    # ── Navy hero block (top 44 %) ───────────────────────────────────────────
    hero_h = h * 0.44
    canv.setFillColor(NAVY)
    canv.rect(0, h - hero_h, w, hero_h, stroke=0, fill=1)

    # Accent stripe at bottom of hero
    canv.setFillColor(ACCENT)
    canv.rect(0, h - hero_h, w, 5, stroke=0, fill=1)

    # Title — word-wrapped, white, centered vertically in hero
    _canvas_wrapped(canv, query,
                    cx=w / 2, baseline=h - hero_h * 0.40,
                    max_w=w - 2.6*inch,
                    font="Helvetica-Bold", size=28,
                    fill=WHITE, line_h=36)

    # Thin divider rule inside hero
    mid = w / 2
    canv.setStrokeColor(ACCENT)
    canv.setLineWidth(1.2)
    canv.line(mid - 1.5*inch, h - hero_h * 0.72,
              mid + 1.5*inch, h - hero_h * 0.72)

    # Subtitle inside hero
    canv.setFillColor(colors.HexColor("#a0aec0"))
    canv.setFont("Helvetica-Oblique", 12)
    canv.drawCentredString(mid, h - hero_h * 0.82, "AI-Powered Research Report")

    # ── Metadata card (white area below hero) ────────────────────────────────
    card_h = 1.30 * inch
    card_y = h - hero_h - 1.10*inch - card_h
    canv.setFillColor(CARD)
    canv.roundRect(M_LR, card_y, w - 2*M_LR, card_h, 6, stroke=0, fill=1)
    canv.setStrokeColor(LGREY)
    canv.setLineWidth(0.7)
    canv.roundRect(M_LR, card_y, w - 2*M_LR, card_h, 6, stroke=1, fill=0)

    lx     = M_LR + 0.26*inch
    label_x = lx
    value_x = lx + 1.30*inch
    ly      = card_y + card_h - 0.40*inch
    rows = [
        ("GENERATED",   date_str),
        ("TYPE",        "Academic Research Paper"),
        ("ENGINE",      "Groq LLaMA 3.3 · Tavily Search"),
    ]
    for label, val in rows:
        canv.setFont("Helvetica-Bold", 8.5)
        canv.setFillColor(GREY)
        canv.drawString(label_x, ly, label)
        canv.setFont("Helvetica", 9.5)
        canv.setFillColor(TEXT_C)
        canv.drawString(value_x, ly, val)
        ly -= 0.29*inch

    # ── Footer bar ────────────────────────────────────────────────────────────
    canv.setFillColor(NAVY)
    canv.rect(0, 0, w, 0.30*inch, stroke=0, fill=1)
    canv.setFillColor(colors.HexColor("#6384b8"))
    canv.setFont("Helvetica", 7.5)
    canv.drawCentredString(w / 2, 0.09*inch, "Generated by Research Writer Assistant")


def _canvas_wrapped(canv, text, cx, baseline, max_w, font, size, fill, line_h):
    """Naive word-wrap for canvas drawing (no XML support needed)."""
    canv.setFont(font, size)
    canv.setFillColor(fill)
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        if canv.stringWidth(test, font, size) <= max_w:
            cur.append(w)
        else:
            if cur: lines.append(" ".join(cur))
            cur = [w]
    if cur: lines.append(" ".join(cur))

    total_h = (len(lines) - 1) * line_h
    y = baseline + total_h / 2
    for line in lines:
        canv.drawCentredString(cx, y, line)
        y -= line_h


def _body_draw(canv, doc):
    """Header and footer for all body pages (page 2+)."""
    w, h = PW, PH
    title = doc._cover_query

    # Header rule + text
    canv.setStrokeColor(LGREY)
    canv.setLineWidth(0.5)
    canv.line(M_LR, h - 0.62*inch, w - M_LR, h - 0.62*inch)
    canv.setFont("Helvetica-Oblique", 8.5)
    canv.setFillColor(MUTED)
    short = (title[:60] + "…") if len(title) > 60 else title
    canv.drawString(M_LR, h - 0.50*inch, short)
    canv.drawRightString(w - M_LR, h - 0.50*inch, "Research Report")

    # Footer rule + page number
    canv.setStrokeColor(LGREY)
    canv.setLineWidth(0.5)
    canv.line(M_LR, 0.60*inch, w - M_LR, 0.60*inch)
    canv.setFont("Helvetica", 8.5)
    canv.setFillColor(MUTED)
    canv.drawCentredString(w / 2, 0.40*inch, f"— {doc.page - 1} —")


# ═══ Text classification ══════════════════════════════════════════════════════
_ROMAN = re.compile(
    r"^(XIV|XIII|XII|XI|IX|VIII|VII|VI|IV|III|II|I|X{1,3}|V)\.\s+\S",
    re.IGNORECASE,
)
_NUM_H     = re.compile(r"^\d{1,2}\.\s+[A-Z]")
_HASH1     = re.compile(r"^#\s+(.+)")
_HASH2     = re.compile(r"^##\s+(.+)")
_HASH3     = re.compile(r"^###\s+(.+)")
_BULLET_RE = re.compile(r"^[\*\-•]\s+(.+)")
_BOLD_ONLY = re.compile(r"^\*\*(.+?)\*\*[:\s]*$")


def _strip_md_bold(s: str) -> str:
    m = re.match(r"^\*\*(.+?)\*\*$", s.strip())
    return m.group(1).strip() if m else s.strip()


def _xml_escape(text: str) -> str:
    """Escape & then convert **bold** / *italic* to RL XML tags."""
    text = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#\d+;)", "&amp;", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__",     r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*",     r"<i>\1</i>", text)
    return text.strip()


def _classify(raw: str):
    """Return (kind, plain_text) for one raw line."""
    s = raw.strip()
    if not s:
        return "blank", ""

    # Markdown headings
    for pat, kind in [(_HASH1, "h1"), (_HASH2, "h2"), (_HASH3, "h3")]:
        m = pat.match(s)
        if m:
            return kind, m.group(1)

    # Strip possible bold wrapper, then test for Roman / numeric heading
    inner = _strip_md_bold(s)
    if _ROMAN.match(inner):
        text = re.sub(r"^[IVXLCivxlc]+\.\s+", "", inner)
        return "h1", text
    if _NUM_H.match(inner):
        text = re.sub(r"^\d+\.\s+", "", inner)
        return "h1", text

    # Bold-only → H2
    m = _BOLD_ONLY.match(s)
    if m:
        return "h2", m.group(1)

    # Bullet
    m = _BULLET_RE.match(s)
    if m:
        return "bullet", m.group(1)

    # Numbered list item (single digit at line start)
    m = re.match(r"^\d+\.\s+(.+)", s)
    if m:
        return "bullet", m.group(1)

    return "body", s


# ═══ Parser ════════════════════════════════════════════════════════════════════
def _parse_text(text: str, S: dict) -> list[tuple[str, object]]:
    """
    Convert raw LLM text into a list of (kind, flowable) tuples.
    kind ∈ {'h1', 'h2', 'h3', 'rule', 'bullet', 'body'}
    """
    result     = []
    in_refs    = False

    for raw in text.split("\n"):
        kind, content = _classify(raw)

        if kind == "blank":
            continue

        if kind in ("h1", "h2") and re.search(r"refer", content, re.I):
            in_refs = True

        if kind == "h1":
            result.append(("h1",  Paragraph(_xml_escape(content), S["h1"])))
            result.append(("rule", HRFlowable(
                width="100%", thickness=1.2, color=ACCENT, spaceAfter=5)))

        elif kind == "h2":
            result.append(("h2", Paragraph(_xml_escape(content), S["h2"])))

        elif kind == "h3":
            result.append(("h3", Paragraph(_xml_escape(content), S["h3"])))

        elif kind == "bullet":
            # \u2002 = en-space after bullet for clean gap
            result.append(("bullet",
                Paragraph(f"•\u2002{_xml_escape(content)}", S["bullet"])))

        else:
            style = S["ref"] if in_refs else S["body"]
            result.append(("body", Paragraph(_xml_escape(content), style)))

    return result


# ═══ Image helpers ════════════════════════════════════════════════════════════
_UA = {"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"}


def _fetch_image(url: str, max_w: float, max_h: float):
    if not url:
        return None
    try:
        r = requests.get(url, timeout=14, headers=_UA)
        r.raise_for_status()
        img = RLImage(BytesIO(r.content))
        iw, ih = img.imageWidth, img.imageHeight
        if iw <= 0 or ih <= 0:
            return None
        scale = min(max_w / iw, max_h / ih, 1.0)
        img.drawWidth  = iw * scale
        img.drawHeight = ih * scale
        img.hAlign = "CENTER"
        return img
    except Exception as e:
        print(f"[PDF] Image download failed ({str(url)[:60]}): {e}")
        return None


def _image_block(img, caption: str, S: dict) -> KeepTogether:
    return KeepTogether([
        Spacer(1, 8),
        img,
        Paragraph(caption, S["caption"]),
        Spacer(1, 8),
    ])


def _section_name(parsed: list, before_index: int) -> str:
    """Return the text of the last H1 seen before `before_index`."""
    for i in range(before_index - 1, -1, -1):
        kind, fl = parsed[i]
        if kind == "h1":
            try:
                # Paragraph stores its source text in .text after init
                txt = getattr(fl, "_text", None) or fl.text
                # Strip XML tags for a clean caption
                return re.sub(r"<[^>]+>", "", txt).strip()
            except Exception:
                return ""
    return ""


# ═══ Main generator ════════════════════════════════════════════════════════════
@step_logger
def generate_pdf(state: dict) -> dict:
    query    = state.get("query", "Research Report")
    sections = state.get("sections", [])
    img_urls = state.get("images", [])
    pdf_path = "research_paper.pdf"
    S        = _make_styles()

    # ── Parse body ────────────────────────────────────────────────────────────
    parsed: list[tuple[str, object]] = []
    for sec in sections:
        parsed.extend(_parse_text(sec, S))

    # ── Section boundaries (H1 positions) ────────────────────────────────────
    h1_idx = [i for i, (k, _) in enumerate(parsed) if k == "h1"]

    # ── Download images ───────────────────────────────────────────────────────
    img_max_w = TEXT_W * 0.82
    img_max_h = 2.70 * inch
    downloaded = []
    for url in img_urls:
        img = _fetch_image(url, img_max_w, img_max_h)
        if img:
            downloaded.append(img)

    # ── Schedule image insertion points ──────────────────────────────────────
    # Images go *just before* an H1 heading (= end of the prior section),
    # distributed evenly across sections.  Never mid-paragraph.
    inserts: dict[int, list] = {}   # parsed-list index → [image block, ...]

    if downloaded and h1_idx:
        # Candidate positions: just before each H1 after the first
        candidates = list(h1_idx[1:]) + [len(parsed)]   # last slot = end of doc
        n          = len(downloaded)
        step       = max(1, len(candidates) // n)
        chosen     = [candidates[min(i * step, len(candidates) - 1)]
                      for i in range(n)]

        for fig_num, (img, pos) in enumerate(zip(downloaded, chosen), 1):
            sec_name = _section_name(parsed, pos)
            caption  = f"Figure {fig_num}: {sec_name}" if sec_name else \
                       f"Figure {fig_num}: {query}"
            blk = _image_block(img, caption, S)
            inserts.setdefault(pos, []).append(blk)

    # ── Assemble body flowables with images injected ──────────────────────────
    body: list = []
    for i, (kind, fl) in enumerate(parsed):
        for blk in inserts.get(i, []):
            body.append(blk)
        body.append(fl)
    for blk in inserts.get(len(parsed), []):
        body.append(blk)

    # ── Build document ────────────────────────────────────────────────────────
    date_str = datetime.now().strftime("%B %d, %Y")

    doc = BaseDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=M_LR, rightMargin=M_LR,
        topMargin=M_TOP, bottomMargin=M_BOT,
        title=query,
        author="Research Writer Assistant",
    )
    # Attach metadata needed by page callbacks
    doc._cover_query = query
    doc._cover_date  = date_str

    cover_frame = Frame(0, 0, PW, PH, id="cover",
                        leftPadding=0, rightPadding=0,
                        topPadding=0, bottomPadding=0)
    body_frame  = Frame(M_LR, M_BOT, TEXT_W, TEXT_H, id="body")

    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=_cover_draw),
        PageTemplate(id="main",  frames=[body_frame],  onPage=_body_draw),
    ])

    story = [
        # Page 1: cover (uses cover frame — but we draw everything via canvas,
        # so we just need a dummy spacer that fills the frame)
        Spacer(PW, PH),
        # Switch to body template, start new page
        NextPageTemplate("main"),
        PageBreak(),
        # Actual content
        *body,
    ]

    doc.build(story)
    state["pdf_path"] = pdf_path
    return state