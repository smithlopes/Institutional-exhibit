from __future__ import annotations

import re
from dataclasses import dataclass

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox, IdentityTransform

from .spec import SPEC

S = SPEC

_DOLLAR = re.compile(r"(?<!\\)\$")


def _esc(s: str) -> str:
    """Escape bare $ so matplotlib doesn't treat it as mathtext."""
    return _DOLLAR.sub(r"\\$", s)


@dataclass
class Frame:
    width: int = 1920
    height: int = 1080
    title: str = ""
    subtitle: str = ""
    source: str = ""
    note: str = ""
    dpi: int = 100
    background: str = "#FFFFFF"
    debug: bool = False          # draws margin lines + plot-area box

    def __post_init__(self):
        self.fig = Figure(figsize=(self.width / self.dpi, self.height / self.dpi),
                          dpi=self.dpi, facecolor=self.background)
        self.canvas = FigureCanvasAgg(self.fig)
        self._renderer = self.canvas.get_renderer()
        self._build()

    # ---------- helpers ----------
    def _pt(self, px: float) -> float:
        return px * 72 / self.dpi

    def _wrap(self, text, size_px, weight, style, max_w):
        if not text:
            return []
        t = self.fig.text(0, 0, "", fontsize=self._pt(size_px), fontfamily=list(S.font),
                          fontweight=weight, fontstyle=style)
        lines, cur = [], ""
        for word in text.split():
            trial = f"{cur} {word}".strip()
            t.set_text(_esc(trial))
            if cur and t.get_window_extent(self._renderer).width > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        if cur:
            lines.append(cur)
        t.remove()
        return lines

    def _draw(self, lines, top, lh, base, size, weight, style, color):
        for i, line in enumerate(lines):
            y = top + i * lh + base          # baseline position, px from top
            self.fig.text(S.margin_x / self.width, 1 - y / self.height, _esc(line),
                          ha="left", va="baseline", color=color,
                          fontsize=self._pt(size), fontfamily=list(S.font),
                          fontweight=weight, fontstyle=style)

    # ---------- layout ----------
    def _build(self):
        W, H = self.width, self.height
        w = W - 2 * S.margin_x

        title = self._wrap(self.title, S.title_size, S.title_weight, "normal", w)
        sub_top = S.margin_top + len(title) * S.title_lh + S.title_gap
        sub = self._wrap(self.subtitle, S.subtitle_size, 400, "normal", w)
        sub_bottom = sub_top + len(sub) * S.subtitle_lh

        note = self._wrap(self.note, S.footer_size, 400, "italic", w)
        src = self._wrap(self.source, S.footer_size, 400, "italic", w)

        # Bottom-up: note always ends exactly margin_bottom above the image edge.
        note_top = H - S.margin_bottom - len(note) * S.footer_lh
        src_top = note_top - S.footer_gap - len(src) * S.footer_lh

        self.plot_top = sub_bottom + S.gap       # fixed gap below subtitle
        self.plot_bottom = src_top - S.gap       # fixed gap above source
        self.plot_left = S.margin_x
        self.plot_right = W - S.margin_x

        if self.plot_bottom <= self.plot_top:
            raise ValueError("Text is too long for this canvas height: "
                             "no room left for the plot area.")

        self._draw(title, S.margin_top, S.title_lh, S.title_baseline,
                   S.title_size, S.title_weight, "normal", "#000000")
        self._draw(sub, sub_top, S.subtitle_lh, S.subtitle_baseline,
                   S.subtitle_size, 400, "normal", "#000000")
        self._draw(src, src_top, S.footer_lh, S.footer_baseline,
                   S.footer_size, 400, "italic", "#434343")
        self._draw(note, note_top, S.footer_lh, S.footer_baseline,
                   S.footer_size, 400, "italic", "#434343")

        if self.debug:
            self._draw_debug()

    @property
    def plot_rect_px(self):
        """(left, top, width, height) in px, origin top-left."""
        return (self.plot_left, self.plot_top,
                self.plot_right - self.plot_left, self.plot_bottom - self.plot_top)

    def _draw_debug(self):
        ident = IdentityTransform()
        W, H = self.width, self.height
        self.fig.add_artist(Rectangle((self.plot_left, H - self.plot_bottom),
                                      self.plot_right - self.plot_left,
                                      self.plot_bottom - self.plot_top,
                                      transform=ident, facecolor="#D9D9D9", zorder=-10))
        m = dict(transform=ident, color="#F17000", lw=1)
        for xs, ys in [((0, W), (H - S.margin_top,) * 2),
                       ((0, W), (S.margin_bottom,) * 2),
                       ((S.margin_x,) * 2, (0, H)),
                       ((W - S.margin_x,) * 2, (0, H))]:
            self.fig.add_artist(Line2D(xs, ys, **m))

    # ---------- plotting ----------
    def add_axes(self):
        """Axes initially filling the plot area; call fit() after plotting."""
        l, t, w, h = self.plot_rect_px
        return self.fig.add_axes([l / self.width, 1 - (t + h) / self.height,
                                  w / self.width, h / self.height])

    def fit(self, axes, extra_artists=(), iterations=5):
        """Resize axes so axes + tick labels + axis titles + legend
        (incl. twin axes and fig.legend via extra_artists) fill the plot area exactly."""
        axes = list(axes)
        W, H = self.width, self.height
        target = Bbox.from_extents(self.plot_left, H - self.plot_bottom,
                                   self.plot_right, H - self.plot_top)
        main = axes[0]
        for _ in range(iterations):
            boxes = [a.get_tightbbox(self._renderer) for a in axes]
            boxes += [a.get_window_extent(self._renderer) for a in extra_artists]
            bb = Bbox.union(boxes)
            p = main.get_position()
            x0, x1, y0, y1 = p.x0 * W, p.x1 * W, p.y0 * H, p.y1 * H
            new = Bbox.from_extents(
                target.x0 + (x0 - bb.x0), target.y0 + (y0 - bb.y0),
                target.x1 - (bb.x1 - x1), target.y1 - (bb.y1 - y1))
            for a in axes:
                a.set_position([new.x0 / W, new.y0 / H, new.width / W, new.height / H])

    def save(self, path, **kw):
        self.fig.savefig(path, dpi=self.dpi, facecolor=self.background, **kw)