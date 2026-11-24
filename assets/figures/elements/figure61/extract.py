"""Separate the Figure 6.1 artwork; diagram labels and connectors stay in SVG."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE / 'assets/figures/figures/part3/section6/object_detection.webp'
src = Image.open(SOURCE).convert('RGB')
records = []


def save(name, box, polygon=None, clean=False, note=''):
    arr = np.array(src.crop(box))
    if name=='objects/speed-sign':
        # Restore the vertical post where detection and explanatory lines cross it.
        for y0,y1 in [(210,220),(234,251),(315,330)]:
            a,b=y0-box[1],y1-box[1]
            for row in range(a,b):
                t=(row-a+1)/(b-a+1)
                arr[row]=((1-t)*arr[a-1]+t*arr[b]).astype('uint8')
    if clean:
        # The blue labels and thin boxes overlap the original street sketch.
        # Fill only these annotation pixels with their nearest unmarked neighbor.
        rgb = arr.astype(int)
        mask = (rgb[:,:,2]-rgb[:,:,0]>20)&(rgb[:,:,2]-rgb[:,:,1]>5)
        mask = binary_dilation(mask,iterations=1)
        # The black dashed explanatory leaders are confined to the right margin.
        yy,xx = np.indices(mask.shape)
        xx += box[0]; yy += box[1]
        m=Image.new('1',(arr.shape[1],arr.shape[0]));d=ImageDraw.Draw(m)
        for points in [[(1393,278),(1544,210),(1570,204)],[(1398,334),(1570,303)],[(1480,415),(1570,399)]]:
            d.line([(x-box[0],y-box[1]) for x,y in points],fill=1,width=18)
        mask |= np.array(m)
        idx=distance_transform_edt(mask,return_distances=False,return_indices=True)
        arr[mask]=arr[tuple(idx[:,mask])]
        # Labels occupied blank strips over the street illustration.
        for x0,y0,x1,y1 in [(195,96,344,129),(483,125,617,157),(704,186,1117,218),(1177,247,1400,280),(1417,73,1522,103)]:
            arr[max(0,y0-box[1]):y1-box[1],max(0,x0-box[0]):x1-box[0]]=255
        gray=np.min(arr,axis=2);arr=np.repeat(gray[:,:,None],3,axis=2)
    rgb=arr.astype(float)
    alpha=255-rgb.min(axis=2); alpha[alpha<7]=0
    if polygon:
        m=Image.new('L',(arr.shape[1],arr.shape[0]));ImageDraw.Draw(m).polygon([(x-box[0],y-box[1]) for x,y in polygon],fill=255)
        alpha=np.minimum(alpha,np.array(m))
    color=np.clip(255-(255-rgb)*255/np.maximum(alpha[:,:,None],1),0,255).astype('uint8')
    out=Image.fromarray(np.dstack([color,alpha.astype('uint8')]),'RGBA')
    dest=ROOT/(name+'.png');dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest)
    records.append(dict(file=name+'.png',box=box,size=list(out.size),note=note))


save('scene/street',(20,21,1568,517),clean=True,
     note='Blue detections and dashed explanatory leaders removed. Occluded sketch strokes at these intersections are approximated locally; original objects remain in the scene.')
save('objects/person-left',(199,142,340,435),[
 (260,145),(281,143),(293,150),(292,166),(295,175),(285,183),(280,189),
 (284,201),(291,214),(295,242),(303,265),(318,277),(324,291),(316,297),(308,288),(298,285),
 (291,271),(281,249),(278,281),(288,306),(304,338),(319,368),(321,402),(335,414),(340,424),
 (329,432),(313,432),(300,426),(297,414),(286,392),(271,358),(259,342),(249,366),(232,397),
 (230,409),(244,418),(242,426),(231,431),(211,425),(202,419),(202,411),(214,399),(227,367),
 (237,337),(239,319),(237,309),(231,308),(235,286),(222,279),(214,269),(216,244),(220,224),
 (228,211),(238,202),(241,190),(247,183),(250,173),(249,159)])
save('objects/person-right',(496,169,609,388),[
 (532,173),(546,169),(557,173),(562,184),(562,197),(553,206),(560,214),(565,233),(569,251),
 (579,266),(583,281),(577,288),(569,281),(563,274),(563,291),(559,308),(556,318),
 (568,337),(586,360),(604,367),(607,375),(599,382),(580,383),(569,373),(551,351),
 (538,336),(527,355),(516,369),(533,375),(535,381),(528,386),(512,383),(498,376),
 (497,368),(508,351),(517,329),(525,307),(519,304),(518,295),(510,290),(510,278),
 (518,256),(521,237),(525,219),(530,207),(526,200),(520,204),(516,215),(509,218),
 (511,207),(517,196),(520,190),(521,178)])
save('objects/car',(705,224,1110,399),[
 (708,313),(720,296),(743,289),(769,282),(801,261),(834,244),(868,233),(902,227),
 (951,225),(987,231),(1019,243),(1048,259),(1066,272),(1087,277),(1095,286),(1100,305),
 (1106,315),(1108,335),(1104,346),(1091,350),(1083,369),(1072,377),(1055,376),(1047,364),
 (916,380),(911,391),(899,398),(885,396),(876,386),(873,373),(770,380),(758,387),
 (741,387),(732,379),(723,373),(712,365),(707,353)])
save('objects/cyclist',(1195,283,1393,471),[
 (1285,286),(1299,283),(1310,288),(1316,300),(1310,308),(1320,313),(1335,312),(1351,316),
 (1361,327),(1365,344),(1356,352),(1343,356),(1329,365),(1325,376),(1320,387),(1328,400),
 (1345,394),(1365,395),(1382,407),(1392,429),(1390,450),(1377,466),(1354,471),
 (1334,465),(1320,453),(1300,456),(1293,451),(1280,430),(1276,445),(1265,462),
 (1247,471),(1227,470),(1208,457),(1196,438),(1197,418),(1206,400),(1223,390),
 (1248,389),(1248,380),(1255,366),(1252,361),(1242,360),(1240,350),(1245,343),
 (1259,347),(1274,340),(1286,328),(1292,315),(1287,309),(1280,303)])
save('objects/speed-sign',(1438,114,1513,397),[
 (1468,115),(1490,115),(1506,127),(1512,148),(1507,171),(1496,183),(1480,189),
 (1481,349),(1485,352),(1485,393),(1476,397),(1470,394),(1468,353),(1470,350),(1470,188),
 (1455,183),(1442,170),(1438,150),(1442,131),(1453,119)])
save('methods/handcrafted-features',(42,729,193,895))
save('methods/bicycle-icon',(945,816,994,848),[(947,818),(970,816),(992,820),(994,846),(945,848)])

(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)),assets=records),indent=2))
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
sheet=Image.new('RGB',(1280,930),'#e3e8ed');draw=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
    if i==0:x,y,w,h=10,10,1260,400
    else:x,y,w,h=10+(i-1)%4*320,425+(i-1)//4*250,300,235
    draw.rounded_rectangle((x,y,x+w,y+h),10,fill='#fafafa',outline='#b5c1ce')
    im=Image.open(ROOT/r['file']);im.thumbnail((w-24,h-42),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+(w-im.width)//2,y+8+(h-42-im.height)//2),im)
    draw.text((x+12,y+h-28),r['file'].replace('.png',''),font=font,fill='#223443')
sheet.save(ROOT/'overview.png')
for r in records:
    im=Image.open(ROOT/r['file']);assert im.mode=='RGBA' and im.getbbox() and im.getchannel('A').getextrema()[0]==0
print('Verified',len(records),'transparent PNG assets')
