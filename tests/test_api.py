from copy import deepcopy
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.engine import analyze
from src.narrative import Narrator
from src.server import make_server, State
from test_engine import alarm, host, write_fixture


def report_fixture():
    with tempfile.TemporaryDirectory() as directory:
        write_fixture(directory, [alarm("a1", "h", "s", 0, "disk_full"), alarm("a2", "h", "s", 30, "disk_full")], [host("h", "s")], [])
        return analyze(directory)


class ActionTests(unittest.TestCase):
    def setUp(self):
        self.state = State(report_fixture()); self.ident = self.state.report["incidents"][0]["id"]

    def test_lifecycle_and_version_conflict(self):
        body = {"owner": "DBA nöbetçisi", "status": "investigating", "note": "Disk kontrolü başladı", "version": 1}
        action = self.state.update_action(self.ident, body)
        self.assertEqual(action["version"], 2)
        with self.assertRaises(RuntimeError): self.state.update_action(self.ident, body)
        action = self.state.update_action(self.ident, dict(body, status="resolved", version=2, note="Operatör kapasiteyi doğruladı"))
        self.assertEqual(len(action["history"]), 2)
        action = self.state.update_action(self.ident, dict(body, status="open", version=3))
        self.assertEqual(action["status"], "open")

    def test_transition_and_input_validation(self):
        body = {"owner": "DBA", "status": "investigating", "note": "", "version": 1}
        for bad in [dict(body, owner=" "), dict(body, status="resolved"), dict(body, version=True), dict(body, note="a" * 1001), [], dict(body, status=[] )]:
            with self.subTest(bad=bad), self.assertRaises(ValueError): self.state.update_action(self.ident, bad)
        self.state.update_action(self.ident, body)
        with self.assertRaises(ValueError): self.state.update_action(self.ident, dict(body, status="resolved", version=2))

    def test_snapshots_do_not_mutate_state(self):
        self.state.snapshot()["incidents"][0]["action"]["owner"] = "mutated"
        self.assertNotEqual(self.state.incident(self.ident)["action"]["owner"], "mutated")


class NarrativeTests(unittest.TestCase):
    def setUp(self):
        self.incident = report_fixture()["incidents"][0]
        with patch.dict("os.environ", {"LLM_ENABLED": "false"}): self.narrator = Narrator()

    def test_disabled_does_not_call_provider(self):
        with patch("src.narrative.build_opener") as opener:
            result = self.narrator.explain(self.incident)
            self.assertEqual(result["source"], "template"); opener.assert_not_called()

    def test_provider_failure_falls_back_without_leaking_error(self):
        self.narrator.enabled = True; self.narrator.endpoint = "https://example.invalid/v1/messages"; self.narrator.key = "private-placeholder"
        with patch("src.narrative.build_opener", side_effect=TimeoutError("private-placeholder")):
            result = self.narrator.explain(self.incident)
        self.assertEqual(result["source"], "template")
        self.assertNotIn("private-placeholder", json.dumps(result))

    def test_fabricated_evidence_rejected_and_valid_response_cached(self):
        self.narrator.enabled = True; self.narrator.endpoint = "https://example.invalid/v1/messages"; self.narrator.key = "test"
        for ident, expected in [("fabricated", "template"), ("a1", "llm")]:
            raw = json.dumps({"content": [{"type": "text", "text": json.dumps({"summary": "Disk kapasitesi hipotezi inceleme gerektiriyor.", "evidence_ids": [ident]})}]}).encode()
            with patch("src.narrative.build_opener") as opener:
                opener.return_value.open.return_value.__enter__.return_value.read.return_value = raw
                self.assertEqual(self.narrator.explain(self.incident)["source"], expected)
                if expected == "llm":
                    self.narrator.explain(self.incident)
                    self.assertEqual(opener.call_count, 1)


class HttpIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.dict("os.environ", {"LLM_ENABLED": "false"}): cls.server = make_server(report_fixture(), port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()
        cls.base = "http://127.0.0.1:" + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join(timeout=2)

    def request(self, path, body=None, headers=None):
        request = Request(self.base + path, data=json.dumps(body).encode() if body is not None else None,
                          headers={"Content-Type": "application/json", **(headers or {})})
        try: response = urlopen(request, timeout=5)
        except HTTPError as error: response = error
        with response:
            raw = response.read()
            return response.status, json.loads(raw) if response.headers["Content-Type"].startswith("application/json") else raw

    def test_end_to_end_report_filter_action_export(self):
        code, report = self.request("/api/report"); self.assertEqual(code, 200); self.assertNotIn("alarms", report)
        ident = report["incidents"][0]["id"]
        code, alarms = self.request("/api/alarms?incident_id=" + ident + "&limit=1")
        self.assertEqual(alarms["total"], 2); self.assertEqual(len(alarms["items"]), 1)
        code, action = self.request(f"/api/incidents/{ident}/action", {"owner": "Demo DBA", "status": "investigating", "note": "Başlandı", "version": 1})
        self.assertEqual(code, 200); self.assertEqual(action["version"], 2)
        code, export = self.request("/api/export")
        self.assertEqual(export["incidents"][0]["action"]["owner"], "Demo DBA"); self.assertEqual(len(export["alarms"]), 2)
        code, narrative = self.request(f"/api/incidents/{ident}/narrative", {})
        self.assertEqual(narrative["source"], "template")

    def test_bad_requests_and_private_files(self):
        for path, expected in [("/.env",404),("/../src/engine.py",404),("/api/alarms?offset=bad",400),("/api/alarms?decision=bad",400)]:
            with self.subTest(path=path): self.assertEqual(self.request(path)[0], expected)
        self.assertEqual(self.request("/api/report", headers={"Origin": "https://foreign.example"})[0], 403)
        self.assertEqual(self.request("/api/report", headers={"Host": "foreign.example"})[0], 403)
        code, _ = self.request("/api/incidents/unknown/action", {"owner":"x", "status":"open", "note":"", "version":1})
        self.assertEqual(code, 404)

    def test_ui_assets_are_served(self):
        for path in ["/", "/app.js", "/styles.css"]:
            self.assertEqual(self.request(path)[0], 200)


if __name__ == "__main__":
    unittest.main()
