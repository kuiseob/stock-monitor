# Windows 설치 및 실행 가이드

Windows 환경에서 Stock Monitor를 설치하고 실행하는 방법입니다.

## 🚀 빠른 시작 (권장)

### 방법 1: run.bat 파일 사용 (가장 간단)

**필수 요구사항:**
- Windows 7 이상
- Python 3.9 이상 설치됨

**실행 방법:**

1. **프로젝트 폴더에서 `run.bat` 더블클릭**
   - 또는 명령 프롬프트에서: `run.bat`

2. **자동으로 다음이 실행됩니다:**
   - 가상환경 생성
   - 필요한 패키지 설치
   - Streamlit 앱 시작

3. **브라우저에서 접속:**
   - http://localhost:8501

**장점:**
- ✅ 가장 간단함
- ✅ Python만 필요
- ✅ 모든 Windows 버전 지원

---

## 🔧 상세 설치 가이드

### Step 1: Python 설치

1. **Python 다운로드**
   - https://www.python.org/downloads/ 방문
   - Windows 64-bit 다운로드 (Python 3.12 권장)

2. **설치**
   - 인스톨러 실행
   - **중요:** "Add Python to PATH" 체크
   - "Install Now" 클릭
   - 설치 완료

3. **Python 설치 확인**
   ```cmd
   python --version
   ```
   - 버전이 표시되면 정상

---

### Step 2: 프로젝트 다운로드

1. **GitHub에서 다운로드**
   ```
   git clone <repository-url>
   cd stock-monitor
   ```
   
   또는 ZIP 파일로 다운로드:
   - 프로젝트 폴더를 압축 해제

---

### Step 3: 가상환경 설정

명령 프롬프트 또는 PowerShell에서:

```cmd
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
venv\Scripts\activate.bat

# 또는 PowerShell 사용 시:
venv\Scripts\Activate.ps1
```

---

### Step 4: 의존성 설치

```cmd
pip install -r requirements.txt
```

---

### Step 5: 환경변수 설정

```cmd
# .env 파일 생성
copy .env.example .env

# 텍스트 에디터로 편집 (메모장, VS Code 등)
notepad .env
```

**.env 파일 내용:**
```bash
SAMSUNG_API_KEY=your_api_key_here
SAMSUNG_ACCOUNT_ID=your_account_id_here
SAMSUNG_API_SECRET=your_secret_key_here
ATOSPLUS_WS_URL=wss://api.atosplus.samsung.co.kr/websocket
DEFAULT_STOCKS=005930,000660,006400,051910,005380
DATABASE_PATH=./data/stock_data.db
RETENTION_DAYS=30
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

---

### Step 6: 앱 실행

```cmd
# 방법 1: run.bat 사용 (권장)
run.bat

# 방법 2: 직접 실행
streamlit run streamlit/app.py

# 방법 3: Makefile 사용 (만약 Make 설치되어 있으면)
make run
```

---

## 📦 Windows EXE 빌더

Python이 설치되지 않은 다른 PC에서 실행할 수 있는 독립 실행 파일을 만들 수 있습니다.

### EXE 빌드 방법

#### 방법 1: Python 스크립트로 빌드

```cmd
# 가상환경 활성화
venv\Scripts\activate.bat

# 빌드 스크립트 실행
python build_windows_exe.py
```

**결과:**
- `dist/StockMonitor.exe` 생성
- 약 300-400MB (Streamlit 포함)

#### 방법 2: PyInstaller 직접 사용

```cmd
pip install pyinstaller

pyinstaller ^
  --name=StockMonitor ^
  --onefile ^
  --windowed ^
  streamlit/app.py
```

---

## 🎯 실행 방법

### 방법 1: run.bat (권장)
```
double-click run.bat
```

### 방법 2: 명령 프롬프트
```cmd
cd C:\path\to\stock-monitor
venv\Scripts\activate.bat
streamlit run streamlit/app.py
```

### 방법 3: PowerShell
```powershell
cd C:\path\to\stock-monitor
venv\Scripts\Activate.ps1
streamlit run streamlit/app.py
```

### 방법 4: Windows EXE
```
double-click dist/StockMonitor.exe
```

---

## 🌐 브라우저 접속

앱이 시작되면 다음 주소를 브라우저에 입력:
```
http://localhost:8501
```

또는 자동으로 열릴 것입니다.

---

## 🐛 문제 해결

### 1. Python을 찾을 수 없다는 오류

**해결책:**
1. Python이 설치되었는지 확인
2. Python을 재설치할 때 "Add Python to PATH" 체크
3. 컴퓨터 재부팅

**확인:**
```cmd
python --version
```

---

### 2. "pip" 명령을 찾을 수 없다

**해결책:**
```cmd
python -m pip install -r requirements.txt
```

---

### 3. 포트 8501이 이미 사용 중

**해결책:**
```cmd
# 다른 포트 사용
streamlit run streamlit/app.py --server.port 8502
```

---

### 4. API 연결 실패

**확인 사항:**
1. `.env` 파일에서 API 키가 올바른지 확인
2. 인터넷 연결 확인
3. 방화벽 설정 확인

---

### 5. "ModuleNotFoundError" 오류

**해결책:**
```cmd
# 가상환경이 활성화되어 있는지 확인
venv\Scripts\activate.bat

# 의존성 재설치
pip install -r requirements.txt
```

---

## 📊 시스템 요구사항

| 항목 | 사양 |
|------|------|
| **OS** | Windows 7 이상 |
| **Python** | 3.9 이상 |
| **RAM** | 2GB 이상 (권장: 4GB+) |
| **디스크** | 500MB 이상 (EXE: 300-400MB) |
| **네트워크** | 인터넷 연결 필수 |

---

## 💾 데이터 저장소

데이터는 다음 위치에 저장됩니다:

```
stock-monitor/
├── data/
│   └── stock_data.db      (SQLite 데이터베이스)
├── logs/
│   └── app.log            (로그 파일)
└── .env                   (설정 파일)
```

---

## 🔐 보안 주의사항

1. **API 키 보호**
   - `.env` 파일은 절대 공유하지 마세요
   - `.gitignore`에 포함되어 버전 관리되지 않음

2. **주기적인 백업**
   ```cmd
   copy data\stock_data.db data\stock_data_backup.db
   ```

---

## ⌨️ 유용한 Windows 명령어

```cmd
# 현재 디렉토리 출력
cd

# 디렉토리 변경
cd C:\Users\YourName\stock-monitor

# 파일 목록 보기
dir

# 텍스트 파일 편집
notepad .env

# 프로세스 종료
taskkill /F /IM python.exe

# 포트 사용 확인
netstat -ano | findstr :8501

# 포트 사용 프로세스 종료
taskkill /F /PID <PID>
```

---

## 📚 추가 참고

- **README.md** - 프로젝트 개요
- **SETUP.md** - 상세 설정 가이드
- **DEPLOYMENT.md** - 배포 옵션

---

## 🎓 Python 기초 팁

### Windows에서 Python 경로 확인

```cmd
where python
where pip
```

### 여러 Python 버전이 설치된 경우

```cmd
# 특정 Python 버전 사용
C:\Python312\python.exe -m venv venv
```

---

## 🔄 일반적인 작업 흐름

```cmd
# 1. 프로젝트 폴더로 이동
cd C:\Users\YourName\stock-monitor

# 2. 가상환경 활성화
venv\Scripts\activate.bat

# 3. 앱 실행
streamlit run streamlit/app.py

# 4. 브라우저에서 http://localhost:8501 접속

# 5. Ctrl+C로 앱 종료

# 6. 가상환경 비활성화 (선택사항)
deactivate
```

---

## 💡 팁

1. **단축키 만들기**
   - `run.bat`을 데스크톱에 바로가기 생성
   - 클릭만으로 앱 실행 가능

2. **작업 스케줄러에 등록**
   - Windows 작업 스케줄러에서 매일 앱 자동 실행

3. **서비스로 실행**
   - NSSM(Non-Sucking Service Manager) 사용

---

## 📞 문제 발생 시

1. **logs/app.log 확인**
   - 오류 메시지 확인

2. **명령 프롬프트에서 직접 실행**
   - 오류 메시지 확인

3. **GitHub Issues에 보고**
   - 오류 메시지와 함께 보고

---

## ✅ 체크리스트

- [ ] Python 3.9+ 설치
- [ ] 프로젝트 다운로드
- [ ] 가상환경 생성
- [ ] 의존성 설치
- [ ] .env 파일 설정
- [ ] run.bat 또는 streamlit 명령어로 앱 실행
- [ ] http://localhost:8501 접속 확인

모두 완료하셨으면 앱이 정상 작동합니다! 🎉
