from xml.etree import ElementTree
from itertools import tee, izip
from click import echo, style

def pairs(iterable):
    for i in iterable:
        yield i, next(iterable)

def get_regions(roifile):
    """
    Imports a ROI from an ENVI 5 xml file.

    Currently only works for polygon exterior rings,
    and ignores all CRS settings.
    """
    tree = ElementTree.parse(roifile)
    for region in tree.iterfind('Region'):
        p = region.getchildren()[0].find('Polygon')
        if p is None:
            r = lambda x: style(x,fg='red')
            echo(r('Area ')+region.attrib['name']+r(' is not a polygon'))
            continue
        e = p.find('Exterior')
        r = e.find('LinearRing')
        coords = (float(i) for i in
            r.find('Coordinates').text.strip().split())
        yield dict(
            type='Feature',
            geometry=dict(
                type='Polygon',
                coordinates=[list(pairs(coords))]),
            properties=region.attrib)
