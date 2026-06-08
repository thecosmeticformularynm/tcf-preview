#!/usr/bin/env python3
"""
The Cosmetic Formulary — Authority Image System generator
=========================================================
Reads tcf-image-system.json and generates the 10 brand/authority images with
gpt-image-1 (1536x1024, quality high). The shared global_negative_prompt is
appended to each prompt as an "Avoid" clause (gpt-image-1 has no negative field).

USAGE
  export OPENAI_API_KEY=sk-...           # or place key in /tmp/.tcf_oai_key
  python3 generate-system.py --dry-run    # write resolved prompts, NO api calls
  python3 generate-system.py --only tcf-01-hero
  python3 generate-system.py --priority 1 # only priority<=1
  python3 generate-system.py              # generate all
OUTPUT
  system-images/<image_name>.png          # 1536x1024 png
  system-images/prompts/<image_name>.txt  # exact resolved prompt
  system-image-report.json
"""
import os, sys, json, base64, time, urllib.request

ROOT     = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "tcf-image-system.json")
OUT      = os.path.join(ROOT, "system-images")
PROMPTS  = os.path.join(OUT, "prompts")
REPORT   = os.path.join(ROOT, "system-image-report.json")
MODEL    = "gpt-image-1"
SIZE     = "1536x1024"   # 16:9 landscape
QUALITY  = "high"

def api_key():
    k = os.environ.get("OPENAI_API_KEY")
    if not k and os.path.exists("/tmp/.tcf_oai_key"):
        k = open("/tmp/.tcf_oai_key").read().strip()
    return k

def resolved_prompt(img, neg):
    p = img["prompt"].strip()
    return f"{p} Aspect ratio 16:9. Avoid in the image: {neg}."

def main():
    os.makedirs(PROMPTS, exist_ok=True)
    man = json.load(open(MANIFEST))
    neg = man["global_negative_prompt"]
    imgs = man["images"]
    args = sys.argv[1:]
    if "--only" in args:
        name = args[args.index("--only")+1]; imgs = [i for i in imgs if i["image_name"] == name]
    if "--priority" in args:
        lvl = int(args[args.index("--priority")+1]); imgs = [i for i in imgs if i["priority"] <= lvl]

    for img in imgs:
        open(os.path.join(PROMPTS, img["image_name"]+".txt"), "w").write(resolved_prompt(img, neg))
    if "--dry-run" in args:
        print(f"Resolved {len(imgs)} prompts -> {PROMPTS}/")
        for i in imgs: print(f"  [{i['priority']}] {i['image_name']:30} {i['size'] if 'size' in i else SIZE}")
        return

    key = api_key()
    if not key: sys.exit("ERROR: set OPENAI_API_KEY (or /tmp/.tcf_oai_key)")
    report = []
    for img in imgs:
        name = img["image_name"]
        body = json.dumps({"model": MODEL, "prompt": resolved_prompt(img, neg),
                           "size": SIZE, "quality": QUALITY, "n": 1}).encode()
        req = urllib.request.Request("https://api.openai.com/v1/images/generations",
            data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=420) as r:
                data = json.load(r)
            b64 = data["data"][0]["b64_json"]
            open(os.path.join(OUT, name+".png"), "wb").write(base64.b64decode(b64))
            status = "ok"
        except Exception as ex:
            status = f"FAIL: {ex}"
        report.append({"image_name": name, "status": status, "priority": img["priority"]})
        print(status, name, flush=True)
        time.sleep(1)
    json.dump(report, open(REPORT, "w"), indent=2)
    ok = sum(1 for r in report if r["status"] == "ok")
    print(f"\nReport: {REPORT}  ({ok}/{len(report)} ok)")

if __name__ == "__main__":
    main()
