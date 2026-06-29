"""
=============================================================
  NEW CASE STUDY TEMPLATE  —  copy this file, rename it, fill it in
=============================================================
  1. Save a copy as  case_<country>.py   (e.g. case_peru.py)
  2. Fill in every line marked  # FILL
  3. Put your photos somewhere and point to them below
  4. Run:   python3 build_case.py case_<country>.py
  5. Find your PDF in the  output/  folder

  You do NOT touch the math, the layout, or the fonts — those are locked.
  Leave  box_price_usd = None  and the box price will auto-calculate to
  hold the standard 13%-cheaper positioning.
=============================================================
"""
from powerfix_engine import CaseInputs, Source

CASE = CaseInputs(
    # ---- identity / header ----
    case_number   = 0,                       # FILL  e.g. 6
    country       = "",                      # FILL  e.g. "Peru"
    location_line = "",                      # FILL  e.g. "Lima, Peru · Av. ... · Tarifa real de contrato · 2026"
    currency_code = "",                      # FILL  local currency symbol, e.g. "S/" or "$"

    # ---- the real government rate (RESEARCHED — see README step 1) ----
    gov_rate_per_m2_usd   = 0.00,            # FILL  the all-in $/m2 from the real contract
    gov_rate_per_m2_local = None,            # FILL (optional) local-currency rate for display
    method_label          = "ASFALTO CALIENTE",  # or "ASFALTO FRÍO"
    method_subtitle       = "Metodolog\u00eda observada \u2014 corte 8\u00d7 del bache original",

    # ---- FX ----
    fx_local_per_usd = 1.00,                 # FILL  local units per US$1
    fx_source = Source(
        label  = "",                         # FILL  e.g. "Banco Central"
        url    = "",                         # FILL  link to the rate
        detail = "",                         # FILL  short description
    ),

    # ---- box price ----
    box_price_usd = None,                    # leave None to auto-position at 13%; or FILL a confirmed price

    # ---- primary source (the contract the rate comes from) ----
    primary_source = Source(
        label  = "",                         # FILL  the clickable link text (publisher)
        url    = "",                         # FILL  the URL  (use None if no public URL exists)
        detail = "",                         # FILL  contract identifier: agency, contractor, date, amount
    ),

    # ---- cross-checks (0, 1, or more corroborating contracts) ----
    cross_checks = [
        # Source(label="", url="", detail=""),
    ],

    # ---- photos: (path, TAG shown on photo, caption under photo) ----
    photos = [
        # ("/path/to/before.jpg", "PASO 1 · CORTE",   "caption..."),
        # ("/path/to/after.jpg",  "PASO 2 · RELLENO", "caption..."),
    ],

    # ---- optional extra honesty note (leave "" to auto-generate) ----
    extra_footnote = "",
)
