{# Cross-warehouse median. DuckDB has an exact median() aggregate; BigQuery does not,
   so it uses APPROX_QUANTILES (approximate, fine at listing volumes). #}
{% macro median(column) %}
    {{ return(adapter.dispatch('median')(column)) }}
{% endmacro %}

{% macro default__median(column) %}
    percentile_cont(0.5) within group (order by {{ column }})
{% endmacro %}

{% macro duckdb__median(column) %}
    median({{ column }})
{% endmacro %}

{% macro bigquery__median(column) %}
    approx_quantiles({{ column }}, 2)[offset(1)]
{% endmacro %}
