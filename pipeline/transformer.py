"""Stateless, functional transformations of validated transaction records."""

from decimal import Decimal

# Illustrative rates for this simulated assignment; not a tax-compliance tool.
TAX_RATES = {
    "ON": Decimal("0.13"),
    "AB": Decimal("0.05"),
    "BC": Decimal("0.12"),
}


def active_transactions(records):
    """Keep active transactions without modifying the incoming collection."""
    return list(filter(lambda record: record.active, records))


def enrich_transaction(record):
    """Return a new dictionary containing financial calculations for a record."""
    tax = record.revenue * TAX_RATES[record.region]
    profit = record.revenue - record.cost
    margin = (profit / record.revenue * 100) if record.revenue else Decimal("0")

    return {
        "transaction": record,
        "gross_sales": record.revenue,
        "estimated_tax": tax,
        "customer_total": record.revenue + tax,
        "profit_before_overhead": profit,
        "margin_percent": margin,
    }


def transform_transactions(records):
    """Apply the same pure calculation to each record using map()."""
    return list(map(lambda record: enrich_transaction(record), records))
