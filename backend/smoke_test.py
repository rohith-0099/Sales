import io
import unittest
from pathlib import Path

from app import app


ROOT_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DATASET = ROOT_DIR / "test_data" / "synthetic_shop_sales_1_year.csv"


class RetailApiSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def _upload_sample_dataset(self, country_code="IN"):
        with SAMPLE_DATASET.open("rb") as file_handle:
            response = self.client.post(
                "/api/upload-csv",
                data={
                    "file": (io.BytesIO(file_handle.read()), SAMPLE_DATASET.name),
                    "country_code": country_code,
                },
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 200, response.get_json())
        payload = response.get_json()
        self.assertTrue(payload["success"])
        return payload

    def test_upload_and_aggregate_forecast_flow(self):
        upload_payload = self._upload_sample_dataset()
        response = self.client.post(
            "/api/forecast",
            json={
                "upload_id": upload_payload["upload_id"],
                "country_code": "IN",
                "forecast_periods": 7,
            },
        )

        self.assertEqual(response.status_code, 200, response.get_json())
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["metrics"]["scope"], "aggregate")
        self.assertEqual(len(payload["forecast"]), 7)

    def test_product_scope_forecast_flow(self):
        upload_payload = self._upload_sample_dataset()
        product_key = upload_payload["sample_products"][0]

        response = self.client.post(
            "/api/forecast",
            json={
                "upload_id": upload_payload["upload_id"],
                "country_code": "IN",
                "forecast_periods": 7,
                "selected_product": product_key,
            },
        )

        self.assertEqual(response.status_code, 200, response.get_json())
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["metrics"]["scope"], "product")
        self.assertEqual(payload["selected_product"], product_key)

    def test_future_holiday_coverage_expands_beyond_2026(self):
        response = self.client.get("/api/holidays?market=US&start=2027-11-20&end=2027-11-30")
        self.assertEqual(response.status_code, 200, response.get_json())
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertTrue(any(item["festival"] == "Thanksgiving Day" for item in payload["holidays"]))

    def test_runtime_metadata_endpoints(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200, response.get_json())
        payload = response.get_json()
        self.assertEqual(payload["status"], "healthy")
        self.assertEqual(payload["runtime_mode"], "upload_forecasting")

        response = self.client.get("/api/model-info")
        self.assertEqual(response.status_code, 200, response.get_json())
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["runtime_mode"], "upload_forecasting")
        self.assertEqual(payload["forecast_engine"]["base_model"], "Prophet")


if __name__ == "__main__":
    unittest.main()
