#!/usr/bin/env python3
"""
auto_case.py  —  fully automated PowerFix case study generator.

Usage:
    python3 auto_case.py Peru
    python3 auto_case.py "Dominican Republic" --case-number 7

The script:
  1. Uses Claude API + web_search to find a real government hot-asphalt
     contract rate ($/m2) for the given territory.
  2. Finds the official FX rate from the territory's central bank.
  3. Finds social-media / news evidence of conventional pothole crews.
  4. Feeds the results into compute() + render() and saves a PDF to output/.

No manual data entry required.
"""

import sys
import os
import json
import argparse
import re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import anthropic
from powerfix_engine import CaseInputs, Source, compute
from powerfix_render import render


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def next_case_number() -> int:
    """Auto-detect the next case number by scanning output/ for existing PDFs."""
    out_dir = os.path.join(HERE, "output")
    if not os.path.isdir(out_dir):
        return 6
    nums = []
    for fname in os.listdir(out_dir):
        m = re.match(r"PowerFix_CaseStudy(\d+)_", fname)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1 if nums else 6


def research_territory(territory: str, api_key: str = None) -> dict:
    """
    Call Claude (opus-4-8, web_search) to research the three required data
    points for the given territory and return them as a structured dict.
    """
    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    prompt = f"""You are a research assistant for PowerFix, a pothole-repair product company.
I need you to research the following three things for **{territory}** and return ONLY a valid JSON object (no prose, no markdown fences).

## Task 1 — Government hot-asphalt contract rate
Search for a real, verifiable government road-repair or pothole-filling contract in {territory} that specifies a unit price in $/m2 or local-currency/m2 for HOT asphalt (asfalto caliente, mezcla asfáltica en caliente, etc.).
- Prefer the most recent contract (2023-2026).
- If the rate is in local currency, also record the USD equivalent using a recent exchange rate.
- Record the exact source: publisher/agency name, URL, and a one-line contract identifier (agency, contractor, date, total amount if available).

## Task 2 — Official FX rate
Find the official exchange rate (local currency per 1 US dollar) from the territory's central bank or official monetary authority.
- Record the rate, the institution name, and the URL of the rates page.

## Task 3 — Social media / news evidence of conventional pothole crews
Find a real social-media post, YouTube video, or news article that shows government workers doing conventional pothole repair (cutting, filling, compacting) in {territory}.
- Ideal sources: Twitter/X, Instagram, YouTube, TikTok, local news.
- Record the source label (e.g. "@municapital" or "La Prensa"), the URL, and a one-line description.

## Task 4 — Before/after photos of a real pothole repair
Try to find a real BEFORE photo (the pothole, unrepaired) and AFTER photo (same pothole, repaired with conventional hot asphalt) from {territory} — ideally from the same Instagram post, news article, or municipal social account as Task 3.
- Only record an image URL if it is a DIRECT image file link (ends in .jpg/.jpeg/.png/.webp, or is a CDN-hosted image URL that loads as an image, not an Instagram post page URL). Instagram post pages (instagram.com/p/...) are NOT direct image links — only use them if you can resolve the actual underlying image CDN URL (e.g. from an embedded preview, a news article that re-hosts the photo, or an open-graph image meta tag).
- If you cannot find direct-loadable image URLs for both before and after, set both fields to null — do not guess or fabricate a URL.

## Output format (return EXACTLY this JSON, no other text):
{{
  "territory": "{territory}",
  "currency_code": "<local currency symbol, e.g. S/ or RD$ or COP>",
  "gov_rate_per_m2_usd": <float — the all-in $/m2 rate>,
  "gov_rate_per_m2_local": <float or null — local-currency rate if found>,
  "method_label": "ASFALTO CALIENTE",
  "location_line": "<City, Territory · brief contract description · year>",
  "primary_source": {{
    "label": "<publisher name>",
    "url": "<URL or null>",
    "detail": "<one-line contract identifier>"
  }},
  "cross_checks": [
    {{ "label": "<name>", "url": "<URL or null>", "detail": "<short description>" }}
  ],
  "fx_local_per_usd": <float>,
  "fx_source": {{
    "label": "<institution name>",
    "url": "<URL>",
    "detail": "<short description, e.g. 'Banco Central, tipo de cambio, jun 2026'>"
  }},
  "social_media": {{
    "label": "<source label>",
    "url": "<URL or null>",
    "detail": "<one-line description of what the footage shows>"
  }},
  "before_after_photos": {{
    "before_image_url": "<direct image URL of the unrepaired pothole, or null>",
    "after_image_url": "<direct image URL of the repaired pothole, or null>",
    "source_label": "<e.g. '@municapital Instagram'>",
    "source_url": "<post or article URL, or null>"
  }},
  "confidence": "<high|medium|low>",
  "notes": "<any caveats about data quality or what was not found>"
}}

Search thoroughly. If you cannot find a contract with an explicit $/m2 price, estimate from the total contract value divided by the area covered (if both are available). If hot asphalt is not found, use cold asphalt and change method_label to "ASFALTO FRÍO". If the rate truly cannot be determined, set gov_rate_per_m2_usd to null and explain in notes.
"""

    print(f"  → Researching {territory} with Claude + web_search …")

    # Use streaming to avoid timeout on long research tasks
    result_text = ""
    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            pass
        final = stream.get_final_message()

    # Extract the text content (skip thinking blocks and tool use blocks)
    for block in final.content:
        if block.type == "text":
            result_text += block.text

    # Parse JSON — strip markdown fences if Claude accidentally added them
    result_text = result_text.strip()
    if result_text.startswith("```"):
        result_text = re.sub(r"^```[a-z]*\n?", "", result_text)
        result_text = re.sub(r"\n?```$", "", result_text.strip())

    try:
        data = json.loads(result_text)
    except json.JSONDecodeError:
        # Try to extract the first {...} block
        m = re.search(r"\{[\s\S]+\}", result_text)
        if m:
            data = json.loads(m.group(0))
        else:
            raise ValueError(
                f"Claude did not return valid JSON.\n\nRaw output:\n{result_text[:2000]}"
            )

    return data


def build_case_inputs(data: dict, case_number: int) -> CaseInputs:
    """Convert the raw research dict into a CaseInputs object."""

    rate_usd = data.get("gov_rate_per_m2_usd")
    if rate_usd is None:
        raise ValueError(
            f"Could not determine $/m2 rate for {data.get('territory')}.\n"
            f"Notes from research: {data.get('notes', 'none')}"
        )

    def make_source(d: dict) -> Source:
        return Source(
            label=d.get("label", ""),
            url=d.get("url") or None,
            detail=d.get("detail", ""),
        )

    cross_checks = [make_source(x) for x in data.get("cross_checks", [])]

    # Add social-media source to cross_checks if found
    social = data.get("social_media")
    if social and social.get("label"):
        cross_checks.append(make_source(social))

    # Build extra_footnote
    notes = data.get("notes", "")
    backcalc_note = (
        f"Precio/caja PowerPatch calibrado para 13% más barato que convencional "
        f"(posicionamiento, no precio de catálogo confirmado)."
    )
    extra = backcalc_note
    if social and social.get("label"):
        extra += f" Fotos/vídeo: {social['label']}."
    if notes:
        extra += f" {notes}"

    return CaseInputs(
        case_number=case_number,
        country=data.get("territory", ""),
        location_line=data.get("location_line", ""),
        currency_code=data.get("currency_code", ""),
        gov_rate_per_m2_usd=float(rate_usd),
        gov_rate_per_m2_local=data.get("gov_rate_per_m2_local"),
        method_label=data.get("method_label", "ASFALTO CALIENTE"),
        method_subtitle="Metodología observada — corte 8× del bache original",
        fx_local_per_usd=float(data.get("fx_local_per_usd", 1.0)),
        fx_source=make_source(data.get("fx_source", {})),
        box_price_usd=None,  # always auto-position at 13% cheaper
        primary_source=make_source(data.get("primary_source", {})),
        cross_checks=cross_checks,
        photos=[],  # filled in later by try_download_photos(), if found
        extra_footnote=extra,
    )


def try_download_photos(data: dict, tmp_dir: str) -> list:
    """
    Best-effort download of the before/after photo URLs Claude found.
    Returns a list of (path, tag, caption) tuples suitable for CaseInputs.photos,
    or [] if no usable direct-image URLs were found or the download failed.
    Instagram post pages are not directly downloadable — only direct CDN/image
    URLs work, so this frequently comes back empty. That's expected.
    """
    import requests

    info = data.get("before_after_photos") or {}
    before_url = info.get("before_image_url")
    after_url = info.get("after_image_url")
    if not before_url or not after_url:
        return []

    targets = [
        ("before", before_url, "PASO 1 · ANTES", "Bache real, sin reparar."),
        ("after", after_url, "PASO 2 · DESPUÉS", "Mismo bache, reparación convencional completada."),
    ]
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        photos = []
        for label, url, tag, caption in targets:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            ctype = resp.headers.get("Content-Type", "")
            if "image" not in ctype:
                return []  # not a real image URL — bail on both
            ext = ".png" if "png" in ctype else ".jpg"
            path = os.path.join(tmp_dir, f"{label}{ext}")
            with open(path, "wb") as f:
                f.write(resp.content)
            photos.append((path, tag, caption))
        return photos
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Auto-generate a PowerFix case study PDF for any territory."
    )
    parser.add_argument("territory", help='Territory name, e.g. "Peru" or "Dominican Republic"')
    parser.add_argument(
        "--case-number", type=int, default=None,
        help="Case number (default: auto-detected from output/ folder)"
    )
    args = parser.parse_args()

    territory = args.territory
    case_number = args.case_number or next_case_number()

    print("=" * 60)
    print(f"  PowerFix Auto Case Study Generator")
    print(f"  Territory : {territory}")
    print(f"  Case #    : {case_number}")
    print("=" * 60)

    # Step 1 — Research
    data = research_territory(territory)

    print(f"\n  Research complete (confidence: {data.get('confidence', '?')})")
    print(f"  Gov rate  : US${data.get('gov_rate_per_m2_usd')} /m2  "
          f"({data.get('gov_rate_per_m2_local')} {data.get('currency_code')})")
    print(f"  FX        : 1 USD = {data.get('fx_local_per_usd')} {data.get('currency_code')}")
    print(f"  Source    : {data.get('primary_source', {}).get('label', 'n/a')}")
    if data.get("notes"):
        print(f"  Notes     : {data['notes']}")

    # Step 2 — Build inputs
    inp = build_case_inputs(data, case_number)

    # Step 3 — Compute
    res = compute(inp)

    print("\n  --- Math check ---")
    print(f"  Pothole (1 box) : {res.pothole_m2} m2")
    print(f"  Cut zone (8×)   : {res.cut_zone_m2} m2")
    print(f"  Gov total       : US${res.conventional_total_usd}")
    print(f"  PowerPatch box  : US${res.powerpatch_box_usd}  "
          f"{'(back-calculated)' if res.box_is_backcalculated else '(confirmed)'}")
    print(f"  Savings         : US${res.savings_usd}  ({res.savings_pct}%)")
    print(f"  Speed           : {res.speed_multiple}× faster")

    # Step 4 — Render PDF
    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    safe_name = territory.replace(" ", "_")
    out_path = os.path.join(out_dir, f"PowerFix_CaseStudy{case_number}_{safe_name}.pdf")

    render(inp, res, out_path)
    print(f"\n  ✓ PDF saved to: {out_path}")
    print("=" * 60)

    # Optionally save the raw research data alongside the PDF for audit
    json_path = out_path.replace(".pdf", "_research.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Research data : {json_path}")


if __name__ == "__main__":
    main()
