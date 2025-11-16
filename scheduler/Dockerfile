# Provided at repo root as Dockerfile.scheduler, but we include a minimal one here for local
FROM python:3.11-slim
WORKDIR /app
COPY backend/app /app/app
COPY scheduler/run_monthly_pipeline.sh /run_monthly_pipeline.sh
COPY demo /app/demo
RUN chmod +x /run_monthly_pipeline.sh
CMD ["/run_monthly_pipeline.sh"]

