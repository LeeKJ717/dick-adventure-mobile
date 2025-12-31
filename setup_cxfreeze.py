"""
cx_Freeze setup script for DEQJAM
"""
import sys
from cx_Freeze import setup, Executable

# 포함할 파일들
include_files = [
    ("fig", "fig"),  # 이미지 파일들
]

# 제외할 모듈들
excludes = [
    "tkinter",
    "unittest",
    "email",
    "http",
    "xml",
    "pydoc",
]

# 빌드 옵션
build_exe_options = {
    "packages": ["pygame", "PIL"],
    "include_files": include_files,
    "excludes": excludes,
    "optimize": 2,
}

# 실행 파일 설정
executable = Executable(
    script="main.py",
    base="Win32GUI",  # 콘솔 창 숨김 (GUI만 표시)
    target_name="DEQJAM.exe",
    icon=None,
)

setup(
    name="DEQJAM",
    version="1.0",
    description="2D Open World Side-View Game",
    options={"build_exe": build_exe_options},
    executables=[executable],
)
