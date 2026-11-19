#!/usr/bin/env python3
"""Fetch the public GitHub contribution calendar and derive yearly activity statistics."""
import datetime, json, os, re, sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup

USERNAME=os.environ.get("GH_PROFILE_USER","aymanechoukri")
URL=f"https://github.com/users/{USERNAME}/contributions"
OUTPUT=Path(__file__).resolve().parents[1]/"data"/"contributions.json"

def fetch_days():
    response=requests.get(URL,headers={"User-Agent":"profile-readme-bot/1.0"},timeout=30)
    response.raise_for_status()
    soup=BeautifulSoup(response.text,"html.parser")
    cells=soup.select("td.ContributionCalendar-day")
    if not cells:
        raise RuntimeError("GitHub contribution calendar markup changed or no data was returned.")
    days=[]
    for cell in cells:
        day_date=cell.get("data-date")
        if not day_date: continue
        tooltip=soup.find("tool-tip",attrs={"for":cell.get("id")}) if cell.get("id") else None
        tooltip_text=tooltip.get_text(strip=True) if tooltip else ""
        match=re.match(r"(\d+)",tooltip_text)
        count=0 if re.search(r"no contributions",tooltip_text,re.I) else int(match.group(1)) if match else 0
        days.append({"date":day_date,"count":count,"level":int(cell.get("data-level") or 0)})
    days.sort(key=lambda item:item["date"])
    return days

def streak(days):
    idx=len(days)-1
    if idx>=0 and days[idx]["count"]==0: idx-=1
    count=0
    while idx>=0 and days[idx]["count"]>0:
        count+=1; idx-=1
    return count

def build(days):
    if not days: raise RuntimeError("No contribution days found.")
    total=sum(d["count"] for d in days)
    active=sum(1 for d in days if d["count"]>0)
    best=max(days,key=lambda d:d["count"])
    monthly={}
    for d in days:
        key=d["date"][:7]; monthly[key]=monthly.get(key,0)+d["count"]
    runs=[]; current=0; longest=0
    for d in days:
        current=current+1 if d["count"]>0 else 0
        longest=max(longest,current)
    return {
      "username":USERNAME,
      "generated_at":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
      "range":{"start":days[0]["date"],"end":days[-1]["date"]},
      "total_contributions":total,
      "active_days":active,
      "avg_per_active_day":round(total/active,1) if active else 0,
      "current_streak":{"length":streak(days)},
      "longest_streak":{"length":longest},
      "best_day":{"date":best["date"],"count":best["count"]},
      "monthly":[{"month":k,"total":v} for k,v in sorted(monthly.items())],
      "days":days
    }

if __name__=="__main__":
    days=fetch_days()
    data=build(days)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(data,indent=2),encoding="utf-8")
    print(f"Wrote {OUTPUT}: {data['total_contributions']} contributions; current streak {data['current_streak']['length']}")
