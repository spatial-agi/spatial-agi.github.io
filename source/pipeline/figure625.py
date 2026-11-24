"""Source-aligned reconstruction of Figure 6.25: temporal localization tasks."""
import json
from html import escape
from pathlib import Path
SITE = Path(__file__).resolve().parents[2]
INFO = {
'offline': {'t':'Offline temporal action localization','b':'The full video is available. Predict the start, end, action class and confidence of each action instance. The example separates walking, opening and retrieving.'},
'online': {'t':'Online onset detection','b':'Only the observed video prefix is available at the current time. Detection follows the actual onset; the time difference is the detection delay. Future frames remain unseen.'},
'weak': {'t':'Weakly supervised localization','b':'Training provides a video-level action label without temporal boundaries. Multiple-instance learning or pseudo-labels help infer candidate action intervals.'},
'single': {'t':'Single-video grounding','b':'Given one video and a natural-language query, rank candidate moments and return the best matching interval with its relevance score.'},
'corpus': {'t':'Corpus-level retrieval','b':'Search a video collection with the query, retrieve the relevant video and then localize the matching temporal interval inside it.'},
'highlights': {'t':'Grounding and highlights','b':'Predict the interval that matches the query together with clip saliency. The two peaks illustrate ranked highlights within the video; their ranks are illustrative.'},
}
def fig625():
    out=[];add=out.append
    def text(x,y,t,size=31,cls='text',raw=False):
        add(f'<text class="f625-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{t if raw else escape(t)}</text>')
    def rect(x,y,w,h,cls,rx=0):add(f'<rect class="f625-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')
    def path(d,cls='blue',arrow=False,flow=False):
        add(f'<path class="f625-{cls}{" f625-route" if flow else ""}" d="{d}"'+(f' marker-end="url(#f625-{"ink" if cls=="ink" else "blue"})"' if arrow else '')+'/>')
    def image(name,x,y,w,h):add(f'<image href="/assets/img/figs/f625/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')
    def frames(x,y,size=177,step=185):
        for i in range(3):image(f'shared-video/frame-{i:02}',x+i*step,y,size,size)
    def interval(x,y,end,dashed=False):
        path(f'M{x} {y}H{end}','dashed' if dashed else 'interval',flow=True)
        path(f'M{x} {y-14}V{y+14}M{end} {y-14}V{y+14}','tick-dashed' if dashed else 'tick')
    def zone(k,x,y,w,h,draw):
        add(f'<g class="f625-zone" data-k="{k}" tabindex="0" role="button" aria-pressed="false" aria-label="{INFO[k]["t"]}">');draw();rect(x,y,w,h,'hit',5);add('</g>')
    add('<div class="nf nf-625" data-nf="625" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1185" role="group" aria-label="Figure 6.25: temporal localization task settings"><defs>')
    for name,color in [('blue','#4146eb'),('ink','#2c373d')]:
        add(f'<marker id="f625-{name}" markerUnits="userSpaceOnUse" markerWidth="17" markerHeight="17" refX="12" refY="8" orient="auto"><path d="M3 3L12 8L3 13" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    add('</defs><rect width="2000" height="1185" fill="white"/><g class="f625-scaffold">')
    text(1000,55,'TAL · predefined action classes',36,'heading')
    text(1000,646,'TSG · “the person opens the microwave”',36,'heading')
    for x in [667,1333]:path(f'M{x} 91V576M{x} 671V1164','divider')
    path('M17 594H1983','divider')
    for x,y,t in [(333,135,'(a) Offline TAL'),(1000,135,'(b) Online onset detection'),(1667,135,'(c) Weakly supervised TAL'),(333,723,'(d) Single-video grounding'),(1000,723,'(e) Corpus-level retrieval'),(1667,723,'(f) Grounding + highlights')]:text(x,y,t,36,'title')
    add('</g>')
    def offline():
        frames(55,189);path('M55 391H606','ink',True,True)
        for x,y,end,lx,label in [(65,437,211,537,'walk 0.91'),(249,486,399,538,'open 0.87'),(443,535,588,240,'retrieve 0.79')]:interval(x,y,end);text(lx,y+8,label)
    zone('offline',42,180,583,386,offline)
    def online():
        for i in range(2):image(f'shared-video/frame-{i:02}',723+i*185,189,177,178)
        rect(1092,189,177,178,'future');text(1190,217,'unseen');text(1178,289,'?',48,'unknown')
        path('M723 391H1274','ink',True,True);path('M1092 183V411','now');text(1088,177,'now',31,'blue-text')
        path('M916 382V451M1009 382V451','guide');path('M916 449H1007','blue',True,True)
        text(891,505,'onset');text(1036,505,'detected')
        text(917,552,'Δ = t<tspan baseline-shift="sub" font-size="23" font-style="normal">detect</tspan> − t<tspan baseline-shift="sub" font-size="23" font-style="normal">onset</tspan>',34,'math',True)
    zone('online',710,151,579,416,online)
    def weak():
        rect(1378,184,576,84,'label',8);text(1667,234,'Label: open microwave',34)
        frames(1387,276,170,185);path('M1385 455H1944','ink',True,True)
        for x,end in [(1405,1549),(1586,1746),(1792,1926)]:interval(x,504,end,True)
        text(1667,562,'Infer boundaries · MIL / pseudo-labels',30)
    zone('weak',1368,175,596,399,weak)
    def single():
        frames(55,755);path('M55 957H606','ink',True,True);interval(243,997,415)
        text(331,1057,'(τ<tspan baseline-shift="sub" font-size="25">s</tspan>, τ<tspan baseline-shift="sub" font-size="25">e</tspan>, r)',36,'math',True)
        interval(83,1104,199,True);interval(459,1104,570,True)
        text(331,1161,'Best match; other candidates ranked',30)
    zone('single',42,744,585,428,single)
    def corpus():
        for name,x,y in [('cooking',720,738),('cycling',818,738),('microwave',916,738),('reading',720,836),('washing',818,836),('laundry',916,836)]:image('e-corpus/'+name,x,y,90,90)
        rect(916,738,91,89,'selection');text(858,976,'Video corpus + query',30)
        path('M1024 846H1101','blue',True,True);image('e-retrieved/video-03',1133,788,128,129)
        text(1193,963,'Video 3',31,'blue-text');path('M1194 985V1030','blue',True,True);interval(1127,1077,1232)
        text(1000,1151,'Retrieve video → localize interval',30)
    zone('corpus',708,733,572,434,corpus)
    def highlights():
        frames(1387,742,139,185)
        path('M1387 997H1552C1582 997 1588 986 1601 942C1607 920 1610 911 1613 911C1626 911 1634 979 1653 992C1676 1012 1688 968 1700 946C1706 935 1709 935 1711 935C1726 935 1735 981 1751 991C1764 999 1783 997 1805 997H1939','curve',flow=True)
        text(1613,897,'1',31,'blue-text');text(1711,922,'2',31,'blue-text');path('M1387 1009H1939','ink',True,True)
        interval(1576,1062,1748);text(1667,1117,'Grounded interval + clip saliency',31)
        text(1667,1160,'1, 2: highlight ranks (illustrative)',30)
    zone('highlights',1375,733,581,438,highlights)
    add('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps(INFO)+'</script></div>')
    return ''.join(out)
if __name__=='__main__':
    (SITE/'example/figure625.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure625-1"><title>Figure 6.25 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.25 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/temporal_localization_task_settings.webp" alt="Original temporal localization task settings"><h2>Interactive reconstruction</h2>'''+fig625()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure625-1';mountNative();</script></html>''')
