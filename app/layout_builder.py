from app.schemas import ComicResponse


def build_comic_layout(
    comic: ComicResponse
) -> list[dict]:

    return [
        panel.model_dump()
        for panel in comic.panels
    ]