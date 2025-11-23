#!/bin/bash

echo "🎴 Cognitive Deck - 시작 스크립트"
echo ""

# Go 서버 빌드
echo "📦 Go 서버 빌드 중..."
go build -o bin/server cmd/server/*.go
if [ $? -ne 0 ]; then
    echo "❌ Go 서버 빌드 실패"
    exit 1
fi
echo "✅ Go 서버 빌드 완료"

# Go 서버 시작
echo "🚀 Go API 서버 시작 중..."
./bin/server > /tmp/go-server.log 2>&1 &
GO_PID=$!
echo "✅ Go API 서버 시작됨 (PID: $GO_PID, 포트: 8080)"

# npm 의존성 확인
if [ ! -d "web/node_modules" ]; then
    echo "📦 npm 의존성 설치 중..."
    cd web && npm install && cd ..
    echo "✅ npm 의존성 설치 완료"
fi

# React 서버 시작
echo "🌐 React 개발 서버 시작 중..."
cd web && npm start > /tmp/react-dev.log 2>&1 &
REACT_PID=$!
echo "✅ React 개발 서버 시작됨 (PID: $REACT_PID, 포트: 3000)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ 서버 실행 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Go API 서버: http://localhost:8080"
echo "📍 React Web UI: http://localhost:3000"
echo ""
echo "🔍 로그 확인:"
echo "   Go API: tail -f /tmp/go-server.log"
echo "   React: tail -f /tmp/react-dev.log"
echo ""
echo "🛑 서버 종료:"
echo "   kill $GO_PID $REACT_PID"
echo ""
echo "💡 브라우저에서 http://localhost:3000 을 열어주세요!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
