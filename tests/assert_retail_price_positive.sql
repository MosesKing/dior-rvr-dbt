-- Fails if a retail price is zero or negative (the RVR divides by it).
select *
from {{ ref('stg_retail_products') }}
where retail_price_eur <= 0
