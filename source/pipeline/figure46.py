"""Figure 4.6 native SVG, keeping the original 2000 × 666 layout."""
import html
import json
import math


def fig46():
    blue,ink='#00549B','#101414'
    notes={
      'binaural':dict(t='Binaural cues · ITD and ILD',b='Interaural time differences (ITD) and level differences (ILD) compare the signals reaching the two ears. The moving dots illustrate the two propagation paths.'),
      'monaural':dict(t='Monaural spectral cues',b='The torso, head and pinnae filter incoming sound in a direction-dependent way. These spectral changes provide spatial cues at a single ear.'),
      'hrtf':dict(t='Head-related transfer function',b='The HRTF summarizes direction-dependent acoustic filtering. Peaks and notches change with sound direction; this curve is an illustrative magnitude response.'),
      'room':dict(t='Room propagation paths',b='Direct sound arrives first. Reflections travel longer paths, while many later reflections form a diffuse reverberant field.'),
      'response':dict(t='Room impulse response',b='The response separates the direct arrival, discrete early reflections and a decaying late reverberation tail. The sweep illustrates increasing arrival time.')}
    out=['<div class="nf nf-46" data-nf="46" data-pagefind-ignore="all"><div class="f46-viewport"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 666" role="group" aria-label="Figure 4.6: binaural, monaural and environmental acoustic spatial cues">',
      '<defs><marker id="f46-blue" markerWidth="15" markerHeight="14" refX="13" refY="7" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L15 7L0 14L3 7Z" fill="#00549B"/></marker><marker id="f46-black" markerWidth="11" markerHeight="10" refX="10" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L11 5L0 10L2 5Z" fill="#101414"/></marker><clipPath id="f46-response-clip"><rect x="1388" y="342" width="526" height="159"/></clipPath></defs>']
    def text(x,y,s,size=28,color=ink,anchor='start',cls=''):
        spans=''.join(f'<tspan x="{x}" dy="{0 if i==0 else size*1.28}">{html.escape(line)}</tspan>' for i,line in enumerate(s.split('\n')))
        return f'<text class="f46-text {cls}" x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{spans}</text>'
    def rect(x,y,w,h,r=0):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="white" stroke="{ink}" stroke-width="1.7"/>'
    def path(d,color=ink,width=1.7,dash=None,arrow=False,delay=0,duration=1400):
        a=f' stroke-dasharray="{dash}"' if dash else ''
        if arrow:a+=f' marker-end="url(#{"f46-blue" if color==blue else "f46-black"})"'
        return f'<path class="{"f46-route" if arrow and color==blue else "f46-line"}" data-delay="{delay}" data-duration="{duration}" d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{a}/>'
    def image(k,x,y,w,h):return f'<image href="/assets/img/figs/f46/{k}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>'
    def zone(k,x,y,w,h,content):
        return f'<g class="f46-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{html.escape(notes[k]["t"])}"><rect class="f46-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="transparent"/>{content}</g>'
    out += [rect(26,15,538,637,17),rect(592,15,716,637,17),rect(1331,15,659,637,17)]
    a=image('a/head-top',239,185,247,296)+image('a/sound-source',70,80,78,76)
    a+=text(107,207,'Sound\nSource',31,anchor='middle')+text(218,166,'Δt (ITD)',24,blue)+text(146,294,'ΔL (ILD)',24,blue)
    a+=path('M146 144L452 303',blue,2.5,arrow=True,duration=1650)+path('M141 155L256 300',blue,2.5,arrow=True,duration=1250)
    out.append(zone('binaural',45,64,477,447,a))
    b=image('b/head-profile',608,160,302,356)+image('b/sound-source',678,42,87,74)+text(829,79,'Sound\nSource',31,anchor='middle')
    b+=path('M722 121V284',blue,1.8,arrow=True,duration=1300)+path('M721 333Q742 336 757 349',blue,1.5,arrow=True,delay=1300,duration=700)
    out.append(zone('monaural',606,37,310,494,b))
    h=rect(934,175,347,325,7)+text(1151,226,'HRTF Magnitude',31,anchor='middle')
    h+=path('M1000 219V426H1264')+path('M1000 323H1264','#8e9399',1,'5 6')
    for y,label in [(219,'20'),(271,'10'),(323,'0'),(375,'-10'),(426,'-20')]:
        h+=path(f'M994 {y}H1005',width=1)+text(988,y+6,label,18,anchor='end')
    for x,label in [(1042,'10²'),(1132,'10³'),(1222,'10⁴')]:h+=path(f'M{x} 423V434',width=1)+text(x,456,label,18,anchor='middle')
    h+=text(1134,481,'Frequency (Hz)',20,anchor='middle')+'<text class="f46-text" transform="translate(957 324) rotate(-90)" text-anchor="middle" font-size="20">|H(f)| (dB)</text>'
    curve='M1001 303C1017 296 1030 300 1040 310S1051 342 1058 383S1065 362 1074 326S1092 260 1103 265S1115 293 1130 295S1143 292 1153 313S1163 357 1170 373S1178 350 1186 324S1197 313 1203 293S1213 237 1220 246S1227 292 1237 288S1246 321 1255 338S1268 372 1273 386'
    h+=path(curve,blue,2.6)
    out.append(zone('hrtf',930,171,355,333,h))
    room=path('M1354 73L1412 39H1915L1970 73V292H1354V73H1970M1412 39V247H1915V39M1354 292L1412 247M1915 247L1970 292',width=1.7)
    room+=image('c/speaker',1422,131,44,59)+image('c/listener',1725,151,54,59)
    room+=text(1453,210,'Sound\nSource',20,anchor='middle')+text(1759,234,'Listener',16,anchor='middle')+text(1611,136,'Direct\nsound',17,blue,anchor='middle')
    room+=path('M1468 159L1721 180',blue,2,arrow=True,duration=1100)+path('M1468 132L1592 39L1745 151',blue,1.9,'6 6',True,0,2000)+path('M1467 174L1675 283L1732 215',blue,1.9,'6 6',True,0,2400)
    cloud='M1810 143C1787 129 1800 109 1815 106C1816 87 1837 77 1853 88C1865 73 1878 82 1881 88C1895 76 1907 91 1907 97C1927 94 1940 109 1938 120C1957 133 1956 153 1946 163C1960 180 1942 197 1928 197C1917 216 1903 211 1892 204C1874 219 1864 207 1857 203C1841 216 1828 205 1827 196C1809 201 1798 184 1802 173C1791 162 1797 149 1810 143Z'
    room+=f'<path d="{cloud}" fill="#E3F0FF" stroke="#76A9C6" stroke-width="1.2"/>'+text(1877,124,'Late\nreverberation\n(diffuse field)',17,blue,'middle')
    out.append(zone('room',1348,32,628,267,room))
    response=rect(1387,311,546,260,7)+text(1684,347,'Room Impulse Response',31,anchor='middle')
    response+=path('M1387 500H1916',arrow=True)+path('M1363 483V358',arrow=True)
    response+='<text class="f46-text" transform="translate(1368 433) rotate(-90)" font-size="18" text-anchor="middle">Amplitude</text>'
    response+=text(1633,557,'Time (s)',19,anchor='middle')+path('M1677 550H1747',arrow=True)
    for x,label in [(1417,'0'),(1490,'0.02'),(1556,'0.04'),(1623,'0.06'),(1689,'0.08'),(1758,'0.10'),(1830,'0.20'),(1903,'0.30')]:
        response+=path(f'M{x} 500V507',width=1)+text(x,528,label,18,anchor='middle')
    response+=path('M1417 500V349',blue,3)+text(1428,361,'Direct\nsound',17,blue)
    for x,height in [(1514,67),(1543,42),(1571,68),(1593,42),(1608,29),(1617,17)]:response+=path(f'M{x} 500V{500-height}',blue,2)
    response+=path('M1502 420Q1502 413 1511 413H1565Q1571 412 1571 405Q1571 413 1578 413H1635Q1642 413 1642 420',blue,1.2)
    response+=text(1574,400,'Early reflections',17,blue,'middle')+text(1802,400,'Late reverberation\n(diffuse tail)',17,blue,'middle')
    # Dense, decaying reflection spikes preserve the printed illustration's silhouette.
    for i in range(230):
        x=1651+i*1.1; height=59*math.exp(-i/58)*(0.65+0.35*abs(math.cos(i*1.8)))
        response+=path(f'M{x:.2f} 500V{500-height:.2f}',blue,1)
    response+='<g clip-path="url(#f46-response-clip)"><path class="f46-sweep" d="M1417 343V500" stroke="#47A8CF" stroke-width="2.5" opacity="0"/></g>'
    out.append(zone('response',1380,306,559,271,response))
    out += [text(295,626,'Binaural Cues (ITD, ILD)',39,anchor='middle'),text(950,626,'Monaural Spectral Cues',39,anchor='middle'),text(1661,626,'Environmental Reverberation',38,anchor='middle'),'<g class="f46-pulses" aria-hidden="true"></g></svg></div><div class="nf-card" hidden></div><script type="application/json" class="nf-info">'+json.dumps(notes,ensure_ascii=False)+'</script></div>']
    return ''.join(out)
