@echo off
chcp 65001 > nul
echo.
echo ====================================
echo  HDCPA Research Plugin Installer
echo ====================================
echo.
echo 이 스크립트는 Claude Code CLI로 플러그인을 자동 설치합니다.
echo.

where claude >nul 2>nul
if %errorlevel% neq 0 (
    echo [오류] Claude Code CLI가 설치되어 있지 않습니다.
    echo.
    echo 먼저 다음을 설치하세요:
    echo   1. Node.js: https://nodejs.org/
    echo   2. Claude Code: npm install -g @anthropic-ai/claude-code
    echo.
    pause
    exit /b 1
)

echo [1/2] 마켓플레이스 등록 중...
claude plugin marketplace add "%~dp0"
if %errorlevel% neq 0 (
    echo [오류] 마켓플레이스 등록 실패
    pause
    exit /b 1
)

echo.
echo [2/2] 플러그인 설치 중...
claude plugin install company-research@hdcpa-research-marketplace
if %errorlevel% neq 0 (
    echo [오류] 플러그인 설치 실패
    pause
    exit /b 1
)

echo.
echo ====================================
echo  ✓ 설치 완료!
echo ====================================
echo.
echo 설치된 플러그인 확인:
claude plugin list
echo.
echo 사용법:
echo   1. Claude Code 또는 Cowork 시작
echo   2. "SK하이닉스 투자 검토 보고서 만들어줘" 라고 입력
echo.
pause
