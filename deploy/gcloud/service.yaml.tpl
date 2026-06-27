# Cloud Run multi-container service spec — fully $0-cost architecture.
# Placeholders (${...}) are substituted by deploy.sh via envsubst before apply.
#
# Both Postgres and Redis run as sidecars (localhost only) instead of Cloud SQL /
# Memorystore — zero extra GCP service cost, but two real trade-offs accepted here:
#   1. maxScale is pinned to 1: with >1 instances each would get its own unshared
#      Postgres/Redis, breaking both data consistency and the cache/rate-limiter.
#   2. Postgres storage is NOT persistent: every cold start re-seeds from the
#      baked-in catalog dump (see deploy/gcloud/db/). Orders created against a
#      live instance are lost when that instance is recycled. Fine for a mock/demo
#      catalog server; revisit with Cloud SQL if real order data must survive.
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ${SERVICE_NAME}
  labels:
    cloud.googleapis.com/location: ${REGION}
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "1"
        run.googleapis.com/startup-cpu-boost: "true"
    spec:
      serviceAccountName: snoonu-mcp-runtime@${PROJECT_ID}.iam.gserviceaccount.com
      containerConcurrency: 40
      containers:
        - name: mcp-server
          image: ${IMAGE}
          ports:
            - containerPort: 8080
          env:
            - name: SNOONU_REDIS_URL
              value: redis://localhost:6379/0
            - name: SNOONU_DB_URL
              value: postgresql://snoonu:snoonu@localhost:5432/snoonu_mcp
            - name: SNOONU_MCP_WORKERS
              value: "2"
            - name: SNOONU_LOG_JSON
              value: "true"
            - name: SNOONU_LOG_LEVEL
              value: "INFO"
            # MCP's DNS-rebinding protection only trusts localhost by default;
            # the deployed Cloud Run hostname(s) must be allowlisted explicitly.
            # Cloud Run exposes the service under BOTH a project-number hostname
            # and a separate hash-based hostname (the one status.url reports) —
            # both must be listed, EXISTING_HOST is the latter, fetched pre-deploy.
            - name: SNOONU_ALLOWED_HOSTS
              value: "${SERVICE_NAME}-${PROJECT_NUMBER}.${REGION}.run.app,${EXISTING_HOST},127.0.0.1:*,localhost:*,[::1]:*"
          resources:
            limits:
              cpu: "1"
              memory: 512Mi
          startupProbe:
            httpGet:
              path: /health
              port: 8080
            periodSeconds: 5
            failureThreshold: 12
          livenessProbe:
            httpGet:
              path: /ready
              port: 8080
            periodSeconds: 30
            failureThreshold: 5
        - name: redis
          image: redis:7-alpine
          resources:
            limits:
              cpu: "0.5"
              memory: 128Mi
          startupProbe:
            tcpSocket:
              port: 6379
            periodSeconds: 2
            failureThreshold: 10
        - name: postgres
          image: ${PG_IMAGE}
          env:
            - name: POSTGRES_USER
              value: snoonu
            - name: POSTGRES_PASSWORD
              value: snoonu
            - name: POSTGRES_DB
              value: snoonu_mcp
          resources:
            limits:
              cpu: "1"
              memory: 512Mi
          startupProbe:
            tcpSocket:
              port: 5432
            periodSeconds: 2
            failureThreshold: 30
