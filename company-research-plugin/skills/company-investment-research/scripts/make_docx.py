#!/usr/bin/env python3
"""5페이지 한국어 투자검토 보고서 (.docx) 생성기"""
import argparse, json
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

C_PRIMARY="C0392B"; C_DARK="1F2A44"; C_GREY="5A6478"; C_LIGHT="F4F6FA"; C_BORDER="CCD2DD"; C_GREEN="27AE60"
KFONT = '맑은 고딕'

def set_cell_bg(cell,color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'),color)
    tcPr.append(shd)

def set_cell_borders(cell, color=C_BORDER, sz=6):
    tcPr = cell._tc.get_or_add_tcPr()
    tcB = OxmlElement('w:tcBorders')
    for edge in ('top','left','bottom','right'):
        b = OxmlElement(f'w:{edge}')
        b.set(qn('w:val'),'single'); b.set(qn('w:sz'),str(sz)); b.set(qn('w:color'),color)
        tcB.append(b)
    tcPr.append(tcB)

def add_run(cell, text, *, size=10, bold=False, color=None, align=None):
    p = cell.paragraphs[0] if not cell.paragraphs[0].text else cell.add_paragraph()
    if align is not None: p.alignment = align
    r = p.add_run(text); r.font.name=KFONT; r.font.size=Pt(size); r.bold=bold
    if color: r.font.color.rgb = RGBColor.from_string(color)
    rpr = r._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rpr.append(rf)
    rf.set(qn('w:eastAsia'),KFONT); rf.set(qn('w:hAnsi'),KFONT)
    return r

def add_paragraph(doc, text, *, size=10.5, bold=False, color=None, align=None,
                  space_after=Pt(4), indent=None):
    p = doc.add_paragraph()
    if align is not None: p.alignment = align
    pf = p.paragraph_format; pf.space_after = space_after; pf.line_spacing = 1.3
    if indent is not None: pf.left_indent = indent
    r = p.add_run(text); r.font.name=KFONT; r.font.size=Pt(size); r.bold=bold
    if color: r.font.color.rgb = RGBColor.from_string(color)
    rpr = r._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rpr.append(rf)
    rf.set(qn('w:eastAsia'),KFONT); rf.set(qn('w:hAnsi'),KFONT)
    return p

def section_header(doc, num, title, color=C_PRIMARY):
    p = doc.add_paragraph()
    p.paragraph_format.space_before=Pt(8); p.paragraph_format.space_after=Pt(6)
    r1 = p.add_run(f"  {num}  ")
    r1.font.name=KFONT; r1.font.size=Pt(13); r1.bold=True
    r1.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
    rpr = r1._element.get_or_add_rPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'),color)
    rpr.append(shd)
    r2 = p.add_run(f"  {title}")
    r2.font.name=KFONT; r2.font.size=Pt(13); r2.bold=True
    r2.font.color.rgb = RGBColor.from_string(C_DARK)
    rpr2 = r2._element.get_or_add_rPr()
    rf = OxmlElement('w:rFonts'); rf.set(qn('w:eastAsia'),KFONT); rpr2.append(rf)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'),'single'); bottom.set(qn('w:sz'),'12')
    bottom.set(qn('w:space'),'4'); bottom.set(qn('w:color'),color)
    pBdr.append(bottom); pPr.append(pBdr)

def make_table(doc, rows, cols, widths_cm):
    tbl = doc.add_table(rows=rows, cols=cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER; tbl.autofit=False
    for row in tbl.rows:
        for i, cell in enumerate(row.cells):
            cell.width = Cm(widths_cm[i])
            set_cell_borders(cell)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    tblW = tbl._tbl.tblPr.find(qn('w:tblW'))
    if tblW is None:
        tblW = OxmlElement('w:tblW'); tbl._tbl.tblPr.append(tblW)
    tblW.set(qn('w:w'), str(int(sum(widths_cm)*567))); tblW.set(qn('w:type'),'dxa')
    return tbl

def header_row(tbl, idx, headers, color=C_DARK):
    for i,h in enumerate(headers):
        c = tbl.rows[idx].cells[i]
        set_cell_bg(c, color); c.text=''
        add_run(c, h, size=10, bold=True, color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)

def fill_row(tbl, idx, vals, *, bold=None, colors=None, aligns=None, bgs=None):
    bold=bold or []; colors=colors or {}; aligns=aligns or {}; bgs=bgs or {}
    for i,v in enumerate(vals):
        c = tbl.rows[idx].cells[i]; c.text=''
        if i in bgs: set_cell_bg(c, bgs[i])
        add_run(c, str(v), size=10, bold=(i in bold),
                color=colors.get(i), align=aligns.get(i, WD_ALIGN_PARAGRAPH.CENTER))

def build(data, charts, out):
    doc = Document()
    sec = doc.sections[0]
    sec.page_height=Mm(297); sec.page_width=Mm(210)
    sec.top_margin=Cm(1.6); sec.bottom_margin=Cm(1.6)
    sec.left_margin=Cm(1.8); sec.right_margin=Cm(1.8)
    style = doc.styles['Normal']; style.font.name=KFONT; style.font.size=Pt(10.5)
    rpr = style.element.rPr
    rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf=OxmlElement('w:rFonts'); rpr.append(rf)
    rf.set(qn('w:eastAsia'), KFONT)

    # Title
    tp = doc.add_paragraph(); tp.paragraph_format.space_after=Pt(2)
    r = tp.add_run(f"{data['company']} ({data['ticker']}) 종합 검토 보고서")
    r.font.name=KFONT; r.font.size=Pt(20); r.bold=True
    r.font.color.rgb = RGBColor.from_string(C_DARK)
    rfr = OxmlElement('w:rFonts'); rfr.set(qn('w:eastAsia'),KFONT)
    r._element.get_or_add_rPr().append(rfr)

    sp = doc.add_paragraph(); sp.paragraph_format.space_after=Pt(4)
    sr = sp.add_run(f"최근 1~2주 주요 보도 + 시세·재무지표 종합 │ 작성일: {data['as_of']}")
    sr.font.name=KFONT; sr.font.size=Pt(10); sr.font.color.rgb=RGBColor.from_string(C_GREY)
    pPr = sp._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr'); btm = OxmlElement('w:bottom')
    btm.set(qn('w:val'),'single'); btm.set(qn('w:sz'),'18')
    btm.set(qn('w:space'),'6'); btm.set(qn('w:color'),C_PRIMARY)
    pBdr.append(btm); pPr.append(pBdr)

    # Quote card
    add_paragraph(doc," ",size=4,space_after=Pt(2))
    q = data["quote"]
    qc = make_table(doc,2,4,[4.5,4.0,4.5,4.5])
    labels = [f"현재가 ({data['as_of'][-5:].replace('-','/')})", "시가총액", "52주 최고/최저", "PER / EPS"]
    for i,lbl in enumerate(labels):
        c = qc.rows[0].cells[i]; set_cell_bg(c, C_DARK); c.text=''
        add_run(c, lbl, size=9, bold=True, color="A4C8FF", align=WD_ALIGN_PARAGRAPH.CENTER)
    chg = f"({'▼' if q.get('change_pct',0)<0 else '▲'}{abs(q.get('change_pct',0)):.2f}%)"
    vals = [
        f"₩{q['price_krw']:,}\n{chg}",
        f"{q['market_cap_krw_trn']:.1f}조 원\n(세계 {q.get('global_rank_by_mcap','-')}위)",
        f"{q['week52_high']/10000:.1f}만 / {q['week52_low']/10000:.1f}만",
        f"{q['pe_ratio']:.1f}배 / {q['eps_krw']:,}원"
    ]
    for i,v in enumerate(vals):
        c = qc.rows[1].cells[i]; set_cell_bg(c,"F8FAFD"); c.text=''
        for j,line in enumerate(v.split('\n')):
            if j==0:
                add_run(c,line,size=11,bold=True,color=C_DARK,align=WD_ALIGN_PARAGRAPH.CENTER)
            else:
                add_run(c,line,size=8.5,color=C_GREY,align=WD_ALIGN_PARAGRAPH.CENTER)

    # Exec summary
    add_paragraph(doc," ",size=2,space_after=Pt(2))
    et = make_table(doc,1,1,[17.5])
    ec = et.rows[0].cells[0]; set_cell_bg(ec, C_LIGHT)
    tcPr = ec._tc.get_or_add_tcPr()
    ex = tcPr.find(qn('w:tcBorders'))
    if ex is not None: tcPr.remove(ex)
    tcB = OxmlElement('w:tcBorders')
    for edge,(c,s) in [('top',(C_BORDER,4)),('right',(C_BORDER,4)),('bottom',(C_BORDER,4)),('left',(C_PRIMARY,24))]:
        b = OxmlElement(f'w:{edge}')
        b.set(qn('w:val'),'single'); b.set(qn('w:sz'),str(s)); b.set(qn('w:color'),c)
        tcB.append(b)
    tcPr.append(tcB)
    ec.text=''; add_run(ec,"■ 핵심 한 줄 요약",size=11,bold=True,color=C_PRIMARY)
    for b in data.get("executive_summary",[]):
        p = ec.add_paragraph()
        p.paragraph_format.left_indent=Cm(0.4); p.paragraph_format.space_after=Pt(2)
        r = p.add_run("• "+b); r.font.name=KFONT; r.font.size=Pt(10)
        r.font.color.rgb = RGBColor.from_string(C_DARK)

    # ① 분기 손익
    section_header(doc, "①", "분기 실적 — 최근 4개 분기")
    qs = data["quarterly_pnl_krw_trn"]
    t1 = make_table(doc, 6, 6, [3.5,2.6,2.6,2.6,2.6,3.6])
    header_row(t1, 0, ["구분 (조 원)"]+[q["quarter"] for q in qs]+["YoY 증감률"])
    rev=[q["revenue"] for q in qs]; op=[q["operating_profit"] for q in qs]
    ni=[q["net_income"] for q in qs]; eb=[q.get("ebitda",0) for q in qs]
    om = [o/r*100 for o,r in zip(op,rev)]
    def yoy(n,o): return f"+{(n/o-1)*100:.0f}%" if o>0 else "-"
    rows = [
        ("매출액",*[f"{x:.2f}" for x in rev], yoy(rev[-1],rev[0])),
        ("영업이익",*[f"{x:.2f}" for x in op], yoy(op[-1],op[0])),
        ("영업이익률",*[f"{x:.1f}%" for x in om], f"+{om[-1]-om[0]:.0f}%p"),
        ("당기순이익",*[f"{x:.2f}" for x in ni], yoy(ni[-1],ni[0])),
        ("EBITDA",*[f"{x:.2f}" for x in eb], yoy(eb[-1],eb[0])),
    ]
    for i,row in enumerate(rows,1):
        fill_row(t1,i,row, bold=[0,4], colors={4:C_PRIMARY,5:C_GREEN},
                 bgs={4:"FFF4F1"} if i in (1,2,4) else {},
                 aligns={0:WD_ALIGN_PARAGRAPH.LEFT})
    add_paragraph(doc,"↳ 출처: 구글파이낸스 분기 손익계산서",size=8.5,color=C_GREY)

    img = charts/"q_perf.png"
    if img.exists():
        p = doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(img), width=Cm(15.5))

    add_paragraph(doc,"■ 핵심 포인트",size=10.5,bold=True,color=C_DARK)
    for pt in data.get("key_points",[]):
        add_paragraph(doc,"• "+pt, size=10, indent=Cm(0.4), space_after=Pt(2))

    doc.add_page_break()

    # ② 시세·수급
    section_header(doc, "②", "시세 · 수급 동향")
    t2 = make_table(doc, 6, 4, [3.5,5.5,3.5,5.0])
    header_row(t2, 0, ["항목","값","항목","값"])
    qrows = [
        ("현재가", f"₩{q['price_krw']:,} ({chg})", "시가총액", f"{q['market_cap_krw_trn']:.1f}조 원"),
        ("52주 최고", f"₩{q['week52_high']:,}", "52주 최저", f"₩{q['week52_low']:,}"),
        ("PER", f"{q['pe_ratio']:.1f}배", "EPS", f"{q['eps_krw']:,}원"),
        ("배당수익률", f"{q.get('dividend_yield_pct',0):.2f}%", "거래량", f"{q['volume']:,}"),
        ("외국인", data.get("foreign_flow","-"), "기관", data.get("institutional_flow","-")),
    ]
    for i,row in enumerate(qrows,1):
        fill_row(t2,i,row, bold=[0,2],
                 aligns={k:WD_ALIGN_PARAGRAPH.LEFT for k in (0,1,2,3)},
                 bgs={0:C_LIGHT,2:C_LIGHT})
    img = charts/"price.png"
    if img.exists():
        p = doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(img), width=Cm(15.5))
    for pt in data.get("supply_demand_bullets",[]):
        add_paragraph(doc,"• "+pt, size=10, indent=Cm(0.4), space_after=Pt(2))

    # ③ 시장 동향
    section_header(doc, "③", "시장·사업 동향")
    mm = data.get("memory_market_rows", [])
    if mm:
        t3 = make_table(doc, len(mm)+1, 3, [3.8,5.5,8.2])
        header_row(t3, 0, ["품목/주제","동향","시사점"])
        for i,row in enumerate(mm,1):
            fill_row(t3,i,row,bold=[0],
                     aligns={0:WD_ALIGN_PARAGRAPH.CENTER,1:WD_ALIGN_PARAGRAPH.LEFT,2:WD_ALIGN_PARAGRAPH.LEFT},
                     bgs={0:C_LIGHT})

    doc.add_page_break()

    # ④ 컨센서스 · SWOT
    section_header(doc, "④", "증권가 컨센서스 및 리스크")
    cr = data.get("consensus_rows",[])
    if cr:
        t4 = make_table(doc, len(cr)+1, 4, [3.5,4.2,4.5,5.3])
        header_row(t4, 0, ["증권사","투자의견","목표주가","주요 논거"])
        for i,row in enumerate(cr,1):
            color = {1:C_PRIMARY} if "하향" in str(row[1]) or "보유" in str(row[1]) else {}
            fill_row(t4,i,row, bold=[0,1,2],
                     aligns={0:WD_ALIGN_PARAGRAPH.LEFT,1:WD_ALIGN_PARAGRAPH.CENTER,2:WD_ALIGN_PARAGRAPH.CENTER,3:WD_ALIGN_PARAGRAPH.LEFT},
                     colors=color, bgs={0:C_LIGHT})
    img = charts/"margins.png"
    if img.exists():
        p = doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(img), width=Cm(15.5))
    tw, hw = data.get("tailwinds",[]), data.get("headwinds",[])
    if tw or hw:
        add_paragraph(doc,"■ 기회 vs. 리스크",size=10.5,bold=True,color=C_DARK)
        n = max(len(tw),len(hw))
        sw = make_table(doc, n+1, 2, [8.75,8.75])
        header_row(sw, 0, ["기회 (Tailwinds)","리스크 (Headwinds)"])
        for i in range(n):
            set_cell_bg(sw.rows[i+1].cells[0],"EAF6EE")
            set_cell_bg(sw.rows[i+1].cells[1],"FDEDEB")
            sw.rows[i+1].cells[0].text=''; sw.rows[i+1].cells[1].text=''
            if i<len(tw): add_run(sw.rows[i+1].cells[0], "✓ "+tw[i], size=10, color=C_DARK, align=WD_ALIGN_PARAGRAPH.LEFT)
            if i<len(hw): add_run(sw.rows[i+1].cells[1], "△ "+hw[i], size=10, color=C_DARK, align=WD_ALIGN_PARAGRAPH.LEFT)

    # ⑤ 기타 이슈
    section_header(doc, "⑤", "그룹 영향 · 사회·문화적 이슈")
    ot = data.get("other_issues_rows",[])
    if ot:
        t5 = make_table(doc, len(ot)+1, 3, [2.8,7.0,7.7])
        header_row(t5, 0, ["분류","이슈 요약","해석·시사점"])
        for i,row in enumerate(ot,1):
            fill_row(t5,i,row,bold=[0],
                     aligns={0:WD_ALIGN_PARAGRAPH.CENTER,1:WD_ALIGN_PARAGRAPH.LEFT,2:WD_ALIGN_PARAGRAPH.LEFT},
                     bgs={0:C_LIGHT})

    # 출처
    add_paragraph(doc," ",size=2,space_after=Pt(4))
    ft = make_table(doc, 1, 1, [17.5])
    fc = ft.rows[0].cells[0]; set_cell_bg(fc,"FAFBFD"); fc.text=''
    add_run(fc,"출처 및 면책",size=9,bold=True,color=C_DARK)
    for s in data.get("sources",[]):
        p = fc.add_paragraph(); p.paragraph_format.space_after=Pt(1)
        r = p.add_run("• "+s if not s.startswith('※') else s)
        r.font.name=KFONT; r.font.size=Pt(8.5); r.font.color.rgb = RGBColor.from_string(C_GREY)

    p = doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_before=Pt(6)
    r = p.add_run(f"Prepared by {data.get('author_email','')}")
    r.font.name=KFONT; r.font.size=Pt(8.5)
    r.font.color.rgb = RGBColor.from_string(C_GREY); r.italic=True

    doc.save(out); print(f"Saved: {out}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--charts", required=True); ap.add_argument("--out", required=True)
    args = ap.parse_args()
    data = json.load(open(args.data, encoding='utf-8'))
    build(data, Path(args.charts), args.out)

if __name__ == "__main__":
    main()
