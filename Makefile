.PHONY: run tests stop

run: 
	@echo 'Starting containers...'
	@docker-compose up -d --build

tests: 
	@echo 'Running tests...'
	@docker-compose run \
	  --rm \
	  --no-deps \
	  --entrypoint='' \
	  app-jobrunner \
	  bash -c "python -m unittest discover btc_guru/tests/ -v \
	  && python -m mypy --config-file btc_guru/tests/mypy.ini btc_guru/**/*.py"

stop:
	@docker-compose down
