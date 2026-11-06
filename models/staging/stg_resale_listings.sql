select
    listing_id,
    retail_product_id,
    source,
    cast(resale_price_eur as {{ dbt.type_numeric() }})    as resale_price_eur,
    currency,
    cast(listing_date as date)          as listing_date
from {{ ref('raw_resale_listings') }}
