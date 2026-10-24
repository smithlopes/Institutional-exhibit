from dataclasses import dataclass

from matplotlib.ticker import FuncFormatter


@dataclass(frozen=True)
class Theme:
    """Chart styling. Sizes are canvas px (converted to points at draw time)."""
    # colours
    series: tuple = ("#6b8fd1", "#e8856a", "#55a868", "#9b8ac4")  # blue, orange, green, purple
    line: str = "#fcb149"
    ink: str = "#000000"
    subtitle_ink: str = "#000000"
    foot: str = "#8c8c8c"
    axis: str = "#7f7f7f"
    grid: str = "#b9b9b9"

    # text inside the plot area
    tick_size: float = 17.33
    label_size: float = 17.33
    label_pad: float = 16.67
    legend_size: float = 18.33
    legend_handlelength: float = 1.6
    legend_columnspacing: float = 1.8
    legend_handletextpad: float = 0.7
    legend_gap: float = 20          # tick labels -> legend

    # lines
    spine_w: float = 2.5
    grid_w: float = 1.67
    tick_w: float = 2.0
    xtick_len: float = 8.33
    xtick_pad: float = 13.33
    ytick_pad: float = 8.33
    bar_edge_w: float = 0.83
    line_w: float = 4.67
    marker: float = 8.33
    marker_edge_w: float = 2.0
    partial_alpha: float = 0.6      # for a partial final period


THEME = Theme()

# Tick formatters ($ is escaped so matplotlib doesn't read it as mathtext)
usd_bn = FuncFormatter(lambda v, _: f"US\\${v:,.0f}bn")
inr = FuncFormatter(lambda v, _: f"₹{v:,.0f}")