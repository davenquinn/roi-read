import numpy as N
from xml.etree import ElementTree
from rasterio.features import shapes
from shapely.geometry import shape, mapping, MultiPolygon

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

def extract_geometry(geometry_def, force_multi=True):
    """
    Extracts polygon(s) from geometry definition
    object.
    """
    polygons = [i for i in geometry_def
            if i.tag == 'Polygon']

    if len(polygons) == 1 and not force_multi:
        p = polygons[0]
        return dict(
            type='Polygon',
            coordinates=polygon_coords(polygons[0]))
    else:
        return dict(
            type='MultiPolygon',
            coordinates=[polygon_coords(i)
                for i in polygons])

def extract_pixels(pixel_def, force_multi=True):
    _ = pixel_def.find('Coordinates')
    nums = (int(i) for i in _.text.strip().split())
    idxs = N.array([(b,a) for a,b in pairs(nums)])
    im_shape = tuple(i.max()+1 for i in idxs.T)

    mask = N.zeros(im_shape,dtype=N.uint8)
    for i in idxs:
        mask[tuple(i)] = 1

    s = [geom
        for geom, value
        in shapes(mask)
        if value == 1]

    if len(s) == 1 and not force_multi:
        return s[0]
    else:
        return mapping(MultiPolygon([shape(i)
            for i in s]))

def get_regions(roifile):
    """
    Imports a ROI from an ENVI 5 xml file.

    Currently only works for polygon exterior rings,
    and ignores all CRS settings.
    """
    tree = ElementTree.parse(roifile)
    for region in tree.iterfind('Region'):
        reg = region.getchildren()[0]
        if reg.tag == 'GeometryDef':
            geom = extract_geometry(reg)
        elif reg.tag == 'PixelDef':
            geom = extract_pixels(reg)

        yield dict(
            type='Feature',
            geometry=geom,
            properties=region.attrib)
