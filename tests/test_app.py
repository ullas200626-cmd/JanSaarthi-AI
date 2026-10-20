
import os
import re
import tempfile
import unittest
from pathlib import Path

import database
import app as main_app
import admin_dashboard as admin_app


class JanSaarthiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"

        # Both applications use the same database module.
        database.DATABASE_PATH = self.db_path
        database.initialize_database()

        secret_key = os.environ.get(
            "JANSAARTHI_SECRET_KEY",
            "test-secret-key-for-unit-tests-123456",
        )

        main_app.app.config.update(
            TESTING=True,
            SECRET_KEY=secret_key,
        )

        admin_app.app.config.update(
            TESTING=True,
            SECRET_KEY=secret_key,
            WTF_CSRF_ENABLED=True,
        )

        self.client = main_app.app.test_client()
        self.admin_client = admin_app.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def register_complaint(self):
        response = self.client.post(
            "/api/complaints",
            json={
                "message": "There is no water supply in our village.",
                "issue": "water",
                "language": "English",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
            msg=response.get_data(as_text=True),
        )

        data = response.get_json()
        self.assertTrue(data["success"])
        return data["complaint"]

    def login_admin(self):
        password = os.environ.get("JANSAARTHI_TEST_ADMIN_PASSWORD")
        username = os.environ.get("JANSAARTHI_ADMIN_USERNAME", "")

        self.assertTrue(
            password,
            "Set JANSAARTHI_TEST_ADMIN_PASSWORD in PowerShell first.",
        )
        self.assertTrue(username, "Admin username environment variable is missing.")

        page = self.admin_client.get("/login")
        self.assertEqual(page.status_code, 200)

        match = re.search(
            r'name="csrf_token"\s+value="([^"]+)"',
            page.get_data(as_text=True),
        )
        self.assertIsNotNone(match, "Login form CSRF token not found.")

        response = self.admin_client.post(
            "/login",
            data={
                "csrf_token": match.group(1),
                "username": username,
                "password": password,
            },
            follow_redirects=True,
        )

        self.assertEqual(
            response.status_code,
            200,
            msg=response.get_data(as_text=True),
        )
        self.assertIn(b"csrf-token", response.data)
        return response

    def get_admin_csrf_token(self):
        response = self.admin_client.get("/")
        self.assertEqual(response.status_code, 200)

        match = re.search(
            r'<meta name="csrf-token"\s+content="([^"]+)"',
            response.get_data(as_text=True),
        )
        self.assertIsNotNone(match, "Dashboard CSRF token not found.")
        return match.group(1)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_chat_recognises_water_issue(self):
        response = self.client.post(
            "/api/chat",
            json={
                "message": "There is no water supply in our village.",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
            msg=response.get_data(as_text=True),
        )
        self.assertEqual(response.get_json()["issue"], "water")

    def test_register_and_track_complaint(self):
        complaint = self.register_complaint()
        complaint_id = complaint["complaint_id"]

        response = self.client.get(
            f"/api/complaints/{complaint_id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["complaint"]["complaint_id"],
            complaint_id,
        )

    def test_unknown_complaint_returns_not_found(self):
        response = self.client.get("/api/complaints/JS-UNKNOWN")
        self.assertEqual(response.status_code, 404)

    def test_admin_dashboard_counts_complaints(self):
        self.register_complaint()
        self.login_admin()

        response = self.admin_client.get("/api/admin/dashboard")
        self.assertEqual(
            response.status_code,
            200,
            msg=response.get_data(as_text=True),
        )

        data = response.get_json()
        self.assertEqual(data["counts"]["total"], 1)
        self.assertEqual(data["counts"]["submitted"], 1)

    def test_status_update_is_visible_when_tracking(self):
        complaint = self.register_complaint()
        complaint_id = complaint["complaint_id"]

        self.login_admin()
        csrf_token = self.get_admin_csrf_token()

        response = self.admin_client.patch(
            f"/api/admin/complaints/{complaint_id}",
            json={"status": "In Progress"},
            headers={"X-CSRFToken": csrf_token},
        )

        self.assertEqual(
            response.status_code,
            200,
            msg=response.get_data(as_text=True),
        )
        self.assertEqual(response.get_json()["status"], "In Progress")

        tracking = self.client.get(
            f"/api/complaints/{complaint_id}"
        )
        self.assertEqual(tracking.status_code, 200)
        self.assertEqual(
            tracking.get_json()["complaint"]["status"],
            "In Progress",
        )

    def test_invalid_status_is_rejected(self):
        complaint = self.register_complaint()
        complaint_id = complaint["complaint_id"]

        self.login_admin()
        csrf_token = self.get_admin_csrf_token()

        response = self.admin_client.patch(
            f"/api/admin/complaints/{complaint_id}",
            json={"status": "Not a valid status"},
            headers={"X-CSRFToken": csrf_token},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
