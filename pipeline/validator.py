"""Validate CSV rows and convert acceptable values to typed records."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

from pipeline.schema import TransactionRecord


REQUIRED_FIELDS = (
    "transaction_id",
    "branch_id",
    "transaction_date",
    "customer_tier",
    "item_count",
    "revenue",
    "cost",
    "region",
    "active",
)

VALID_TIERS = {"BRONZE", "SILVER", "GOLD", "PLATINUM"}
VALID_REGIONS = {"ON", "AB", "BC"}


def parse_boolean(value):
    """Convert common CSV boolean text to True or False."""
    value = str(value).strip().lower()
    if value in {"true", "yes", "y", "1"}:
        return True
    if value in {"false", "no", "n", "0"}:
        return False
    raise ValueError("active must be true/false, yes/no, or 1/0")


def parse_money(value, field_name):
    """Convert a money field to a finite, nonnegative Decimal."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_name} must be a number") from None

    if not amount.is_finite() or amount < 0:
        raise ValueError(f"{field_name} must be finite and nonnegative")
    return amount


def validate_record(raw_row):
    """Return (TransactionRecord, None) or (None, reason) for a CSV row."""
    if not isinstance(raw_row, dict):
        return None, "row is not a dictionary"
    if None in raw_row:
        return None, "row has more values than header columns"

    # Normalize headers and whitespace without changing the original row.
    row = {
        key.strip().lower(): value.strip() if isinstance(value, str) else value
        for key, value in raw_row.items()
    }

    missing = [name for name in REQUIRED_FIELDS if not row.get(name)]
    if missing:
        return None, "missing fields: " + ", ".join(missing)

    try:
        date_text = row["transaction_date"]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text):
            raise ValueError("transaction_date must use YYYY-MM-DD")
        transaction_date = datetime.strptime(date_text, "%Y-%m-%d").date()

        item_count = int(row["item_count"])
        if item_count <= 0:
            raise ValueError("item_count must be greater than zero")

        revenue = parse_money(row["revenue"], "revenue")
        cost = parse_money(row["cost"], "cost")
        active = parse_boolean(row["active"])

        tier = row["customer_tier"].upper()
        if tier not in VALID_TIERS:
            raise ValueError("unknown customer_tier: " + tier)

        region = row["region"].upper()
        if region not in VALID_REGIONS:
            raise ValueError("unknown region: " + region)

    except (ValueError, TypeError, OverflowError) as error:
        return None, str(error)

    record = TransactionRecord(
        transaction_id=row["transaction_id"],
        branch_id=row["branch_id"].upper(),
        transaction_date=transaction_date,
        customer_tier=tier,
        item_count=item_count,
        revenue=revenue,
        cost=cost,
        region=region,
        active=active,
    )
    return record, None
