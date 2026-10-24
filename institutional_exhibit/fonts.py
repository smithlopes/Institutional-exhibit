from pathlib import Path
from tempfile import gettempdir

from matplotlib import font_manager as fm

_CANDIDATE_DIRS = [
    Path(__file__).parent / "fonts",          # bundled copies, if you add them
    Path.home() / "Library" / "Fonts",         # macOS user fonts
    Path("/Library/Fonts"),
    Path.home() / ".fonts",
    Path.home() / ".local" / "share" / "fonts",
    Path("/usr/share/fonts/truetype/inter"),
]
_REGULAR = "Inter-VariableFont_opsz,wght.ttf"
_ITALIC = "Inter-Italic-VariableFont_opsz,wght.ttf"


def _find(name):
    for d in _CANDIDATE_DIRS:
        if (d / name).exists():
            return d / name
    return None


def register_inter() -> bool:
    """Register Inter (regular, italic, generated ExtraBold). False if unavailable."""
    reg, ita = _find(_REGULAR), _find(_ITALIC)
    if reg is None:
        return False
    fm.fontManager.addfont(str(reg))
    if ita is not None:
        fm.fontManager.addfont(str(ita))

    try:
        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import instantiateVariableFont
    except ImportError:
        return True                              # regular/italic only

    xb = Path(gettempdir()) / "institutional-exhibit-inter-extrabold.ttf"
    if not xb.exists():
        font = instantiateVariableFont(TTFont(str(reg)), {"opsz": 32, "wght": 800},
                                       inplace=False)
        names = {1: "Inter ExtraBold", 2: "Regular", 4: "Inter ExtraBold",
                 6: "Inter-ExtraBold", 16: "Inter ExtraBold", 17: "Regular"}
        for rec in font["name"].names:
            if rec.nameID in names:
                rec.string = names[rec.nameID].encode(rec.getEncoding())
        font.save(str(xb))
    fm.fontManager.addfont(str(xb))
    return True