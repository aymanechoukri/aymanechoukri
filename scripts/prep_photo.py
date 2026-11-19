"""Prepare a portrait for ASCII conversion using background removal and edge-preserving contrast."""
import os, sys, cv2, numpy as np
from PIL import Image
from rembg import remove
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,"assets","aymane-profile-avatar.jpg")
OUT=sys.argv[2] if len(sys.argv)>2 else os.path.join(ROOT,"assets","aymane-profile-prepped.png")
cut=remove(Image.open(SRC).convert("RGBA"))
rgb=np.asarray(cut.convert("RGB")); alpha=np.asarray(cut.getchannel("A"))
gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY); smooth=gray
for _ in range(3): smooth=cv2.bilateralFilter(smooth,9,40,9)
subject=smooth[alpha>128]
if not subject.size: raise ValueError("No portrait subject detected.")
lo,hi=np.percentile(subject,[2,92]); hi=max(hi,lo+1)
tone=np.clip((smooth.astype(np.float32)-lo)/(hi-lo),0,1)
fine=cv2.GaussianBlur(smooth,(0,0),1.5).astype(np.float32)
coarse=cv2.GaussianBlur(smooth,(0,0),6).astype(np.float32)
lines=np.clip((coarse-fine)/40.0,0,1)
out=np.clip(tone-.55*lines,0,1)*255
mask=cv2.GaussianBlur(alpha.astype(np.float32)/255.0,(0,0),1.0)
out=out*mask+255*(1-mask)
ys,xs=np.where(alpha>20); side=max(xs.max()-xs.min(),ys.max()-ys.min())+60
cx,cy=(xs.min()+xs.max())//2,(ys.min()+ys.max())//2
canvas=np.full((side,side),255,np.uint8); x0,y0=cx-side//2,cy-side//2
sx0,sy0=max(x0,0),max(y0,0); sx1,sy1=min(x0+side,out.shape[1]),min(y0+side,out.shape[0])
canvas[sy0-y0:sy1-y0,sx0-x0:sx1-x0]=out[sy0:sy1,sx0:sx1].astype(np.uint8)
Image.fromarray(canvas,mode="L").save(OUT); print("wrote",OUT)
