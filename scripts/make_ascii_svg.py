"""Create a high-resolution monochrome ASCII SVG from the prepared portrait."""
from PIL import Image
import html, os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,"assets","aymane-profile-prepped.png")
OUT=sys.argv[2] if len(sys.argv)>2 else os.path.join(ROOT,"assets","aymane-ascii.svg")
COLS=int(os.environ.get("COLS","180")); width=800; cw=width/COLS; ch=cw*15/8; rows=round(COLS*8/15)
ramp=" .`:-=+*cs#%@"; im=Image.open(SRC).convert("L").resize((COLS,rows),Image.Resampling.LANCZOS); px=im.load()
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{rows*ch:.1f}">']
for y in range(rows):
 line=[]
 for x in range(COLS):
  lum=(px[x,y]/255.0)**1.12
  if lum>=.80: line.append(" ")
  else: line.append(ramp[max(0,min(len(ramp)-1,round((1-lum)*(len(ramp)-1))))])
 parts.append(f'<text xml:space="preserve" x="0" y="{y*ch+ch*.74:.1f}" font-size="{ch*.86:.1f}" textLength="{width}" lengthAdjust="spacing">{html.escape("".join(line))}</text>')
parts.append("</svg>")
open(OUT,"w",encoding="utf-8").write("".join(parts)); print("wrote",OUT)
