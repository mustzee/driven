.PHONY: help build-go build-docker deploy-k8s clean

help: ## 도움말 표시
	@echo "🎴 Cognitive Deck - Make 명령어"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ==================== 로컬 개발 ====================

run-go: ## Go API 서버 실행
	go run cmd/server/main.go

run-python: ## Python 예시 실행
	python python/examples/lunch_decision.py

test-go: ## Go 테스트 실행
	go test ./...

# ==================== Docker ====================

build-backend: ## 백엔드 Docker 이미지 빌드
	docker build -f Dockerfile.backend -t cognitive-deck-backend:latest .

build-frontend: ## 프론트엔드 Docker 이미지 빌드
	docker build -f Dockerfile.frontend -t cognitive-deck-frontend:latest .

build-docker: build-backend build-frontend ## 모든 Docker 이미지 빌드

docker-up: build-docker ## Docker Compose로 전체 스택 실행
	docker-compose up -d

docker-down: ## Docker Compose 중지
	docker-compose down

docker-logs: ## Docker 로그 확인
	docker-compose logs -f

# ==================== Kubernetes (Minikube) ====================

minikube-start: ## Minikube 시작
	minikube start --driver=docker --cpus=2 --memory=4096

minikube-load-images: build-docker ## Minikube에 이미지 로드
	minikube image load cognitive-deck-backend:latest
	minikube image load cognitive-deck-frontend:latest

k8s-apply: ## Kubernetes 리소스 적용
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/backend-deployment.yaml
	kubectl apply -f k8s/frontend-deployment.yaml
	kubectl apply -f k8s/ingress.yaml

k8s-deploy: minikube-load-images k8s-apply ## Minikube에 전체 배포

k8s-status: ## Kubernetes 상태 확인
	kubectl get all -n cognitive-deck

k8s-logs-backend: ## 백엔드 로그 확인
	kubectl logs -n cognitive-deck -l app=backend -f

k8s-logs-frontend: ## 프론트엔드 로그 확인
	kubectl logs -n cognitive-deck -l app=frontend -f

k8s-delete: ## Kubernetes 리소스 삭제
	kubectl delete namespace cognitive-deck

minikube-url: ## Minikube 서비스 URL 확인
	@echo "Frontend: http://$$(minikube ip):30080"
	minikube service frontend -n cognitive-deck --url

# ==================== 정리 ====================

clean: ## 빌드 파일 정리
	rm -rf web/build
	rm -rf web/node_modules
	go clean

clean-all: docker-down k8s-delete clean ## 모든 리소스 정리
