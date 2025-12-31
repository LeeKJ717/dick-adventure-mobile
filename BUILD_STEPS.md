# 안드로이드 빌드 단계별 가이드

이 문서는 6단계부터의 실제 빌드 과정을 안내합니다.

## 6단계: buildozer.spec 설정 완료 ✅

`buildozer.spec` 파일이 이미 수정되었습니다. 서명 키를 생성한 후 주석을 해제하세요.

## 7단계: 서명 키 생성

### 방법 1: 스크립트 사용 (권장)

**Linux/WSL2:**
```bash
chmod +x create_keystore.sh
./create_keystore.sh
```

**Windows:**
```cmd
create_keystore.bat
```

### 방법 2: 수동 생성

```bash
keytool -genkey -v -keystore deqjam-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias deqjam
```

**입력 정보:**
- 키 저장소 비밀번호: (안전한 비밀번호 입력)
- 이름과 성: (예: Lee KJ)
- 조직 단위: (예: Development)
- 조직: (예: LeeKJ717)
- 도시: (예: Seoul)
- 시/도: (예: Seoul)
- 국가 코드: KR
- 비밀번호 확인: (위와 동일)

### 서명 정보를 buildozer.spec에 추가

서명 키 생성 후 `buildozer.spec` 파일을 열고 다음 줄의 주석을 해제하고 실제 값으로 채우세요:

```ini
# 절대 경로로 변경 (예: /home/사용자명/DEQJAM_2025-1231/deqjam-release-key.jks)
android.keystore_path = /mnt/c/Users/UserK/Desktop/DEQJAM_2025-1231/deqjam-release-key.jks

# alias는 deqjam으로 설정
android.keystore_alias = deqjam

# 생성 시 입력한 비밀번호
android.keystore_password = 당신의_비밀번호
```

## 8단계: AAB 파일 빌드

### 사전 준비 확인

1. **WSL2 설치 확인:**
   ```powershell
   wsl --list --verbose
   ```

2. **필수 패키지 설치 (WSL2/Ubuntu):**
   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   ```

3. **Buildozer 설치:**
   ```bash
   pip install buildozer cython
   ```

4. **Android SDK 설치:**
   - Android Studio 설치 또는
   - 명령줄로 SDK 설치 (ANDROID_BUILD_GUIDE.md 참조)

5. **환경 변수 설정:**
   ```bash
   export ANDROID_HOME=~/android-sdk
   export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
   ```

### 빌드 실행

```bash
# WSL2에서 프로젝트 디렉토리로 이동
cd /mnt/c/Users/UserK/Desktop/DEQJAM_2025-1231

# 첫 빌드는 시간이 오래 걸립니다 (10-30분)
buildozer android release
```

**빌드 성공 시:**
- 파일 위치: `bin/deqjam-1.0.0-arm64-v8a-release.aab`
- 이 파일을 구글 플레이 콘솔에 업로드하세요

## 9단계: 구글 플레이 콘솔 업로드

### 1. 개발자 계정 준비
- [Google Play Console](https://play.google.com/console) 접속
- 개발자 등록 ($25 일회성 결제)

### 2. 새 앱 생성
1. "앱 만들기" 클릭
2. 앱 정보 입력:
   - 앱 이름: **DEQJAM**
   - 기본 언어: **한국어**
   - 앱 또는 게임: **게임**
   - 무료 또는 유료: **무료**

### 3. AAB 파일 업로드
1. 왼쪽 메뉴에서 "프로덕션" 선택
2. "새 버전 만들기" 클릭
3. "앱 번들 업로드" 클릭
4. `bin/deqjam-1.0.0-arm64-v8a-release.aab` 파일 선택

### 4. 스토어 등록 정보 작성
필수 항목:
- **앱 설명** (최소 80자)
- **스크린샷** (최소 2개, 권장 5개)
  - 전화: 최소 2개 (16:9 또는 9:16)
  - 7인치 태블릿: 최소 1개
  - 10인치 태블릿: 최소 1개
- **고해상도 아이콘** (512x512 PNG, 투명 배경 없음)
- **기능 그래픽** (1024x500 PNG, 선택사항)

### 5. 콘텐츠 등급
- "콘텐츠 등급" 메뉴에서 설문 작성
- 게임 특성에 맞게 답변

### 6. 가격 및 배포
- "가격 및 배포" 메뉴
- 무료 앱으로 설정
- 배포 국가 선택

### 7. 검토 제출
- 모든 필수 정보 입력 완료 후
- "검토 제출" 클릭
- 검토는 보통 1-3일 소요

## 문제 해결

### 빌드 오류
```bash
# 빌드 캐시 정리 후 재시도
buildozer android clean
buildozer android release
```

### 메모리 부족
```bash
export JAVA_OPTS="-Xmx2048m"
buildozer android release
```

### NDK 경로 오류
`buildozer.spec`에서 `android.ndk = 25b` 확인

## 다음 단계 체크리스트

- [ ] 서명 키 생성 완료
- [ ] buildozer.spec에 서명 정보 추가 완료
- [ ] WSL2 설치 완료
- [ ] 필수 패키지 설치 완료
- [ ] Buildozer 설치 완료
- [ ] Android SDK 설치 완료
- [ ] AAB 파일 빌드 완료
- [ ] 구글 플레이 개발자 계정 생성 완료
- [ ] 앱 정보 입력 완료
- [ ] AAB 파일 업로드 완료
- [ ] 스토어 등록 정보 작성 완료
- [ ] 검토 제출 완료

