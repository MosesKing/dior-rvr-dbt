{# Statut lisible par un non-technicien, à partir du RVR (en %) et du volume d'annonces #}
{% macro rvr_status(rvr_pct, listing_count) %}
    case
        when {{ listing_count }} = 0 then 'non rattaché'
        when {{ listing_count }} < {{ var('min_listings') }} then 'volume insuffisant'
        when {{ rvr_pct }} >= 100 then 'se revend plus cher'
        when {{ rvr_pct }} >= 90 then 'garde sa valeur'
        else 'se déprécie'
    end
{% endmacro %}
