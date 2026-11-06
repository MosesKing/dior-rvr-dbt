-- Couverture du matching par catégorie : le vrai goulot du projet, suivi comme un KPI.
select
    p.category,
    count(*)                                          as products,
    sum(case when p.listing_count > 0 then 1 else 0 end) as products_with_listings,
    sum(p.listing_count)                              as matched_listings
from {{ ref('mart_rvr_by_product') }} p
group by 1
