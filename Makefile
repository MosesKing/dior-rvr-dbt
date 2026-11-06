.PHONY: build docs charts clean

build:
	dbt build --profiles-dir .

docs:
	dbt docs generate --profiles-dir .
	dbt docs serve --profiles-dir .

charts: build
	python scripts/render_charts.py

clean:
	rm -rf target logs dior_rvr.duckdb
