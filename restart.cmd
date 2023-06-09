py docker_refresher.py
kubectl delete --all=true
minikube delete --all=true
minikube start
cd manifests && kubectl apply -f .
minikube service --all
