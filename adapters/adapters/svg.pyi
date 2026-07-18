from _typeshed import Incomplete
from checker import FAIL as FAIL

PAD: int
PANEL_W: int
MAX_SCALE: float
PASS_FILL: Incomplete
PASS_STROKE: Incomplete
FAIL_FILL: Incomplete
FAIL_STROKE: Incomplete
GREEN: Incomplete
RED: Incomplete
INK: Incomplete

def render_document(document: dict, title: str) -> str: ...
def render_pair(left: dict, right: dict, left_title: str, right_title: str) -> str: ...
