import os
import uuid
from pathlib import Path

from PIL import Image, ImageDraw
from dotenv import load_dotenv

load_dotenv()

BASE = Path("static/panels")
BASE.mkdir(parents=True, exist_ok=True)


def _placeholder(number, title, filename):
    img = Image.new("RGB", (1024, 1024), (235, 242, 255))
    d = ImageDraw.Draw(img)

    d.rounded_rectangle(
        (60, 60, 964, 964),
        radius=40,
        outline=(80, 110, 170),
        width=8
    )

    d.text(
        (90, 100),
        f"Comic Panel {number}",
        fill=(30, 50, 90)
    )

    d.text(
        (90, 160),
        title[:70],
        fill=(30, 50, 90)
    )

    d.text(
        (90, 900),
        "AI illustration",
        fill=(70, 70, 70)
    )

    path = BASE / filename
    img.save(path)

    return str(path).replace("\\", "/")


def generate_image(panel_number, scene, art_style="animated cartoon"):

    token = os.getenv("HF_TOKEN") or os.getenv("HF_API_KEY")

    if not token or token.startswith("PASTE_"):
        print("ERROR: HF_TOKEN not found")
        return _placeholder(
            panel_number,
            scene,
            f"comic_{uuid.uuid4().hex[:10]}_panel_{panel_number}.png"
        )

    filename = (
        f"comic_{uuid.uuid4().hex[:10]}_"
        f"panel_{panel_number}.png"
    )

    try:
        from huggingface_hub import InferenceClient

        # Let Hugging Face automatically choose
        # an available inference provider.
        client = InferenceClient(
            api_key=token,
            timeout=180
        )

        prompt = (
            "2D animated cartoon comic illustration, "
            "children friendly, colorful, expressive characters, "
            "fantasy school setting, "
            f"{art_style}, "
            f"scene: {scene}, "
            "high quality digital illustration, "
            "no text, no letters, no logo, no watermark"
        )

        print()
        print("=" * 60)
        print(f"GENERATING COMIC PANEL {panel_number}")
        print("=" * 60)
        print(f"Scene: {scene}")
        print("Calling Hugging Face Inference Providers...")
        print("Please wait...")

        image = client.text_to_image(
            prompt=prompt,
            model=os.getenv("HF_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
        )

        path = BASE / filename
        image.save(path)

        print(f"SUCCESS: {path}")

        return str(path).replace("\\", "/")

    except Exception as e:

        print()
        print("!!! IMAGE GENERATION FAILED !!!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")

        return _placeholder(
            panel_number,
            scene,
            filename
        )
    r̥