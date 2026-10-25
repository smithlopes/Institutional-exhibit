# Institutional-Exhibit

Report-ready matplotlib charts with a fixed, consistent layout.

You supply a title, subtitle, source and note, plus your data. The library places the text, sizes the chart to fill the remaining space, and applies one house style (fonts, colours, gridlines, legend), so every chart looks the same no matter who made it.

## Install

```bash
pip install institutional-exhibit
```

To upgrade later:

```bash
pip install --upgrade institutional-exhibit
```

Requires Python 3.9 or newer. The Inter font is bundled, so there is nothing else to install. `Frame.show()` needs version 0.5.0 or newer.

## Quick start

```python
import datetime as dt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

from institutional_exhibit import Frame, usd_bn, inr

# Your data: quarter-end dates, four stacked series and one line
dates = [dt.date(2024, 3, 31), dt.date(2024, 6, 30),
         dt.date(2024, 9, 30), dt.date(2024, 12, 31)]
x = mdates.date2num(dates)
fca    = [520, 530, 545, 550]
gold   = [ 60,  70,  80,  90]
sdr    = [ 18,  18,  18,  18]
rtp    = [  4,   4,   5,   5]
usdinr = [83.1, 83.5, 84.0, 85.2]

# 1. Create the frame: canvas size and text
f = Frame(
    width=1920, height=1080,
    title="India's Foreign Exchange Reserves Composition",
    subtitle="Reserves rose US$XXbn over the period, led by foreign currency assets and gold.",
    note="Note: Stacked bars show reserves in US$ billions. USD/INR is the quarterly average.",
    source="Source: Reserve Bank of India; Federal Reserve via FRED",
)

# 2. Get themed axes (twin=True adds a second, right-hand axis)
ax, ax2 = f.add_axes(twin=True)

# 3. Plot with the themed helpers
f.stacked_bars(
    ax, x, [fca, gold, sdr, rtp],
    labels=["Foreign currency assets (FCA)", "Gold reserves", "SDRs",
            "IMF Reserve Tranche Position (RTP)"],
    width=34,              # bar width in days, because x is a date axis
    partial_last=True,     # fades the final bar (the latest period may be partial)
)
f.line(ax2, x, usdinr, label="USD/INR (quarterly average)")

# 4. Axis limits, ticks and labels are yours to set
ax.set_ylim(0, 800)
ax2.set_ylim(82, 96)
ax.set_xlim(x[0] - 70, x[-1] + 70)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.yaxis.set_major_locator(mticker.MultipleLocator(100))
ax.yaxis.set_major_formatter(usd_bn)      # US$100bn, US$200bn, ...
ax2.yaxis.set_major_locator(mticker.MultipleLocator(2))
ax2.yaxis.set_major_formatter(inr)        # ₹82, ₹84, ...
f.ylabels(ax, "Reserves (US$ billions)", ax2, "Indian rupees per US dollar")

# 5. Fit everything into the plot area, then display or save
f.fit()
f.show()                    # opens a window
# f.save("chart.png")       # or write the image to a file
```

Always call `f.fit()` after plotting and axis formatting, and before `show()` or `save()`.

## What you control

| Option | Where | Notes |
|---|---|---|
| Image size | `Frame(width=..., height=...)` | Default 1920 x 1080 px |
| Title, subtitle, source, note | `Frame(...)` | Wrapped automatically |
| Data and series labels | `stacked_bars`, `line` | |
| Axis limits, ticks, tick formats | Standard matplotlib on `ax` / `ax2` | `usd_bn` and `inr` formatters included |
| Axis titles | `f.ylabels(...)` | |
| Debug overlay | `Frame(debug=True)` | Shows the plot area and margin lines |

## What is locked

Font sizes, spacing, colours, gridlines, line weights and legend style are fixed in the library, so charts stay consistent. They can't be changed through `Frame` arguments.

The layout rules are:

- 60 px side margins and a 40 px top margin.
- The note always ends 40 px above the bottom edge, however many lines it wraps to.
- A fixed 30 px gap sits between the last subtitle line and the chart area, and between the chart area and the source line.
- The chart area includes the legend, which sits at the bottom, below the x-axis labels.
- If the subtitle, source or note wrap to more lines, the chart shrinks to make room. If the text is too long for the canvas height, `Frame` raises a `ValueError`.

## Method reference

| Method | What it does |
|---|---|
| `f.add_axes(twin=False)` | Returns one themed axes, or `(ax, ax2)` with `twin=True` |
| `f.stacked_bars(ax, x, series, labels, width=0.7, partial_last=False)` | Stacked bars in the theme colours; adds them to the legend |
| `f.line(ax, x, y, label)` | Themed line with white-faced markers; adds it to the legend |
| `f.add_legend_item(handle, label)` | Adds a custom legend entry |
| `f.ylabels(ax, left, ax2=None, right=None)` | Sets the axis titles |
| `f.fit()` | Places the legend and sizes the axes to fill the plot area |
| `f.show()` | Renders the frame and displays it with `plt.show()`; nothing is saved |
| `f.save(path)` | Writes the image at the exact pixel size |
| `f.plot_rect_px` | `(left, top, width, height)` of the plot area in pixels |

Dollar signs in text are escaped for you, so `US$100bn` displays as written.

## Showing and saving

- `f.show()` opens the full 1920 x 1080 frame in a plot window. Large frames may be scaled to fit your screen, so zoom in to inspect fine detail.
- `f.save("chart.png")` writes the image at the exact pixel size, with no cropping or extra padding. Use `.png` for slides and reports.

## Fonts

Charts use Inter, which is bundled with the package under the SIL Open Font License (see `institutional_exhibit/fonts/OFL.txt`). The ExtraBold title weight is generated on import with `fonttools` and cached in your temporary folder, so no system fonts are needed.

## Troubleshooting

- **A different font appears, or `findfont` warnings print:** make sure you aren't importing a local folder named `institutional_exhibit` instead of the installed package. Check with `python -c "import institutional_exhibit as m; print(m.__file__)"`; the path should be inside `site-packages`.
- **`ValueError: Text is too long`:** shorten the subtitle or note, or increase the canvas `height`.
- **Chart doesn't fill the area:** call `f.fit()` after all plotting and axis formatting.
- **`AttributeError: 'Frame' object has no attribute 'show'`:** upgrade with `pip install --upgrade institutional-exhibit` (needs 0.5.0 or newer).
- **`show()` opens no window or a blank one:** your matplotlib backend may be non-interactive. Check `matplotlib.get_backend()`, and use `f.save("chart.png")` instead if you are running without a display.

## License

MIT. Inter is licensed separately under the SIL Open Font License 1.1.