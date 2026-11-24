"""Native redraw of Figure 6.18: action classification, localization and detection."""
import json
from html import escape
from pathlib import Path

INFO = {
    "classification": {"t": "Action classification", "b": "Trimmed video clips are assigned an action class. The timeline summarizes representative RGB, 3D convolution, sparse sampling and attention methods."},
    "localization": {"t": "Temporal action localization", "b": "Untrimmed video is searched for one action interval. Methods differ in proposal generation and supervision, from sliding windows to boundary pairing, video labels and point labels."},
    "detection": {"t": "Temporal action detection", "b": "Detection predicts multiple temporal intervals and their classes. The mechanisms progress from anchors and proposals to boundary-based and query-based formulations."},
}


def fig618():
    out = []
    add = out.append
    info = dict(INFO)
    active_bounds = None

    def text(x, y, value, size=28, cls="text", anchor="middle", weight=None):
        w = f' font-weight="{weight}"' if weight else ""
        add(f'<text class="f618-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}"{w}>{value}</text>')

    def path(d, cls="ink", arrow=None, flow=False):
        add(f'<path class="f618-{cls}{" f618-route" if flow else ""}" d="{d}"' + (f' marker-end="url(#f618-{arrow})"' if arrow else "") + '/>')

    def image(name, x, y, w, h):
        add(f'<image href="/assets/img/figs/f618/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/>')

    def begin(key, bounds, title, body):
        nonlocal active_bounds
        active_bounds = bounds
        info[key] = {'t': title, 'b': body}
        add(f'<g class="f618-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(title)}">')

    def end():
        x, y, w, h = active_bounds
        add(f'<rect class="f618-hit" x="{x}" y="{y}" width="{w}" height="{h}"/>')
        add('</g>')

    def method(x, y, w, title, sub, year):
        begin(f'method-{y}-{x}', (x-4,y-4,w+8,173), title,
              f'{title} ({year}). This timeline node highlights {sub.lower()} within the representative methods shown in the figure. Timeline spacing indicates publication order, not computational dependencies.')
        add(f'<rect class="f618-method" x="{x}" y="{y}" width="{w}" height="105" rx="7"/>')
        text(x+w/2, y+43, title, 29)
        text(x+w/2, y+86, sub, 28)
        mid=x+w/2
        path(f'M{mid} {y+105}V{y+122}', 'tick')
        text(mid, y+160, year, 28, 'year')
        end()

    def timeline(y, left=430, right=1965):
        path(f'M{left} {y}H{right}', 'timeline', 'gray')

    def photo_strip(group, x, y, w, h, count=6):
        names = [f'{group}/frame-{i:02}' for i in range(1, count+1)]
        if group == 'classification': names = [f'classification/serve-0{i}' for i in range(1,4)]
        if group == 'two-stream': names = ['two-stream/rgb']
        gap=3; cell=(w-gap*(count-1))/count
        for i,name in enumerate(names):
            image(name, x+i*(cell+gap), y, cell, h)
            add(f'<rect class="f618-photo-line" x="{x+i*(cell+gap)}" y="{y}" width="{cell}" height="{h}"/>')

    add('<div class="nf nf-618" data-nf="618" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1277" role="group" aria-label="Figure 6.18: action classification, localization and detection methods"><defs>')
    add('<marker id="f618-gray" markerWidth="15" markerHeight="15" markerUnits="userSpaceOnUse" refX="13" refY="7.5" orient="auto"><path d="M1 1L13 7.5L1 14Z" fill="#a8b1b7"/></marker><marker id="f618-blue" markerWidth="17" markerHeight="17" markerUnits="userSpaceOnUse" refX="15" refY="8.5" orient="auto"><path d="M1 1L15 8.5L1 16Z" fill="#4545ed"/></marker></defs><rect width="2000" height="1277" fill="white"/>')

    def classification():
        add('<g class="f618-scaffold">')
        text(65, 72, '(i) Classification', 36, 'title', 'start')
        text(102, 161, 'Trimmed → class', 28, 'text', 'start')
        add('</g>')
        boxes=[(436,70,294,'Two-Stream','RGB + flow','2014'),(748,70,154,'C3D','3D','2015'),(919,70,154,'TSN','Segments','2016'),(1090,70,268,'I3D / P3D','3D / factored','2017'),(1376,70,269,'R(2+1)D','Factored','2018'),(1669,70,286,'RViT','Attention','2022')]
        for b in boxes: method(b[0],40,b[2],b[3],b[4],b[5])
        timeline(166)
        begin('classification-input', (22, 235, 365, 172), 'Trimmed tennis-serve clip', 'These frames show a single trimmed tennis serve. Classification predicts the action label without estimating temporal boundaries.')
        photo_strip('classification',30,245,345,92,3)
        text(203, 385, '“tennis serve”', 28, 'blue-text')
        end()
        begin('two-stream', (420, 219, 433, 193), 'Two-stream fusion', 'Separate appearance and motion streams process RGB frames and optical flow. Their features are fused to predict the action class.')
        text(645, 250, 'Two-stream fusion', 28, 'title')
        photo_strip('two-stream',446,261,62,50,1)
        path('M517 283H551','blue','blue',True)
        # RGB and optical-flow feature streams fuse before classification.
        for yy in (253,325):
            for i,offset,hh in [(0,0,59),(1,8,44),(2,16,29),(3,8,44)]:
                add(f'<rect class="f618-feature" x="{566+i*17}" y="{yy+offset}" width="11" height="{hh}"/>')
        for y in (344,368):
            for x in (452,477,502):
                path(f'M{x} {y+3}l10 -7','flow-arrow','blue')
        path('M517 354H551','blue','blue',True)
        text(492, 404, 'RGB / flow', 28)
        path('M639 283H670V320','connector')
        path('M639 354H670V320','connector')
        path('M670 320H724','blue','blue',True)
        add('<rect class="f618-method" x="735" y="286" width="105" height="68" rx="9"/>'); text(787,330,'Class',27)
        end()
        begin('convolution', (917, 218, 490, 194), '3D and factorized convolution', 'Video clips form a space-time volume. 3D convolution jointly extracts spatial and temporal features; factorization separates spatial and temporal operations.')
        text(1153, 250, '3D / factorized convolution', 28, 'title')
        for i in range(3): add(f'<rect class="f618-feature" x="{941+i*17}" y="{292-i*13}" width="78" height="69"/>')
        path('M1068 317H1127','blue','blue',True)
        for i,yy,hh in [(0,288,58),(1,295,44),(2,303,28),(3,295,44)]:
            add(f'<rect class="f618-feature" x="{1148+i*17}" y="{yy}" width="11" height="{hh}"/>')
        path('M1227 317H1278','blue','blue',True); text(1338,325,'Class',27)
        text(1155,406,'Clip → space–time features',27)
        end()
        begin('attention', (1430, 218, 535, 194), 'Sampling and attention', 'Sparse snippets represent different times in a video. Connections across sampled tokens model temporal context and long-range dependencies.')
        text(1708,250,'Sampling / attention',28,'title')
        for i in range(4):
            x=1505+i*98
            add(f'<rect class="f618-feature" x="{x}" y="{277}" width="52" height="44"/>')
            if i<3: path(f'M{x+53} 299H{x+93}','blue','blue',True)
            path(f'M{x+26} 323V354','connector')
        path('M1531 354H1825','connector')
        text(1655,406,'Sparse snippets / temporal context',26)
        end()
        path('M16 420H1984','divider')

    def localization():
        add('<g class="f618-scaffold">')
        text(75, 481, '(ii) Localization', 36, 'title', 'start')
        text(75, 574, 'Boundary estimation', 28, 'text', 'start')
        add('</g>')
        for x,w,t,s,y in [(449,268,'SSN','Completeness','2017'),(796,400,'BSN / AutoLoc','Boundary / weak','2018'),(1273,272,'CoLA','Video labels','2021'),(1643,312,'Realign','Point labels','2024')]: method(x,457,w,t,s,y)
        timeline(584)
        # Untrimmed video strip and independently drawn labeled interval.
        begin('localization-input', (22, 655, 365, 170), 'Action interval in untrimmed video', 'The highlighted interval marks the start and end of an action within the full video sequence.')
        photo_strip('localization',30,712,346,45)
        add('<rect class="f618-interval" x="108" y="668" width="184" height="11"/>')
        path('M108 679V706M292 679V706','guide')
        text(203,808,'Untrimmed video',27)
        end()
        begin('sliding-windows', (422, 618, 345, 207), 'Sliding-window proposals', 'Overlapping temporal windows provide candidate action intervals. The model scores and classifies each proposal.')
        text(585, 650, 'Sliding windows', 27, 'title')
        for x,y,w in [(447,727,166),(499,708,166),(551,690,166)]: add(f'<rect class="f618-feature" x="{x}" y="{y}" width="{w}" height="18"/>')
        path('M440 773H741','gray','gray',True); text(590,808,'Classify proposals',26)
        end()
        begin('boundary-pairing', (811, 618, 416, 207), 'Boundary pairing', 'Solid and dashed curves represent start and end scores. Pairing candidate boundaries produces an action interval.')
        text(1005,650,'Boundary pairing',27,'title')
        path('M837 755H1205','gray','gray',True)
        path('M846 755C900 755 902 702 949 702C987 702 1004 755 1040 755','ink')
        path('M1011 755C1061 755 1073 702 1121 702C1161 702 1174 755 1205 755','dashed')
        add('<rect class="f618-interval" x="925" y="760" width="202" height="10"/>')
        path('M925 770V791M1127 770V791','guide')
        text(1025,808,'Start (solid) / end (dashed)',25)
        end()
        add('<g class="f618-scaffold">')
        text(1610,668,'Training supervision alternatives',27,'title')
        add('</g>')
        begin('video-label', (1315, 684, 290, 141), 'Video-level supervision', 'The score distribution summarizes evidence over time when only the video action label is available.')
        for i,h in enumerate((13,29,53,75,50,22)):
            add(f'<rect class="f618-feature" x="{1348+i*34}" y="{767-h}" width="21" height="{h}"/>')
        path('M1331 769H1590','gray','gray',True)
        text(1462,813,'Video label',26)
        end()
        begin('labeled-frame', (1683, 684, 283, 141), 'Point supervision', 'A labeled frame supplies one temporal point inside an action. The dashed guide relates this annotation to the video timeline.')
        path('M1698 769H1954','gray','gray',True)
        path('M1825 707V766','dashed-blue')
        add('<circle class="f618-point" cx="1825" cy="698" r="9"/>')
        text(1825,813,'Labeled frame',26)
        end()
        path('M16 837H1984','divider')

    def detection():
        add('<g class="f618-scaffold">')
        text(92, 914, '(iii) Detection', 36, 'title', 'start')
        text(92, 1000, 'Intervals + classes', 28, 'text', 'start')
        add('</g>')
        boxes=[(434,877,166,'S-CNN','Anchors','2016'),(620,877,258,'SSAD / TURN','Proposals','2017'),(897,877,193,'TSA-Net','Boundary','2019'),(1108,877,267,'AFSD / BGCN','Free / boundary','2021'),(1393,877,160,'ReAct','Queries','2022'),(1572,877,190,'Self-DETR','Queries','2023'),(1780,877,178,'DualDETR','Queries','2024')]
        for b in boxes: method(b[0],b[1],b[2],b[3],b[4],b[5])
        timeline(1004)
        # Two labeled temporal extents over the same untrimmed sequence.
        begin('detection-input', (22, 1073, 365, 175), 'Multiple action instances', 'Several action instances can occur in an untrimmed video. Each predicted interval needs its own start, end and action category.')
        photo_strip('detection',30,1128,345,46)
        for x,w,y in [(45,100,1084),(181,167,1104)]:
            add(f'<rect class="f618-interval" x="{x}" y="{y}" width="{w}" height="10"/>')
            path(f'M{x} {y+10}V1121M{x+w} {y+10}V1121','guide')
        text(210,1234,'Untrimmed video',27)
        end()
        begin('anchors', (421, 1041, 346, 184), 'Anchor-based detection', 'Predefined intervals at multiple temporal scales act as anchors. Detection scores and refines them to obtain action instances.')
        text(579,1069,'Anchors',27,'title')
        for i in range(3):
            y=1103+i*28
            add(f'<rect class="f618-feature" x="446" y="{y}" width="{289-i*24}" height="14"/>')
            for x in (520,594): path(f'M{x} {y}V{y+14}','grid')
        path('M442 1205H753','gray','gray',True)
        end()
        begin('anchor-free', (824, 1041, 352, 184), 'Anchor-free detection', 'An action center predicts distances toward the start and end boundaries, avoiding a predefined set of temporal anchors.')
        text(1000,1069,'Anchor-free',27,'title')
        path('M844 1205H1158','gray','gray',True)
        path('M999 1135H873','blue','blue',True); path('M1018 1135H1143','blue','blue',True); add('<circle class="f618-point" cx="1006" cy="1135" r="8"/>'); path('M1006 1147V1198','grid')
        end()
        begin('boundaries', (1215, 1054, 350, 202), 'Boundary-based detection', 'Alternating solid start peaks and dashed end peaks delimit multiple action instances. The bars below show the resulting temporal intervals.')
        text(1378,1088,'Boundaries',27,'title')
        path('M1235 1198H1546','gray','gray',True)
        for center,style in [(1285,'ink'),(1374,'dashed'),(1430,'ink'),(1508,'dashed')]:
            path(f'M{center-46} 1198C{center-20} 1198 {center-14} 1142 {center} 1142C{center+14} 1142 {center+21} 1198 {center+46} 1198',style)
        for x,w in [(1286,83),(1434,80)]:
            add(f'<rect class="f618-interval" x="{x}" y="1214" width="{w}" height="10"/>')
            path(f'M{x} 1224V1250M{x+w} 1224V1250','guide')
        end()
        begin('queries', (1595,1054,389,220), 'Query-based detection', 'Learned queries enter a decoder and produce a set of action predictions. Each output contains a temporal interval and an action class.')
        text(1768,1088,'Queries',27,'title')
        add('<rect class="f618-method" x="1615" y="1147" width="352" height="57" rx="9"/>'); text(1791,1183,'Decoder',27)
        for x in (1671,1782,1892):
            add(f'<circle class="f618-point-open" cx="{x}" cy="1105" r="5.5"/>'); path(f'M{x} 1113V1141','blue','blue',True)
            path(f'M{x} 1209V1230','blue','blue',True)
            add(f'<rect class="f618-interval" x="{x-37}" y="1235" width="74" height="10"/>')
            path(f'M{x-37} 1245V1269M{x+37} 1245V1269','guide')

        end()

    classification()
    localization()
    detection()
    add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(info)+'</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    site=Path(__file__).resolve().parents[2]
    (site/'example/figure618.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure618-5"><title>Figure 6.18 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.18 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/action_detection_method_1.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig618()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure618-5';mountNative();</script></html>''')
