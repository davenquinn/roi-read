import numpy as N
from os import path
from shapely.geometry import shape, Polygon, mapping
from rasterio.features import shapes,geometry_mask
from affine import Affine

from . import get_regions

image_sizes = dict(
    FRT0000CBE5=(640,480),
    HRL0000B8C2=(320,480))

def fixture(*args):
    """
    Gets a test fixture by path
    """
    return path.join(
        path.dirname(__file__),
        '..','test-fixtures',*args)

def test_import_roi():
    """
    Tests that we can successfully import a ROI from
    an ENVI 5 XML file.
    """
    fn = fixture('FRT0000CBE5.xml')
    data = list(get_regions(fn))
    assert len(data) == 20

    shapes = [shape(r['geometry']) for r in data]

def test_rasterize():
    """
    Test roundtripping from image mask to polygon
    and back again using rasterio's built-in functions.
    """
    image_shape = (200,100)
    coords = [(33,27),(50,22),(80,55)]
    coords.append(coords[0])
    poly = Polygon(shell=coords)
    p = mapping(poly)

    # Create initial mask
    mask0 = geometry_mask((p,),
        image_shape,Affine.identity(),invert=True)

    m = mask0.astype(N.uint8)
    s = [geom for geom,value in shapes(m)
            if value == 1]

    mask1 = geometry_mask(s,image_shape,Affine.identity(),invert=True)

    assert mask0.sum() == mask1.sum()
    assert N.allclose(mask0,mask1)

