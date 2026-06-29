"""
CASE DATA — Guatemala (Case Study #5)
=====================================
COPY THIS FILE for each new country and change ONLY the values below.
Then run:   python3 build_case.py case_guatemala.py
The math, layout, fonts, and styling are all handled automatically.

Fields you must fill:
  - case_number, country, location_line
  - gov_rate_per_m2_usd  (the real researched government rate, ALL-IN)
  - fx_local_per_usd     (exchange rate)
  - primary_source       (the contract the rate comes from)
  - photos               (your before/after images)

Optional:
  - gov_rate_per_m2_local (for display, e.g. Q378.71)
  - box_price_usd         (leave as None to auto-position at 13% cheaper)
  - cross_checks          (other contracts that corroborate the rate)
  - method_label          ("ASFALTO CALIENTE" or "ASFALTO FRÍO")
"""
from powerfix_engine import CaseInputs, Source

CASE = CaseInputs(
    # ---- identity ----
    case_number   = 5,
    country       = "Guatemala",
    location_line = "Guatemala, Ciudad de Guatemala \u00b7 Zona 14 \u00b7 Tarifa real de contrato gubernamental \u00b7 2026",
    currency_code = "Q",

    # ---- the real government rate (researched) ----
    gov_rate_per_m2_usd   = 49.70,
    gov_rate_per_m2_local = 378.71,
    method_label          = "ASFALTO CALIENTE",
    method_subtitle       = "Metodolog\u00eda observada \u2014 corte 8\u00d7 del bache original",

    # ---- FX ----
    fx_local_per_usd = 7.62,
    fx_source = Source(
        label  = "Banguat",
        url    = "https://www.banguat.gob.gt/page/tipos-de-cambio-de-referencia",
        detail = "Banco de Guatemala, tipo de cambio de referencia, jun 2026",
    ),

    # ---- box price: None => auto-positioned to hold 13% ----
    box_price_usd = None,

    # ---- primary source (the contract the rate is built on) ----
    primary_source = Source(
        label  = "Prensa Comunitaria (+8 hojas del contrato escaneadas)",
        url    = "https://prensacomunitaria.org/2025/08/municipalidad-de-guatemala-destina-q44-millones-para-bacheo-de-calles/",
        detail = "Contrato Muni. de Guatemala / Pavimentos del Norte, S.A., adjudicado 7 jul 2025 (Q44,557,066 / 117,654 m2)",
    ),

    # ---- cross-checks ----
    cross_checks = [
        Source(label="Maro Magazine",
               url="https://maromagazine.com/noticias/mixco-descontento-netobran",
               detail="Mixco material Q176.35/m2 \u00b7 Mixco/Asfaltos de Guatemala recapeo Q13.6M \u2248 Q173.78/m2"),
    ],

    # ---- photos (path, TAG, caption) ----
    photos = [
        ("/home/claude/gt_case_study/photo_cut_crop.jpg",  "PASO 1 \u00b7 CORTE",
         "Corte rectangular alrededor del bache \u2014 la zona cortada es mucho mayor al defecto real."),
        ("/home/claude/gt_case_study/photo_fill_crop.jpg", "PASO 2 \u00b7 RELLENO",
         "Cuadrilla rellenando manualmente el corte con mezcla y compactando con pis\u00f3n."),
    ],

    extra_footnote = "Precio/caja PowerPatch (US$114.16) calibrado para 13% m\u00e1s barato (posicionamiento, no precio de cat\u00e1logo confirmado). Fotos: @muniauxiliarz14. No se hall\u00f3 contrato gubernamental de asfalto en fr\u00edo en Guatemala.",
)
