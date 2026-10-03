from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm


BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_FOLDER = BASE_DIR / "exports"

EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)


def save_pdf(comic: dict) -> str:

    filename = (
        "comic_"
        + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        + ".pdf"
    )

    pdf_path = EXPORT_FOLDER / filename

    styles = getSampleStyleSheet()

    document = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    content = []

    # Title
    content.append(
        Paragraph(
            str(comic.get("title", "ComicCraft Comic")),
            styles["Title"],
        )
    )

    content.append(Spacer(1, 10))

    # Basic information
    content.append(
        Paragraph(
            f"Style: {comic.get('style', '')}",
            styles["Normal"],
        )
    )

    content.append(
        Paragraph(
            f"Language: {comic.get('language', '')}",
            styles["Normal"],
        )
    )

    content.append(Spacer(1, 10))

    # Characters
    content.append(
        Paragraph(
            "<b>Characters</b>",
            styles["Heading2"],
        )
    )

    characters = comic.get("characters", [])

    for character in characters:
        content.append(
            Paragraph(
                f"• {str(character)}",
                styles["Normal"],
            )
        )

    content.append(Spacer(1, 15))

    # Panels
    panels = comic.get("panels", [])

    for panel in panels:

        panel_number = panel.get("panel", "")
        title = panel.get("title", "")

        content.append(
            Paragraph(
                f"Panel {panel_number}: {title}",
                styles["Heading2"],
            )
        )

        content.append(
            Paragraph(
                f"<b>Scene:</b> "
                f"{panel.get('scene_description', '')}",
                styles["BodyText"],
            )
        )

        content.append(Spacer(1, 5))

        content.append(
            Paragraph(
                f"<b>Narration:</b> "
                f"{panel.get('narration', '')}",
                styles["BodyText"],
            )
        )

        content.append(Spacer(1, 5))

        dialogue = panel.get("dialogue", [])

        if dialogue:
            content.append(
                Paragraph(
                    "<b>Dialogue:</b>",
                    styles["BodyText"],
                )
            )

            for line in dialogue:
                content.append(
                    Paragraph(
                        f"• {str(line)}",
                        styles["BodyText"],
                    )
                )

        content.append(Spacer(1, 15))

    # Create PDF
    document.build(content)

    # Verify that the PDF really exists
    if not pdf_path.exists():
        raise RuntimeError(
            "PDF was not created."
        )

    return str(pdf_path)