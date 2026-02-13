# init venv from imports
.PHONY: venv
venv:
	test -f requirements.txt || (uvx pipreqs . --mode no-pin --encoding utf-8 --ignore .venv && mv requirements.txt requirements.in && uv pip compile requirements.in -o requirements.txt)
	uv venv .venv --python 3.11
	uv pip install -r requirements.txt
	@echo "activate venv with: \033[1;33msource .venv/bin/activate\033[0m"

# dump + compile dependencies
.PHONY: lock
lock:
	uv pip freeze > requirements.in
	uv pip compile requirements.in -o requirements.txt

# format, typecheck, test
.PHONY: precommit
precommit:
	uvx isort .
	uvx autoflake --remove-all-unused-imports --recursive --in-place .
	uvx black --line-length 5000 .
	uvx ruff check --fix .
	# uv run --with pytest pytest tests/ -v
