# Windows 배포 및 EXE 생성 가이드

Windows에서 Stock Monitor를 배포하고 실행 파일(EXE)을 생성하는 방법입니다.

---

## 📋 목차

1. [빠른 시작](#빠른-시작)
2. [2가지 실행 방법](#2가지-실행-방법)
3. [EXE 생성 방법](#exe-생성-방법)
4. [배포 방법](#배포-방법)
5. [트러블슈팅](#트러블슈팅)

---

## 🚀 빠른 시작

### 가장 간단한 방법: run.bat

1. **stock-monitor 폴더 열기**
2. **run.bat 더블클릭**
3. **자동으로 앱 실행됨**

완료! 이것만으로도 충분합니다. 👍

---

## 2가지 실행 방법

### 방법 1️⃣: run.bat 파일 (권장)

**장점:**
- ✅ 가장 간단
- ✅ Python만 필요
- ✅ 자동으로 설정 처리
- ✅ 모든 Windows 버전 지원

**실행:**
```bash
double-click run.bat
```

**동작:**
1. 가상환경 자동 생성
2. 필요한 패키지 자동 설치
3. 앱 자동 실행
4. 브라우저 자동 열기

---

### 방법 2️⃣: Windows EXE 파일

**장점:**
- ✅ Python 설치 불필요
- ✅ 다른 PC에 배포 용이
- ✅ 독립 실행형

**단점:**
- ⚠️ 파일 크기 크다 (300-400MB)
- ⚠️ 첫 실행 시 오래 걸린다 (1-2분)
- ⚠️ 생성에 시간이 걸린다 (2-5분)

---

## EXE 생성 방법

### 단계별 가이드

#### Step 1: build.bat 실행

```bash
double-click build.bat
```

**또는 명령 프롬프트에서:**
```cmd
build.bat
```

#### Step 2: 빌드 진행

```
[INFO] 가상환경을 생성 중입니다...
[INFO] PyInstaller를 설치 중입니다...
[INFO] 필요한 패키지를 설치 중입니다...
[INFO] Windows EXE 파일을 생성 중입니다...
(약 2-5분 소요)
```

#### Step 3: 완료

```
빌드 완료!
dist\StockMonitor.exe 파일이 생성되었습니다.
```

### EXE 파일 위치

```
stock-monitor/
└── dist/
    ├── StockMonitor.exe          ← 이것을 실행하면 됨
    ├── _internal/                ← 필요한 라이브러리
    └── (여러 .pyd 파일들)
```

---

## 실행 파일 크기

| 파일 | 크기 |
|------|------|
| StockMonitor.exe | 200-300MB |
| 전체 dist 폴더 | 300-400MB |

**압축 시:** 약 100-150MB (ZIP)

---

## 배포 방법

### 방법 1: 단일 EXE 파일

```
배포 대상: dist/StockMonitor.exe

장점:
- 단일 파일로 간단함

단점:
- 첫 실행 시 로딩 (1-2분)
- 임시 폴더에 파일 풀어짐
```

### 방법 2: dist 폴더 전체 (권장)

```
배포 대상: dist/ 폴더 전체

장점:
- 더 빠른 실행 (초기 로딩 없음)
- 안정적

단점:
- 폴더 크기가 큼 (300-400MB)
- ZIP으로 압축해서 배포 권장
```

### 방법 3: 설치 프로그램 (고급)

NSIS (Nullsoft Scriptable Install System)를 사용하여 Windows 설치 마법사 만들기

**nsis_installer.nsi 예제:**
```nsis
; 간단한 설치 프로그램 스크립트
; NSIS에서 컴파일

Name "Stock Monitor"
OutFile "StockMonitor-Setup.exe"

InstallDir "$PROGRAMFILES\StockMonitor"

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\*.*"
  CreateDirectory "$SMPROGRAMS\Stock Monitor"
  CreateShortCut "$SMPROGRAMS\Stock Monitor\Stock Monitor.lnk" "$INSTDIR\StockMonitor.exe"
  CreateShortCut "$DESKTOP\Stock Monitor.lnk" "$INSTDIR\StockMonitor.exe"
SectionEnd

Section "Uninstall"
  RMDir /r "$INSTDIR"
  RMDir /r "$SMPROGRAMS\Stock Monitor"
  Delete "$DESKTOP\Stock Monitor.lnk"
SectionEnd
```

---

## 📦 배포 패키지 준비

### ZIP 파일로 배포

```cmd
# dist 폴더를 ZIP으로 압축
# Windows 탐색기에서:
# 1. dist 폴더 우클릭
# 2. 보내기 → 압축된 폴더
# 3. StockMonitor.zip 생성

# 또는 PowerShell에서:
Compress-Archive -Path dist -DestinationPath StockMonitor.zip
```

### 배포 체크리스트

배포하기 전에 확인하세요:

- [ ] dist/StockMonitor.exe가 정상 작동하는가?
- [ ] .env 파일이 포함되어 있는가?
- [ ] 첫 실행 시 로딩 완료까지 기다렸는가?
- [ ] config/ 폴더가 포함되어 있는가?
- [ ] 설치 문서가 포함되어 있는가?

---

## 🎯 사용자를 위한 설치 가이드

EXE를 배포할 때 사용자에게 제공할 가이드:

### 설치 방법

**Option 1: 자동 설치**
```
1. StockMonitor.exe를 더블클릭
2. 자동으로 설치 및 실행됨
3. 브라우저에서 http://localhost:8501 접속
```

**Option 2: 수동 설치**
```
1. StockMonitor.zip 압축 해제
2. dist/StockMonitor.exe 실행
3. 브라우저에서 http://localhost:8501 접속
```

### 첫 실행 시 주의사항

```
⚠️ 첫 실행 시 1-2분 정도 로딩됩니다.
⚠️ "응답 없음" 표시가 나올 수 있지만 정상입니다.
⚠️ 인터넷 연결이 필요합니다.
```

### API 키 설정

```
1. 앱이 실행된 후 Settings 탭으로 이동
2. .env 파일을 텍스트 에디터로 열기:
   - StockMonitor.exe와 같은 폴더의 .env
3. SAMSUNG_API_KEY 등을 실제 값으로 변경
4. 앱 재시작
```

---

## 🔧 커스터마이징

### 아이콘 변경

```cmd
python create_icon.py
```

이후 EXE 빌드 시 custom 아이콘이 사용됩니다.

---

## 📊 빌드 설정 커스터마이징

**build_windows_exe.py의 설정:**

```python
pyinstaller_cmd = (
    "pyinstaller "
    "--name=StockMonitor "          # EXE 파일명 변경
    "--onefile "                    # 단일 파일로 생성
    "--windowed "                   # 콘솔창 없음
    "--icon=stock-monitor.ico "     # 아이콘 설정
    "--add-data=\"streamlit:streamlit\" "
    # ... 추가 설정
)
```

### 콘솔 창 표시

```python
# --windowed를 제거하면 콘솔 창이 표시됨
```

---

## ⚠️ 트러블슈팅

### EXE 빌드 실패

**오류:** "PyInstaller not found"

**해결:**
```cmd
pip install pyinstaller
```

---

### EXE 실행 오류: "ModuleNotFoundError"

**원인:** 의존성 누락

**해결:**
```cmd
# build_windows_exe.py의 hidden-import 확인
--hidden-import=streamlit
--hidden-import=pandas
```

---

### EXE 파일이 너무 크다

**해결:**
```cmd
# 불필요한 모듈 제외
pyinstaller ... --exclude-module=numpy_core
```

---

### 실행 시 "응답 없음" 메시지

**정상입니다.** 첫 실행 시는 1-2분 걸립니다.

---

## 📈 성능 비교

| 방식 | 설치 크기 | 첫 실행 | 실행 속도 | Python 필요 |
|------|---------|--------|---------|-----------|
| run.bat | 50MB | 빠름 | 빠름 | ✅ 필수 |
| EXE | 300MB | 느림 | 보통 | ❌ 불필요 |
| ZIP | 100MB | 빠름 | 빠름 | ✅ 필수 |

---

## 🔐 보안 고려사항

### API 키 보호

```
⚠️ .env 파일에 API 키가 있습니다.
⚠️ 공개 저장소에 업로드하지 마세요.
⚠️ 사용자에게 배포할 때 API 키를 제거하거나 교체하세요.
```

### 바이러스 경고

일부 백신 프로그램이 PyInstaller 생성 파일을 의심할 수 있습니다:

```
해결: PyInstaller 서명 또는 신뢰도 높은 배포 채널 사용
```

---

## 📝 배포 체크리스트

배포 전 확인사항:

- [ ] build.bat으로 EXE 빌드 완료
- [ ] dist/StockMonitor.exe 테스트 완료
- [ ] .env 파일 설정 확인
- [ ] 첫 실행 1-2분 로딩 확인
- [ ] API 키 설정 가능 확인
- [ ] 설치 가이드 준비
- [ ] ZIP 파일 생성
- [ ] 설치 문서 포함
- [ ] 라이센스 파일 포함
- [ ] README 파일 포함

---

## 🎓 다음 단계

### 추가 배포 옵션

1. **Microsoft Store 등록** (고급)
2. **Windows Installer (.MSI) 생성** (고급)
3. **코드 서명** (보안 강화)
4. **자동 업데이트** (사용자 편의)

---

## 📞 지원

문제가 발생하면:

1. **WINDOWS_GUIDE.md** 확인
2. **logs/app.log** 확인
3. **build.bat 재실행** 시도

---

## ✅ 요약

**Windows에서 실행:**

```
# 가장 간단한 방법:
double-click run.bat

# EXE 파일 만들기:
double-click build.bat
```

완료! 🎉
