def build_comic_layout(outline, story, image_paths):
    story_map = {p["panel"]: p for p in story.get("panels", [])}
    layout = []
    for p in outline.get("panels", [])[:5]:
        s = story_map.get(p["panel"], {})
        layout.append({"panel": p["panel"], "title": p["title"], "scene": p["scene"], "image": image_paths[p["panel"]-1], "caption": s.get("caption", p["title"]), "narration": s.get("narration", p["scene"]), "dialogue": s.get("dialogue", "")})
    return layout
