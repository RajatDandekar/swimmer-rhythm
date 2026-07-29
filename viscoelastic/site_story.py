"""Cartoon story panels, told from the swimmer's point of view.

CHARACTER CONSISTENCY IS THE WHOLE PROBLEM. Generating eight panels from eight independent text
prompts produces eight different creatures, which destroys the illusion that this is one
character having one experience. So: generate a character sheet FIRST, then pass that image back
as a reference alongside every subsequent panel prompt. The model then draws the same creature
rather than re-inventing it.

The character is the physics, drawn cutely. The real swimmer is two unequal spheres on a rod
with exactly one degree of freedom, so the cartoon is a round body with ONE arm that can only
open and close. That single arm is the whole reason it cannot swim in water -- there is nothing
else it could possibly do differently.
"""
import base64
import json
import os
import sys
import urllib.request

KEY = os.environ["GEMINI_API_KEY"]
MODEL = os.environ.get("IMG_MODEL", "gemini-3-pro-image")
OUT = "site/figures/story"

CHARACTER = (
    "The character is a cute cartoon microorganism: a large round friendly body in bright "
    "cyan-teal, like a soft bubble, with two big expressive black eyes with white highlights "
    "and a simple curved mouth. It has exactly ONE arm on its left side -- a slender grey "
    "springy rod ending in a small round magenta ball, like a little mitten. It has no legs "
    "and no other limbs. Thick clean dark outlines, flat cheerful colours with soft shading, "
    "warm children's picture-book style, expressive and charming.")

STYLE = (" Clean bright white background, generous white space, simple and uncluttered. "
         "Palette limited to cyan-teal, warm orange, magenta, and soft grey. "
         "Absolutely no text, no letters, no numbers, no words, no speech bubbles, no labels "
         "anywhere in the image. Wide landscape composition.")

PANELS = {
    "01_meet": ("Full-body character sheet, the creature floating in empty clear water, "
                "centred, arm half open, smiling hopefully at the viewer."),
    "02_stuck": ("The same creature in clear empty water, arm swinging open and closed, "
                 "with small motion arcs around the arm. Its expression is straining and "
                 "determined but it is plainly going nowhere at all. Empty water, no wake, "
                 "no trail behind it whatsoever."),
    "03_defeated": ("The same creature slumped and deflated in clear empty water, eyes closed, "
                    "mouth a small flat exhausted line, arm hanging limp. Utterly still water "
                    "around it. A picture of quiet defeat."),
    "04_newfluid": ("The same creature, eyes wide with surprise and delight, now surrounded by "
                    "delicate curling golden-orange elastic filaments threading through the "
                    "space around it like soft springs. It has clearly just moved forward a "
                    "little, leaving a faint trail. Wonder on its face."),
    "05_discovery": ("The same creature with a huge delighted grin and one raised eyebrow, "
                     "mid-stroke, pausing dramatically with its arm held closed while the "
                     "golden filaments around it stretch taut. A moment of realisation and "
                     "mischief."),
    "06_victory": ("The same creature zooming forward fast, grinning triumphantly, with speed "
                   "lines behind it and golden filaments streaming back in its wake. Full of "
                   "confidence and joy."),
    "07_wrongfluid": ("The same creature in a visibly denser, heavier fluid packed with many "
                      "more thick tangled golden filaments. Its face is confused and dismayed, "
                      "eyebrows up, mouth open in dismay -- it is straining with the very same "
                      "stroke but slipping BACKWARD, with its motion trail pointing the wrong "
                      "way behind it."),
    "08_relearn": ("The same creature with a thoughtful expression, one eye squinting, clearly "
                   "working something out, with a small bright glowing idea-spark floating "
                   "above its head. The dense golden filaments around it are calm and waiting."),
    "09_mastery": ("The same creature swimming forward smoothly and serenely through the dense "
                   "golden filaments, eyes gently closed in contented mastery, a small peaceful "
                   "smile, its arm caught mid-stroke in a graceful pose, moving confidently."),
}


def call(parts):
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps({"contents": [{"parts": parts}]}).encode(),
        headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        print(f"    HTTP {e.code}: {e.read()[:250].decode(errors='replace')}")
        return None
    for c in d.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            if "inlineData" in p:
                return base64.b64decode(p["inlineData"]["data"])
    print(f"    no image (finishReason={d.get('candidates',[{}])[0].get('finishReason','?')})")
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:] or list(PANELS)
    ref = None
    refpath = f"{OUT}/01_meet.png"
    if os.path.exists(refpath) and "01_meet" not in names:
        ref = open(refpath, "rb").read()
        print("reusing existing character sheet as reference")

    for n in names:
        desc = PANELS[n]
        print(f"  {n} ...", flush=True)
        if ref is None:
            parts = [{"text": CHARACTER + " " + desc + STYLE}]
        else:
            # the reference image goes FIRST so the model anchors on it before reading the scene
            parts = [
                {"inlineData": {"mimeType": "image/png",
                                "data": base64.b64encode(ref).decode()}},
                {"text": "Draw a NEW illustration of the exact same character shown in the "
                         "reference image, keeping its body shape, colours, single arm and "
                         "style identical. " + desc + STYLE},
            ]
        raw = call(parts)
        if raw:
            open(f"{OUT}/{n}.png", "wb").write(raw)
            print(f"    wrote {OUT}/{n}.png ({len(raw)//1024} kB)")
            if n == "01_meet":
                ref = raw
        elif n == "01_meet":
            print("    character sheet failed — cannot anchor the rest"); return


if __name__ == "__main__":
    main()
