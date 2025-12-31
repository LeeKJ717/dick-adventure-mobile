@echo off
chcp 65001 >nul 2>&1
echo ==========================================
echo DEQJAM 안드로이드 빌드
echo ==========================================

echo.
echo [1/3] Buildozer 설치 확인...
python -m pip install buildozer
if errorlevel 1 (
    echo ERROR: Buildozer 설치 실패!
    pause
    exit /b 1
)

echo.
echo [2/3] Python-for-Android 의존성 설치...
python -m pip install cython
if errorlevel 1 (
    echo ERROR: Cython 설치 실패!
    pause
    exit /b 1
)

echo.
echo [3/3] 안드로이드 APK 빌드 중...
echo 이 작업은 시간이 오래 걸릴 수 있습니다 (10-30분)...
echo.
buildozer android debug

if errorlevel 1 (
    echo.
    echo ==========================================
    echo 빌드 실패!
    echo 에러 로그를 확인하세요.
    echo ==========================================
    pause
    exit /b 1
) else (
    echo.
    echo ==========================================
    echo 빌드 완료!
    echo APK 파일 위치: bin\deqjam-1.0.0-arm64-v8a-debug.apk
    echo ==========================================
    pause
)

