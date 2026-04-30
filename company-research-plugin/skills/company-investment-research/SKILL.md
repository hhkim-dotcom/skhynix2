---
name: company-investment-research
description: 한국 상장기업 투자검토용 종합 보고서 생성. "투자 검토", "종합 보고서", "회사 분석", "[종목명] 보고서" 같은 요청에 사용. 두 서브에이전트(naver-news-researcher, chrome-finance-researcher)를 병렬로 호출해 한국어 뉴스와 시세·재무 데이터를 동시 수집한 뒤, 표·차트·SWOT가 포함된 5페이지 Word(.docx) 보고서를 생성합니다. SK하이닉스, 삼성전자 등 코스피 종목과 투자 검토 키워드가 함께 나오면 적극 트리거.
---

# 한국 상장기업 투자검토 보고서 생성

## 사용 시점
- "[회사명] 투자 검토 보고서 만들어줘"
- "[종목명] 종합 분석 자료 5페이지로 정리해줘"

## 워크플로우

### Step 1: 두 서브에이전트를 병렬로 호출 (가장 중요)

**반드시 단일 어시스턴트 메시지에 Task 호출 2개를 함께 넣어야 병렬 실행됩니다:**

```
Task(subagent_type="naver-news-researcher", prompt="회사: {COMPANY}, 종목: {TICKER}, 14일")
Task(subagent_type="chrome-finance-researcher", prompt="회사: {COMPANY}, 종목: {TICKER}, KRX")
```

### Step 2: 결과 통합 → JSON 빌드
두 JSON을 받아 시세 카드, 분기 손익, 컨센서스, SWOT 섹션 합성

### Step 3: 차트 생성
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/company-investment-research/scripts/make_charts.py \
    --data /tmp/research_data.json --outdir /tmp/charts
```

### Step 4: Word 보고서 빌드
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/company-investment-research/scripts/make_docx.py \
    --data /tmp/research_data.json --charts /tmp/charts \
    --out "{회사명}_종합검토보고서_{YYYYMMDD}.docx"
```

### Step 5: [보고서 열기](computer://...) 링크로 사용자에게 전달

## 5페이지 구성

| Page | 내용 |
|------|------|
| 1 | 표지 + 시세 카드 + 핵심 요약 + 분기 손익표 + 분기 차트 |
| 2 | 시세·수급 표 + 주가 차트 + 수급 핵심 |
| 3 | 시장·사업 동향 표 + 컨센서스 비교 표 |
| 4 | 수익성 추이 차트 + SWOT-lite |
| 5 | 그룹·보상·ESG·브랜드 분석 + 출처·면책 |

## 가이드
- **병렬 실행 필수**: Task 호출은 한 메시지에 두 개를 함께
- **5페이지 엄수**: 표·차트로 압축
- **본문 한글, 차트 라벨 영문**: 한글 폰트 의존성 회피
- **인용 14단어 이하**: 저작권
- **면책**: 보고서 마지막에 "투자판단 근거가 아닙니다" 명시

## 의존성
- NaverSearch MCP (네이버 검색 API)
- Claude in Chrome MCP
- Python: python-docx, matplotlib
