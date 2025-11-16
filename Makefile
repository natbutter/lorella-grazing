.PHONY: build demo-data train-demo run test

build:
	docker-compose build

demo-data:
	python demo/generate_sample_data.py

train-demo:
	python backend/app/ml/train_demo.py

run:
	docker-compose up --build

test:
	pytest -q

