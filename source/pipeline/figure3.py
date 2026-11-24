"""Figure III: independent artwork and SVG diagram elements in the source coordinates."""
import html
import json

INFO = {
    'scene': dict(t='A given scene', b='The same room provides the visual evidence for objects, geometry, relations and motion.'),
    'objects': dict(t='Objects', b='Object recognition separates scene entities, including the cup and cylindrical object.'),
    'depth': dict(t='Depth', b='Depth describes the distance and geometric layout of the scene.'),
    'relations': dict(t='Relational structure', b='A structured representation connects entities through spatial relationships.'),
    'motion': dict(t='Motion', b='Temporal evidence tracks how positions and scene configurations change.'),
    'reason': dict(t='Inference and planning', b='The planned route carries the cup around the obstacle to the shelf. The moving pulse follows the intended path.'),
    'image': dict(t='Image generation', b='An intent can be expressed as an image of a spatially consistent scene.'),
    'scene3d': dict(t='3D scene generation', b='Generation can construct the geometry and arrangement of a three-dimensional scene.'),
    'video': dict(t='Video generation', b='A sequence of frames extends spatial consistency through time.'),
    'body': dict(t='Motion generation', b='A sequence of articulated poses describes the person carrying the cup to the shelf.'),
    'world': dict(t='World generation', b='A generated world brings objects, layout and spatial interactions together.'),
    'loop': dict(t='Generation runs the loop in reverse', b='Perception maps a given scene to a structured understanding. Generation maps an intent back to spatial content.'),
}


def fig3opener():
    def image(name, x, y, w, h, cls=''):
        return f'<image class="f3-art {cls}" href="/assets/img/figs/fop3/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/>'

    def path(d, cls='', color='#999', width=1.5, arrow=False, dash=None):
        extra = ' marker-end="url(#f3-blue)"' if arrow and color == '#4164db' else ' marker-end="url(#f3-gray)"' if arrow else ''
        if dash:
            extra += f' stroke-dasharray="{dash}"'
        return f'<path class="{cls}" d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{extra}/>'

    def zone(k, box, content):
        x, y, w, h = box
        return f'<g class="f3-zone" data-k="{k}" tabindex="0" role="button" aria-pressed="false" aria-label="{html.escape(INFO[k]["t"])}"><rect class="f3-hit" x="{x}" y="{y}" width="{w}" height="{h}" fill="transparent"/>{content}</g>'

    out = ['<div class="nf nf-3op" data-nf="3op" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1250" role="group" aria-label="Figure III: perception, reasoning and generation">',
           '<defs><marker id="f3-gray" markerUnits="userSpaceOnUse" markerWidth="13" markerHeight="12" refX="11" refY="6" orient="auto"><path d="M0 0L13 6L0 12L3 6Z" fill="#aaa"/></marker><marker id="f3-blue" markerUnits="userSpaceOnUse" markerWidth="24" markerHeight="20" refX="21" refY="10" orient="auto"><path d="M0 0L24 10L0 20L6 10Z" fill="#4164db"/></marker><radialGradient id="f3-glow"><stop stop-color="#365dff" stop-opacity=".36"/><stop offset="1" stop-color="#365dff" stop-opacity="0"/></radialGradient></defs>']
    out.append(zone('scene', (0, 210, 190, 805), image('perceive/scene', 0, 210, 475, 828)))
    planes = [
        ('objects', (195,250,107,411), 'M191 315L305 244V674L191 594Z'),
        ('depth', (312,268,98,472), 'M307 332L412 262V747L307 664Z'),
        ('relations', (420,284,101,515), 'M415 351L525 279V805L415 724Z'),
        ('motion', (533,287,98,526), 'M530 353L634 287V819L530 741Z'),
    ]
    for k, (x,y,w,h), border in planes:
        content = image('perceive/'+k,x,y,w,h) + path(border, 'f3-plane', '#999',1.45)
        out.append(zone(k, (x,y,w,h), content))
    out.append(zone('motion', (299,776,296,153), image('perceive/motion-sequence',299,776,296,153)))
    route = 'M850 650C812 655 788 655 790 615C790 583 827 554 853 542C876 532 895 529 909 529M941 505C944 464 971 472 999 474C1057 483 1068 440 1095 420C1122 399 1157 385 1190 384'
    reason = image('reason/room-and-robot',656,218,693,808)
    reason += path(route,'f3-plan f3-route','#4164db',2.4,dash='12 9')
    for x,y in [(815,650),(793,601),(853,542),(999,474),(1095,420)]:
        reason += f'<circle cx="{x}" cy="{y}" r="4.2" fill="#b5c9ff" stroke="#4164db" stroke-width="2"/>'
    out.append(zone('reason',(656,218,693,808),reason))

    branches = [
        'M1376 635C1452 603 1473 288 1575 283',
        'M1376 635C1455 609 1494 474 1575 464',
        'M1376 635L1509 632',
        'M1376 635C1436 651 1453 754 1527 766',
        'M1376 635C1451 708 1453 920 1530 939',
    ]
    out += ['<g class="f3-branches">'] + [path(d,'f3-route f3-branch','#aaa',1.65,arrow=True) for d in branches] + ['</g>']
    out += ['<circle class="f3-halo" cx="1376" cy="635" r="55" fill="url(#f3-glow)"/>', '<circle class="f3-hub" cx="1376" cy="635" r="6.5" fill="#b5d6ff" stroke="#4164db" stroke-width="2.5"/>']
    out.append(zone('image',(1591,217,338,153),image('generate/image',1591,217,338,153)))
    out.append(zone('scene3d',(1595,372,326,206),image('generate/scene-3d',1595,372,326,206)))
    film = '<rect x="1524" y="582" width="447" height="103" fill="#f8f8f8" stroke="#888" stroke-width="1.5"/>'
    for x in range(1530,1964,13):
        for y in [586,674]:
            film += f'<rect x="{x}" y="{y}" width="7" height="8" rx="1" fill="white" stroke="#888" stroke-width=".9"/>'
    for i,(x,w) in enumerate([(1530,104),(1640,100),(1746,103),(1855,106)]):
        film += image(f'generate/video-frame-{i+1}',x,600,w,69,'f3-sequence')
        film += f'<rect x="{x}" y="600" width="{w}" height="69" fill="none" stroke="#888" stroke-width="1"/>'
    out.append(zone('video',(1524,582,447,103),film))
    motion = ''
    for i,(x,w) in enumerate([(1530,104),(1643,101),(1757,94),(1860,108)]):
        motion += image(f'generate/motion-frame-{i+1}',x,699,w,127,'f3-sequence')
    for x in [1630,1740,1843]:
        motion += path(f'M{x} 765h21','f3-step','#aaa',1.6,True)
    out.append(zone('body',(1528,699,440,127),motion))
    out.append(zone('world',(1542,828,415,300),image('generate/world',1542,828,415,300)))
    loop = path('M1675 1099C1367 1241 366 1274 111 994','f3-loop f3-route','#4164db',2.6,True,'19 14')
    loop += '<text class="f3-note" x="1000" y="1185" text-anchor="middle" font-size="28">generation runs the loop in reverse</text>'
    out.append(zone('loop',(260,1126,1400,112),loop))
    out += ['<g class="f3-pulses" aria-hidden="true" pointer-events="none"></g></svg>']
    # Match the existing opener's live title positions and navigation exactly.
    out.append('<nav class="op-zones" aria-label="In this part">')
    for i,(head,sub) in enumerate([('Perceive','A scene that is given'),('Reason','A scene that is understood'),('Generate','A scene that is made')]):
        out.append(f'<a class="op-z" href="/read/chapter-{i+6}/" style="--i:{i}"><span class="op-n">{i+1}</span><span class="op-txt"><span class="op-h">{head}</span><span class="op-s">{sub}</span><span class="op-go">Chapter {i+6} →</span></span></a>')
    out.append('</nav><div class="nf-card" role="status" hidden></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
    return ''.join(out)
