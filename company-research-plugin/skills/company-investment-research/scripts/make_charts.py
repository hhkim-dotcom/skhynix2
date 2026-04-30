#!/usr/bin/env python3
"""차트 PNG 생성 — 분기 실적·수익성·주가"""
import argparse, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

C_RED, C_NAVY, C_BLUE = '#E74C3C', '#1F2A44', '#3F7DD7'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
    'axes.spines.top':False,'axes.spines.right':False})

def chart_q_perf(data, out):
    qs = data["quarterly_pnl_krw_trn"]
    quarters = [q["quarter"] for q in qs]
    rev, op = [q["revenue"] for q in qs], [q["operating_profit"] for q in qs]
    fig,ax = plt.subplots(figsize=(7,3.6),dpi=180)
    x = np.arange(len(quarters)); w=0.38
    b1 = ax.bar(x-w/2, rev, w, label='Revenue (KRW tn)', color=C_NAVY)
    b2 = ax.bar(x+w/2, op, w, label='Operating Profit (KRW tn)', color=C_RED)
    for bars,vals in [(b1,rev),(b2,op)]:
        for bar,v in zip(bars,vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(vals)*0.025,
                f'{v:.1f}', ha='center', fontsize=9, fontweight='bold', color=bar.get_facecolor())
    ax.set_xticks(x); ax.set_xticklabels(quarters)
    ax.set_ylabel('KRW Trillion')
    ax.set_title(f'{data.get("company_en","Company")} Quarterly Revenue & Operating Profit',
                 fontsize=12, fontweight='bold', pad=12, color=C_NAVY)
    ax.set_ylim(0, max(rev)*1.20); ax.legend(loc='upper left', frameon=False)
    ax.grid(axis='y', linestyle='--', alpha=0.35)
    plt.tight_layout(); plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='white'); plt.close()

def chart_margins(data, out):
    qs = data["quarterly_pnl_krw_trn"]
    q = [q["quarter"] for q in qs]
    om = [x["operating_profit"]/x["revenue"]*100 for x in qs]
    nm = [x["net_income"]/x["revenue"]*100 for x in qs]
    fig,ax = plt.subplots(figsize=(7,3.2),dpi=180)
    ax.plot(q, om, marker='o', linewidth=2.5, markersize=8, color=C_RED, label='Operating Margin %')
    ax.plot(q, nm, marker='s', linewidth=2.5, markersize=8, color=C_BLUE, label='Net Margin %', linestyle='--')
    for i,(a,b) in enumerate(zip(om,nm)):
        ax.text(i,a+2.5,f'{a:.0f}%',ha='center',fontsize=9,color=C_RED,fontweight='bold')
        ax.text(i,b-4.5,f'{b:.0f}%',ha='center',fontsize=9,color=C_BLUE,fontweight='bold')
    ax.set_ylabel('Margin %')
    ax.set_ylim(min(min(om),min(nm))-10, max(max(om),max(nm))+15)
    ax.set_title('Profitability Trend', fontsize=12, fontweight='bold', pad=12, color=C_NAVY)
    ax.legend(loc='lower right', frameon=False)
    ax.grid(axis='y', linestyle='--', alpha=0.35)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    plt.tight_layout(); plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='white'); plt.close()

def chart_price(data, out):
    if not data.get("price_history"): return
    ph = data["price_history"]
    dates = [p["date"] for p in ph]; prices = [p["price_krw"]/1000 for p in ph]
    fig,ax = plt.subplots(figsize=(7,3.2),dpi=180)
    ax.fill_between(range(len(dates)), prices, alpha=0.18, color=C_RED)
    ax.plot(range(len(dates)), prices, marker='o', color=C_RED, linewidth=2.5, markersize=7)
    for i,p in enumerate(prices):
        ax.text(i, p+max(prices)*0.02, f'{p/1000:.2f}M', ha='center', fontsize=8, color=C_NAVY)
    ax.set_xticks(range(len(dates))); ax.set_xticklabels(dates, fontsize=9)
    ax.set_ylabel('Price (KRW thousands)')
    ax.set_title(f'{data.get("company_en","Company")} Share Price', fontsize=12, fontweight='bold', pad=12, color=C_NAVY)
    ax.set_ylim(min(prices)*0.92, max(prices)*1.08)
    ax.grid(axis='y', linestyle='--', alpha=0.35)
    plt.tight_layout(); plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='white'); plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    data = json.load(open(args.data, encoding='utf-8'))
    od = Path(args.outdir); od.mkdir(parents=True, exist_ok=True)
    chart_q_perf(data, od/"q_perf.png")
    chart_margins(data, od/"margins.png")
    chart_price(data, od/"price.png")
    print(f"Charts written to {od}")

if __name__ == "__main__":
    main()
