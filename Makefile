.PHONY: install run validate guard test samples package clean

install:
	python -m pip install -r requirements.txt

run:
	streamlit run streamlit_app.py

validate:
	python scripts/validate.py

guard:
	python scripts/repository_guard.py

test:
	python -m unittest discover -s tests -v

samples:
	python scripts/generate_samples.py

package:
	python scripts/build_release.py

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .nora_data dist
	rm -f validation_reports/*.md
