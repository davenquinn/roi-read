from os import path
from shapely.geometry import shape

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

