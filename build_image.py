from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "entry.png"
HERO = ROOT / "assets" / "media-generation-news-hero-skyline-0-f21ba6bd-9313-424c-ae43-e6ef7d3f7cb3.png"

WIDTH = HEIGHT = 1024
MARGIN = 20
CONTENT_WIDTH = WIDTH - 2 * MARGIN
MAX_BYTES = 1024 * 1024

PAPER = "#f7f3ea"
CARD = "#fbf8f1"
INK = "#1a1a1a"
BODY = "#34312d"
MUTED = "#686157"
NAVY = "#1e3a5f"
GOLD = "#e5b13c"
RULE = "#cfc6b6"

FONT_DIR = Path("/usr/share/fonts/truetype")
SANS = FONT_DIR / "liberation" / "LiberationSans-Regular.ttf"
SANS_BOLD = FONT_DIR / "liberation" / "LiberationSans-Bold.ttf"
CONDENSED = FONT_DIR / "noto" / "NotoSans-Condensed.ttf"
CONDENSED_BOLD = FONT_DIR / "noto" / "NotoSans-CondensedBold.ttf"
EXTRA_CONDENSED = FONT_DIR / "noto" / "NotoSans-ExtraCondensed.ttf"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def width(text: str, face: ImageFont.FreeTypeFont, tracking: float = 0) -> float:
    return face.getlength(text) + max(0, len(text) - 1) * tracking


def draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    face: ImageFont.FreeTypeFont,
    fill: str,
    tracking: float = 0,
) -> None:
    x, y = xy
    if not tracking:
        draw.text((x, y), text, font=face, fill=fill)
        return
    for char in text:
        draw.text((x, y), char, font=face, fill=fill)
        x += face.getlength(char) + tracking


def wrap(text: str, face: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        if width(candidate, face) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_paragraph(
    text: str,
    path: Path,
    preferred: int,
    minimum: int,
    max_width: int,
    max_lines: int,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(preferred, minimum - 1, -1):
        face = font(path, size)
        lines = wrap(text, face, max_width)
        if len(lines) <= max_lines:
            return face, lines, max(17, round(size * 1.14))
    face = font(path, minimum)
    return face, wrap(text, face, max_width), max(17, round(minimum * 1.14))


def draw_rule(draw: ImageDraw.ImageDraw, y: int, color: str = RULE, thickness: int = 1) -> None:
    draw.rectangle((MARGIN, y, WIDTH - MARGIN, y + thickness - 1), fill=color)


def main() -> None:
    page = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(page)

    # Masthead
    draw.rectangle((0, 0, WIDTH, 126), fill=NAVY)
    draw.rectangle((0, 122, WIDTH, 126), fill=GOLD)
    masthead = font(SANS_BOLD, 64)
    date_face = font(SANS_BOLD, 27)
    title = "THE WORLD IN ONE DAY"
    date = "FRIDAY · 20 NOVEMBER 2026"
    draw_text(draw, ((WIDTH - width(title, masthead)) / 2, 20), title, masthead, "white")
    draw_text(draw, ((WIDTH - width(date, date_face)) / 2, 88), date, date_face, GOLD)

    # Lead banner
    hero_y, hero_h = 138, 218
    hero = ImageOps.fit(
        Image.open(HERO).convert("RGB"),
        (CONTENT_WIDTH, hero_h),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    page.paste(hero, (MARGIN, hero_y))
    draw.rectangle((MARGIN, hero_y, MARGIN + CONTENT_WIDTH - 1, hero_y + hero_h - 1), outline=NAVY, width=2)

    lead_face = font(SANS_BOLD, 52)
    lead = "PEACE DECLARED — THEN WAR"
    draw_text(draw, (MARGIN, 363), lead, lead_face, INK)

    summary_face = font(CONDENSED, 21)
    summary = [
        "Hours after Trump, Xi and Putin sign a joint peace declaration in Shenzhen, Russia launches",
        "a massive overnight missile and drone attack on Ukraine, killing at least five in Kyiv.",
    ]
    for index, line in enumerate(summary):
        draw_text(draw, (MARGIN, 423 + index * 26), line, summary_face, BODY)

    # Story grid
    stories = [
        {
            "kicker": "JUSTICE · THE HAGUE",
            "color": "#2d6b64",
            "headline": "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
            "summary": "The International Court of Justice rules Myanmar committed genocide against the Rohingya — the first such finding against a state.",
        },
        {
            "kicker": "ECONOMY · NEW YORK / TOKYO",
            "color": "#925d14",
            "headline": "AI'S BIG DAY, MARKETS' BAD DAY",
            "summary": "Anthropic debuts on Nasdaq, closing 17% above its offer price — the first purely AI company to go public — as AI-bubble fears sink Asian markets; the Nikkei falls 4.8%.",
        },
        {
            "kicker": "CONFLICT · RIYADH",
            "color": "#9f382c",
            "headline": "MISSILE HITS RIYADH TOWER",
            "summary": "A Houthi missile strikes Riyadh's financial district, damaging the Saudi sovereign wealth fund's tower.",
        },
        {
            "kicker": "TECH · CALIFORNIA",
            "color": "#315f86",
            "headline": "CALIFORNIA SUBPOENAS NVIDIA",
            "summary": "California's attorney general subpoenas Nvidia over whether advanced AI chips reached China.",
        },
    ]

    grid_y, gap, card_h = 486, 10, 194
    card_w = (CONTENT_WIDTH - gap) // 2
    for index, story in enumerate(stories):
        col, row = index % 2, index // 2
        x = MARGIN + col * (card_w + gap)
        y = grid_y + row * (card_h + gap)
        x2, y2 = x + card_w - 1, y + card_h - 1

        draw.rounded_rectangle((x, y, x2, y2), radius=3, fill=CARD, outline=RULE, width=1)
        draw.rectangle((x + 1, y + 1, x2 - 1, y + 6), fill=story["color"])
        draw.rounded_rectangle((x + 1, y + 1, x + 5, y + 6), radius=2, fill=story["color"])

        kicker_face = font(CONDENSED_BOLD, 14)
        draw_text(draw, (x + 18, y + 16), story["kicker"], kicker_face, story["color"], tracking=1.1)

        inner = card_w - 36
        headline_face, headline_lines, headline_line_h = fit_paragraph(
            story["headline"], CONDENSED_BOLD, 27, 23, inner, 2
        )
        headline_y = y + 39
        for line_index, line in enumerate(headline_lines):
            draw_text(draw, (x + 18, headline_y + line_index * headline_line_h), line, headline_face, INK)

        body_top = headline_y + len(headline_lines) * headline_line_h + 5
        body_face, body_lines, body_line_h = fit_paragraph(
            story["summary"], CONDENSED, 21, 18, inner, 3
        )
        for line_index, line in enumerate(body_lines):
            draw_text(draw, (x + 18, body_top + line_index * body_line_h), line, body_face, BODY)

    # Also today
    strip_y = 892
    draw_rule(draw, strip_y, NAVY, 2)
    label_face = font(CONDENSED_BOLD, 14)
    draw_text(draw, (MARGIN, strip_y + 10), "ALSO TODAY", label_face, NAVY, tracking=2.0)
    also_face = font(EXTRA_CONDENSED, 18)
    also = "UK pledges 1,000+ drones for Ukraine in a £260m package · Kenya discharges its last Ebola patient · US Senate rejects Iran war-powers resolution 51–48"
    draw_text(draw, (MARGIN, strip_y + 33), also, also_face, BODY)

    # Footer
    draw_rule(draw, 963, RULE, 1)
    footer_face = font(SANS, 13)
    footer = "Sources: CNN · BBC · One Turn · IANS — 20 Nov 2026 · Made by an AI agent for make.fun"
    draw_text(draw, ((WIDTH - width(footer, footer_face)) / 2, 973), footer, footer_face, MUTED)

    page.save(OUT, "PNG", optimize=True)
    if OUT.stat().st_size > MAX_BYTES:
        page.save(OUT, "JPEG", quality=88, optimize=True, progressive=False)

    with Image.open(OUT) as check:
        check.verify()
    with Image.open(OUT) as check:
        check.load()
        print(f"wrote {OUT} | {check.format} {check.width}x{check.height} | {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
