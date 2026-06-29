"""
PowerFix case-study RENDERER  (locked layout — do not edit per-country)
=======================================================================
Draws the standard 2-page PowerFix one-pager from CaseInputs + CaseResults.
Page 1: header, stats row, two-method comparison, savings bar, savings stats,
        feature callouts, clickable sources footnote.
Page 2: up to 2 photos with tags/captions + projection disclaimer.

Everything visual (fonts, colors, spacing, the lightning wordmark) is fixed
here so every country comes out identical in style.
"""
import os
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts") + "/"

# register fonts once
_REG = False
def _register_fonts():
    global _REG
    if _REG: return
    pdfmetrics.registerFont(TTFont("Barlow", FD+"Barlow-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Barlow-Bold", FD+"Barlow-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("BarlowCond", FD+"BarlowCondensed-Medium.ttf"))
    pdfmetrics.registerFont(TTFont("BarlowCond-SB", FD+"BarlowCondensed-SemiBold.ttf"))
    pdfmetrics.registerFont(TTFont("BarlowCond-Bold", FD+"BarlowCondensed-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("BarlowCond-XBold", FD+"BarlowCondensed-ExtraBold.ttf"))
    _REG = True

# palette (locked)
PAGE_W, PAGE_H = 792, 542
BG     = HexColor("#0e0e0f")
PANEL  = HexColor("#1a1a1b")
STROKE = HexColor("#34343a")
WHITE  = HexColor("#f4f3f1")
GRAY   = HexColor("#a3a2a0")
GRAY2  = HexColor("#6f6e6c")
RED    = HexColor("#e8442a")
BLUE   = HexColor("#3f7fe0")
GREEN  = HexColor("#46c97e")
LINK   = HexColor("#5a9bff")
PEACH  = HexColor("#ffe6df")


def render(inp, res, out_path):
    _register_fonts()
    c = canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
    M = 26
    US = inp.usd_symbol

    def text(x, y, s, font="Barlow", size=9, color=WHITE, anchor="left", tracking=0):
        c.setFont(font, size); c.setFillColor(color)
        if tracking and anchor == "left":
            cx = x
            for ch in s:
                c.drawString(cx, y, ch); cx += stringWidth(ch, font, size) + tracking
            return
        if anchor == "left": c.drawString(x, y, s)
        elif anchor == "middle": c.drawCentredString(x, y, s)
        elif anchor == "right": c.drawRightString(x, y, s)

    def bgfill():
        c.setFillColor(BG); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    def lightning(cx, cy, h, color):
        c.setFillColor(color)
        s = h/14.0
        pts = [(7,14),(3,7),(6,7),(4,0),(11,8),(7,8),(9,14)]
        p = c.beginPath()
        p.moveTo(cx+(pts[0][0]-6)*s, cy+(pts[0][1]-7)*s)
        for (xx,yy) in pts[1:]:
            p.lineTo(cx+(xx-6)*s, cy+(yy-7)*s)
        p.close(); c.drawPath(p, fill=1, stroke=0)

    def header(title, subtitle, badge=None):
        lightning(M+6, PAGE_H-30, 22, RED)
        hx = M + 20
        c.setFillColor(WHITE); c.setFont("BarlowCond-XBold", 18); c.drawString(hx, PAGE_H-30, "Power")
        wpx = hx + stringWidth("Power", "BarlowCond-XBold", 18)
        c.setFillColor(RED); c.drawString(wpx, PAGE_H-30, "Fix")
        text(hx, PAGE_H-42, "R E P A I R .   R E I N V E N T E D .", "Barlow", 5.6, GRAY2)
        text(PAGE_W/2, PAGE_H-26, title, "BarlowCond-XBold", 17, WHITE, "middle")
        text(PAGE_W/2, PAGE_H-40, subtitle, "Barlow", 8, GRAY, "middle")
        if badge:
            bw_, bh_ = 128, 30
            c.setFillColor(RED); c.rect(PAGE_W-M-bw_, PAGE_H-42, bw_, bh_, fill=1, stroke=0)
            text(PAGE_W-M-bw_/2, PAGE_H-32, badge, "BarlowCond-XBold", 13, WHITE, "middle")

    # ============ PAGE 1 ============
    bgfill()
    header("POWERPATCH \u2014 CASE STUDY #%d" % inp.case_number,
           inp.location_line, badge="%d\u00d7 M\u00c1S R\u00c1PIDO" % res.speed_multiple)

    # stats row
    sr_top = PAGE_H-58; sr_h = 40
    rate_disp = "%s%.2f/m2 *" % (US, res.gov_rate_per_m2_usd)
    stats = [
        ("BACHE REAL", "%.2f m2" % res.pothole_m2),
        ("ZONA DE CORTE (%d\u00d7)" % int(res.cut_multiplier), "%.2f m2" % res.cut_zone_m2),
        ("EXPANSI\u00d3N DE HUELLA", res.footprint_expansion_pct),
        ("POWERPATCH APLICADO", "1 caja \u00b7 20 kg"),
        ("TARIFA GOB. (TODO INCL.)", rate_disp),
    ]
    n=len(stats); cw=(PAGE_W-2*M)/n
    c.setFillColor(PANEL); c.rect(M, sr_top-sr_h, PAGE_W-2*M, sr_h, fill=1, stroke=0)
    c.setStrokeColor(STROKE); c.setLineWidth(0.8); c.rect(M, sr_top-sr_h, PAGE_W-2*M, sr_h, fill=0, stroke=1)
    for i,(lab,val) in enumerate(stats):
        x=M+i*cw
        if i>0: c.setStrokeColor(STROKE); c.line(x, sr_top-sr_h+6, x, sr_top-6)
        text(x+12, sr_top-15, lab, "Barlow", 5.6, GRAY, tracking=0.4)
        text(x+12, sr_top-31, val, "BarlowCond-Bold", 14, WHITE)

    sec_y = sr_top-sr_h-15
    text(M, sec_y, "C O M P A R A C I \u00d3 N   D E   C O S T O   G U B E R N A M E N T A L   \u2014   M I S M A   R E P A R A C I \u00d3 N ,   D O S   M \u00c9 T O D O S", "Barlow", 6.4, GRAY2)

    # comparison columns
    col_top = sec_y-8; col_h = 168; col_gap = 8
    col_w = (PAGE_W-2*M-col_gap)/2
    def column(x, accent, num, title, subtitle, rows, total, time_label, crew_label):
        c.setFillColor(PANEL); c.rect(x, col_top-col_h, col_w, col_h, fill=1, stroke=0)
        c.setFillColor(accent); c.rect(x, col_top-3, col_w, 3, fill=1, stroke=0)
        px=x+18; py=col_top-20
        text(px,py,num,"Barlow-Bold",8.5,accent)
        text(px,py-16,title,"BarlowCond-XBold",16.5,WHITE)
        text(px,py-30,subtitle,"Barlow",7.4,GRAY)
        ry=py-50
        for lab,val in rows:
            text(px,ry,lab,"Barlow",8,GRAY)
            text(x+col_w-18,ry,val,"Barlow-Bold",8,WHITE,"right")
            c.setStrokeColor(STROKE); c.setLineWidth(0.5); c.line(px, ry-5, x+col_w-18, ry-5)
            ry-=15
        total_y=ry-14
        text(px,total_y,total,"BarlowCond-XBold",27,WHITE)
        text(px, col_top-col_h+12, time_label, "Barlow-Bold",8,accent)
        text(x+col_w-18, col_top-col_h+12, crew_label, "Barlow",7.4,GRAY,"right")

    box_star = " *" if res.box_is_backcalculated else ""
    column(M, RED, "01", inp.method_label, inp.method_subtitle,
        [("Zona de reparaci\u00f3n","%.2f m2 (%d\u00d7 bache)" % (res.cut_zone_m2, int(res.cut_multiplier))),
         ("Tarifa (contrato gob., todo incl.)", rate_disp),
         ("Cuadrilla","Cuadrilla completa + maquinaria")],
        "%s%.2f" % (US, res.conventional_total_usd), res.conv_time_label, "CUADRILLA COMPLETA")

    column(M+col_w+col_gap, BLUE, "02", "POWERPATCH",
        "Rellena solo el bache real \u2014 sin expandir \u00b7 sin cortar",
        [("\u00c1rea rellenada","%.2f m2 (bache real)" % res.pothole_m2),
         ("Material","1 caja \u00b7 20 kg"),
         ("Precio/caja (posicionado, ver nota)" if res.box_is_backcalculated else "Precio/caja",
          "%s%.2f%s" % (US, res.powerpatch_box_usd, box_star)),
         ("Cuadrilla","2 personas \u00b7 sin maquinaria")],
        "%s%.2f" % (US, res.powerpatch_box_usd), res.pp_time_label, "2 PERSONAS")

    # savings bar
    sb_top = col_top-col_h-8; sb_h=32
    c.setFillColor(RED); c.rect(M, sb_top-sb_h, PAGE_W-2*M, sb_h, fill=1, stroke=0)
    text(M+16, sb_top-13, "POWERPATCH   %d\u00d7 M\u00c1S R\u00c1PIDO" % res.speed_multiple, "BarlowCond-XBold", 13, WHITE)
    text(M+16, sb_top-25, "2 PERSONAS \u00b7 ~3 MIN \u00b7 SIN MAQUINARIA \u00b7 SIN CIERRE DE V\u00cdA", "Barlow", 6.4, PEACH, tracking=0.3)
    text(PAGE_W-M-16, sb_top-13, "%s%.2f / CAJA" % (US, res.powerpatch_box_usd), "BarlowCond-XBold", 15, WHITE, "right")
    text(PAGE_W-M-16, sb_top-25, "vs %s%.2f \u00b7 ~1h 45min %s" % (US, res.conventional_total_usd, inp.method_label.lower()), "Barlow", 6.6, PEACH, "right")

    # savings stats
    ss_label_y = sb_top-sb_h-13
    text(M, ss_label_y, "A H O R R O   V S   P O W E R P A T C H", "Barlow-Bold", 7, WHITE, tracking=0.3)
    ss_top = ss_label_y-8; ss_h=46
    c.setFillColor(PANEL); c.rect(M, ss_top-ss_h, PAGE_W-2*M, ss_h, fill=1, stroke=0)
    c.setStrokeColor(STROKE); c.setLineWidth(0.8); c.rect(M, ss_top-ss_h, PAGE_W-2*M, ss_h, fill=0, stroke=1)
    ss=[("%s%d" % (US, round(res.savings_usd)), "vs %s \u2014 todo incl." % inp.method_label.title(), GREEN),
        ("%d%%" % round(res.savings_pct), "m\u00e1s barato \u00b7 todo incl. vs todo incl.", GREEN),
        ("%d\u00d7" % res.speed_multiple, "m\u00e1s r\u00e1pido que reparaci\u00f3n convencional", RED)]
    sw=(PAGE_W-2*M)/3
    for i,(big,small,col) in enumerate(ss):
        x=M+i*sw
        if i>0: c.setStrokeColor(STROKE); c.line(x, ss_top-ss_h+7, x, ss_top-7)
        text(x+sw/2, ss_top-22, big, "BarlowCond-XBold", 21, col, "middle")
        text(x+sw/2, ss_top-37, small, "Barlow", 6.6, GRAY, "middle")

    # feature callouts
    feat_top = ss_top-ss_h-12
    feats=[("MINUTOS, NO HORAS","~3 min vs ~1h 45min de la cuadrilla convencional."),
           ("SIN MAQUINARIA","Equipo pesado y combustible \u2014 eliminados."),
           ("SIN CIERRE DE V\u00cdA","La calle permanece abierta. Cero interrupci\u00f3n.")]
    fw=(PAGE_W-2*M)/3
    for i,(t,d) in enumerate(feats):
        x=M+i*fw
        c.setFillColor(RED); c.rect(x, feat_top-26, 2, 26, fill=1, stroke=0)
        text(x+12, feat_top-9, t, "Barlow-Bold", 7.8, WHITE)
        text(x+12, feat_top-20, d, "Barlow", 6.6, GRAY)

    # ---- clickable sources footnote ----
    src_top = feat_top-26-12
    c.setStrokeColor(STROKE); c.setLineWidth(0.5); c.line(M, src_top, PAGE_W-M, src_top)
    fy = src_top-11

    def seg(x, y, s, font, size, color):
        c.setFont(font, size); c.setFillColor(color); c.drawString(x, y, s)
        return x + stringWidth(s, font, size)
    def linkseg(x, y, label, url, size=6.6):
        c.setFont("Barlow", size); c.setFillColor(LINK); c.drawString(x, y, label)
        w = stringWidth(label, "Barlow", size)
        if url: c.linkURL(url, (x, y-2, x+w, y+7), relative=0)
        return x + w

    # line 1: the * + primary source
    if inp.primary_source:
        x = seg(M, fy, "* ", "Barlow-Bold", 6.6, RED)
        ps = inp.primary_source
        rate_txt = "Tarifa %s%.2f/m2" % (US, res.gov_rate_per_m2_usd)
        if inp.gov_rate_per_m2_local:
            rate_txt += " (%s%.2f/m2)" % (inp.currency_code, inp.gov_rate_per_m2_local)
        x = seg(x, fy, "%s, todo incluido \u2014 %s. Verificar: " % (rate_txt, ps.detail), "Barlow", 6.6, GRAY)
        if ps.url: linkseg(x, fy, ps.label, ps.url)
        else: seg(x, fy, ps.label + " (sin URL p\u00fablico)", "Barlow", 6.6, GRAY)

    # line 2: cross-checks + FX
    fy2 = fy-11
    if inp.cross_checks or inp.fx_source:
        x = seg(M, fy2, "Cross-checks: ", "Barlow", 6.6, GRAY)
        for i, cc in enumerate(inp.cross_checks):
            x = seg(x, fy2, cc.detail + " ", "Barlow", 6.6, GRAY)
            if cc.url: x = linkseg(x, fy2, "(%s)" % cc.label, cc.url)
            else: x = seg(x, fy2, "(%s)" % cc.label, "Barlow", 6.6, GRAY)
            x = seg(x, fy2, " \u00b7 ", "Barlow", 6.6, GRAY)
        if inp.fx_source:
            x = seg(x, fy2, "FX %s%.2f=%s1 " % (inp.currency_code, inp.fx_local_per_usd, US), "Barlow", 6.6, GRAY)
            if inp.fx_source.url: linkseg(x, fy2, "(%s)" % inp.fx_source.label, inp.fx_source.url)

    # line 3: honesty note
    fy3 = fy2-11
    note = inp.extra_footnote
    if res.box_is_backcalculated and not note:
        note = ("Precio/caja PowerPatch (%s%.2f) calibrado para %d%% m\u00e1s barato (posicionamiento, no precio de cat\u00e1logo confirmado)."
                % (US, res.powerpatch_box_usd, round(res.savings_pct)))
    if note:
        text(M, fy3, note, "Barlow", 6.3, GRAY2)

    c.showPage()

    # ============ PAGE 2: photos ============
    bgfill()
    header("AS\u00cd SE VE EL M\u00c9TODO CONVENCIONAL EN %s" % inp.country.upper(),
           inp.photos_subtitle if hasattr(inp, "photos_subtitle") and inp.photos_subtitle else
           "Corte y relleno real \u00b7 m\u00e9todo convencional documentado")

    if inp.photos:
        img_top=PAGE_H-58; img_h=378; img_gap=14
        nph = min(len(inp.photos), 2)
        img_w=(PAGE_W-2*M-img_gap)/2 if nph==2 else (PAGE_W-2*M)
        from PIL import Image as PILImage
        def draw_photo(path,x,y_top,w,h,tag,caption):
            pim=PILImage.open(path); iw,ih=pim.size
            tr=w/h; sr=iw/ih
            if sr>tr:
                nw=ih*tr; ox=(iw-nw)/2; crop=(ox,0,ox+nw,ih)
            else:
                nh=iw/tr; oy=(ih-nh)/2; crop=(0,oy,iw,oy+nh)
            tmp=os.path.join(HERE,"output","_fit_%d.jpg" % (abs(hash(path))%99999))
            pim.crop(tuple(int(v) for v in crop)).resize((int(w*2),int(h*2))).save(tmp,quality=90)
            c.drawImage(tmp,x,y_top-h,width=w,height=h)
            c.setFillColor(RED); c.rect(x,y_top-h,84,16,fill=1,stroke=0)
            text(x+42,y_top-h+5,tag,"Barlow-Bold",7,WHITE,"middle")
            c.setFillColor(PANEL); c.rect(x,y_top-h-24,w,24,fill=1,stroke=0)
            text(x+10,y_top-h-16,caption,"Barlow",6.8,WHITE)
        for i,(path,tag,caption) in enumerate(inp.photos[:2]):
            x = M + i*(img_w+img_gap)
            draw_photo(path, x, img_top, img_w, img_h, tag, caption)

        note_y2 = img_top-img_h-24-16
        text(M, note_y2, "Estas fotos documentan el m\u00e9todo convencional real en %s. La aplicaci\u00f3n de PowerPatch en la p\u00e1gina 1 es proyectada \u2014 no desplegada en este sitio." % inp.country, "Barlow", 7, GRAY)
    else:
        text(PAGE_W/2, PAGE_H/2, "(sin fotos cargadas)", "Barlow", 12, GRAY2, "middle")

    c.showPage()
    c.save()
    return out_path
