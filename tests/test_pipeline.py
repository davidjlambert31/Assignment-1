"""Unit tests for schema validation, transformations, and reporting."""

import unittest
from decimal import Decimal

from pipeline.reporter import RetailReport
from pipeline.transformer import active_transactions, enrich_transaction
from pipeline.validator import validate_record


class RetailPipelineTests(unittest.TestCase):
    """Test the main behaviors expected by the assignment rubric."""

    def setUp(self):
        self.raw = {
            "transaction_id": "T001",
            "branch_id": " on-101 ",
            "transaction_date": "2026-10-01",
            "customer_tier": " gold ",
            "item_count": "3",
            "revenue": "150.00",
            "cost": "90.00",
            "region": "ON",
            "active": "true",
        }

    def test_valid_row_is_coerced_to_correct_types(self):
        record, error = validate_record(self.raw)
        self.assertIsNone(error)
        self.assertEqual(record.branch_id, "ON-101")
        self.assertEqual(record.customer_tier, "GOLD")
        self.assertEqual(record.item_count, 3)
        self.assertEqual(record.revenue, Decimal("150.00"))
        self.assertTrue(record.active)

    def test_negative_revenue_is_rejected(self):
        invalid = {**self.raw, "revenue": "-10.00"}
        record, error = validate_record(invalid)
        self.assertIsNone(record)
        self.assertIn("nonnegative", error)

    def test_invalid_date_is_rejected(self):
        invalid = {**self.raw, "transaction_date": "2026-02-30"}
        record, error = validate_record(invalid)
        self.assertIsNone(record)
        self.assertIsNotNone(error)

    def test_missing_branch_id_is_rejected(self):
        invalid = {**self.raw, "branch_id": ""}
        record, error = validate_record(invalid)
        self.assertIsNone(record)
        self.assertIn("branch_id", error)

    def test_filter_keeps_active_records_only(self):
        active, _ = validate_record(self.raw)
        inactive, _ = validate_record({**self.raw, "active": "false"})
        original = [active, inactive]
        result = active_transactions(original)
        self.assertEqual(result, [active])
        self.assertEqual(len(original), 2)

    def test_tax_and_margin_do_not_mutate_source(self):
        record, _ = validate_record(self.raw)
        original_revenue = record.revenue
        enriched = enrich_transaction(record)
        self.assertEqual(enriched["estimated_tax"], Decimal("19.5000"))
        self.assertEqual(enriched["profit_before_overhead"], Decimal("60.00"))
        self.assertEqual(enriched["margin_percent"], Decimal("40.0"))
        self.assertEqual(record.revenue, original_revenue)

    def test_report_aggregation_and_retention(self):
        first, _ = validate_record(self.raw)
        second, _ = validate_record({
            **self.raw,
            "transaction_id": "T002",
            "branch_id": "AB-201",
            "revenue": "100.00",
            "cost": "40.00",
            "region": "AB",
            "customer_tier": "silver",
        })
        inactive, _ = validate_record({
            **self.raw,
            "transaction_id": "T003",
            "revenue": "999.00",
            "active": "false",
        })
        report = RetailReport([first, second, inactive], [(5, "bad date")], 4)
        metrics = report.calculate_metrics()
        self.assertEqual(metrics["gross_sales"], Decimal("250.00"))
        self.assertEqual(metrics["top_branch"], "ON-101")
        self.assertEqual(metrics["tier_counts"], {"GOLD": 1, "SILVER": 1})
        self.assertEqual(metrics["retention_percent"], 75.0)
        self.assertEqual(metrics["active_rows"], 2)


if __name__ == "__main__":
    unittest.main()
