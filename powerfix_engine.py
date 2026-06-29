"""
PowerFix case-study MATH ENGINE  (locked methodology — do not edit per-country)
=============================================================================
This file encodes the fixed PowerFix methodology constants and the math that
turns a few real inputs into every derived figure on the one-pager.

The ONLY things that change per case study are passed in as `CaseInputs`:
  - country / location / labels
  - the real government rate (per m2) + its source/citation
  - the FX rate + its source
  - (optional) a real confirmed PowerPatch box price; if omitted it is
    back-calculated to hold the standard 13% positioning, and clearly
    flagged as value-positioned.

Everything else (pothole size, cut multiplier, consumption, speed) is a
locked constant shared across ALL PowerFix case studies.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


# ----------------------------------------------------------------------
# LOCKED METHODOLOGY CONSTANTS  (shared across every case study)
# ----------------------------------------------------------------------
class Const:
    BOX_KG            = 20.0      # one PowerPatch box = 20 kg
    CONSUMPTION_KG_M2 = 60.6      # PowerPatch coverage rate
    CUT_MULTIPLIER    = 8.0       # conventional saw-cut zone = 8x the real pothole (+700%)
    POSITION_DISCOUNT = 0.13      # PowerPatch positioned 13% cheaper than conventional
    CONV_MINUTES      = 105       # conventional single-pothole time (1h45)
    PP_MINUTES        = 3         # PowerPatch single-pothole time (~3 min)

    # Derived "standard pothole" = the area one box fills:
    @classmethod
    def standard_pothole_m2(cls):
        return cls.BOX_KG / cls.CONSUMPTION_KG_M2      # 0.330 m2

    @classmethod
    def speed_multiple(cls):
        return round(cls.CONV_MINUTES / cls.PP_MINUTES)  # 35x


# ----------------------------------------------------------------------
# PER-CASE INPUTS  (the small bit that changes each time)
# ----------------------------------------------------------------------
@dataclass
class Source:
    label: str                       # short label shown in the footnote
    url: Optional[str] = None        # clickable link (None = no public URL)
    detail: str = ""                 # one-line description / contract identifier


@dataclass
class CaseInputs:
    # --- identity / header ---
    case_number: int
    country: str                     # "Guatemala"
    location_line: str               # "Ciudad de Guatemala · Zona 14 · Tarifa real de contrato gubernamental · 2026"
    currency_code: str               # "Q" (local) — used in footnote text
    usd_symbol: str = "US$"

    # --- the real, researched government rate ---
    gov_rate_per_m2_usd: float = 0.0     # e.g. 49.70  (ALL-IN, hot or cold)
    gov_rate_per_m2_local: Optional[float] = None  # e.g. 378.71 (for display)
    method_label: str = "ASFALTO CALIENTE"          # or "ASFALTO FRÍO"
    method_subtitle: str = "Metodología observada — corte 8× del bache original"

    # --- FX ---
    fx_local_per_usd: float = 1.0        # e.g. 7.62
    fx_source: Optional[Source] = None

    # --- PowerPatch box price ---
    box_price_usd: Optional[float] = None   # if known/confirmed, pass it.
                                            # if None -> back-calculated to hold 13%.

    # --- sources (primary + cross-checks) ---
    primary_source: Optional[Source] = None
    cross_checks: List[Source] = field(default_factory=list)

    # --- photos (page 2) : list of (path, tag, caption) ---
    photos: List[tuple] = field(default_factory=list)

    # --- honest-disclosure note (auto-filled, but overridable) ---
    extra_footnote: str = ""


# ----------------------------------------------------------------------
# THE MATH  (locked — produces every number the template prints)
# ----------------------------------------------------------------------
@dataclass
class CaseResults:
    pothole_m2: float
    cut_zone_m2: float
    cut_multiplier: float
    footprint_expansion_pct: str
    gov_rate_per_m2_usd: float
    conventional_total_usd: float
    powerpatch_box_usd: float
    box_is_backcalculated: bool
    savings_usd: float
    savings_pct: float
    speed_multiple: int
    conv_time_label: str
    pp_time_label: str


def compute(inp: CaseInputs) -> CaseResults:
    pothole = Const.standard_pothole_m2()
    cut = pothole * Const.CUT_MULTIPLIER
    conv_total = cut * inp.gov_rate_per_m2_usd

    if inp.box_price_usd is not None:
        box = inp.box_price_usd
        backcalc = False
    else:
        # value-position the single box to hold exactly 13% cheaper
        box = conv_total * (1 - Const.POSITION_DISCOUNT)
        backcalc = True

    savings = conv_total - box
    savings_pct = (savings / conv_total * 100) if conv_total else 0.0

    return CaseResults(
        pothole_m2=round(pothole, 2),
        cut_zone_m2=round(cut, 2),
        cut_multiplier=Const.CUT_MULTIPLIER,
        footprint_expansion_pct=f"+{int((Const.CUT_MULTIPLIER-1)*100)}%",
        gov_rate_per_m2_usd=round(inp.gov_rate_per_m2_usd, 2),
        conventional_total_usd=round(conv_total, 2),
        powerpatch_box_usd=round(box, 2),
        box_is_backcalculated=backcalc,
        savings_usd=round(savings, 2),
        savings_pct=round(savings_pct, 1),
        speed_multiple=Const.speed_multiple(),
        conv_time_label="~1H 45MIN",
        pp_time_label="~3 MIN",
    )


if __name__ == "__main__":
    # quick self-test with the Guatemala numbers
    gt = CaseInputs(
        case_number=5, country="Guatemala",
        location_line="x", currency_code="Q",
        gov_rate_per_m2_usd=49.70, gov_rate_per_m2_local=378.71,
        fx_local_per_usd=7.62,
    )
    r = compute(gt)
    print("pothole", r.pothole_m2, "cut", r.cut_zone_m2)
    print("conv", r.conventional_total_usd, "box", r.powerpatch_box_usd,
          "backcalc", r.box_is_backcalculated)
    print("savings", r.savings_usd, r.savings_pct, "% speed", r.speed_multiple)
