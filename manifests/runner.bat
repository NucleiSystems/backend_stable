cd manifests
kubectl delete --all=true
minikube delete --all=true
minikube start

@echo off
echo Applying the manifest for the Postgres pod...
kubectl apply -f ipfs-deployment.yaml --skip-validation
kubectl apply -f PersistantVolume.yaml
kubectl apply -f PersistentVolumeClaim.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f redis-server-deployment.yaml


echo Checking if the Postgres pod is running...
:check_postgres
kubectl get pods | find "postgres"
if %errorlevel% == 0 (
  echo The Postgres pod is running
  echo Applying the manifest for the Nuclei backend...
  timeout /t 150

  kubectl apply -f nuclei_backend-deployment.yaml
) else (
  echo The Postgres pod is not running, trying again in 10 seconds...
  timeout /t 10
  goto check_postgres
)

minikube service --all
