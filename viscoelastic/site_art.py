"""Generate the site's conceptual artwork with Gemini image models (Nano Banana).

Scientific data figures are NOT generated here -- those come from site_figures.py, plotted from
the real result JSONs. A generative model must never draw a chart on this site: the credibility
of the claim rests on every number tracing to a run. These illustrate ideas (what a scallop is,
what fluid memory feels like), where an artist's impression is honest and a plot would not be.

Light theme, keyed to the Vizuara mark: magenta / orange / cyan on white.
"""
import base64
import json
import os
import sys
import urllib.request

KEY = os.environ["GEMINI_API_KEY"]
MODEL = os.environ.get("IMG_MODEL", "gemini-3-pro-image")
OUT = "site/figures"

STYLE = ("Editorial scientific illustration for a modern physics feature, LIGHT THEME. "
         "Clean bright white background, generous negative space, airy and elegant. Restrained "
         "palette of exactly three accent colours: vivid magenta (#e6009e), warm orange "
         "(#ef8f1c), bright cyan (#1a9fd4), plus soft grey linework. Crisp vector-adjacent "
         "rendering, subtle soft shadows, delicate line weights, a refined museum-poster feel. "
         "Absolutely no text, no letters, no numbers, no labels, no arrows, no captions, no "
         "watermarks anywhere in the image. Wide aspect.")

PROMPTS = {
    "hero": (
        "A single microscopic swimmer floating on a clean white field: two smooth spheres of "
        "different sizes — one small magenta, one larger cyan — joined by a slender grey rod, "
        "like a microscopic dumbbell. Around them, fine delicate orange filaments curl through "
        "the white space like stretched silk threads, denser and more taut near the spheres, "
        "loosening into soft open curls further away, as if the empty space itself is holding "
        "a memory of where the spheres have been. Serene, weightless, beautifully minimal. "
        + STYLE),
    "scallop": (
        "Two simple elegant scallop shells drawn as fine line illustrations on a clean white "
        "field, side by side, separated by generous white space. The left shell sits in a "
        "faintly outlined region of perfectly still, empty, featureless space — nothing around "
        "it, no trail, motionless. The right shell sits in a region threaded with fine curling "
        "orange and magenta filaments that stretch and coil behind it like slow silk, and the "
        "shell is clearly displaced forward from a soft ghosted outline of its original "
        "position, leaving a delicate trail. A study in contrast between emptiness and memory. "
        + STYLE),
    "reversal": (
        "A visual metaphor for a strategy reversing. Two identical smooth spheres, one orange "
        "and one cyan, racing left to right along two parallel lanes on a clean white field. "
        "On the left half of the image the cyan sphere is clearly ahead of the orange one. The "
        "lanes cross over at a single vivid magenta point in the exact centre. On the right "
        "half the positions are swapped and the orange sphere is now clearly ahead. The "
        "swapping is unmistakable and the crossing point is the focal centre of the "
        "composition. Elegant, graphic, instantly readable. " + STYLE),
    "memory": (
        "A close-up illustration of what makes a fluid remember: long tangled polymer chains "
        "drawn as fine flowing filament lines on a clean white field. On the left they are "
        "loose, relaxed, softly coiled in pale grey. Moving right they are progressively "
        "stretched taut and straight, glowing warm orange under tension, at maximum stretch in "
        "the centre. Then to the far right they are slowly relaxing back into loose coils "
        "again, fading from orange through soft magenta back to pale grey. A gradient of "
        "tension and release across the frame, like a slow breath. " + STYLE),
}


def generate(name, prompt):
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode(),
        headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        print(f"  {name}: HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
        return False
    for c in d.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            if "inlineData" in p:
                raw = base64.b64decode(p["inlineData"]["data"])
                open(f"{OUT}/{name}.png", "wb").write(raw)
                print(f"  {name}: wrote {OUT}/{name}.png ({len(raw)//1024} kB)")
                return True
    fr = d.get("candidates", [{}])[0].get("finishReason", "?")
    print(f"  {name}: no image returned (finishReason={fr})")
    return False


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    which = sys.argv[1:] or list(PROMPTS)
    print(f"model: {MODEL}")
    ok = sum(generate(n, PROMPTS[n]) for n in which)
    print(f"{ok}/{len(which)} images generated")
