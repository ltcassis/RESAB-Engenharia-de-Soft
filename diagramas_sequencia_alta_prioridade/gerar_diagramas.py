"""Gera os seis diagramas em PlantUML, SVG e PNG. Requer Pillow apenas para PNG."""
from pathlib import Path
from html import escape
import os
import textwrap
import argparse
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
from requisitos_diagramas import DIAGRAMAS

NAVY, BLUE, GRAY = "#eeeeee", "#eeeeee", "#bfbfbf"
BACKGROUND, TAB, ACTIVATION = "#111111", "#67adff", "#168dbb"
FONT_DIR = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"

def generate(slug, title, subtitle, participants, events, note, tema="escuro"):
    if tema == "claro":
        NAVY, BLUE, GRAY = "#172b42", "#263e56", "#596b7d"
        BACKGROUND, TAB, ACTIVATION = "#ffffff", "#d9eafe", "#74b6e6"
        SEPARATOR, REFERENCE = "#c5d0dc", "#edf4fb"
        output = ROOT / "versao_clara"
    else:
        NAVY, BLUE, GRAY = "#eeeeee", "#eeeeee", "#bfbfbf"
        BACKGROUND, TAB, ACTIVATION = "#111111", "#67adff", "#168dbb"
        SEPARATOR, REFERENCE = "#555555", "#202020"
        output = ROOT
    output.mkdir(parents=True, exist_ok=True)
    width = 480 * len(participants)
    xs = [240 + i * 480 for i in range(len(participants))]
    rf = title.split(" — ", 1)[0]
    # Cabeçalho apenas com o RF; sem subtítulo ou legenda de rodapé.
    heights = {"m":84,"r":76,"alt":56,"loop":56,"opt":56,"else":56,"end":28,"ref":80}
    height = 240 + sum(heights[e[0]] for e in events) + 45
    im = Image.new("RGB", (width,height), BACKGROUND)
    draw = ImageDraw.Draw(im)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>']
    def font(size,bold=False):
        return ImageFont.truetype(str(FONT_DIR / ("arialbd.ttf" if bold else "arial.ttf")),size)
    def text(x,y,s,size=22,color=NAVY,bold=False,anchor="start"):
        f=font(size,bold)
        w=draw.textlength(s,font=f)
        left=x-w/2 if anchor=="middle" else x
        draw.text((left,y),s,font=f,fill=color)
        svg.append(f'<text x="{x}" y="{y+size}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" text-anchor="{anchor}" fill="{color}">{escape(s)}</text>')
    def line(x1,y1,x2,y2,color=GRAY,dashed=False,stroke=2):
        if dashed:
            length=((x2-x1)**2+(y2-y1)**2)**.5
            for n in range(0,int(length),13):
                a=n/length; b=min(n+7,length)/length
                draw.line((x1+(x2-x1)*a,y1+(y2-y1)*a,x1+(x2-x1)*b,y1+(y2-y1)*b),fill=color,width=stroke)
        else: draw.line((x1,y1,x2,y2),fill=color,width=stroke)
        dash=' stroke-dasharray="7 6"' if dashed else ''
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{stroke}"{dash}/>')
    def rect(x,y,w,h,fill=BACKGROUND,stroke=GRAY,radius=0):
        draw.rounded_rectangle((x,y,x+w,y+h),radius=radius,fill=fill,outline=stroke,width=2)
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill or "none"}" stroke="{stroke}" stroke-width="2"/>')
    def arrow(x1,y,x2,dashed=False):
        line(x1,y,x2,y,BLUE,dashed)
        direction=1 if x2>x1 else -1
        line(x2-direction*13,y-7,x2,y,BLUE)
        line(x2-direction*13,y+7,x2,y,BLUE)
        if not dashed:
            points=[(x2,y),(x2-direction*13,y-7),(x2-direction*13,y+7)]
            draw.polygon(points,fill=BLUE)
            svg.append(f'<polygon points="{" ".join(f"{x},{yy}" for x,yy in points)}" fill="{BLUE}"/>')
    text(55,30,rf,38,bold=True)
    line(55,88,width-55,88,SEPARATOR,stroke=2)
    bottom=height-35
    for x,(label,kind) in zip(xs,participants):
        if kind == "actor":
            draw.ellipse((x-12,103,x+12,127),outline=NAVY,width=2)
            svg.append(f'<circle cx="{x}" cy="115" r="12" fill="none" stroke="{NAVY}" stroke-width="2"/>')
            line(x,127,x,159,NAVY);line(x-25,137,x+25,137,NAVY)
            line(x,159,x-24,185,NAVY);line(x,159,x+24,185,NAVY)
            text(x,191,label,21,bold=True,anchor="middle")
        else:
            rect(x-205,123,410,79,BACKGROUND,BLUE)
            text(x,133,f"«{kind}»",18,color=GRAY,anchor="middle")
            text(x,163,label,22,bold=True,anchor="middle")
            label_width=draw.textlength(label,font=font(22,True))
            line(x-label_width/2,191,x+label_width/2,191,NAVY,stroke=1)
        line(x,220 if kind == "actor" else 202,x,bottom,GRAY,True)
    # Uma ativação se estende da chamada até seu retorno, inclusive chamadas aninhadas.
    pending=[]; spans=[]; depths=[0]*len(participants); cursor=240
    for event in events:
        kind=event[0]
        if kind == 'm':
            _,a,b,_=event
            pending.append((a,b,cursor+(40 if a==b else 54),depths[b]))
            depths[b]+=1
        elif kind == 'r':
            _,a,b,_=event
            caller,callee,start,depth=pending.pop()
            assert (caller,callee)==(b,a), (rf,event,caller,callee)
            depths[a]-=1
            spans.append((callee,start,cursor+(65 if a==b else 54),depth))
        cursor+=heights[kind]
    assert not pending
    for participant,start,end,depth in sorted(spans,key=lambda item:item[3]):
        if participants[participant][1]!='actor':
            rect(xs[participant]-10+depth*12,start,20,end-start,ACTIVATION,ACTIVATION)
    puml=["@startuml",f"title {rf}","autonumber","hide footbox","skinparam shadowing false","skinparam sequenceMessageAlign center","skinparam responseMessageBelowArrow false"]
    puml.extend([f"skinparam backgroundColor {BACKGROUND}", f"skinparam defaultFontColor {NAVY}",
                 "skinparam sequence {", f" ArrowColor {BLUE}", f" LifeLineBorderColor {GRAY}",
                 f" LifeLineBackgroundColor {ACTIVATION}", f" ParticipantBorderColor {BLUE}",
                 f" ParticipantBackgroundColor {BACKGROUND}", f" ParticipantFontColor {NAVY}",
                 f" ActorBorderColor {NAVY}", f" ActorBackgroundColor {BACKGROUND}", f" ActorFontColor {NAVY}",
                 f" GroupBorderColor {NAVY}", f" GroupBackgroundColor {BACKGROUND}", f" GroupFontColor {NAVY}",
                 f" GroupHeaderFontColor {NAVY}", "}", f"skinparam noteBackgroundColor {REFERENCE}",
                 f"skinparam noteFontColor {NAVY}", f"skinparam noteBorderColor {GRAY}"])
    for i,(label,kind) in enumerate(participants): puml.append(f'{kind} "{label}" as P{i}')
    y=240; stack=[]; number=0
    for e in events:
        typ=e[0]; h=heights[typ]
        if typ in ("alt","loop","opt"):
            left=48+len(stack)*18; right=width-48-len(stack)*18
            rect(left+10,y+5,170,36,TAB,TAB,radius=7)
            label=typ
            text(left+95,y+10,label,20,bold=True,anchor="middle")
            text(left+200,y+10,"["+e[1]+"]",21,bold=True)
            stack.append((left,right,y));puml.append(f"{typ} {e[1]}")
        elif typ=="else":
            left,right,_=stack[-1]
            line(left,y,right,y,NAVY,True)
            text(left+200,y+9,"["+e[1]+"]",21,bold=True)
            puml.append("else "+e[1])
        elif typ=="end":
            left,right,top=stack.pop()
            rect(left,top,right-left,y+10-top,None,NAVY,radius=22)
            puml.append("end")
        elif typ=="ref":
            first,last=e[2:4] if len(e)>2 else (0,len(participants)-1)
            left=xs[first]-205; right=xs[last]+205
            rect(left,y+8,right-left,54,REFERENCE,BLUE,radius=8)
            text(left+17,y+20,"ref",21,bold=True)
            text(left+100,y+20,e[1],22)
            targets=f"P{first}" if first==last else f"P{first},P{last}"
            puml.append(f"ref over {targets} : {e[1]}")
        else:
            _,a,b,label=e;number+=1
            x1,x2=xs[a],xs[b];ay=y+54
            puml.append(f'P{a} {"-->" if typ=="r" else "->"} P{b} : {label}')
            if typ=="m" and participants[b][1]!="actor":
                puml.append(f'activate P{b}')
            elif typ=="r" and participants[a][1]!="actor":
                puml.append(f'deactivate P{a}')
            if a==b:
                # Self calls extend left in the last column and right otherwise.
                dx=-65 if a==len(xs)-1 else 65
                line(x1,y+40,x1+dx,y+40,BLUE,typ=="r")
                line(x1+dx,y+40,x1+dx,y+65,BLUE,typ=="r")
                arrow(x1+dx,y+65,x1,typ=="r")
                tx=x1-30 if dx<0 else x1+30
                if dx<0: tx=x1-draw.textlength(f"{number}. {label}",font=font(21))-20
                text(tx,y+7,f"{number}. {label}",21)
            else:
                wrapped=textwrap.wrap(f"{number}. {label}",width=max(28,int(abs(x2-x1)/10)))
                for j,t in enumerate(wrapped):text((x1+x2)/2,y+2+j*24,t,21,anchor="middle")
                arrow(x1,ay,x2,typ=="r")
        y+=h
    assert not stack
    puml.append("@enduml")
    (output/(slug+".puml")).write_text("\n".join(puml)+"\n",encoding="utf-8")
    (output/(slug+".svg")).write_text("\n".join(svg+["</svg>"]),encoding="utf-8")
    im.save(output/(slug+".png"))
    print(f"{slug}: {width} x {height}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tema", choices=("escuro", "claro"), default="escuro")
    args = parser.parse_args()
    for diagram in DIAGRAMAS: generate(*diagram, tema=args.tema)
