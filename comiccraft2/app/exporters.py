from pathlib import Path
from datetime import datetime
from fpdf import FPDF

OUT = Path("static/exports")
OUT.mkdir(parents=True, exist_ok=True)


def safe(text):
    """Convert text to PDF-safe Latin-1 text."""
    text = str(text or "")

    # Replace problematic Unicode characters
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2022": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode("latin-1", "replace").decode("latin-1")


def clean_text(text):
    """Prevent FPDF errors caused by extremely long words."""
    text = safe(text)

    words = text.split()
    fixed_words = []

    for word in words:
        # Break extremely long words into smaller pieces
        if len(word) > 40:
            chunks = [
                word[i:i + 35]
                for i in range(0, len(word), 35)
            ]
            fixed_words.append(" ".join(chunks))
        else:
            fixed_words.append(word)

    return " ".join(fixed_words)


def write_text(pdf, text, font_style="", font_size=11, height=6):
    """Safely write wrapped text to the PDF."""
    text = clean_text(text)

    if not text.strip():
        return

    pdf.set_font("Helvetica", font_style, font_size)

    # Explicit width prevents FPDF horizontal-space errors
    pdf.multi_cell(
        w=180,
        h=height,
        text=text,
        align="L"
    )


def save_pdf(layout):
    filename = f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = OUT / filename

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()

        # Title
        pdf.set_xy(15, 15)
        write_text(
            pdf,
            panel.get("title", "Comic Panel"),
            font_style="B",
            font_size=18,
            height=9
        )

        # Image
        image_path = panel.get("image")

        if image_path and Path(image_path).exists():
            try:
                pdf.image(
                    image_path,
                    x=15,
                    y=38,
                    w=180
                )
            except Exception:
                pass

        # Put text in a safe area near bottom
        pdf.set_xy(15, 225)

        write_text(
            pdf,
            panel.get("caption", ""),
            font_style="B",
            font_size=12,
            height=7
        )

        write_text(
            pdf,
            panel.get("narration", ""),
            font_style="",
            font_size=10,
            height=6
        )

        dialogue = panel.get("dialogue")

        if dialogue:
            pdf.ln(2)

            write_text(
                pdf,
                dialogue,
                font_style="I",
                font_size=10,
                height=6
            )

    pdf.output(str(path))

    return filename