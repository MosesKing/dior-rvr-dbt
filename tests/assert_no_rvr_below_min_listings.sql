-- Échoue si un RVR est affiché alors que le volume d'annonces est sous le minimum.
select *
from {{ ref('mart_rvr_by_product') }}
where rvr_pct is not null
  and listing_count < {{ var('min_listings') }}
