from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from urllib.request import Request, urlopen
import io, math

W,H=1200,630
OUT=Path(__file__).resolve().parents[1]/"og-novedades-iso-sst.jpg"

NAVY=(0,32,91)
TEAL=(0,123,133)
CYAN=(0,194,202)
GREEN=(112,173,71)
YELLOW=(255,182,0)
INK=(37,58,89)
LIGHT=(248,250,252)
WHITE=(255,255,255)

img=Image.new("RGB",(W,H),LIGHT)
px=img.load()
# soft horizontal gradient
for x in range(W):
    t=x/(W-1)
    r=int(248*(1-t)+225*t)
    g=int(250*(1-t)+243*t)
    b=int(252*(1-t)+248*t)
    for y in range(H):
        px[x,y]=(r,g,b)

draw=ImageDraw.Draw(img)

font_paths=[
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]
def fnt(size,bold=True):
    path=font_paths[0 if bold else 1]
    return ImageFont.truetype(path,size)

# Right-side navy field
draw.rounded_rectangle((760,-30,1240,670),radius=90,fill=NAVY)
# subtle arcs/globe
for rad,alpha in [(190,55),(145,45),(105,38)]:
    box=(985-rad,315-rad,985+rad,315+rad)
    draw.ellipse(box,outline=(42,196,210),width=2)
draw.arc((785,55,1175,445),200,340,fill=(30,175,190),width=3)
draw.arc((820,80,1160,420),20,170,fill=(255,182,0),width=3)

# Radar
cx,cy=975,320
for r in (55,105,155):
    draw.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(0,190,205),width=2)
draw.line((cx-160,cy,cx+160,cy),fill=(0,160,178),width=2)
draw.line((cx,cy-160,cx,cy+160),fill=(0,160,178),width=2)
angle=-35*math.pi/180
ex=cx+155*math.cos(angle); ey=cy+155*math.sin(angle)
draw.polygon([(cx,cy),(ex,ey),(cx+145*math.cos(angle+.12),cy+145*math.sin(angle+.12))],fill=(59,220,101))
for x,y,c in [(1035,265,GREEN),(900,365,YELLOW),(1065,390,CYAN),(930,250,WHITE)]:
    draw.ellipse((x-8,y-8,x+8,y+8),fill=c)

# logo from official repository
logo_url="https://raw.githubusercontent.com/movidasst/principal/main/logo-oficial-movida-sst-plus.png"
try:
    req=Request(logo_url,headers={"User-Agent":"MovidaSST-OG"})
    data=urlopen(req,timeout=20).read()
    logo=Image.open(io.BytesIO(data)).convert("RGBA")
    logo.thumbnail((190,190),Image.Resampling.LANCZOS)
    shadow=Image.new("RGBA",(230,230),(0,0,0,0))
    sh=Image.new("RGBA",logo.size,(0,0,0,0)); sh.alpha_composite(logo)
    sh=sh.filter(ImageFilter.GaussianBlur(8))
    shadow.alpha_composite(sh,(20,22))
    img.paste(shadow,(35,20),shadow)
    img.paste(logo,(55,38),logo)
except Exception:
    draw.ellipse((55,38,225,208),fill=TEAL,outline=NAVY,width=8)
    draw.text((95,88),"M+",font=fnt(48),fill=WHITE)

# brand heading
draw.text((260,48),"LA MOVIDA",font=fnt(42),fill=NAVY)
draw.text((260,94),"DE SST+",font=fnt(42),fill=NAVY)
draw.text((260,145),"DE LA REACCIÓN A LA PREVENCIÓN",font=fnt(18),fill=INK)

# main headline
draw.text((60,245),"Novedades",font=fnt(76),fill=NAVY)
draw.text((60,320),"ISO",font=fnt(84),fill=TEAL)
draw.text((215,330),"en",font=fnt(58),fill=NAVY)
draw.text((305,320),"SST",font=fnt(84),fill=GREEN)

# radar pill
draw.rounded_rectangle((60,430,580,500),radius=24,fill=NAVY)
draw.ellipse((80,445,125,490),outline=CYAN,width=3)
draw.ellipse((90,455,115,480),outline=CYAN,width=2)
draw.line((102,467,125,451),fill=GREEN,width=3)
draw.text((145,445),"Radar ISO SST",font=fnt(38),fill=WHITE)

# support text
draw.text((60,515),"Seguimiento de normas y proyectos relevantes",font=fnt(22,False),fill=INK)
draw.text((60,545),"para Seguridad y Salud en el Trabajo",font=fnt(22,False),fill=INK)

# URL bar
draw.rounded_rectangle((60,580,600,620),radius=18,fill=NAVY)
draw.text((85,589),"novedades.movidasst.com",font=fnt(22),fill=WHITE)

# ISO cards
def card(y,num,color):
    x=720
    draw.rounded_rectangle((x,y,x+300,y+92),radius=18,fill=WHITE,outline=(220,229,235),width=2)
    draw.rounded_rectangle((x,y,x+12,y+92),radius=6,fill=color)
    draw.text((x+34,y+12),"ISO",font=fnt(20),fill=INK)
    draw.text((x+34,y+37),num,font=fnt(34),fill=NAVY)
    draw.ellipse((x+245,y+32,x+267,y+54),fill=color)
card(105,"45007",GREEN)
card(215,"45008",YELLOW)
card(425,"45009",CYAN)

img.save(OUT,"JPEG",quality=88,optimize=True,progressive=True)
print(f"generated {OUT} {OUT.stat().st_size} bytes")
