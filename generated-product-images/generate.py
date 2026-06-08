#!/usr/bin/env python3
"""
The Cosmetic Formulary — Product Image Generation System
=========================================================
Repeatable pipeline that generates premium clinical product photography for every
product in one consistent brand style using OpenAI gpt-image-1.

USAGE
  export OPENAI_API_KEY=sk-...            # or place key in /tmp/.tcf_oai_key
  python3 generate.py --dry-run           # build manifest + prompts, NO api calls
  python3 generate.py --only <handle>     # (re)generate a single product
  python3 generate.py --batch             # generate every product in the manifest
  python3 generate.py --review            # print packaging-confidence review only

OUTPUT
  generated-product-images/
    product-image-manifest.json           # structured manifest (Step 5 format)
    image-generation-report.json          # per-run results
    prompts/<handle>.txt                  # exact prompt used per image
    images/<handle>.png                   # 1024x1024 png, named by handle
"""
import os, sys, json, base64, time, urllib.request, urllib.error

ROOT      = os.path.dirname(os.path.abspath(__file__))
IMG_DIR   = os.path.join(ROOT, "images")
PROMPT_DIR= os.path.join(ROOT, "prompts")
MANIFEST  = os.path.join(ROOT, "product-image-manifest.json")
REPORT    = os.path.join(ROOT, "image-generation-report.json")
MODEL     = "gpt-image-1"
SIZE      = "1024x1024"
QUALITY   = "high"

# ---- MASTER PROMPT TEMPLATE (Step 3) ---------------------------------------
MASTER_PROMPT = (
 "Create a premium clinical studio product photograph for The Cosmetic Formulary. "
 "A single cosmetic product, centered and standing upright, on a clean bright white to very "
 "soft cool-gray seamless studio background. No props. No ingredient smear. No swatch. No hands. "
 "No lifestyle background. High-key diffused studio lighting with one soft, natural grounding "
 "shadow directly beneath the product. The packaging must be exactly this type: {PACKAGING}. "
 "Packaging is matte white with a clear over-cap where applicable, brushed-silver lid where a jar. "
 "Label design, printed cleanly on the front: a bold CIRCULAR logo reading 'THE COSMETIC FORMULARY' "
 "in the upper third; the product name '{NAME}' below it in elegant black serif-free typography; "
 "a short thin horizontal divider line; the words 'PROFESSIONAL FORMULA' in spaced uppercase; and "
 "'{SIZE}' small at the bottom. Spelling must be exact and crisply legible. Clinical dermatology "
 "aesthetic, stainless-steel lab-adjacent mood, billion-dollar institutional cosmetic-manufacturing "
 "quality. Sharp, photorealistic, minimal. NOT spa, NOT organic, NOT earthy, NOT handmade, NOT generic."
)

# ---- BOTTLE / PACKAGE MAPPING (Step 2) -------------------------------------
# productType -> (packaging_type, confidence, note)
PACKAGING = {
 "Serum":          ("white cylindrical airless pump bottle with a clear over-cap", "high",   ""),
 "Oil":            ("white cylindrical glass bottle with a black dropper cap",     "medium", "oil could ship as pump instead of dropper"),
 "Cream":          ("low wide white cosmetic jar with a brushed-silver lid",       "medium", "cream could be airless pump instead of jar"),
 "Cleanser":       ("tall white pump bottle, larger retail/back-bar format",       "high",   ""),
 "Cleansing Oil":  ("white cylindrical bottle with a pump",                        "medium", "could be dropper"),
 "SPF / Sunscreen":("white airless pump bottle with a clear over-cap",             "medium", "SPF often ships as a squeeze tube"),
 "Toner":          ("tall slim white bottle with a clear over-cap",                "medium", "toner/mist may be a fine-mist sprayer"),
 "Toner Pad":      ("wide squat white pad jar with a brushed-silver lid",          "high",   ""),
 "Aqueous Gel":    ("white airless pump bottle with a clear over-cap",             "medium", "could be a tube"),
 "Lotion":         ("white airless pump bottle",                                   "medium", "could be a jar"),
 "Exfoliator":     ("white squeeze tube with a flip cap",                          "medium", "powder exfoliant would be a sifter jar"),
 "Mask":           ("low wide white cosmetic jar with a brushed-silver lid",       "high",   ""),
 "Eye Cream":      ("small white airless pump bottle with a clear over-cap",       "medium", "eye products may be a small tube"),
 "Body Oil":       ("tall frosted-glass bottle with a pump",                       "medium", "could be a dropper"),
 "Body Scrub":     ("wide white jar with a brushed-silver lid",                    "high",   ""),
 "Lip Balm":       ("white squeeze tube",                                          "medium", "lip could be a small pot/jar"),
 "Moisturizer":    ("low white cosmetic jar with a brushed-silver lid",            "medium", "moisturizer could be a pump bottle"),
}
# per-handle overrides for known special cases (highest priority)
OVERRIDES = {
 "gentle-cleanser":            ("tall white pump bottle, larger retail/back-bar format", "high",   "typed 'Cream' in Shopify but is a cleanser"),
 "complexion-renewal-pads":    ("wide squat white pad jar with a brushed-silver lid",    "high",   "treatment pads"),
 "exfoliating-polish":         ("white airless pump bottle",                             "medium", "scrub-polish; pump or tube"),
 "daily-microfoliant-dermaclear-micro-milk-peel": ("white jar with a sifter/shaker lid","low",    "POWDER exfoliant — confirm jar vs sachet"),
 "muscle-joint-relief-creme-musclease-active-body-oil": ("white airless pump bottle",    "medium","body cream; pump or jar"),
 "botanical-kinetics-toning-mist-cream-skin-refiner": ("white bottle with a fine-mist sprayer cap","medium","toning MIST"),
 "lip-saver-spf-lip-sleeping-mask": ("white squeeze lip tube","medium","lip balm/mask"),
}

# ---- PRODUCT DATA (Step 1) -------------------------------------------------
# handle, label name, productType, label size string
PRODUCTS = [
 ("restorative-skin-complex","Restorative Peptide Complex","Serum","0.5 fl oz | 15 mL"),
 ("vitamin-e-oil-antioxidant-serum","Vitamin E Antioxidant Oil","Oil","1 fl oz | 30 mL"),
 ("clenziderm-bpo-cleanser-5","BPO Clarifying Cleanser 5%","Cleanser","6.7 fl oz | 200 mL"),
 ("nu-derm-clear-fx","Brightening Arbutin Serum","Serum","1 fl oz | 30 mL"),
 ("professional-c-serum-10","Professional C Serum 10%","Serum","1 fl oz | 30 mL"),
 ("professional-c-serum-20","Professional C Serum 20%","Serum","1 fl oz | 30 mL"),
 ("retinol-05","Retinol 0.5%","Serum","1 fl oz | 30 mL"),
 ("retinol-10","Retinol 1.0%","Serum","1 fl oz | 30 mL"),
 ("sun-shield-tint-spf-50","Tinted Mineral SPF 50","SPF / Sunscreen","2.5 fl oz | 75 mL"),
 ("retinol-treatment-for-sensitive-skin","Gentle Retinol Treatment","Serum","1 fl oz | 30 mL"),
 ("c-correcting-complex-30-thd-chassis-at-20","C+ Correcting Complex 20%","Serum","1 fl oz | 30 mL"),
 ("c-correcting-complex-30","C+ Correcting Complex 30%","Serum","1 fl oz | 30 mL"),
 ("dej-face-cream","Cellular Renewal Face Cream","Cream","1.7 oz | 48 mL"),
 ("intellishade-truphysical","Tinted Mineral SPF Moisturizer","SPF / Sunscreen","2.5 fl oz | 75 mL"),
 ("nectifirm-advanced","Advanced Neck Firming Cream","Cream","1.7 oz | 48 mL"),
 ("age-interrupter-advanced","Glycation Repair Cream","Cream","1.7 oz | 48 mL"),
 ("c-e-ferulic","CE Ferulic Antioxidant Serum","Serum","1 fl oz | 30 mL"),
 ("discoloration-defense","Discoloration Defense Serum","Serum","1 fl oz | 30 mL"),
 ("ha-intensifier","Hyaluronic Acid Intensifier","Serum","1 fl oz | 30 mL"),
 ("lha-toner","LHA Exfoliating Toner","Toner","6.7 fl oz | 200 mL"),
 ("gentle-cleanser","Gentle Daily Cleanser","Cleanser","6.7 fl oz | 200 mL"),
 ("simply-clean-nu-derm-foaming-gel","Foaming Gel Cleanser","Cleanser","8 fl oz | 240 mL"),
 ("phloretin-cf","Phloretin CF Antioxidant Serum","Serum","1 fl oz | 30 mL"),
 ("phyto-corrective-gel","Phyto Corrective Soothing Gel","Aqueous Gel","1 fl oz | 30 mL"),
 ("silymarin-cf","Silymarin CF Antioxidant Serum","Serum","1 fl oz | 30 mL"),
 ("triple-lipid-restore-2-4-2","Triple Lipid Restore Cream","Cream","1.7 oz | 48 mL"),
 ("lytera-20","Advanced Brightening Complex","Serum","2 fl oz | 60 mL"),
 ("azelaic-acid-10-suspension-azelaic-booster","Azelaic Acid 10% Booster","Lotion","1 fl oz | 30 mL"),
 ("niacinamide-10-zinc-1","Niacinamide 10% + Zinc 1%","Serum","1 fl oz | 30 mL"),
 ("complexion-renewal-pads","Complexion Renewal Pads","Toner Pad","60 pads"),
 ("daily-power-defense","Daily Power Defense Moisturizer","Lotion","2 fl oz | 60 mL"),
 ("exfoliating-polish","Exfoliating Polish","Exfoliator","3.7 oz | 110 mL"),
 ("oclipse-smart-tone-spf-50","Smart Tone Mineral SPF 50","SPF / Sunscreen","2.5 fl oz | 75 mL"),
 ("retinol-skin-brightener-05","Retinol Skin Brightener 0.5%","Serum","1 fl oz | 30 mL"),
 ("growth-factor-serum-plus-tns-advanced","Growth Factor Renewal Serum","Serum","1 fl oz | 30 mL"),
 ("active-serum","Active Serum","Serum","1 fl oz | 30 mL"),
 ("super-serum-advance","Super Antioxidant Serum","Serum","1 fl oz | 30 mL"),
 ("botanical-kinetics-cleansing-oil-ginseng-cleansing-oil","Botanical Cleansing Oil","Cleansing Oil","6.7 fl oz | 200 mL"),
 ("special-cleansing-gel-low-ph-good-morning-gel","Low-pH Gel Cleanser","Cleanser","6.7 fl oz | 200 mL"),
 ("daily-microfoliant-dermaclear-micro-milk-peel","Daily Rice Microfoliant","Exfoliator","2.6 oz | 75 g"),
 ("exfoliating-cleanser-the-rice-polish","Rice Polish Exfoliating Cleanser","Exfoliator","3.9 fl oz | 115 mL"),
 ("clay-treatment-super-volcanic-pore-clay-mask","Volcanic Clay Pore Mask","Mask","4 fl oz | 120 mL"),
 ("professional-cream-mask-water-sleeping-mask","Overnight Water Sleeping Mask","Mask","2.5 fl oz | 75 mL"),
 ("iluma-brightening-serum-aha-7-whitehead-power-liquid","Brightening AHA Power Serum","Serum","2 fl oz | 60 mL"),
 ("botanical-kinetics-toning-mist-cream-skin-refiner","Botanical Toning Mist","Toner","6.7 fl oz | 200 mL"),
 ("moisture-x10-water-bank-blue-ha-serum","Blue HA Moisture Serum","Serum","1.7 fl oz | 50 mL"),
 ("total-eye-care-concentrated-ginseng-eye-cream","Ginseng Total Eye Cream","Eye Cream","0.5 fl oz | 15 mL"),
 ("herbal-select-massage-oil-frangipani-monoi-body-oil","Frangipani Monoi Body Oil","Body Oil","8 fl oz | 240 mL"),
 ("muscle-joint-relief-creme-musclease-active-body-oil","Muscle & Joint Relief Cream","Cream","4 fl oz | 120 mL"),
 ("exfoliating-body-scrub-coco-rose-body-polish","Coco Rose Body Polish","Body Scrub","8.8 oz | 250 g"),
 ("lip-saver-spf-lip-sleeping-mask","Lip Repair & SPF Balm","Lip Balm","0.5 oz | 15 g"),
 ("pore-refining-toner-pads-refined-medicube-zero-pore-chemistry","Pore-Refining Toner Pads","Toner Pad","60 pads"),
 ("pdrn-pink-collagen-serum-refined-medicube-chemistry","PDRN Pink Collagen Serum","Serum","1 fl oz | 30 mL"),
 ("pdrn-pink-collagen-capsule-cream-refined-medicube-chemistry","PDRN Collagen Capsule Cream","Cream","1.7 oz | 48 mL"),
 # ---- kept Clean Beauty Labs basics ----
 ("full-size-cream-cleanser-003","Cream Cleanser","Cleanser","6 fl oz | 177 mL"),
 ("full-size-oil-cleanser-001","Oil Cleanser","Cleanser","6 fl oz | 177 mL"),
 ("6oz-gel-cleanser-glycolic-acid-001","Gel Cleanser","Cleanser","6 fl oz | 177 mL"),
 ("full-size-lotion-002","Daily Moisturizer","Moisturizer","1 oz | 30 mL"),
]

def pkg_for(handle, ptype):
    if handle in OVERRIDES: return OVERRIDES[handle]
    return PACKAGING.get(ptype, ("white cylindrical airless pump bottle with a clear over-cap","low","unknown type — confirm"))

def build_manifest():
    m = []
    for handle, name, ptype, size in PRODUCTS:
        pkg, conf, note = pkg_for(handle, ptype)
        m.append({
            "handle": handle, "title": name, "category": ptype, "size": size,
            "packaging_type": pkg, "label_logo": "bold circular The Cosmetic Formulary logo",
            "label_title": name, "label_subtitle": "PROFESSIONAL FORMULA",
            "background": "clean bright white / soft cool gray",
            "style": "clinical premium dermatology product photography",
            "packaging_confidence": conf, "packaging_note": note,
            "alt_text": f"The Cosmetic Formulary {name} in {pkg}",
        })
    return m

def prompt_for(e):
    return MASTER_PROMPT.format(PACKAGING=e["packaging_type"], NAME=e["title"], SIZE=e["size"])

def api_key():
    k = os.environ.get("OPENAI_API_KEY")
    if not k and os.path.exists("/tmp/.tcf_oai_key"):
        k = open("/tmp/.tcf_oai_key").read().strip()
    return k

def generate_one(e, key):
    body = json.dumps({"model": MODEL, "prompt": prompt_for(e), "size": SIZE,
                       "quality": QUALITY, "n": 1}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.load(r)
    b64 = data["data"][0]["b64_json"]
    open(os.path.join(IMG_DIR, e["handle"]+".png"), "wb").write(base64.b64decode(b64))
    open(os.path.join(PROMPT_DIR, e["handle"]+".txt"), "w").write(prompt_for(e))

def main():
    os.makedirs(IMG_DIR, exist_ok=True); os.makedirs(PROMPT_DIR, exist_ok=True)
    man = build_manifest()
    json.dump(man, open(MANIFEST, "w"), indent=2)
    args = sys.argv[1:]

    if "--review" in args or "--dry-run" in args:
        for e in man:
            json.dump(prompt_for(e), open(os.path.join(PROMPT_DIR, e["handle"]+".txt"), "w"))
            open(os.path.join(PROMPT_DIR, e["handle"]+".txt"), "w").write(prompt_for(e))
        flagged = [e for e in man if e["packaging_confidence"] != "high"]
        print(f"Manifest written: {MANIFEST} ({len(man)} products)")
        print(f"Prompts written:  {PROMPT_DIR}/")
        print(f"\nPackaging confidence: HIGH={sum(1 for e in man if e['packaging_confidence']=='high')}  "
              f"MEDIUM={sum(1 for e in man if e['packaging_confidence']=='medium')}  "
              f"LOW={sum(1 for e in man if e['packaging_confidence']=='low')}")
        print("\nNEEDS CONFIRMATION (medium/low):")
        for e in flagged:
            print(f"  [{e['packaging_confidence'].upper():6}] {e['title']:38} -> {e['packaging_type']}"
                  + (f"   ({e['packaging_note']})" if e['packaging_note'] else ""))
        return

    key = api_key()
    if not key: sys.exit("ERROR: set OPENAI_API_KEY (or /tmp/.tcf_oai_key)")
    only = None
    if "--only" in args: only = args[args.index("--only")+1]
    targets = [e for e in man if (only is None or e["handle"] == only)]
    report = []
    for e in targets:
        try:
            generate_one(e, key); status = "ok"
        except Exception as ex:
            status = f"FAIL: {ex}"
        report.append({"handle": e["handle"], "status": status,
                       "packaging_confidence": e["packaging_confidence"]})
        print(status, e["handle"])
        time.sleep(1)
    json.dump(report, open(REPORT, "w"), indent=2)
    print(f"\nReport: {REPORT}  ({sum(1 for r in report if r['status']=='ok')}/{len(report)} ok)")

if __name__ == "__main__":
    main()
