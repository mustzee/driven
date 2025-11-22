# 🚀 배포 가이드

## 목차
1. [로컬 개발 환경](#로컬-개발-환경)
2. [Docker Compose 배포](#docker-compose-배포)
3. [Kubernetes (Minikube) 배포](#kubernetes-minikube-배포)
4. [프로덕션 배포](#프로덕션-배포)

---

## 로컬 개발 환경

### 백엔드 (Go)
```bash
# 의존성 설치
go mod tidy

# 서버 실행
make run-go
# 또는
go run cmd/server/main.go

# 테스트
make test-go
```

서버가 `http://localhost:8080`에서 실행됩니다.

### 프론트엔드 (React)
```bash
cd web

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

브라우저가 자동으로 `http://localhost:3000`을 엽니다.

### Python 분석 엔진
```bash
# 의존성 설치
pip install -r python/requirements.txt

# 예시 실행
make run-python
# 또는
python python/examples/lunch_decision.py
python python/examples/full_pipeline.py
```

---

## Docker Compose 배포

가장 빠르게 전체 스택을 실행하는 방법입니다.

### 1. Docker 이미지 빌드 및 실행
```bash
# 이미지 빌드 + 컨테이너 실행
make docker-up

# 또는 수동으로
docker-compose up -d --build
```

### 2. 서비스 접근
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8080
- **Health Check**: http://localhost:8080/health

### 3. 로그 확인
```bash
make docker-logs

# 또는
docker-compose logs -f
```

### 4. 중지
```bash
make docker-down

# 또는
docker-compose down
```

---

## Kubernetes (Minikube) 배포

로컬 Kubernetes 클러스터에 배포하여 프로덕션 환경을 시뮬레이션합니다.

### 전제 조건
- Docker 설치
- Minikube 설치
- kubectl 설치

```bash
# Minikube 설치 (Mac)
brew install minikube

# Minikube 설치 (Linux)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### 1. Minikube 시작
```bash
make minikube-start

# 또는
minikube start --driver=docker --cpus=2 --memory=4096
```

### 2. Docker 이미지 빌드 및 로드
```bash
# 이미지 빌드
make build-docker

# Minikube에 이미지 로드
make minikube-load-images
```

### 3. Kubernetes 리소스 배포
```bash
# 전체 배포 (이미지 로드 + 리소스 적용)
make k8s-deploy

# 또는 수동으로
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

### 4. 배포 상태 확인
```bash
# 모든 리소스 확인
make k8s-status

# 또는
kubectl get all -n cognitive-deck
```

예상 출력:
```
NAME                            READY   STATUS    RESTARTS   AGE
pod/backend-xxxxxxxxxx-xxxxx    1/1     Running   0          1m
pod/backend-xxxxxxxxxx-xxxxx    1/1     Running   0          1m
pod/frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          1m
pod/frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          1m

NAME               TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
service/backend    ClusterIP   10.96.xxx.xxx    <none>        8080/TCP       1m
service/frontend   NodePort    10.96.xxx.xxx    <none>        80:30080/TCP   1m

NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/backend    2/2     2            2           1m
deployment.apps/frontend   2/2     2            2           1m
```

### 5. 서비스 접근
```bash
# 프론트엔드 URL 확인
make minikube-url

# 또는
minikube service frontend -n cognitive-deck --url
```

브라우저에서 출력된 URL (예: `http://192.168.49.2:30080`)로 접속합니다.

### 6. 로그 확인
```bash
# 백엔드 로그
make k8s-logs-backend

# 프론트엔드 로그
make k8s-logs-frontend
```

### 7. 리소스 삭제
```bash
# Namespace 전체 삭제
make k8s-delete

# 또는
kubectl delete namespace cognitive-deck
```

### 8. Minikube 중지/삭제
```bash
# 중지
minikube stop

# 삭제
minikube delete
```

---

## 프로덕션 배포

### AWS EKS / GCP GKE / Azure AKS

#### 1. 컨테이너 레지스트리에 이미지 푸시
```bash
# Docker Hub 예시
docker tag cognitive-deck-backend:latest yourusername/cognitive-deck-backend:v1.0.0
docker tag cognitive-deck-frontend:latest yourusername/cognitive-deck-frontend:v1.0.0

docker push yourusername/cognitive-deck-backend:v1.0.0
docker push yourusername/cognitive-deck-frontend:v1.0.0
```

#### 2. Kubernetes 매니페스트 수정
`k8s/backend-deployment.yaml`과 `k8s/frontend-deployment.yaml`에서 이미지를 업데이트:

```yaml
spec:
  containers:
  - name: backend
    image: yourusername/cognitive-deck-backend:v1.0.0
    imagePullPolicy: Always  # IfNotPresent -> Always 변경
```

#### 3. 배포
```bash
kubectl apply -f k8s/
```

#### 4. Ingress 설정 (클라우드 로드 밸런서)
클라우드 제공자의 Ingress Controller 사용:
- AWS: ALB Ingress Controller
- GCP: GCE Ingress
- Azure: Application Gateway Ingress

---

## 트러블슈팅

### Minikube 이미지 로드 문제
```bash
# Minikube의 Docker 환경 사용
eval $(minikube docker-env)

# 이미지 다시 빌드
make build-docker

# 환경 초기화
eval $(minikube docker-env -u)
```

### Pod이 ImagePullBackOff 상태
```bash
# 이미지가 Minikube에 있는지 확인
minikube ssh
docker images | grep cognitive-deck
```

### 서비스 접근 안 됨
```bash
# NodePort 서비스 확인
kubectl get svc -n cognitive-deck

# Minikube IP 확인
minikube ip

# 직접 접속 시도
curl http://$(minikube ip):30080
```

---

## 모니터링

### Kubernetes Dashboard
```bash
minikube dashboard
```

### 리소스 사용량
```bash
kubectl top pods -n cognitive-deck
kubectl top nodes
```

---

## 확장

### 레플리카 수 조정
```bash
# 백엔드 3개로 확장
kubectl scale deployment backend -n cognitive-deck --replicas=3

# 프론트엔드 5개로 확장
kubectl scale deployment frontend -n cognitive-deck --replicas=5
```

### 오토스케일링 설정
```bash
# HPA (Horizontal Pod Autoscaler) 생성
kubectl autoscale deployment backend -n cognitive-deck \
  --cpu-percent=50 \
  --min=2 \
  --max=10
```

---

## 다음 단계

- [ ] CI/CD 파이프라인 구축 (GitHub Actions, GitLab CI)
- [ ] Helm Chart로 패키징
- [ ] Prometheus + Grafana 모니터링
- [ ] ELK Stack 로깅
- [ ] Service Mesh (Istio, Linkerd)
