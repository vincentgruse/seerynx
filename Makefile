.PHONY: help format secrets mqtt-passwd login build-backend deploy-backend build-frontend deploy-frontend push-backend push-frontend deploy restart-backend restart-frontend prune all

IMAGE_TAG ?= latest
NAMESPACE = seerynx

ifneq ($(wildcard .env),)
    include .env
    export $(shell sed 's/=.*//' .env)
endif

login:
	@podman login $(REGISTRY) --tls-verify=false -u $(REGISTRY_USER) -p $(REGISTRY_PASSWORD)

help:
	@echo "Seerynx — available commands:"
	@echo "  make secrets          Apply K8s secrets from environment"
	@echo "  make build-backend    Build API and Inference images"
	@echo "  make build-frontend   Build the secured Frontend image"
	@echo "  make push-backend     Push backend images to local registry"
	@echo "  make push-frontend    Push frontend image to local registry"
	@echo "  make deploy           Apply all K8s manifests via Kustomize"
	@echo "  make prune            Remove unused podman images to reclaim disk space"
	@echo "  make all              Full build, push, and deploy pipeline"
	@echo "  make format           Format all Python (black) and frontend (prettier) code"

secrets: mqtt-passwd
	@echo "Applying secrets..."
	@kubectl create secret generic postgres-credentials \
		--namespace $(NAMESPACE) \
		--from-literal=username=seerynx \
		--from-literal=password=$(POSTGRES_PASSWORD) \
		--from-literal=database-url=postgresql+asyncpg://seerynx:$(POSTGRES_PASSWORD)@postgres-rw.seerynx.svc.cluster.local/seerynx \
		--dry-run=client -o yaml | kubectl apply -f -
	@kubectl create secret generic seerynx-secrets \
		--namespace $(NAMESPACE) \
		--from-literal=mqtt-password=$(MQTT_PASSWORD) \
		--from-literal=api-key=$(SEERYNX_API_KEY) \
		--dry-run=client -o yaml | kubectl apply -f -
	@kubectl create secret docker-registry local-registry-secret \
		--namespace $(NAMESPACE) \
		--docker-server=$(REGISTRY) \
		--docker-username=$(REGISTRY_USER) \
		--docker-password=$(REGISTRY_PASSWORD) \
		--dry-run=client -o yaml | kubectl apply -f -

mqtt-passwd:
	@echo "Generating Mosquitto password file..."
	@mkdir -p _out
	@podman run --rm docker.io/eclipse-mosquitto:2.0 \
		sh -c "mosquitto_passwd -b -c /tmp/passwd seerynx $(MQTT_PASSWORD) && cat /tmp/passwd" \
		> _out/mosquitto-passwd.tmp
	@kubectl create secret generic mosquitto-passwd \
		--namespace $(NAMESPACE) \
		--from-file=passwd=_out/mosquitto-passwd.tmp \
		--dry-run=client -o yaml | kubectl apply -f -
	@rm -f _out/mosquitto-passwd.tmp

build-backend:
	@echo "Building backend images..."
	podman build -f docker/Dockerfile.api -t $(REGISTRY)/seerynx-api:$(IMAGE_TAG) .
	podman build -f docker/Dockerfile.inference -t $(REGISTRY)/seerynx-inference:$(IMAGE_TAG) .

push-backend: login
	@echo "Pushing backend images..."
	podman push --tls-verify=false $(REGISTRY)/seerynx-api:$(IMAGE_TAG)
	podman push --tls-verify=false $(REGISTRY)/seerynx-inference:$(IMAGE_TAG)

build-frontend:
	podman build -f docker/Dockerfile.frontend \
		--add-host=seerynx.local:$(CLUSTER_IP) \
		--build-arg VITE_API_URL=$(VITE_API_URL) \
		--build-arg API_INTERNAL_URL=$(API_INTERNAL_URL) \
		--build-arg VITE_DISPLAY_TIMEZONE=$(VITE_DISPLAY_TIMEZONE) \
		--secret id=openapi_api_key,env=OPENAPI_API_KEY \
		-t $(REGISTRY)/seerynx-frontend:$(IMAGE_TAG) ./frontend

push-frontend: login
	@echo "Pushing frontend image..."
	podman push --tls-verify=false $(REGISTRY)/seerynx-frontend:$(IMAGE_TAG)

deploy:
	@echo "Deploying all manifests..."
	@rm -rf k8s/.rendered
	@mkdir -p k8s/.rendered
	@for f in k8s/*.yaml; do \
		sed -e "s#__CLUSTER_IP__#$(CLUSTER_IP)#g" -e "s#__FEEDER_IP__#$(FEEDER_IP)#g" -e "s#__REGISTRY__#$(REGISTRY)#g" $$f > k8s/.rendered/$$(basename $$f); \
	done
	kubectl apply -k k8s/.rendered/
	@rm -rf k8s/.rendered

restart-backend:
	@echo "Restarting backend deployments to pick up new images..."
	kubectl rollout restart deployment/seerynx-api deployment/seerynx-inference -n $(NAMESPACE)

restart-frontend:
	@echo "Restarting frontend deployment to pick up new image..."
	kubectl rollout restart deployment/seerynx-frontend -n $(NAMESPACE)

format:
	@echo "Formatting api..."
	cd api && uv run black .
	@echo "Formatting inference..."
	cd inference && uv run black .
	@echo "Formatting feeder..."
	cd feeder && uv run black .
	@echo "Formatting frontend..."
	cd frontend && npm run format

prune:
	@echo "Pruning unused podman images..."
	podman image prune -a -f

all:
	$(MAKE) build-backend
	$(MAKE) push-backend
	$(MAKE) deploy
	$(MAKE) restart-backend
	@echo "Waiting for API to be healthy..."
	kubectl rollout status deployment/seerynx-api -n seerynx --timeout=120s
	$(MAKE) build-frontend
	$(MAKE) push-frontend
	$(MAKE) deploy
	$(MAKE) restart-frontend
	@echo "Waiting for frontend to be healthy..."
	kubectl rollout status deployment/seerynx-frontend -n seerynx --timeout=120s
	@echo "Done."