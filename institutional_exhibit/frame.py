from __future__ import annotations

import re
from dataclasses import dataclass

import matplotlib as mpl
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.transforms import Bbox, IdentityTransform

from .spec import SPEC
from .theme import THEME

S = SPEC
T = THEME

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
        # House font for everything, including tick labels, axis titles and legend
        mpl.rcParams["font.family"] = list(S.font)
        mpl.rcParams["text.hinting"] = "no_hinting"

        self.fig = Figure(figsize=(self.width / self.dpi, self.height / self.dpi),
                          dpi=self.dpi, facecolor=self.background)
        self.canvas = FigureCanvasAgg(self.fig)
        self._renderer = self.canvas.get_renderer()
        self._axes = []
        self._legend_items = []
        self._legend = None
        self._build()

    # ---------- helpers ----------
    def _pt(self, px: float) -> float:
        return px * 72 / self.dpi

    def _wrap(self, text, size_px, weight, style, max_w, family=None):
        if not text:
            return []
        t = self.fig.text(0, 0, "", fontsize=self._pt(size_px),
                          fontfamily=list(family or S.font),
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

    def _draw(self, lines, top, lh, base, size, weight, style, color, family=None):
        for i, line in enumerate(lines):
            y = top + i * lh + base          # baseline position, px from top
            self.fig.text(S.margin_x / self.width, 1 - y / self.height, _esc(line),
                          ha="left", va="baseline", color=color,
                          fontsize=self._pt(size), fontfamily=list(family or S.font),
                          fontweight=weight, fontstyle=style)

    # ---------- layout ----------
    def _build(self):
        W, H = self.width, self.height
        w = W - 2 * S.margin_x

        title = self._wrap(self.title, S.title_size, S.title_weight, "normal", w,
                           family=S.title_font)
        sub_top = S.margin_top + len(title) * S.title_lh + S.title_gap
        sub = self._wrap(self.subtitle, S.subtitle_size, 400, "normal", w)

        note = self._wrap(self.note, S.footer_size, 400, "italic", w)
        src = self._wrap(self.source, S.footer_size, 400, "italic", w)

        # Bottom-up: note always ends exactly margin_bottom above the image edge.
        note_top = H - S.margin_bottom - len(note) * S.footer_lh
        src_top = note_top - S.footer_gap - len(src) * S.footer_lh

        # 22px measured from visible ink, not from the line boxes:
        #   top:    bottom of the last subtitle line's descenders -> plot area
        #   bottom: plot area -> top of the source line's capital letters
        self.plot_top = (sub_top + (len(sub) - 1) * S.subtitle_lh
                         + S.subtitle_baseline + S.subtitle_descent + S.gap)
        self.plot_bottom = src_top + S.footer_baseline - S.footer_cap - S.gap
        self.plot_left = S.margin_x
        self.plot_right = W - S.margin_x

        if self.plot_bottom <= self.plot_top:
            raise ValueError("Text is too long for this canvas height: "
                             "no room left for the plot area.")

        self._draw(title, S.margin_top, S.title_lh, S.title_baseline,
                   S.title_size, S.title_weight, "normal", T.ink, family=S.title_font)
        self._draw(sub, sub_top, S.subtitle_lh, S.subtitle_baseline,
                   S.subtitle_size, 400, "normal", T.subtitle_ink)
        self._draw(src, src_top, S.footer_lh, S.footer_baseline,
                   S.footer_size, 400, "italic", T.foot)
        self._draw(note, note_top, S.footer_lh, S.footer_baseline,
                   S.footer_size, 400, "italic", T.foot)

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

    # ---------- themed axes ----------
    def _style_axes(self, ax, twin=False):
        pt = self._pt
        ax.set_facecolor("none")
        for s in ("top", "right", "left", "bottom"):
            ax.spines[s].set_visible(False)

        if not twin:
            ax.set_axisbelow(True)
            ax.grid(True, axis="y", linestyle="--", linewidth=pt(T.grid_w),
                    color=T.grid, zorder=0)
            for s in ("left", "bottom"):
                ax.spines[s].set_visible(True)
                ax.spines[s].set_color(T.axis)
                ax.spines[s].set_linewidth(pt(T.spine_w))
            ax.tick_params(axis="x", length=pt(T.xtick_len), width=pt(T.tick_w),
                           pad=pt(T.xtick_pad), labelsize=pt(T.tick_size), colors=T.ink)
        else:
            ax.patch.set_visible(False)
            ax.spines["right"].set_visible(True)
            ax.spines["right"].set_color(T.axis)
            ax.spines["right"].set_linewidth(pt(T.spine_w))

        ax.tick_params(axis="y", length=0, pad=pt(T.ytick_pad),
                       labelsize=pt(T.tick_size), colors=T.ink)

    def add_axes(self, twin=False):
        """Themed axes filling the plot area. twin=True returns (ax, ax2).
        Call fit() once everything is plotted."""
        l, t, w, h = self.plot_rect_px
        ax = self.fig.add_axes([l / self.width, 1 - (t + h) / self.height,
                                w / self.width, h / self.height])
        self._style_axes(ax)
        self._axes = [ax]
        if twin:
            ax2 = ax.twinx()
            self._style_axes(ax2, twin=True)
            self._axes.append(ax2)
            return ax, ax2
        return ax

    # ---------- themed plotting ----------
    def stacked_bars(self, ax, x, series, labels, width=0.7, partial_last=False):
        """Stacked bars in theme colours; adds each series to the legend."""
        x = np.asarray(x)
        bottom = np.zeros(len(x))
        for i, (vals, lab) in enumerate(zip(series, labels)):
            c = T.series[i % len(T.series)]
            vals = np.asarray(vals, dtype=float)
            bars = ax.bar(x, vals, width=width, bottom=bottom, color=c,
                          edgecolor="white", linewidth=self._pt(T.bar_edge_w), zorder=3)
            if partial_last:
                bars.patches[-1].set_alpha(T.partial_alpha)
            bottom = bottom + vals
            self._legend_items.append((Patch(facecolor=c), lab))

    def line(self, ax, x, y, label):
        """Line with white-faced markers in the theme line colour; adds it to the legend."""
        kw = dict(color=T.line, linewidth=self._pt(T.line_w), marker="o",
                  markersize=self._pt(T.marker), markerfacecolor="white",
                  markeredgewidth=self._pt(T.marker_edge_w))
        ax.plot(x, y, zorder=5, **kw)
        self._legend_items.append((Line2D([0], [0], **kw), label))

    def add_legend_item(self, handle, label):
        """Add a custom legend entry (appears after the auto-collected ones)."""
        self._legend_items.append((handle, label))

    def ylabels(self, ax, left, ax2=None, right=None):
        kw = dict(fontsize=self._pt(T.label_size), color=T.ink,
                  labelpad=self._pt(T.label_pad))
        ax.set_ylabel(_esc(left), **kw)
        if ax2 is not None and right:
            ax2.set_ylabel(_esc(right), **kw)

    # ---------- legend + fitting ----------
    def _place_legend(self):
        """Legend at the bottom of the plot area. Returns its height in px."""
        if not self._legend_items:
            return 0.0
        if self._legend is not None:
            self._legend.remove()
        handles, labels = zip(*self._legend_items)
        self._legend = self.fig.legend(
            handles, [_esc(l) for l in labels],
            loc="lower center",
            bbox_to_anchor=(0.5, (self.height - self.plot_bottom) / self.height),
            ncol=len(labels), frameon=False, borderpad=0, borderaxespad=0,
            fontsize=self._pt(T.legend_size),
            handlelength=T.legend_handlelength,
            columnspacing=T.legend_columnspacing,
            handletextpad=T.legend_handletextpad)
        for txt in self._legend.get_texts():
            txt.set_color(T.ink)
        return self._legend.get_window_extent(self._renderer).height

    def fit(self, iterations=5):
        """Place the legend at the bottom, then resize the axes so axes + tick labels
        + axis titles fill the rest of the plot area exactly."""
        axes = self._axes
        W, H = self.width, self.height
        leg_h = self._place_legend()
        reserve = leg_h + T.legend_gap if leg_h else 0.0
        target = Bbox.from_extents(self.plot_left, H - self.plot_bottom + reserve,
                                   self.plot_right, H - self.plot_top)
        main = axes[0]
        for _ in range(iterations):
            bb = Bbox.union([a.get_tightbbox(self._renderer) for a in axes])
            p = main.get_position()
            x0, x1, y0, y1 = p.x0 * W, p.x1 * W, p.y0 * H, p.y1 * H
            new = Bbox.from_extents(
                target.x0 + (x0 - bb.x0), target.y0 + (y0 - bb.y0),
                target.x1 - (bb.x1 - x1), target.y1 - (bb.y1 - y1))
            for a in axes:
                a.set_position([new.x0 / W, new.y0 / H, new.width / W, new.height / H])

    def save(self, path, **kw):
        self.fig.savefig(path, dpi=self.dpi, facecolor=self.background, **kw)