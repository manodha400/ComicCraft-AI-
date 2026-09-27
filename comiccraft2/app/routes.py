from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .exporters import save_pdf


router = APIRouter()
templates = Jinja2Templates(directory="templates")


class PromptRequest(BaseModel):
    story_prompt: str
    character: str = "Ari"
    setting: str = "Dragon School"
    tone: str = "funny and adventurous"
    art_style: str = "animated cartoon"


def generate_complete_comic(data: PromptRequest):
    outline = generate_outline(
        data.story_prompt,
        data.character,
        data.setting,
        data.tone,
        data.art_style
    )

    story = generate_story(
        outline,
        data.character,
        data.tone
    )

    images = [
        generate_image(
            p["panel"],
            p["scene"],
            data.art_style
        )
        for p in outline["panels"][:5]
    ]

    layout = build_comic_layout(
        outline,
        story,
        images
    )

    pdf = save_pdf(layout)

    return layout, pdf


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "defaults": {
                "story_prompt": "A new student discovers a tiny dragon with a special power at Dragon School.",
                "character": "Ari",
                "setting": "Dragon School",
                "tone": "funny and adventurous",
                "art_style": "animated cartoon"
            }
        }
    )




@router.post("/generate")
def generate(
    request: Request,
    story_prompt: str = Form(...),
    character: str = Form("Ari"),
    setting: str = Form("Dragon School"),
    tone: str = Form("funny and adventurous"),
    art_style: str = Form("animated cartoon")
):


    data = PromptRequest(
        story_prompt=story_prompt,
        character=character,
        setting=setting,
        tone=tone,
        art_style=art_style
    )

    layout, pdf = generate_complete_comic(data)

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "layout": layout,
            "pdf": pdf
        }
    )


@router.post("/generate-comic/json")
def generate_json(data: PromptRequest):
    layout, pdf = generate_complete_comic(data)

    return JSONResponse({
        "panels": layout,
        "pdf": pdf
    })


@router.get("/test-image")
def test_image():
    path = generate_image(
        1,
        "A cheerful student meeting a tiny friendly dragon at school."
    )

    return {"image": path}


@router.get("/download/{filename}")
def download(filename: str):
    path = Path("static/exports") / filename

    if not path.exists():
        return JSONResponse(
            {"error": "File not found"},
            status_code=404
        )

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/export-success")
def export_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={}
    )