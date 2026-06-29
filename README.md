# PowerFix Case Study Generator

Turn **photos + a location** into a finished, on-brand PowerFix case-study PDF —
without rebuilding the layout or redoing the math every time.

The design, fonts (Barlow Condensed), colors, and all the methodology math
(8× cut, 0.33 m² pothole = 1 box, 60.6 kg/m², 13% positioning, 35× speed) are
**locked**. The only thing that changes per country is a short data file.

---

## The workflow (two stages)

### Stage 1 — Research (this is where Claude helps)
For a new country/territory you need **one real number with a real source**:
the government's per-m² road-repair (bacheo) contract rate, converted to US$.

Hand Claude:
- the **country / city** (and photos if you have them)
- ask: *"find the most relevant, defensible government bacheo/asphalt contract
  for <place>, give me the per-m² rate in US$ and local currency, the FX rate,
  and clickable source links — primary contract plus any cross-checks."*

Claude searches government procurement / news / FX sources, picks the most
defensible contract, shows you the math, and **you approve it**. This step
stays human-in-the-loop on purpose: the whole brand promise is that every
number traces to a real, cited document. A wrong auto-picked source would
quietly break that.

> Honesty rules baked in: if the box price isn't a confirmed PowerFix catalog
> price, it's auto-labeled "posicionado / value-positioned." If a source has no
> public URL, that's stated. If no cold-asphalt government contract exists, the
> footnote says so.

### Stage 2 — Generate (one command)
1. Copy `case_TEMPLATE.py` → `case_<country>.py`
2. Paste in the researched numbers + source links + photo paths
3. Run:
   ```
   python3 build_case.py case_<country>.py
   ```
4. The script prints the math for a final sanity check and writes
   `output/PowerFix_CaseStudy<N>_<Country>.pdf`

That's it. Same format, every time.

---

## Files

| File | What it is | Touch it? |
|------|-----------|-----------|
| `case_TEMPLATE.py` | blank form to copy for each country | ✅ copy & fill |
| `case_guatemala.py` | worked example (Guatemala #5) | reference |
| `build_case.py` | the one command you run | ❌ |
| `powerfix_engine.py` | locked methodology + math | ❌ |
| `powerfix_render.py` | locked layout / fonts / styling | ❌ |
| `fonts/` | Barlow + Barlow Condensed | ❌ |
| `output/` | finished PDFs land here | — |

## Changing the methodology globally
If a constant ever changes for **all** case studies (e.g. a new consumption
rate, or a confirmed box price across countries), edit it **once** in
`powerfix_engine.py` → `class Const`. Every future PDF picks it up automatically.

## Quick start (reproduce Guatemala)
```
python3 build_case.py case_guatemala.py
```
Produces the exact approved Guatemala case study.
