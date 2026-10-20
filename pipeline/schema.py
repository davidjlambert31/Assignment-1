"""Define the standardized transaction entity used throughout the pipeline."""

from datetime import date
from decimal import Decimal


class TransactionRecord:
    """Hold one validated retail transaction with consistent Python types."""

    def __init__(
        self,
        transaction_id: str,
        branch_id: str,
        transaction_date: date,
        customer_tier: str,
        item_count: int,
        revenue: Decimal,
        cost: Decimal,
        region: str,
        active: bool,
    ):
        self.transaction_id = transaction_id
        self.branch_id = branch_id
        self.transaction_date = transaction_date
        self.customer_tier = customer_tier
        self.item_count = item_count
        self.revenue = revenue
        self.cost = cost
        self.region = region
        self.active = active

    def __repr__(self):
        """Provide a short description useful when tracing execution."""
        return (
            f"TransactionRecord(id={self.transaction_id!r}, "
            f"branch={self.branch_id!r}, revenue={self.revenue})"
        )
