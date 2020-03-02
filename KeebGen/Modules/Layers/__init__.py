import adsk.core
import adsk.fusion
from .. import Config
from .. import Sketches


def bezel(keys):
    """, thickness, elevation):"""

    bezel_sketch = Sketches.bezel_cutout(keys)
    bezel_hull_sketch = Sketches.bezel_hull(bezel_sketch)
    offset_sketch = Sketches.offset_sketch(bezel_hull_sketch, 1)
