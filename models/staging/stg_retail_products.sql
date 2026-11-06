select
    retail_product_id,
    product_name,
    lower(trim(category))               as category,
    cast(retail_price_eur as {{ dbt.type_numeric() }})    as retail_price_eur,
    cast(scrape_date as date)           as scrape_date
from {{ ref('raw_retail_products') }}
