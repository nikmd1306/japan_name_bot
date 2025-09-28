PY=uv run

.PHONY: dev migrate upgrade downgrade aerich-init lint

dev:
	$(PY) japan-name-bot

aerich-init:
	$(PY) aerich init -t japan_name_bot.db.TORTOISE_ORM

migrate:
	$(PY) aerich migrate

upgrade:
	$(PY) aerich upgrade

downgrade:
	$(PY) aerich downgrade
