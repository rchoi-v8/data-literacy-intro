# intro-to-data-literacy

데이터 분석 입문 과목의 프로젝트 모음입니다. 프로젝트별로 폴더를 나눠 관리합니다.

## 프로젝트

| 주차 · 프로젝트 | 주제 | 폴더 | 발표 자료 |
|---|---|---|---|
| week-03-titanic | 타이타닉 생존 분석 + 예측 모델 | [`week-03-titanic/`](week-03-titanic/) | [deck](https://rchoi-v8.github.io/intro-to-data-literacy/week-03-titanic/) |
| week-03-pima-indians-diabetes | 피마 인디언 당뇨 예측 | [`week-03-pima-indians-diabetes/`](week-03-pima-indians-diabetes/) | [deck](https://rchoi-v8.github.io/intro-to-data-literacy/week-03-pima-indians-diabetes/) |
| week-05-no-other-choice-reviews | 〈어쩔 수가 없다〉 왓챠피디아 리뷰 15,824건 분석 | [`week-05-no-other-choice-reviews/`](week-05-no-other-choice-reviews/) | [deck](https://rchoi-v8.github.io/data-literacy-intro/week-05-no-other-choice-reviews/) |

## 폴더 구조

```
intro-to-data-literacy/
├─ week-03-titanic/          # 타이타닉 프로젝트
│  ├─ notebooks/             # 분석·모델 노트북
│  ├─ reports/               # 생성된 그래프 이미지
│  ├─ eda_quality_check.py
│  ├─ INSIGHTS.md
│  └─ README.md
├─ week-03-pima-indians-diabetes/   # 피마 인디언 당뇨 프로젝트
│  ├─ analysis.py            # 품질 점검
│  ├─ correlation.py         # 상관관계 시각화
│  ├─ model.py               # 예측 모델
│  ├─ reports/               # 생성된 그래프 이미지 + 모델
│  ├─ REPORT.md
│  └─ README.md
├─ week-05-no-other-choice-reviews/   # 〈어쩔 수가 없다〉 리뷰 분석
│  ├─ make_charts.py         # 차트 생성 스크립트
│  ├─ data/                  # 집계 결과(aggregates.json)
│  ├─ reports/               # 생성된 차트 이미지 5종
│  ├─ REPORT.md
│  └─ README.md
└─ docs/                     # GitHub Pages 사이트 소스
   ├─ index.html             # 프로젝트 목차 (랜딩)
   ├─ week-03-titanic/       # 타이타닉 발표 덱
   ├─ week-03-pima-indians-diabetes/  # 당뇨 발표 덱
   └─ week-05-no-other-choice-reviews/ # 〈어쩔 수가 없다〉 발표 덱
```

## 발표 사이트 (GitHub Pages)

- 랜딩: <https://rchoi-v8.github.io/intro-to-data-literacy/>
- 타이타닉 덱: <https://rchoi-v8.github.io/intro-to-data-literacy/week-03-titanic/>

사이트 소스는 `docs/` 폴더이며, Pages는 `master:/docs` 로 배포됩니다.

## 작성 규칙

- 프로젝트마다 `주차-주제/` 폴더 생성
- 노트북은 `notebooks/`, 산출 이미지는 `reports/`
- 큰 데이터 파일·비밀키는 커밋하지 않기 (`.gitignore` 활용)
- 각 프로젝트에 `README.md` 로 요약·실행법 정리
