import sys
from pathlib import Path


def _prepend_music_labeler_root_to_syspath() -> None:
    root = Path(__file__).resolve().parents[1]
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


_prepend_music_labeler_root_to_syspath()
