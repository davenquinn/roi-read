from xml.etree import ElementTree

def pairs(iterable):
    for i in iterable:
        yield i, next(iterable)

def polygon_coords(polygon):
    e = polygon.find('Exterior')
    r = e.find('LinearRing')
    _ = (float(i) for i in
        r.find('Coordinates')
            .text.strip().split())
    return [list(pairs(_))]

def get_regions(roifile):
    """
    Imports a ROI from an ENVI 5 xml file.

    Currently only works for polygon exterior rings,
    and ignores all CRS settings.
    """
    tree = ElementTree.parse(roifile)
    for region in tree.iterfind('Region'):
        reg = region.getchildren()[0]
        if reg.tag != 'GeometryDef':
            continue

        polygons = [i for i in reg
                if i.tag == 'Polygon']

        if len(polygons) == 1:
            p = polygons[0]
            geom = dict(
                type='Polygon',
                coordinates=polygon_coords(polygons[0]))
        else:
            geom = dict(
                type='MultiPolygon',
                coordinates=[polygon_coords(i)
                    for i in polygons])

        yield dict(
            type='Feature',
            geometry=geom,
            properties=region.attrib)
