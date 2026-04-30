# HDCPA Research Marketplace

한국 상장기업 투자 검토 보고서 자동 생성 플러그인.

## 포함된 플러그인

| 이름 | 설명 |
|------|------|
| `company-research` | 한국 상장기업 투자검토 5페이지 docx 보고서 자동 생성 |

## 설치 방법 (3가지 중 택1)

### 방법 A: Cowork 데스크톱 앱 (GitHub URL)

1. 이 폴더 전체를 본인 GitHub 리포에 업로드 (Public 권장)
2. Cowork → Customize → Plugins → Add Marketplace
3. URL: `https://github.com/<본인>/<리포명>`

### 방법 B: Claude Code CLI (가장 확실)

```cmd
claude plugin marketplace add C:\Users\LG\Desktop\Agent\하이닉스검토\company-research-marketplace
claude plugin install company-research@hdcpa-research-marketplace
```

또는 아래 자동 설치 스크립트 더블클릭:
```
INSTALL.bat
```

### 방법 C: 빠른 사용 (플러그인 없이 매번 요청)

설치 안 하고 그냥 Cowork 채팅에서:
> "SK하이닉스 투자 검토 보고서 만들어줘"

## 사용

설치 후:
- "SK하이닉스 투자 검토 보고서 만들어줘"
- "삼성전자 5페이지 분석 자료 작성해줘"

## 의존성

- NaverSearch MCP, Claude in Chrome MCP
- Python: python-docx, matplotlib

## Author

HDCPA · hhkim@hdcpa.co.kr · v1.0.0
