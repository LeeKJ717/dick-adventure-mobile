# 안드로이드 빌드 가이드

이 가이드는 DEQJAM 게임을 안드로이드 APK로 빌드하고 구글 플레이 스토어에 배포하는 방법을 설명합니다.

## 사전 요구사항

### 1. Linux 또는 WSL2 (Windows Subsystem for Linux)

안드로이드 빌드는 Linux 환경에서 가장 잘 작동합니다. Windows에서는 WSL2를 사용하는 것을 권장합니다.

**WSL2 설치 (Windows):**
```powershell
wsl --install
```

### 2. 필요한 도구 설치

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

#### Fedora:
```bash
sudo dnf install -y git zip unzip java-17-openjdk-devel python3-pip autoconf libtool pkg-config zlib-devel ncurses-devel cmake libffi-devel openssl-devel
```

### 3. Android SDK 및 NDK 설치

#### 방법 1: Android Studio 사용 (권장)
1. [Android Studio](https://developer.android.com/studio) 다운로드 및 설치
2. Android Studio 실행 후 SDK Manager에서:
   - Android SDK Platform 33 설치
   - Android SDK Build-Tools 설치
   - Android NDK (Side by side) 25b 설치

#### 방법 2: 명령줄로 설치
```bash
# SDK 설치
mkdir -p ~/android-sdk
cd ~/android-sdk
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip
mkdir -p cmdline-tools/latest
mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true

# 환경 변수 설정
export ANDROID_HOME=~/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# SDK 및 NDK 설치
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0" "ndk;25.2.9519653"
```

### 4. Buildozer 설치

```bash
pip install buildozer
pip install cython
```

## 빌드 과정

### 1. 프로젝트 디렉토리로 이동

```bash
cd /path/to/DEQJAM_2025-1231
```

### 2. Buildozer 초기화 (처음 한 번만)

```bash
buildozer init
```

이미 `buildozer.spec` 파일이 있으므로 이 단계는 건너뛸 수 있습니다.

### 3. APK 빌드

#### 디버그 빌드:
```bash
buildozer android debug
```

#### 릴리스 빌드 (구글 플레이용):
```bash
buildozer android release
```

빌드된 APK는 `bin/` 디렉토리에 생성됩니다.

## 구글 플레이 스토어 배포

### 1. 서명 키 생성

```bash
keytool -genkey -v -keystore deqjam-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias deqjam
```

### 2. buildozer.spec에 서명 정보 추가

`buildozer.spec` 파일을 열고 다음을 추가:

```ini
# (str) The format used to package the app for release mode (aab or apk).
android.release_artifact = aab

# (str) The format used to package the app for debug mode (apk or aab).
android.debug_artifact = apk

# (str) Full path to a keystore file
android.keystore_path = /path/to/deqjam-release-key.jks

# (str) Keystore alias
android.keystore_alias = deqjam

# (str) Keystore password
android.keystore_password = YOUR_PASSWORD
```

### 3. Android App Bundle (AAB) 빌드

구글 플레이 스토어는 AAB 형식을 요구합니다:

```bash
buildozer android release
```

### 4. 구글 플레이 콘솔에 업로드

1. [Google Play Console](https://play.google.com/console) 접속
2. 새 앱 생성
3. 앱 정보 입력:
   - 앱 이름: DEQJAM
   - 기본 언어: 한국어
   - 앱 또는 게임: 게임
   - 무료 또는 유료: 무료
4. 프로덕션 트랙으로 AAB 파일 업로드
5. 스토어 등록 정보 작성:
   - 앱 설명
   - 스크린샷 (최소 2개)
   - 고해상도 아이콘 (512x512)
   - 기능 그래픽 (선택사항)
6. 콘텐츠 등급 설정
7. 가격 및 배포 설정
8. 검토 제출

## 앱 아이콘 및 리소스

### 아이콘 생성

구글 플레이 스토어는 다음 아이콘을 요구합니다:

1. **고해상도 아이콘**: 512x512 PNG (투명 배경 없음)
2. **기능 그래픽**: 1024x500 PNG (선택사항)

아이콘 파일을 `data/icon.png`에 저장하고 `buildozer.spec`에서 경로를 지정하세요:

```ini
icon.filename = %(source.dir)s/data/icon.png
```

### 스플래시 스크린

앱 시작 화면을 `data/presplash.png`에 저장:

```ini
presplash.filename = %(source.dir)s/data/presplash.png
```

## 문제 해결

### 빌드 오류

1. **NDK 경로 오류**: `buildozer.spec`에서 `android.ndk` 버전 확인
2. **메모리 부족**: `export JAVA_OPTS="-Xmx2048m"` 설정
3. **의존성 오류**: `buildozer android clean` 후 다시 빌드

### 런타임 오류

1. **터치 입력이 작동하지 않음**: `mobile_controls.py` 확인
2. **화면 크기 문제**: `main.py`의 동적 화면 크기 감지 확인
3. **파일 경로 오류**: 안드로이드에서는 상대 경로 사용

## 추가 최적화

### 성능 최적화

1. **프레임레이트 조정**: 안드로이드 기기 성능에 따라 FPS 조정
2. **텍스처 최적화**: 이미지 크기 최적화
3. **메모리 관리**: 불필요한 리소스 해제

### 배터리 최적화

1. 백그라운드 실행 비활성화
2. 불필요한 업데이트 최소화

## 참고 자료

- [Buildozer 문서](https://buildozer.readthedocs.io/)
- [Python-for-Android](https://python-for-android.readthedocs.io/)
- [Google Play Console 도움말](https://support.google.com/googleplay/android-developer)

