import numpy as np
import matplotlib as mpl
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from institutional_exhibit import Frame  # importing also registers the bundled Inter fonts

# Make tick labels, axis titles and the legend use Inter too
mpl.rcParams["font.family"] = ["Helvetica", "DejaVu Sans"]

# ---------- dummy data: Q1 2023 to Q3 2026 ----------
quarters = [f"Q{q} {y}" for y in range(2023, 2027) for q in range(1, 5)][:15]
n = len(quarters)
rng = np.random.default_rng(7)

fca  = 500 + np.cumsum(rng.normal(4, 6, n))
gold = 40 + np.cumsum(rng.normal(3, 2, n))
sdr  = 18 + rng.normal(0, 0.2, n)
rtp  = 4.5 + rng.normal(0, 0.1, n)
usdinr = 82 + np.cumsum(rng.normal(0.25, 0.3, n))

# ---------- frame ----------
f = Frame(
    width=1920, height=1080,
    title="India's Foreign Exchange Reserves Composition",
    subtitle=("Over the period spanning Q1 2023 through Q3 2026, India's overall foreign exchange reserves experienced a sustained expansion, surging by US$XXX.X billion from US$XXX.X billion to US$XXX.X billion. This long-term growth trajectory was primarily fueled by substantial additions to foreign currency assets (FCA) (+US$XXX.X billion) alongside significant valuation gains and strategic acquisitions in gold holdings (+US$XXX.X billion). Over the same multi-year horizon, the USD/INR exchange rate appreciated by X.X% (moving from XX.XX to XX.XX), reflecting broader strength in the US dollar and underlying domestic structural dynamics. Focusing on the latest complete quarter (Q3 2026), foreign reserves grew by US$XX.X billion quarter-on-quarter, driven by robust quarterly inflows in foreign currency assets (+US$XX.X billion) and gold (+US$XX.X billion). As of the week ending DD Month 2026, foreign currency assets continued to dominate the asset allocation mix at XX.X% of total reserves, followed by gold reserves at XX.X%, Special Drawing Rights (SDRs) at X.X%, and India’s Reserve Tranche Position (RTP) in the International Monetary Fund at X.X%."),

    note=("Note: Reserve Bank of India (RBI). The stacked bar chart presents the composition of India’s total official foreign exchange reserves in billions of US Dollars (US$bn), broken down across four key sub-components: Foreign Currency Assets (FCA), Gold, Special Drawing Rights (SDRs), and the Reserve Tranche Position (RTP) with the International Monetary Fund (IMF). Quarterly data points reflect the final published weekly reserve position reported by the RBI within each respective quarter (note that the most recent period may reflect a partial quarter depending on data release schedules). Foreign Currency Assets are expressed in US dollar terms and include the valuation impacts of exchange rate movements in non-US currencies (such as the Euro, Pound Sterling, Japanese Yen, and Chinese Yuan) held within the reserve portfolio. The USD/INR exchange rate line plot represents the period-average spot exchange rate calculated across all trading days within each quarter. In accordance with currency conventions, an upward trend or higher value in the USD/INR exchange rate denotes a depreciation (weakness) of the Indian Rupee against the US Dollar."),

    source="Source: Reserve Bank of India via DBIE; USD/INR: Federal Reserve via FRED",
    debug=False,   # set True to see the grey plot area and orange margin lines
)

# ---------- plot ----------
ax = f.add_axes()
ax2 = ax.twinx()

x = np.arange(n)
colors = ["#1F4E79", "#C9A227", "#7F7F7F", "#F17000"]
bottom = np.zeros(n)
for vals, c in zip([fca, gold, sdr, rtp], colors):
    ax.bar(x, vals, bottom=bottom, color=c, width=0.7)
    bottom += vals

ax2.plot(x, usdinr, color="#000000", lw=2.5, marker="o", ms=5)

ax.set_xticks(x)
ax.set_xticklabels(quarters, rotation=45, ha="right", fontsize=12)
ax.tick_params(axis="y", labelsize=12)
ax2.tick_params(axis="y", labelsize=12)
ax.set_ylabel("US$ billions", fontsize=13)
ax2.set_ylabel("USD/INR", fontsize=13)
ax.margins(x=0.01)
for side in ("top",):
    ax.spines[side].set_visible(False)
    ax2.spines[side].set_visible(False)

# Legend (drawn on ax2 so it sits above the bars and line)
handles = [Patch(color=c) for c in colors] + [Line2D([0], [0], color="#000000", lw=2.5, marker="o")]
labels = ["Foreign currency assets", "Gold", "SDRs", "Reserve tranche position (RTP)", "USD/INR (RHS)"]
ax2.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 1.0),
           ncol=5, frameon=False, fontsize=13)

# ---------- fit axes + labels + legend into the plot area, then save ----------
f.fit([ax, ax2])
f.save("test_chart.png")
print("Saved test_chart.png, plot area (l, t, w, h):", f.plot_rect_px)