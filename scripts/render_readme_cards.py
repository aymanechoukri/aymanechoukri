#!/usr/bin/env python3
"""Render red editorial SVG cards using GitHub contribution data."""
import json, os, urllib.request
from datetime import date, timedelta
from pathlib import Path
from html import escape

ROOT=Path(__file__).resolve().parents[1]
CARDS=ROOT/"cards"
CARDS.mkdir(exist_ok=True)
USER="aymanechoukri"
RED="#B83232"; PAPER="#F4EFE6"; INK="#242321"; MUTED="#756F68"; GOLD="#D9B85A"

def doc(w,h,body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<title>Aymane Chokri — GitHub profile</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&display=swap');
.serif{{font-family:'Instrument Serif',Georgia,serif}} .mono{{font-family:'DM Mono',monospace}}
.rise{{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}} @keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}
@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important}}}}
</style>{body}</svg>'''

def contributions():
    token=os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token: raise RuntimeError("No token available")
    start=(date.today()-timedelta(days=365)).isoformat()
    end=date.today().isoformat()
    query={"query":'query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}',
           "variables":{"login":USER,"from":start+"T00:00:00Z","to":end+"T23:59:59Z"}}
    req=urllib.request.Request("https://api.github.com/graphql",data=json.dumps(query).encode(),
       headers={"Authorization":"Bearer "+token,"Content-Type":"application/json","User-Agent":"profile-readme"})
    with urllib.request.urlopen(req,timeout=25) as res: payload=json.load(res)
    if payload.get("errors"): raise RuntimeError(str(payload["errors"]))
    cal=payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return {"total":cal["totalContributions"],"days":[d for week in cal["weeks"] for d in week["contributionDays"]]}

def hero():
    portrait=["      .-''''-.      ","     /  .--.  \\\\     ","    |  | o o |  |    ","    |  |  ^  |  |    ","     \\\\  '--'  /     ","      '-.__.-'      ","        /||\\\\         ","       /_||_\\\\        "]
    art="".join(f'<text x="38" y="{130+i*13}" class="mono" font-size="10" fill="{RED}">{escape(line)}</text>' for i,line in enumerate(portrait))
    body=f'''<rect width="900" height="260" rx="18" fill="{PAPER}"/><path d="M0 0H900V8H0Z" fill="{RED}"/>
<text x="34" y="48" class="mono" font-size="11" letter-spacing="2" fill="{MUTED}">INDEPENDENT DEVELOPER / MOROCCO</text>
<text x="34" y="105" class="serif rise" font-size="54" fill="{INK}">Aymane Chokri</text>
<text x="34" y="238" class="mono" font-size="11" fill="{MUTED}">BUILD WITH PURPOSE. LEARN IN PUBLIC.</text>{art}
<text x="360" y="151" class="serif" font-size="25" fill="{INK}">I turn ideas into useful</text><text x="360" y="183" class="serif" font-size="25" fill="{RED}">web experiences.</text>
<text x="360" y="216" class="mono" font-size="11" fill="{MUTED}">FRONTEND · BACKEND · CONTINUOUS LEARNING</text>'''
    (CARDS/"hero.svg").write_text(doc(900,260,body),encoding="utf-8")

def worlds():
    entries=[("01","BUILD","Interfaces & applications",RED),("02","CONNECT","APIs & data",INK),("03","LEARN","New tools & ideas","#B08A2E")]
    parts=[]
    for i,(num,title,desc,color) in enumerate(entries):
        x=8+i*300
        parts.append(f'<g class="rise" style="animation-delay:{i*.15}s"><rect x="{x}" y="8" width="284" height="150" rx="12" fill="{PAPER}" stroke="#D9D1C5"/><text x="{x+18}" y="34" class="mono" font-size="10" fill="{MUTED}">{num} / AYMANE&#39;S WORLD</text><text x="{x+18}" y="91" class="serif" font-size="36" fill="{color}">{title}</text><text x="{x+18}" y="122" class="mono" font-size="10" fill="{INK}">{desc}</text></g>')
    (CARDS/"worlds.svg").write_text(doc(900,166,"".join(parts)),encoding="utf-8")

def activity(data):
    buckets=[0]*12
    for item in data["days"]:
        month=int(item["date"][5:7]); buckets[month-1]+=item["contributionCount"]
    maxv=max(buckets) or 1; labels=["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]; bars=[]
    for i,val in enumerate(buckets):
        x=290+i*48; h=85*val/maxv
        bars.append(f'<rect x="{x}" y="{140-h:.1f}" width="27" height="{h:.1f}" rx="3" fill="{RED}" opacity="{.4+.6*val/maxv:.2f}"><animate attributeName="height" from="0" to="{h:.1f}" dur=".7s" begin="{i*.05}s" fill="freeze"/></rect><text x="{x+13}" y="159" text-anchor="middle" class="mono" font-size="8" fill="{MUTED}">{labels[i]}</text>')
    body=f'<rect width="900" height="190" rx="16" fill="{PAPER}"/><text x="28" y="35" class="mono" font-size="10" letter-spacing="2" fill="{MUTED}">THE YEAR IN CONTRIBUTIONS</text><text x="28" y="88" class="serif" font-size="42" fill="{RED}">{data["total"]:,}</text><text x="28" y="111" class="mono" font-size="10" fill="{INK}">CONTRIBUTIONS</text><path d="M260 48V160" stroke="#D9D1C5"/>{"".join(bars)}'
    (CARDS/"activity.svg").write_text(doc(900,190,body),encoding="utf-8")

def heatmap(data):
    days=data["days"][-371:]; cells=[]
    for i,item in enumerate(days):
        x=25+(i//7)*14; y=44+(i%7)*14; count=item["contributionCount"]
        opacity=.12 if count==0 else min(.98,.25+count/12)
        cells.append(f'<rect x="{x}" y="{y}" width="10" height="10" rx="2" fill="{RED}" opacity="{opacity:.2f}"/>')
    body=f'<rect width="900" height="170" rx="16" fill="{PAPER}"/><text x="25" y="27" class="mono" font-size="10" letter-spacing="2" fill="{MUTED}">A YEAR OF SHOWING UP</text>{"".join(cells)}<text x="25" y="158" class="mono" font-size="9" fill="{MUTED}">LESS</text><rect x="70" y="148" width="10" height="10" rx="2" fill="{RED}" opacity=".12"/><rect x="86" y="148" width="10" height="10" rx="2" fill="{RED}" opacity=".45"/><rect x="102" y="148" width="10" height="10" rx="2" fill="{RED}" opacity=".75"/><rect x="118" y="148" width="10" height="10" rx="2" fill="{RED}"/><text x="138" y="158" class="mono" font-size="9" fill="{MUTED}">MORE</text>'
    (CARDS/"heatmap.svg").write_text(doc(900,170,body),encoding="utf-8")

def main():
    hero(); worlds()
    try:
        data=contributions()
        activity(data); heatmap(data)
        (ROOT/"data").mkdir(exist_ok=True)
        (ROOT/"data/contributions.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
    except Exception as exc:
        print("Contribution update skipped:",exc)
        if not (CARDS/"activity.svg").exists():
            activity({"total":0,"days":[]})
            heatmap({"days":[{"contributionCount":0} for _ in range(371)]})
    print("SVG profile cards rendered.")

if __name__=="__main__": main()
