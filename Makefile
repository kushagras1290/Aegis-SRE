.PHONY: bootstrap test verify verify-full demo infra-up infra-down migrate dev-api web security

bootstrap:
	python -m pip install -e '.[dev]'

test:
	python -m pytest

verify:
	python -m compileall -q apps packages tests scripts migrations
	python -m pytest --cov=packages --cov=apps/api --cov=apps/temporal_worker --cov-branch --cov-fail-under=80
	python scripts/static_verify.py
	python scripts/demo.py

security:
	python scripts/static_verify.py

demo:
	python scripts/demo.py

verify-full: verify
	docker compose config --quiet
	opa test infra/opa
	pnpm --dir apps/web install --frozen-lockfile
	pnpm --dir apps/web typecheck
	pnpm --dir apps/web build
	terraform -chdir=infra/terraform fmt -check
	terraform -chdir=infra/terraform init -backend=false
	terraform -chdir=infra/terraform validate
	alembic upgrade head

migrate:
	alembic upgrade head

dev-api:
	uvicorn apps.api.main:app --host 0.0.0.0 --port 8080 --reload

web:
	pnpm --dir apps/web dev

infra-up:
	docker compose up -d

infra-down:
	docker compose down -v
