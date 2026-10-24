import datetime as dt

import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import numpy as np

from institutional_exhibit import Frame, usd_bn, inr

# ---------- font check: should print Inter files, not DejaVu ----------
for fam, w in [("Inter", 400), ("Inter ExtraBold", 800)]:
    print(fam, "->", fm.findfont(fm.FontProperties(family=fam, weight=w),
                                 fallback_to_default=False))

# ---------- dummy data: Q1 2023 to Q3 2026 (quarter-end dates) ----------
dates = []
for y in range(2023, 2027):
    for m, d in [(3, 31), (6, 30), (9, 30), (12, 31)]:
        dates.append(dt.date(y, m, d))
dates = dates[:15]
n = len(dates)
x = mdates.date2num(dates)

rng = np.random.default_rng(7)
fca = np.linspace(505, 630, n) + rng.normal(0, 8, n)
gold = np.linspace(45, 110, n) + rng.normal(0, 3, n)
sdr = 18 + rng.normal(0, 0.3, n)
rtp = 4.5 + rng.normal(0, 0.1, n)
usdinr = np.linspace(82.3, 95.6, n) + rng.normal(0, 0.5, n)

# ---------- frame ----------
f = Frame(
    width=1920, height=1080,
    title="India's Foreign Exchange Reserves Composition",
    subtitle=("From Q1 2023 to Q3 2026, reserves rose US$XXXbn to US$XXXbn "
              "(FCA +US$XXXbn, gold +US$XXXbn); USD/INR climbed X.X%, signalling "
              "rupee weakness. In Q3 2026, reserves rose US$XXbn quarter-on-quarter, "
              "led by FCA (+US$XX.Xbn) and gold (+US$XX.Xbn). On DD Mon, FCA made up "
              "XX.X% of reserves, gold XX.X%, SDRs X.X% and RTP X.X%."),
    note=("Note: Stacked bars show foreign currency assets, gold, SDRs and India's "
          "reserve tranche position in the IMF (RTP), in US$ billions. Quarterly bars "
          "use each period's final available weekly observation (the latest period may "
          "be partial); USD/INR is the quarterly average. A higher USD/INR rate means "
          "a weaker rupee."),
    source="Source: Reserve Bank of India via DBIE; USD/INR: Federal Reserve via FRED",
    debug=False,   # True shows the grey plot area and orange margin lines
)

# ---------- themed plot ----------
ax, ax2 = f.add_axes(twin=True)

f.stacked_bars(
    ax, x, [fca, gold, sdr, rtp],
    labels=["Foreign currency assets (FCA)", "Gold reserves", "SDRs",
            "IMF Reserve Tranche Position (RTP)"],
    width=34, partial_last=True,          # width in days, since x is a date axis
)
f.line(ax2, x, usdinr, label="USD/INR (quarterly average)")

# axis limits are yours to choose; fit() only sizes the outside
ax.set_ylim(0, 800)
ax2.set_ylim(82, 96)
ax.set_xlim(x[0] - 70, x[-1] + 70)

# year ticks, unlabelled quarterly bars (as in the reference)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.yaxis.set_major_locator(plt_ticker := __import__("matplotlib.ticker", fromlist=["x"]).MultipleLocator(100))
ax.yaxis.set_major_formatter(usd_bn)
ax2.yaxis.set_major_locator(__import__("matplotlib.ticker", fromlist=["x"]).MultipleLocator(2))
ax2.yaxis.set_major_formatter(inr)
f.ylabels(ax, "Reserves (US$ billions)", ax2, "Indian rupees per US dollar")

# ---------- legend at the bottom, fit everything into the plot area, save ----------
f.fit()
f.save("test_chart.png")
print("Saved test_chart.png, plot area (l, t, w, h):", f.plot_rect_px)