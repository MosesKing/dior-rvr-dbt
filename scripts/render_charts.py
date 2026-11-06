"""Render the README charts from the dbt output.

Run after `dbt build --profiles-dir .`:
    python scripts/render_charts.py

Reads dior_rvr.duckdb, writes SVGs to assets/. SVGs adapt to light and dark mode.
"""

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

STYLE = """
<style>
  .bg { fill: #FBF8F3; }
  .ink { fill: #1A1A1A; }
  .muted { fill: #6B6460; }
  .rule { stroke: #D9D2C7; }
  .zone-dep { fill: #EFE7DC; }
  .zone-keep { fill: #E6DCC8; }
  .zone-up { fill: #D9C9A3; }
  .dot { fill: #1A1A1A; fill-opacity: 0.55; }
  .median { fill: #A8842C; stroke: #1A1A1A; stroke-width: 1.5; }
  .flag { fill: #B3261E; }
  .gold { fill: #A8842C; }
  text { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }
  @media (prefers-color-scheme: dark) {
    .bg { fill: #161514; }
    .ink { fill: #F2EEE8; }
    .muted { fill: #A39C94; }
    .rule { stroke: #3A3632; }
    .zone-dep { fill: #22201D; }
    .zone-keep { fill: #2E2A24; }
    .zone-up { fill: #3D3528; }
    .dot { fill: #F2EEE8; fill-opacity: 0.6; }
    .median { fill: #D4AF5A; stroke: #F2EEE8; }
    .flag { fill: #F2726A; }
    .gold { fill: #D4AF5A; }
  }
</style>
"""


def fr(v: float) -> str:
    """French decimal format: 24.9 -> 24,9"""
    return f"{v:.1f}".replace(".", ",")


def banner() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="240" viewBox="0 0 960 240" role="img" aria-label="RVR : Resale Value Retention, projet dbt EDHEC">
{STYLE}
<rect class="bg" width="960" height="240" rx="12"/>
<text x="56" y="62" class="muted" font-size="14" letter-spacing="4">EDHEC BUSINESS DATA MANAGEMENT · 2026</text>
<text x="56" y="124" class="ink" font-size="52" font-weight="300" letter-spacing="2">Resale Value Retention</text>
<rect x="56" y="146" width="64" height="3" class="gold"/>
<text x="56" y="190" class="ink" font-size="22" font-weight="300">RVR = prix de revente médian / prix boutique × 100</text>
<text x="904" y="214" class="muted" font-size="13" text-anchor="end">dbt · DuckDB · BigQuery</text>
</svg>
"""


def listings_chart(con) -> str:
    rows = con.sql(
        """
        select p.retail_product_id, p.product_name, p.retail_price_eur,
               l.resale_price_eur, m.rvr_pct, m.status, m.listing_count
        from stg_retail_products p
        join stg_resale_listings l using (retail_product_id)
        join mart_rvr_by_product m using (retail_product_id)
        order by p.retail_product_id, l.resale_price_eur
        """
    ).fetchall()

    products = {}
    for pid, name, retail, resale, rvr, status, n in rows:
        p = products.setdefault(
            pid, {"name": name, "retail": float(retail), "rvr": rvr, "status": status, "n": n, "pts": []}
        )
        p["pts"].append(float(resale) / float(retail) * 100)

    W, H = 960, 440
    x0, x1 = 250, 910
    xmax = 120.0

    def X(v: float) -> float:
        return x0 + (x1 - x0) * min(v, xmax) / xmax

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        'role="img" aria-label="RVR de chaque annonce de revente, par produit">',
        STYLE,
        f'<rect class="bg" width="{W}" height="{H}" rx="12"/>',
        '<text x="40" y="48" class="ink" font-size="20" font-weight="600">Une annonce ne suffit pas</text>',
        '<text x="40" y="74" class="muted" font-size="14">RVR de chaque annonce Vestiaire Collective, par produit. '
        "Chaque point est une annonce.</text>",
    ]

    top, bottom = 110, 360
    out += [
        f'<rect class="zone-dep" x="{X(0)}" y="{top}" width="{X(90) - X(0)}" height="{bottom - top}"/>',
        f'<rect class="zone-keep" x="{X(90)}" y="{top}" width="{X(100) - X(90)}" height="{bottom - top}"/>',
        f'<rect class="zone-up" x="{X(100)}" y="{top}" width="{X(xmax) - X(100)}" height="{bottom - top}"/>',
        f'<text x="{(X(0) + X(90)) / 2}" y="{top + 20}" class="muted" font-size="12" text-anchor="middle">se déprécie</text>',
        f'<text x="{(X(90) + X(100)) / 2}" y="{top + 20}" class="muted" font-size="11" text-anchor="middle">garde</text>',
        f'<text x="{(X(100) + X(xmax)) / 2}" y="{top + 20}" class="muted" font-size="12" text-anchor="middle">se revend plus cher</text>',
    ]
    for t in range(0, 121, 20):
        out.append(f'<line class="rule" x1="{X(t)}" x2="{X(t)}" y1="{bottom}" y2="{bottom + 6}" stroke-width="1"/>')
        out.append(f'<text x="{X(t)}" y="{bottom + 24}" class="muted" font-size="12" text-anchor="middle">{t} %</text>')

    row_y = [180, 280]
    for (pid, p), y in zip(products.items(), row_y):
        out.append(f'<text x="40" y="{y - 6}" class="ink" font-size="15" font-weight="600">{p["name"]}</text>')
        out.append(
            f'<text x="40" y="{y + 14}" class="muted" font-size="12">{p["n"]} annonces · boutique '
            f'{p["retail"]:,.0f} €</text>'.replace(",", "\u202f")
        )
        out.append(f'<line class="rule" x1="{x0}" x2="{x1}" y1="{y}" y2="{y}" stroke-width="1"/>')
        seen: dict[int, int] = {}
        for v in p["pts"]:
            k = round(X(v) / 10)
            dy = [0, 10, -10, 20, -20][seen.get(k, 0) % 5]
            seen[k] = seen.get(k, 0) + 1
            out.append(f'<circle class="dot" cx="{X(v):.1f}" cy="{y + dy}" r="6"/>')
        if p["rvr"] is not None:
            mx = X(float(p["rvr"]))
            out.append(
                f'<path class="median" d="M{mx:.1f},{y - 12} L{mx + 12:.1f},{y} L{mx:.1f},{y + 12} L{mx - 12:.1f},{y} Z"/>'
            )
            out.append(
                f'<text x="{mx:.1f}" y="{y - 28}" class="ink" font-size="13" font-weight="600" text-anchor="middle">'
                f'médiane {fr(float(p["rvr"]))} %</text>'
            )
        else:
            lo, hi = min(p["pts"]), max(p["pts"])
            out.append(
                f'<text x="{X(lo):.1f}" y="{y - 16}" class="muted" font-size="12" text-anchor="middle">{fr(lo)} %</text>'
            )
            out.append(
                f'<text x="{X(hi):.1f}" y="{y - 16}" class="flag" font-size="12" font-weight="600" text-anchor="middle">{fr(hi)} %</text>'
            )
            out.append(
                f'<text x="{x0}" y="{y + 34}" class="flag" font-size="13" font-weight="600">'
                f"{p['n']} annonces : aucun RVR affiché (volume insuffisant)</text>"
            )
            out.append(
                f'<text x="{x0}" y="{y + 52}" class="muted" font-size="12">'
                "Calculé annonce par annonce, ce même sac serait classé à la fois "
                "« se déprécie » et « se revend plus cher ».</text>"
            )

    out.append(
        f'<text x="40" y="{H - 24}" class="muted" font-size="12">◆ RVR retenu (médiane, à partir de 5 annonces)   '
        "● une annonce. Données : extrait du projet, relevé du 30/10/2026.</text>"
    )
    out.append("</svg>")
    return "\n".join(out)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    con = duckdb.connect(str(ROOT / "dior_rvr.duckdb"), read_only=True)
    (ASSETS / "banner.svg").write_text(banner(), encoding="utf-8")
    (ASSETS / "rvr_listings.svg").write_text(listings_chart(con), encoding="utf-8")
    print("wrote assets/banner.svg, assets/rvr_listings.svg")


if __name__ == "__main__":
    main()
