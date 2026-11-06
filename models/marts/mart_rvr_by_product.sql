-- Une ligne par produit Dior : RVR = prix de revente médian / prix boutique x 100,
-- affiché seulement à partir de {{ var('min_listings') }} annonces rattachées.
with listings as (

    select
        retail_product_id,
        count(*)                              as listing_count,
        {{ median("resale_price_eur") }}            as median_resale_price_eur
    from {{ ref('stg_resale_listings') }}
    group by 1

),

joined as (

    select
        r.retail_product_id,
        r.product_name,
        r.category,
        r.retail_price_eur,
        coalesce(l.listing_count, 0)          as listing_count,
        l.median_resale_price_eur
    from {{ ref('stg_retail_products') }} r
    left join listings l using (retail_product_id)

)

select
    *,
    case
        when listing_count >= {{ var('min_listings') }}
        then round(median_resale_price_eur / retail_price_eur * 100, 1)
    end                                        as rvr_pct,
    {{ rvr_status(
        "round(median_resale_price_eur / retail_price_eur * 100, 1)",
        "listing_count"
    ) }}                                       as status
from joined
