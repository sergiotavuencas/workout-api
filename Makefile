run:
	@uvicorn workout_api.main:app --reload

compose:
	@docker-compose up -d

create-migrations:
	@alembic revision --autogenerate -m $(d)

run-migrations:
	@alembic upgrade head

update-requirements:
	@pip freeze > requirements.txt