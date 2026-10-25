from dataclasses import dataclass


@dataclass(frozen=True)
class Spec:
    """House-style constants. Frozen: assignment raises FrozenInstanceError."""
    font: tuple = ("Inter", "Helvetica", "Arial", "DejaVu Sans")
    title_font: tuple = ("Inter ExtraBold", "Inter", "Helvetica", "Arial", "DejaVu Sans")
    title_weight: int = 800       # "Inter ExtraBold" only exists at weight 800

    # margins and gaps (px)
    margin_x: float = 60
    margin_top: float = 40
    margin_bottom: float = 40     # note end -> image bottom, always constant
    gap: float = 30               # subtitle ink -> plot area, plot area -> source ink
    title_gap: float = 5.4        # title -> subtitle
    footer_gap: float = 2         # source -> note

    # typography (px)
    title_size: float = 47.56
    title_lh: float = 57.6
    subtitle_size: float = 20.23
    subtitle_lh: float = 24
    footer_size: float = 16
    footer_lh: float = 20

    # baseline offsets from the top of each line box (px)
    title_baseline: float = 43
    subtitle_baseline: float = 21
    footer_baseline: float = 15

    # ink metrics used to measure the 22px gaps (px)
    subtitle_descent: float = 4.3   # baseline -> bottom of descenders
    footer_cap: float = 11.5        # cap height of the footer text


SPEC = Spec()