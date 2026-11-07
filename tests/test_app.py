import os
import tempfile
import unittest

from app import app
from database import init_db


class LostFoundAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        app.config.update(
            TESTING=True,
            DATABASE=os.path.join(self.temp_dir.name, "test.db"),
            SECRET_KEY="test-secret",
        )
        init_db(app)
        self.client = app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def report(self, kind, name="Blue water bottle", category="Accessories",
               description="Blue steel bottle with a silver cap",
               location="Central Library", event_date="2026-10-10",
               contact="owner@example.com"):
        return self.client.post(
            f"/report/{kind}",
            data={
                "name": name,
                "category": category,
                "description": description,
                "location": location,
                "event_date": event_date,
                "contact": contact,
            },
            follow_redirects=True,
        )

    def test_lost_report_matches_existing_found_item(self):
        self.report("found")
        response = self.report("lost")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Possible matches for Blue water bottle", response.data)
        self.assertIn(b"100%", response.data)

    def test_new_found_report_matches_existing_lost_item(self):
        self.report("lost")
        response = self.report("found")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Possible matches for Blue water bottle", response.data)
        self.assertIn(b"100%", response.data)

    def test_invalid_form_is_rejected(self):
        response = self.client.post(
            "/report/lost",
            data={"name": "", "category": "Invalid"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Name is required", response.data)
        self.assertIn(b"Choose a valid item category", response.data)

    def test_dashboard_shows_reports_and_potential_match(self):
        self.report("lost")
        self.report("found")
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Potential matches", response.data)
        self.assertIn(b"All lost items", response.data)
        self.assertIn(b"All found items", response.data)
        self.assertIn(b"100%", response.data)

    def test_item_detail_is_available(self):
        self.report("found")
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            from database import get_db

            item = get_db().execute(
                "SELECT id FROM items WHERE kind = 'found'"
            ).fetchone()
        detail = self.client.get(f"/items/found/{item['id']}")
        self.assertEqual(detail.status_code, 200)
        self.assertIn(b"owner@example.com", detail.data)


if __name__ == "__main__":
    unittest.main()
