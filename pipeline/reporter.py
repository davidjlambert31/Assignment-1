"""Aggregate validated transactions and format an executive terminal report."""

from decimal import Decimal

from pipeline.schema import TransactionRecord
from pipeline.transformer import active_transactions, transform_transactions


class RetailReport:
    """Calculate business metrics from a collection of TransactionRecord objects."""

    def __init__(self, records, rejected_rows, total_rows):
        # A tuple protects the container from accidental additions or removals.
        self.records = tuple(records)
        self.rejected_rows = tuple(rejected_rows)
        self.total_rows = total_rows

    def calculate_metrics(self):
        """Return summary metrics; only active, valid records affect sales."""
        active = active_transactions(self.records)
        enriched = transform_transactions(active)
        branch_sales = {}
        tier_counts = {}
        tier_sales = {}

        gross_sales = Decimal("0")
        estimated_tax = Decimal("0")
        profit = Decimal("0")

        for item in enriched:
            record = item["transaction"]  # A TransactionRecord object.
            gross_sales += item["gross_sales"]
            estimated_tax += item["estimated_tax"]
            profit += item["profit_before_overhead"]

            branch_sales[record.branch_id] = (
                branch_sales.get(record.branch_id, Decimal("0"))
                + item["gross_sales"]
            )
            tier_counts[record.customer_tier] = (
                tier_counts.get(record.customer_tier, 0) + 1
            )
            tier_sales[record.customer_tier] = (
                tier_sales.get(record.customer_tier, Decimal("0"))
                + item["gross_sales"]
            )

        # Deterministic tie-breaking: alphabetical branch ID on equal sales.
        top_branch = (
            min(branch_sales, key=lambda branch: (-branch_sales[branch], branch))
            if branch_sales else None
        )

        retention = (
            len(self.records) / self.total_rows * 100
            if self.total_rows else 0.0
        )
        overall_margin = (
            profit / gross_sales * 100 if gross_sales else Decimal("0")
        )

        return {
            "total_rows": self.total_rows,
            "valid_rows": len(self.records),
            "rejected_rows": len(self.rejected_rows),
            "retention_percent": retention,
            "active_rows": len(active),
            "gross_sales": gross_sales,
            "estimated_tax": estimated_tax,
            "profit_before_overhead": profit,
            "margin_percent": overall_margin,
            "top_branch": top_branch,
            "branch_sales": branch_sales,
            "tier_counts": tier_counts,
            "tier_sales": tier_sales,
        }


def format_report(report):
    """Build a printable report without printing inside the reporting logic."""
    metrics = report.calculate_metrics()
    top = metrics["top_branch"] or "N/A"

    lines = [
        "=" * 56,
        "RETAIL TRANSACTION PIPELINE - EXECUTIVE SUMMARY",
        "=" * 56,
        f"Rows loaded:             {metrics['total_rows']}",
        f"Rows accepted:           {metrics['valid_rows']}",
        f"Rows rejected:           {metrics['rejected_rows']}",
        f"Clean record retention:  {metrics['retention_percent']:.1f}%",
        f"Active valid rows:       {metrics['active_rows']}",
        "-" * 56,
        f"Total gross sales:       ${metrics['gross_sales']:,.2f}",
        f"Estimated tax collected: ${metrics['estimated_tax']:,.2f}",
        f"Profit before overhead:  ${metrics['profit_before_overhead']:,.2f}",
        f"Margin before overhead:  {metrics['margin_percent']:.1f}%",
        f"Top branch by sales:     {top}",
        "-" * 56,
        "CUSTOMER TIER BREAKDOWN (ACTIVE VALID TRANSACTIONS)",
    ]

    if metrics["tier_counts"]:
        for tier in sorted(metrics["tier_counts"]):
            count = metrics["tier_counts"][tier]
            sales = metrics["tier_sales"][tier]
            lines.append(f"  {tier:<10} {count:>3} transaction(s)   ${sales:>10,.2f}")
    else:
        lines.append("  No active valid transactions")

    if report.rejected_rows:
        lines.extend(["-" * 56, "REJECTED ROWS (FIRST FIVE)"])
        for row_number, reason in report.rejected_rows[:5]:
            lines.append(f"  CSV line {row_number}: {reason}")

    lines.append("=" * 56)
    return "\n".join(lines)
