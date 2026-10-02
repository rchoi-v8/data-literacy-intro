#!/usr/bin/env python3
"""왓챠피디아 리뷰 JSON에서 발표용 차트 이미지를 생성한다.

사용법:
    python3 make_charts.py <reviews.json> [out_dir]
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

# ---- theme ---------------------------------------------------------------
PAPER = "#f5f2ea"
INK = "#191714"
INK_SOFT = "#4a443b"
MUTED = "#8a8272"
LINE = "#d8d1c2"
ACCENT = "#b3261e"
GOLD = "#c98a1b"
GREEN = "#2f6b4f"
BLUE = "#3a6ea5"

for fam in ["Apple SD Gothic Neo", "AppleGothic", "NanumGothic", "Noto Sans CJK KR"]:
    try:
        font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

def style(ax):
    ax.set_facecolor(PAPER)
    for s in ax.spines.values():
        s.set_color(LINE)
    ax.tick_params(colors=INK_SOFT, labelsize=13)
    ax.yaxis.grid(True, color=LINE, linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)

def save(fig, out):
    fig.savefig(out, dpi=200, facecolor=PAPER, bbox_inches="tight", pad_inches=0.35)
    plt.close(fig)
    print("saved", out)

# ---- load ----------------------------------------------------------------
src = Path(sys.argv[1] if len(sys.argv) > 1 else "watcha_no_other_choice_reviews.json")
out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "reports")
out_dir.mkdir(parents=True, exist_ok=True)
data = json.loads(src.read_text(encoding="utf-8"))
reviews = data["reviews"]
rated = [r["rating"] for r in reviews if r["rating"] is not None]

# ---- aggregates ----------------------------------------------------------
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
colors = [ACCENT if x in (4, 4.5) else (GREEN if x >= 3.5 else (GOLD if x >= 3 else LINE)) for x in labels]
fig, ax = plt.subplots(figsize=(11, 5.6))
bars = ax.bar([str(x) for x in labels], counts, color=colors, width=0.72)
for b, c in zip(bars, counts):
    ax.text(b.get_x() + b.get_width() / 2, c + max(counts) * 0.015, f"{c:,}\n{c/len(rated)*100:.1f}%",
            ha="center", va="bottom", fontsize=11, color=INK)
ax.set_title("별점 분포 — 4.0/3.5에 56.6% 집중", fontsize=17, color=INK, pad=16, fontweight="bold")
ax.set_xlabel("별점", color=INK_SOFT, fontsize=13)
ax.set_ylabel("코멘트 수", color=INK_SOFT, fontsize=13)
ax.set_ylim(0, max(counts) * 1.18)
style(ax)
save(fig, out_dir / "rating_distribution.png")

# ---- 2. sentiment donut --------------------------------------------------
sizes = [agg["positive"], agg["neutral"], agg["negative"]]
nice = ["긍정 3.5+", "중립 2.5–3.0", "부정 <2.5"]
cols = [GREEN, GOLD, ACCENT]
fig, ax = plt.subplots(figsize=(8.2, 6.4))
w, t, at = ax.pie(sizes, colors=cols, startangle=90, counterclock=False,
                  wedgeprops=dict(width=0.36, edgecolor=PAPER, linewidth=3),
                  autopct=lambda p: f"{p:.1f}%", pctdistance=0.79,
                  textprops=dict(color=INK, fontsize=13, fontweight="bold"))
ax.text(0, 0.08, f"{agg['avg_rating']}", ha="center", va="center", fontsize=46, color=INK, fontweight="bold")
ax.text(0, -0.2, "리뷰 평균 별점", ha="center", va="center", fontsize=13, color=MUTED)
ax.legend(w, nice, loc="lower center", bbox_to_anchor=(0.5, -0.14), ncol=3, frameon=False,
          fontsize=12, labelcolor=INK_SOFT)
ax.set_title("평가 비율 — 호평 71%", fontsize=17, color=INK, pad=10, fontweight="bold")
save(fig, out_dir / "sentiment_donut.png")

# ---- 3. monthly trend ----------------------------------------------------
by_month = collections.defaultdict(list)
for r in reviews:
    if r["rating"] is not None and r.get("created_at"):
        by_month[r["created_at"][:7]].append(r["rating"])
months = sorted(m for m in by_month if len(by_month[m]) >= 30)
cnts = [len(by_month[m]) for m in months]
avgs = [statistics.mean(by_month[m]) for m in months]
fig, ax = plt.subplots(figsize=(12, 5.8))
ax.bar(months, cnts, color=LINE, width=0.62, label="코멘트 수")
ax.set_ylabel("코멘트 수", color=INK_SOFT, fontsize=13)
ax.tick_params(axis="x", rotation=40)
ax2 = ax.twinx()
ax2.plot(months, avgs, color=ACCENT, marker="o", markersize=6, linewidth=2.6, label="평균 별점")
ax2.set_ylim(3.0, 3.9)
ax2.set_ylabel("평균 별점", color=ACCENT, fontsize=13)
ax2.tick_params(colors=ACCENT)
ax2.spines["top"].set_visible(False)
for s in ax2.spines.values():
    s.set_color(LINE)
ax.set_title("시기별 반응 — 개봉 초 3.61 → 완만한 하락", fontsize=17, color=INK, pad=16, fontweight="bold")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper right", frameon=False, fontsize=11)
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
bar_colors = [ACCENT if s < 3.45 else (GOLD if s < 3.6 else GREEN) for s in scores]
fig, ax = plt.subplots(figsize=(10.5, 6.2))
bars = ax.barh(names, mentions, color=bar_colors, height=0.66)
for b, m, s in zip(bars, mentions, scores):
    ax.text(m + max(mentions) * 0.012, b.get_y() + b.get_height() / 2, f"{m:,}  ({s:.2f})",
            va="center", fontsize=11, color=INK)
ax.set_xlabel("언급 코멘트 수 (괄호 = 해당 리뷰 평균 별점)", color=INK_SOFT, fontsize=12)
ax.set_xlim(0, max(mentions) * 1.22)
ax.set_title("키워드별 언급량·평균 별점 — 초록=호평, 빨강=혹평", fontsize=16, color=INK, pad=16, fontweight="bold")
style(ax)
ax.xaxis.grid(True, color=LINE, linewidth=0.8, alpha=0.7)
ax.yaxis.grid(False)
save(fig, out_dir / "keyword_sentiment.png")

# ---- 5. likes concentration (Pareto) -------------------------------------
likes = sorted((r["likes"] for r in reviews), reverse=True)
total = sum(likes) or 1
cum, run = [], 0
for i, x in enumerate(likes[:300], 1):
    run += x
    cum.append(run / total * 100)
fig, ax = plt.subplots(figsize=(10.5, 5.6))
ax.plot(range(1, len(cum) + 1), cum, color=ACCENT, linewidth=2.8)
ax.fill_between(range(1, len(cum) + 1), cum, color=ACCENT, alpha=0.08)
ax.axhline(80, color=MUTED, linestyle="--", linewidth=1)
for n in (10, 50, 100):
    ax.scatter([n], [cum[n - 1]], color=INK, zorder=5, s=32)
    ax.annotate(f"상위 {n}개 → {cum[n-1]:.0f}%", (n, cum[n - 1]),
                textcoords="offset points", xytext=(10, -14), fontsize=12, color=INK)
ax.set_xlabel("좋아요 상위 코멘트 수", color=INK_SOFT, fontsize=12)
ax.set_ylabel("누적 좋아요 점유율 (%)", color=INK_SOFT, fontsize=12)
ax.set_title("좋아요 집중도 — 소수 리뷰가 여론을 주도", fontsize=17, color=INK, pad=16, fontweight="bold")
style(ax)
save(fig, out_dir / "likes_concentration.png")

print("\nDONE. aggregates:", json.dumps(agg, ensure_ascii=False))
