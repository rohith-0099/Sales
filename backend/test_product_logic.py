import unittest

import pandas as pd

from analytics_engine import filter_dataset_by_product, prepare_uploaded_dataframe, search_products


class ProductLogicTest(unittest.TestCase):
    def setUp(self):
        self.source_df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02"],
                "product_id": ["SKU-1", "SKU-1", "SKU-2", "SKU-2"],
                "product_name": ["Alpha Cleaner", None, "Beta Soap", "Beta Soap"],
                "product_category": ["Home Care", "Home Care", "Personal Care", "Personal Care"],
                "sales": [120, 135, 80, 95],
            }
        )
        prepared = prepare_uploaded_dataframe(self.source_df)
        self.item = {
            "data": prepared["data"],
            "metadata": prepared["metadata"],
        }

    def test_prepare_uploaded_dataframe_keeps_one_canonical_key_per_identifier(self):
        product_rows = self.item["data"].sort_values(["product_identity", "date"]).reset_index(drop=True)

        self.assertEqual(self.item["metadata"]["stats"]["unique_products"], 2)
        self.assertTrue(self.item["metadata"]["product_column"])
        self.assertEqual(
            product_rows.loc[product_rows["product_identity"] == "sku1", "product_key"].nunique(),
            1,
        )
        self.assertEqual(
            product_rows.loc[product_rows["product_identity"] == "sku1", "product_key"].iloc[0],
            "Alpha Cleaner (SKU-1) (Home Care)",
        )

    def test_filter_dataset_by_product_accepts_exact_identifier_alias(self):
        filtered_df, resolved_product = filter_dataset_by_product(self.item, "sku-1")

        self.assertEqual(len(filtered_df), 2)
        self.assertEqual(filtered_df["product_identity"].nunique(), 1)
        self.assertEqual(resolved_product, "Alpha Cleaner (SKU-1) (Home Care)")

    def test_search_products_matches_canonical_identifier_text(self):
        matches = search_products(self.item, "sku1", limit=5)

        self.assertTrue(matches)
        self.assertEqual(matches[0]["value"], "Alpha Cleaner (SKU-1) (Home Care)")

    def test_single_product_upload_disables_product_scope(self):
        single_product_df = self.source_df[self.source_df["product_id"] == "SKU-1"].copy()
        prepared = prepare_uploaded_dataframe(single_product_df)

        self.assertIsNone(prepared["metadata"]["product_column"])
        self.assertEqual(prepared["metadata"]["sample_products"], [])


if __name__ == "__main__":
    unittest.main()
