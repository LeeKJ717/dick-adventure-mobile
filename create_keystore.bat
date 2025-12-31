@echo off
chcp 65001 >nul 2>&1
echo ==========================================
echo DEQJAM 안드로이드 서명 키 생성
echo ==========================================
echo.
echo 이 스크립트는 구글 플레이 스토어 배포를 위한 서명 키를 생성합니다.
echo 생성된 키 파일은 안전하게 보관하세요. 분실하면 앱을 업데이트할 수 없습니다.
echo.

REM 프로젝트 디렉토리 확인
if not exist "buildozer.spec" (
    echo 오류: buildozer.spec 파일을 찾을 수 없습니다.
    echo 프로젝트 루트 디렉토리에서 실행하세요.
    pause
    exit /b 1
)

REM 키 파일이 이미 존재하는지 확인
if exist "deqjam-release-key.jks" (
    echo 경고: deqjam-release-key.jks 파일이 이미 존재합니다.
    set /p overwrite="덮어쓰시겠습니까? (y/N): "
    if /i not "%overwrite%"=="y" (
        echo 취소되었습니다.
        pause
        exit /b 0
    )
)

echo.
echo 서명 키 생성을 시작합니다...
echo 다음 정보를 입력하세요:
echo.

REM 서명 키 생성
keytool -genkey -v -keystore deqjam-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias deqjam

if errorlevel 1 (
    echo.
    echo ==========================================
    echo 서명 키 생성 실패!
    echo ==========================================
    pause
    exit /b 1
) else (
    echo.
    echo ==========================================
    echo 서명 키 생성 완료!
    echo ==========================================
    echo.
    echo 생성된 파일: deqjam-release-key.jks
    echo.
    echo 다음 단계:
    echo 1. buildozer.spec 파일을 열고
    echo 2. android.keystore_path, android.keystore_alias, android.keystore_password의
    echo    주석을 해제하고 실제 값으로 채우세요
    echo.
    echo 주의: 키 파일과 비밀번호를 안전하게 보관하세요!
    pause
)

