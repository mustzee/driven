# 🎴 Cognitive Deck - 데이터 기반 의사결정 시스템

## 컨셉
인간의 제한된 인지 능력을 **카드 덱**으로 모델링하여, 데이터 기반 의사결정을 시각화하고 최적화하는 시스템.

### 핵심 원리
1. **제한된 덱**: 인간은 동시에 7±2개의 정보만 처리 가능 (Miller's Law)
2. **트레이드오프 게이지**: 각 카드는 성향을 가지며, 덱 구성이 전체 의사결정 경향성 결정
3. **수학적 상충 관계**: 같은 카테고리 내 옵션들의 상충도를 정량화하여 연결
4. **목표 기반 배치**: 특정 목표 달성을 위한 최적 카드 조합 추천

## 기술 스택
- **백엔드**: Go 1.21 + Gin (REST API)
- **프론트엔드**: React 18 + Recharts (시각화)
- **분석 엔진**: Python 3.x (상충도 계산, AI 카드 생성)
- **배포**: Docker + Kubernetes (Minikube 지원)
- **인프라**: Nginx, Docker Compose

## 예시: 점심식사 의사결정

```
목표: 만족스러운 점심 선택
덱 슬롯: 7개

활성 카드:
[배고픔:80%] [예산:$$$] [시간:30분]
[동행자:3명] [모험성향] [날씨:비] [거리:중요]

게이지:
정적 ████░░░░░░ 동적
이성 ░░░░░███░░ 감성

결과: B양식 추천 (빠름+맛+거리 가까움)
```

## 프로젝트 구조
```
├── cmd/
│   ├── server/             # Go API 서버
│   └── example/            # Go 예시
├── internal/
│   └── card/               # 카드 & 덱 모델
├── web/                    # React 프론트엔드
│   ├── src/
│   │   ├── components/     # 카드, 게이지 컴포넌트
│   │   └── App.js          # 메인 앱
│   └── public/
├── python/
│   ├── conflict_engine.py  # 상충도 계산
│   ├── ai_card_generator.py # AI 카드 자동 생성
│   └── examples/           # 예시 시나리오
├── k8s/                    # Kubernetes 매니페스트
├── Dockerfile.backend      # 백엔드 컨테이너
├── Dockerfile.frontend     # 프론트엔드 컨테이너
├── docker-compose.yml      # Docker Compose 설정
└── Makefile                # 빌드/배포 명령
```

## 시작하기

### 🚀 Quick Start (Docker Compose)

가장 빠른 방법:
```bash
# 전체 스택 실행 (백엔드 + 프론트엔드)
make docker-up

# 또는
docker-compose up -d --build
```

접속:
- **웹 UI**: http://localhost:3000
- **API**: http://localhost:8080

### 💻 로컬 개발

**백엔드 (Go)**
```bash
make run-go
# 또는
go run cmd/server/main.go
```

**프론트엔드 (React)**
```bash
cd web
npm install
npm start
```

**Python 예시**
```bash
# 의존성 설치
pip install -r python/requirements.txt

# 점심 의사결정 시뮬레이션
python python/examples/lunch_decision.py

# AI 카드 자동 생성
python python/ai_card_generator.py

# 전체 파이프라인
python python/examples/full_pipeline.py
```

### ☸️ Kubernetes (Minikube)

```bash
# 1. Minikube 시작
make minikube-start

# 2. 전체 배포
make k8s-deploy

# 3. URL 확인
make minikube-url
```

자세한 내용은 [DEPLOYMENT.md](DEPLOYMENT.md) 참고

## 뇌과학 & 넛지 기반 설계

### 인지 부하 이론
- 작업 기억 용량: 7±2 청크
- 카드 슬롯 제한으로 강제 우선순위 설정

### 넛지 전략
1. **기본값**: 상황별 프리셋 덱 제공
2. **앵커링**: 첫 카드가 전체 성향 주도
3. **프레이밍**: 시각적 배치로 선택 유도

## 주요 기능

### ✅ 구현 완료
- [x] **카드 시스템** (Go): Miller's Law 기반 7±2 제한 덱
- [x] **트레이드오프 게이지**: 의사결정 성향 실시간 시각화
- [x] **상충도 분석 엔진** (Python): 옵션 간 수학적 상충 관계 계산
- [x] **AI 카드 자동 생성**: 회의록/텍스트에서 카드 추출
- [x] **웹 UI** (React): 인터랙티브 카드 보드
- [x] **RESTful API**: Go Gin 기반 API 서버
- [x] **Docker 컨테이너화**: 백엔드 + 프론트엔드
- [x] **Kubernetes 지원**: Minikube 로컬 배포

### 📊 데모 시나리오
- ✅ 점심식사 의사결정 (뇌과학 기반)
- ✅ 제품 로드맵 전략 수립
- ✅ 현지화 전략 분석

### 🔮 로드맵
- [ ] WebSocket 실시간 업데이트
- [ ] 드래그 앤 드롭 카드 재배치
- [ ] D3.js 고급 시각화
- [ ] 카드 간 연결고리 그래프
- [ ] 다중 덱 비교 기능
- [ ] AI 추천 엔진 고도화
- [ ] 협업 모드 (멀티 유저)
- [ ] 프로덕션 클러스터 배포 (AWS EKS, GKE)
