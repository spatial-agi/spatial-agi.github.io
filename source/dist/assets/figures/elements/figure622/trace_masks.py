"""Reproduce SVG person silhouettes from the original translucent instance masks.

Run extract.py first. Only the two color overlays are traced, within each person's
source region; frame labels and other diagram geometry remain independent.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import binary_closing, binary_fill_holes, label, shift
from matplotlib.figure import Figure

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]


def main():
    manifest = json.loads((ROOT/'manifest.json').read_text())
    original = Image.open(SITE/manifest['source']).convert('RGB')
    result = []
    for record in manifest['assets']:
        clean = np.asarray(Image.open(ROOT/record['file']).convert('RGB'), float)
        raw = np.asarray(original.crop(record['restoration']['segmentation_reference']), float)
        dx, dy = record['restoration']['segmentation_shift']
        raw = shift(raw, (-dy,-dx,0), order=1, mode='nearest')
        shapes = []
        for tint, roi in [([65,70,235], (24,70,98,244)), ([154,89,161], (99,81,160,244))]:
            direction, delta = np.asarray(tint)-clean, raw-clean
            alpha = np.sum(delta*direction, axis=2)/np.maximum(1,np.sum(direction**2, axis=2))
            residual = np.sqrt(np.mean((delta-alpha[:,:,None]*direction)**2, axis=2))
            mask = (alpha>.12)&(alpha<.85)&(residual<22)
            region = np.zeros(mask.shape, bool)
            x0,y0,x1,y1 = roi
            region[y0:y1,x0:x1] = True
            mask = binary_fill_holes(binary_closing(mask&region, iterations=2))
            labels, _ = label(mask)
            sizes = np.bincount(labels.ravel()); sizes[0] = 0
            mask = labels == sizes.argmax()
            fig = Figure(); ax = fig.subplots()
            contours = ax.contour(mask.astype(float), levels=[.5])
            path = max(contours.get_paths(), key=lambda p:len(p.vertices)).cleaned(simplify=True, curves=False)
            shapes.append('M'+'L'.join(f'{x:.1f} {y:.1f}' for x,y in path.vertices[:-1])+'Z')
        result.append(shapes)
    dest = ROOT/'geometry/instance-masks.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2)+'\n')
    print('Traced six SVG person-mask paths from original source overlays.')


if __name__ == '__main__':
    main()
