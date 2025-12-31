#!/bin/bash
# 안드로이드 APK 빌드 스크립트

echo "=========================================="
echo "DEQJAM 안드로이드 빌드"
echo "=========================================="

# Buildozer 설치 확인
if ! command -v buildozer &> /dev/null; then
    echo "Buildozer가 설치되어 있지 않습니다."
    echo "설치 중..."
    pip install buildozer
fi

# Python-for-Android 의존성 설치
echo "Python-for-Android 의존성 설치 중..."
pip install cython

# 안드로이드 빌드
echo "안드로이드 APK 빌드 중..."
echo "이 작업은 시간이 오래 걸릴 수 있습니다 (10-30분)..."
buildozer android debug

if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "빌드 완료!"
    echo "APK 파일 위치: bin/deqjam-1.0.0-arm64-v8a-debug.apk"
    echo "=========================================="
else
    echo "=========================================="
    echo "빌드 실패!"
    echo "에러 로그를 확인하세요."
    echo "=========================================="
fi

