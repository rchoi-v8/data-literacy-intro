#!/usr/bin/env python3
"""왓챠피디아 리뷰 JSON에서 발표용 차트 이미지를 생성한다.

투명 배경 차트를 렌더하며, 슬라이드 배경에 맞춰 다크/라이트 팔레트를 고른다.

사용법:
    python3 make_charts.py <reviews.json> [out_dir] [--light]
"""
import json
import sys
import collections
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---- palette ------------------------------------------------------------
ARGV = [a for a in sys.argv if a != "--light"]
LIGHT = len(ARGV) != len(sys.argv)

if LIGHT:
    BG = "#f7f2e8"
    INK = "#1a1815"
    INK_SOFT = "#4a463f"
    MUTED = "#7a7266"
    LINE = "#ded4c2"
    GOLD = "#b87a12"
    BLUE = "#2f6bd8"
    RED = "#c8402a"
    ORANGE = "#c9773a"
    BAR_GRAY = "#d8cdb8"
else:
    BG = "#101a2b"
    INK = "#ede9df"
    INK_SOFT = "#c9c6bc"
    MUTED = "#9aa2b1"
    LINE = "#2c3a52"
    GOLD = "#e8b04b"
    BLUE = "#7fa9ff"
    RED = "#f07a63"
    ORANGE = "#e8965a"
    BAR_GRAY = "#33425c"

for fam in ["Apple SD Gothic Neo", "AppleGothic", "NanumGothic", "Noto Sans CJK KR"]:
    try:
        font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False


def style(ax):
    ax.set_facecolor("none")
    for s in ax.spines.values():
        s.set_color(LINE)
    ax.tick_params(colors=INK_SOFT, labelsize=16)
    ax.yaxis.grid(True, color=LINE, linewidth=0.7, alpha=0.6)
    ax.set_axisbelow(True)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)


def save(fig, out):
    fig.savefig(out, dpi=200, transparent=True, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("saved", out)


# ---- load ----------------------------------------------------------------
src = Path(ARGV[1] if len(ARGV) > 1 else "watcha_no_other_choice_reviews.json")
out_dir = Path(ARGV[2] if len(ARGV) > 2 else "reports")
out_dir.mkdir(parents=True, exist_ok=True)
data = json.loads(src.read_text(encoding="utf-8"))
reviews = data["reviews"]
rated = [r["rating"] for r in reviews if r["rating"] is not None]

agg = {
    "title": data.get("movie"),
    "total": len(reviews),
    "rated": len(rated),
    "unrated": len(reviews) - len(rated),
    "avg_rating": round(statistics.mean(rated), 3),
    "median_rating": statistics.median(rated),
    "stdev": round(statistics.pstdev(rated), 3),
    "positive": sum(1 for x in rated if x >= 3.5),
    "neutral": sum(1 for x in rated if 2.5 <= x < 3.5),
    "negative": sum(1 for x in rated if x < 2.5),
    "spoilers": sum(1 for r in reviews if r["spoiler"]),
    "likes_total": sum(r["likes"] for r in reviews),
    "rating_dist": {str(k): v for k, v in sorted(collections.Counter(rated).items())},
}
(out_dir.parent / "data").mkdir(exist_ok=True)
(out_dir.parent / "data" / "aggregates.json").write_text(
    json.dumps(agg, ensure_ascii=False, indent=2), encoding="utf-8"
)

# ---- 1. rating distribution ---------------------------------------------
labels = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
counts = [agg["rating_dist"].get(str(x), 0) for x in labels]
colors = [RED if x < 2.5 else (GOLD if x < 3.5 else BLUE) for x in labels]
fig, ax = plt.subplots(figsize=(7.2, 4.2))
bars = ax.bar([str(x) for x in labels], counts, color=colors, width=0.72)
for b, c in zip(bars, counts):
    ax.text(b.get_x() + b.get_width() / 2, c + max(counts) * 0.015, f"{c:,}\n{c/len(rated)*100:.1f}%",
            ha="center", va="bottom", fontsize=14, color=INK)
ax.set_xlabel("별점", color=INK_SOFT, fontsize=16)
ax.set_ylabel("코멘트 수", color=INK_SOFT, fontsize=16)
ax.set_ylim(0, max(counts) * 1.18)
style(ax)
save(fig, out_dir / "rating_distribution.png")

# ---- 2. sentiment donut --------------------------------------------------
sizes = [agg["positive"], agg["neutral"], agg["negative"]]
nice = ["긍정 3.5+", "중립 2.5–3.0", "부정 <2.5"]
cols = [BLUE, GOLD, RED]
fig, ax = plt.subplots(figsize=(6.0, 4.8))
w, t, at = ax.pie(sizes, colors=cols, startangle=90, counterclock=False,
                  wedgeprops=dict(width=0.36, edgecolor=BG, linewidth=3),
                  autopct=lambda p: f"{p:.1f}%", pctdistance=0.79,
                  textprops=dict(color=INK, fontsize=15, fontweight="bold"))
ax.text(0, 0.08, f"{agg['avg_rating']}", ha="center", va="center", fontsize=42, color=INK, fontweight="bold")
ax.text(0, -0.2, "리뷰 평균 별점", ha="center", va="center", fontsize=15, color=MUTED)
ax.legend(w, nice, loc="lower center", bbox_to_anchor=(0.5, -0.14), ncol=3, frameon=False,
          fontsize=14, labelcolor=INK_SOFT)
save(fig, out_dir / "sentiment_donut.png")

# ---- 3. monthly trend ----------------------------------------------------
by_month = collections.defaultdict(list)
for r in reviews:
    if r["rating"] is not None and r.get("created_at"):
        by_month[r["created_at"][:7]].append(r["rating"])
months = sorted(m for m in by_month if len(by_month[m]) >= 30)
cnts = [len(by_month[m]) for m in months]
avgs = [statistics.mean(by_month[m]) for m in months]
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.bar([m[2:4] + "." + m[5:7] for m in months], cnts, color=BAR_GRAY, width=0.62, label="코멘트 수")
ax.set_ylabel("코멘트 수", color=INK_SOFT, fontsize=16)
ax.tick_params(axis="x", rotation=0, labelsize=14)
ax.set_xticks(range(0, len(months), 2))
ax.set_xticklabels([m[2:4] + "." + m[5:7] for m in months][::2])
ax2 = ax.twinx()
ax2.plot([m[2:4] + "." + m[5:7] for m in months], avgs, color=GOLD, marker="o", markersize=6, linewidth=2.8, label="평균 별점")
ax2.set_ylim(3.0, 3.9)
ax2.set_ylabel("평균 별점", color=GOLD, fontsize=16)
ax2.tick_params(colors=GOLD)
ax2.spines["top"].set_visible(False)
for s in ax2.spines.values():
    s.set_color(LINE)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
leg = ax.legend(h1 + h2, l1 + l2, loc="upper right", frameon=False, fontsize=13)
for txt in leg.get_texts():
    txt.set_color(INK_SOFT)
style(ax)
ax2.patch.set_alpha(0)
save(fig, out_dir / "monthly_trend.png")

# ---- 4. keyword sentiment ------------------------------------------------
keywords = ["자본", "블랙코미디", "결말", "미장센", "연출", "박찬욱", "연기", "이병헌",
            "기생충", "원작", "지루", "어렵", "아쉽", "실망"]
krows = []
for kw in keywords:
    vs = [r["rating"] for r in reviews if r["rating"] is not None and kw in (r["text"] or "")]
    if len(vs) >= 15:
        krows.append((kw, len(vs), statistics.mean(vs)))
krows.sort(key=lambda x: x[2])
names = [k[0] for k in krows]
mentions = [k[1] for k in krows]
scores = [k[2] for k in krows]
bar_colors = [RED if s < 3.45 else (GOLD if s < 3.6 else BLUE) for s in scores]
fig, ax = plt.subplots(figsize=(6.8, 4.9))
bars = ax.barh(names, mentions, color=bar_colors, height=0.66)
for b, m, s in zip(bars, mentions, scores):
    ax.text(m + max(mentions) * 0.012, b.get_y() + b.get_height() / 2, f"{m:,}  ({s:.2f})",
            va="center", fontsize=14, color=INK)
ax.set_xlabel("언급 코멘트 수 (괄호 = 평균 별점)", color=INK_SOFT, fontsize=15)
ax.set_xlim(0, max(mentions) * 1.22)
style(ax)
ax.xaxis.grid(True, color=LINE, linewidth=0.8, alpha=0.5)
ax.yaxis.grid(False)
save(fig, out_dir / "keyword_sentiment.png")

# ---- 5. likes concentration (Pareto) -------------------------------------
likes = sorted((r["likes"] for r in reviews), reverse=True)
total = sum(likes) or 1
cum, run = [], 0
for i, x in enumerate(likes[:300], 1):
    run += x
    cum.append(run / total * 100)
fig, ax = plt.subplots(figsize=(6.8, 4.2))
ax.plot(range(1, len(cum) + 1), cum, color=GOLD, linewidth=3)
ax.fill_between(range(1, len(cum) + 1), cum, color=GOLD, alpha=0.10)
ax.axhline(80, color=MUTED, linestyle="--", linewidth=1)
for n in (10, 50, 100):
    ax.scatter([n], [cum[n - 1]], color=INK, zorder=5, s=34)
    ax.annotate(f"상위 {n}개 → {cum[n-1]:.0f}%", (n, cum[n - 1]),
                textcoords="offset points", xytext=(10, -14), fontsize=15, color=INK)
ax.set_xlabel("좋아요 상위 코멘트 수", color=INK_SOFT, fontsize=15)
ax.set_ylabel("누적 좋아요 점유율 (%)", color=INK_SOFT, fontsize=15)
style(ax)
save(fig, out_dir / "likes_concentration.png")

print("\nDONE. aggregates:", json.dumps(agg, ensure_ascii=False))
