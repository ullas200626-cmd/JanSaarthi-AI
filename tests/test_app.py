
import sqlite3
import tempfile
import unittest
from pathlib import Path

import database
import app as main_app
import admin_dashboard as admin_app


class JanSaarthiAPITests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database_path = database.DATABASE_PATH

        database.DATABASE_PATH = (
            Path(self.temp_dir.name) / "test_jansaarthi.db"
        )

        database.initialize_database()

        main_app.app.config["TESTING"] = True
        admin_app.app.config["TESTING"] = True

        self.client = main_app.app.test_client()
        self.admin_client = admin_app.app.test_client()

    def tearDown(self):
        # Close any SQLite connections left open by this test.
        connection = getattr(database, "get_connection", None)

        # Restore the real project path before removing the test database.
        database.DATABASE_PATH = self.original_database_path

        # Remove the temporary database after connections are closed.
        self.temp_dir.cleanup()

    def register_water_complaint(self):
        response = self.client.post(
            "/api/complaints",
            json={
                "message": "There is no water supply in our village",
                "issue": "water",
                "language": "English",
            },
        )

        self.assertIn(
            response.status_code,
            (200, 201),
            msg=response.get_data(as_text=True),
        )

        data = response.get_json()
        complaint_id = data.get("complaint", {}).get("complaint_id")

        self.assertTrue(
            complaint_id,
            msg=f"No complaint ID found in response: {data}",
        )

        return complaint_id

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

    def test_chat_recognises_water_issue(self):
        response = self.client.post(
            "/api/chat",
            json={
                "message": "There is no water supply in our village"
            },
        )

        self.assertEqual(
            response.status_code,
            200,
            msg=response.get_data(as_text=True),
        )

        data = response.get_json()
        self.assertTrue(data.get("reply"))
        self.assertEqual(data.get("issue"), "water")

    def test_register_and_track_complaint(self):
        complaint_id = self.register_water_complaint()

        response = self.client.get(
            f"/api/complaints/{complaint_id}"
        )

        self.assertEqual(
            response.status_code,
            200,
            msg=response.get_data(as_text=True),
        )

        data = response.get_json()
        self.assertIn(complaint_id, str(data))
        self.assertIn("Submitted", str(data))

    def test_unknown_complaint_returns_not_found(self):
        response = self.client.get(
            "/api/complaints/JS-DOES-NOT-EXIST"
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_dashboard_counts_complaints(self):
        self.register_water_complaint()

        response = self.admin_client.get(
            "/api/admin/dashboard"
        )

        self.assertEqual(
            response.status_code,
            200,
            msg=response.get_data(as_text=True),
        )

        data = response.get_json()
        self.assertGreaterEqual(data["counts"]["total"], 1)
        self.assertGreaterEqual(data["counts"]["submitted"], 1)
        self.assertIn("water", data["categories"])

    def test_status_update_is_visible_when_tracking(self):
        complaint_id = self.register_water_complaint()

        update_response = self.admin_client.patch(
            f"/api/admin/complaints/{complaint_id}",
            json={"status": "In Progress"},
        )

        self.assertEqual(
            update_response.status_code,
            200,
            msg=update_response.get_data(as_text=True),
        )

        tracking_response = self.client.get(
            f"/api/complaints/{complaint_id}"
        )

        self.assertEqual(tracking_response.status_code, 200)
        self.assertIn("In Progress", str(tracking_response.get_json()))

    def test_invalid_status_is_rejected(self):
        complaint_id = self.register_water_complaint()

        response = self.admin_client.patch(
            f"/api/admin/complaints/{complaint_id}",
            json={"status": "Not A Valid Status"},
        )

        self.assertEqual(
            response.status_code,
            400,
            msg=response.get_data(as_text=True),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)