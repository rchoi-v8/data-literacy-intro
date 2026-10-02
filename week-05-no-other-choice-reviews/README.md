# Week 05 — 〈어쩔 수가 없다〉 왓챠피디아 리뷰 분석

박찬욱 감독의 2025년 영화 **〈어쩔 수가 없다 (No Other Choice)〉**에 대한 왓챠피디아 코멘트 **15,824건**을 수집·분석한 프로젝트입니다.

- 발표 덱: <https://rchoi-v8.github.io/data-literacy-intro/week-05-no-other-choice-reviews/>
- 원본 데이터: 왓챠피디아 코멘트 (좋아요 순, 2024-08 ~ 2026-10)

## 핵심 결과

| 지표 | 값 |
|---|---|
| 수집 코멘트 | 15,824건 (중복 0) |
| 별점 입력 | 15,750건 / 미입력 74건 |
| 평균 별점 | **3.53 / 5.0** (중앙값 3.5) |
| 긍정 (3.5+) | 11,181건 (**71.0%**) |
| 중립 (2.5–3.0) | 3,388건 (21.5%) |
| 부정 (<2.5) | 1,181건 (**7.5%**) |
| 좋아요 총합 | 42,818 (상위 10건이 37.5%) |

- **호평 우위의 양극단 작품.** 연출·미장센·블랙코미디·알레고리 해석은 호평, 동기 부여 빈약·‘계급 없는 계급 영화’·현실성 괴리는 혹평.
- 개봉 초 3.61 → 이후 3.3~3.5로 완만히 하락. 전체 코멘트의 약 64%가 개봉 직후(2025-09·10)에 집중.
- 다수 리뷰가 〈기생충〉(495회)·〈헤어질 결심〉(278회)과 비교.

## 파일 구성

```
week-05-no-other-choice-reviews/
├─ make_charts.py       # 리뷰 JSON → 차트 PNG 5종 재생성 스크립트
├─ data/
│  └─ aggregates.json   # 집계 결과(소형)
├─ reports/             # 생성된 차트 이미지 5종
│  ├─ rating_distribution.png
│  ├─ sentiment_donut.png
│  ├─ monthly_trend.png
│  ├─ keyword_sentiment.png
│  └─ likes_concentration.png
├─ REPORT.md            # 상세 분석 보고서
└─ README.md
```

발표 덱(HTML)은 `docs/week-05-no-other-choice-reviews/`에 있습니다.

## 차트 재생성

`make_charts.py`는 리뷰 원본 JSON을 입력받습니다.

```bash
python3 make_charts.py /path/to/watcha_no_other_choice_reviews.json reports
```

- 필요 패키지: `matplotlib` (한글 폰트: Apple SD Gothic Neo 등)
- 리뷰 원본(약 8.6MB)은 저장소 규칙에 따라 커밋하지 않았고, 집계 결과만 `data/aggregates.json`으로 남깁니다.

## 수집 방법

왓챠피디아 콘텐츠 페이지의 코멘트 API(`/api/contents/{id}/comments?filter=all&order=popular&page=N&size=30`)를 로그인 세션으로 페이지네이션하여 수집했습니다. 자세한 내용은 `REPORT.md`의 ‘데이터 한계’를 참고하세요.
