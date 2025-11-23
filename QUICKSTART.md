# 🚀 빠른 시작 가이드

## 실행 방법 (3단계)

### 1️⃣ 의존성 설치 (최초 1회만)
```bash
cd web
npm install
cd ..
```

### 2️⃣ 서버 시작
```bash
# 자동 실행 스크립트
./start.sh

# 또는 수동으로:
# 터미널 1 - Go 서버
go build -o bin/server cmd/server/*.go
./bin/server

# 터미널 2 - React 서버
cd web
npm start
```

### 3️⃣ 브라우저 열기
```
http://localhost:3000
```

## ✅ 정상 작동 확인

서버가 시작되면:
- Go API: `http://localhost:8080`
- React UI: `http://localhost:3000`

테스트:
```bash
# API 테스트
curl http://localhost:8080/api/v1/frameworks

# 프록시 테스트
curl http://localhost:3000/api/v1/frameworks
```

## 🎯 사용법

1. **프레임워크 선택**: 7가지 중 상황에 맞는 것 선택
2. **정보 확인**: 장단점, 적합 상황 확인
3. **카드 작성**: 가이드에 따라 정보 입력
4. **분석 실행**: 자동 분석 시작
5. **결과 확인**: Gap 분석, 추천사항 확인

## ❌ 문제 해결

### 서버가 시작 안됨
```bash
# 포트가 사용 중이라면
lsof -ti:8080 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# 다시 시작
./start.sh
```

### npm 에러
```bash
cd web
rm -rf node_modules package-lock.json
npm install
```

### Go 빌드 에러
```bash
go mod tidy
go build -o bin/server cmd/server/*.go
```

## 📋 요구사항

- Go 1.16+
- Python 3.8+
- Node.js 14+
- npm 6+
