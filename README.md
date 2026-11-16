# Scale-to-Zero Job Processing (Redis + KEDA + Kubernetes)

## How it works
Client -> API (FastAPI) -> Redis queue -> KEDA watches queue -> Kubernetes starts workers -> workers process jobs -> queue empty -> back to 0 workers

## Files
- app.py        API: POST /jobs adds a job, GET /jobs/{id} shows status/result
- worker.py     Takes jobs from the queue and processes them
- Dockerfile    One image used by both the API and the worker
- k8s/          Redis, API, worker and the KEDA scaler

## Requirements (Windows)
Docker Desktop, minikube, kubectl, helm

## Run it (PowerShell)
minikube start --driver=docker
minikube image build -t scale-app:1.0 .

helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda --namespace keda --create-namespace

kubectl apply -f k8s/

# Terminal 2: watch pods
kubectl get pods -w

# Terminal 3: open the API
kubectl port-forward svc/api 8000:8000

# Send jobs (use curl.exe in PowerShell)
curl.exe -X POST "http://localhost:8000/jobs?text=hello%20world"
curl.exe "http://localhost:8000/jobs/<job_id>"

## What you should see
1. Before any job: no worker pods.
2. After sending jobs: a worker pod appears.
3. Send 15+ jobs quickly: more worker pods appear (up to 5).
4. When the queue is empty: workers disappear after ~30s.

## Clean up
kubectl delete -f k8s/
minikube stop
