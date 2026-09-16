import csv
from datetime import datetime, timedelta
import json
from pathlib import Path
import random
import shutil
import tempfile
import unittest

from src.engine import analyze, Graph, parse_message

DATA = Path(__file__).resolve().parents[2] / "katilimci_paketi"


def write_fixture(directory, alarms, hosts, dependencies):
    path = Path(directory)
    (path / "alarms.json").write_text(json.dumps(alarms), encoding="utf-8")
    for name, rows, fields in [
        ("host_inventory.csv", hosts, ["host", "servis", "veri_merkezi", "kabin", "ortam", "is_kritikligi"]),
        ("service_dependencies.csv", dependencies, ["kaynak_servis", "hedef_servis", "bagimlilik_tipi", "kritiklik"]),
    ]:
        with (path / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader(); writer.writerows(rows)


def host(name, service, dc="d1", rack="r1"):
    return {"host": name, "servis": service, "veri_merkezi": dc, "kabin": rack, "ortam": "prod", "is_kritikligi": "kritik"}


def alarm(ident, hostname, service, seconds, typ, dc="d1", rack="r1", message="Ariza belirtisi", severity=4):
    return {"alarm_id": ident, "timestamp": (datetime(2031, 1, 1) + timedelta(seconds=seconds)).isoformat(),
            "source_system": "test", "host": hostname, "service": service, "severity": severity,
            "alarm_type": typ, "message": message, "tags": {"veri_merkezi": dc, "kabin": rack, "ortam": "prod"}}


class EngineSyntheticTests(unittest.TestCase):
    def run_fixture(self, alarms, hosts, dependencies=()):
        with tempfile.TemporaryDirectory() as directory:
            write_fixture(directory, alarms, hosts, dependencies)
            return analyze(directory)

    def test_directed_paths_and_cycles(self):
        graph = Graph([{"kaynak_servis": a, "hedef_servis": b} for a, b in [("client", "api"), ("api", "db"), ("db", "api")]])
        self.assertEqual(graph.path("client", "db"), ["client", "api", "db"])
        self.assertIsNone(graph.path("db", "client"))
        self.assertEqual(graph.dependents({"db"}), {"client", "api", "db"})

    def test_message_target_and_numeric_units(self):
        self.assertEqual(parse_message("abc-api servisine timeout 2300 ms")[0], "abc-api")
        self.assertEqual(parse_message("Bellek yuzde 63,5")[1]["percent"], 63.5)
        self.assertNotIn("percent", parse_message("HTTP 503; 300 ms")[1])

    def test_same_rack_name_in_different_datacenters_is_not_one_event(self):
        alarms = [alarm(f"a{dc}{i}", dc, dc, i * 30, "network_down", dc=dc) for dc in ["d1", "d2"] for i in range(3)]
        result = self.run_fixture(alarms, [host(dc, dc, dc=dc) for dc in ["d1", "d2"]])
        self.assertEqual(result["summary"]["incident_count"], 2)
        self.assertEqual({i["root"]["scope"] for i in result["incidents"]}, {"d1/r1", "d2/r1"})

    def test_independent_events_are_not_trimmed_to_fifteen(self):
        hosts = [host(f"h{i}", f"s{i}") for i in range(16)]
        alarms = [alarm(f"a{i}-{j}", f"h{i}", f"s{i}", j * 30, "ext_unreach") for i in range(16) for j in range(2)]
        result = self.run_fixture(alarms, hosts)
        self.assertEqual(result["summary"]["incident_count"], 16)
        self.assertFalse(result["summary"]["card_limit_pass"])
        self.assertEqual(sum(i["alarm_count"] for i in result["incidents"]), 32)

    def test_unknown_and_isolated_strong_signals_stay_uncertain(self):
        result = self.run_fixture([alarm("a1", "h", "s", 0, "brand_new_type"), alarm("a2", "h", "s", 20, "disk_full")], [host("h", "s")])
        self.assertEqual(result["summary"]["incident_count"], 0)
        self.assertEqual(result["summary"]["uncertain_count"], 2)
        self.assertFalse(result["summary"]["card_limit_pass"])

    def test_low_severity_slow_rise_is_preserved(self):
        alarms = [alarm(f"a{i}", "h", "s", i * 300, "mem_high", message=f"Bellek yuzde {40+i*3}", severity=2) for i in range(6)]
        alarms += [alarm("gc1", "h", "s", 1900, "gc_pressure"), alarm("gc2", "h", "s", 2000, "gc_pressure")]
        result = self.run_fixture(alarms, [host("h", "s")])
        self.assertEqual(result["summary"]["assigned_count"], 8)
        self.assertEqual(result["incidents"][0]["start"], alarms[0]["timestamp"])

    def test_large_jump_before_slow_trend_does_not_backdate_onset(self):
        alarms = [alarm("stray", "h", "s", 0, "mem_high", message="Bellek yuzde 32", severity=2)]
        alarms += [alarm(f"a{i}", "h", "s", 300 + i * 300, "mem_high", message=f"Bellek yuzde {44+i*3}", severity=2) for i in range(6)]
        alarms += [alarm("gc1", "h", "s", 2000, "gc_pressure"), alarm("gc2", "h", "s", 2100, "gc_pressure")]
        result = self.run_fixture(alarms, [host("h", "s")])
        self.assertEqual(result["incidents"][0]["start"], alarms[1]["timestamp"])
        self.assertNotEqual(result["alarms"][0]["decision"], "incident")

    def test_invalid_data_fail_closed_without_silent_dropping(self):
        good = alarm("a", "h", "s", 0, "timeout")
        for bad in [dict(good, severity=9), dict(good, timestamp="bad"), dict(good, host="unknown"), dict(good, service="wrong"), dict(good, tags=[]), dict(good, message=None)]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.run_fixture([good, dict(bad, alarm_id="b")], [host("h", "s")])
        with self.assertRaises(ValueError):
            self.run_fixture([good, good], [host("h", "s")])


@unittest.skipUnless((DATA / "alarms.json").exists(), "Katılımcı paketi bulunamadı; sentetik testler kullanılabilir.")
class ParticipantRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = analyze(DATA)

    def fixture_copy(self, directory):
        for name in ["alarms.json", "alarms.csv", "host_inventory.csv", "service_dependencies.csv"]:
            shutil.copyfile(DATA / name, Path(directory) / name)

    def decision_map(self, report):
        kinds = {i["id"]: i["kind"] for i in report["incidents"]}
        return {a["alarm_id"]: (a["decision"], kinds.get(a["incident_id"]), a["reason"]) for a in report["alarms"]}

    def test_full_coverage_and_last_records(self):
        r = self.report; s = r["summary"]
        self.assertEqual(s["input_count"], 3000)
        self.assertEqual(s["assigned_count"] + s["noise_count"] + s["uncertain_count"], 3000)
        self.assertEqual(len({a["alarm_id"] for a in r["alarms"]}), 3000)
        self.assertEqual(s["end"], "2026-09-10T03:30:20")
        self.assertTrue(all(a["reason"] for a in r["alarms"]))
        self.assertTrue(all(i["action"]["owner"] and i["action"]["status"] for i in r["incidents"]))

    def test_concurrent_mobile_timeouts_follow_message_target(self):
        kinds = {i["id"]: i["kind"] for i in self.report["incidents"]}
        group = [a for a in self.report["alarms"] if a["service"] == "mobile-bff" and a["alarm_type"] == "timeout" and "02:35" <= a["timestamp"][11:16] <= "03:05"]
        self.assertEqual(len(group), 38)
        counts = {"memory": 0, "external": 0}
        for a in group:
            expected = "memory" if a["message_target"] == "session-service" else "external"
            self.assertEqual(kinds.get(a["incident_id"]), expected)
            self.assertIn("validated_message_target", a["evidence_codes"])
            counts[expected] += 1
        self.assertEqual(counts, {"memory": 12, "external": 26})

    def test_external_root_and_79_targeted_timeouts_share_one_card(self):
        external = next(i for i in self.report["incidents"] if i["kind"] == "external")
        roots = [a for a in self.report["alarms"] if a["alarm_type"] in {"ext_unreach", "ext_slow"}]
        calls = [a for a in self.report["alarms"] if a["alarm_type"] == "timeout" and a["message_target"] == "payment-provider-gw"]
        self.assertEqual(len(roots), 24); self.assertEqual(len(calls), 79)
        self.assertEqual(len({a["service"] for a in calls}), 3)
        self.assertEqual({a["incident_id"] for a in roots + calls}, {external["id"]})
        self.assertEqual(external["end"], "2026-09-10T03:01:16")

    def test_seven_late_critical_alarms_are_not_orphaned(self):
        external = next(i for i in self.report["incidents"] if i["kind"] == "external")
        tail = [a for a in self.report["alarms"] if a["severity"] == 5 and "02:58" <= a["timestamp"][11:16] <= "03:01"]
        self.assertEqual(len(tail), 7)
        self.assertTrue(all(a["decision"] == "incident" and a["incident_id"] == external["id"] for a in tail))

    def test_dns_corroboration_does_not_invent_dependency_edges(self):
        network = next(i for i in self.report["incidents"] if i["kind"] == "network")
        dns = next(d for d in network["dependency_evidence"] if d["target"] == "dns-resolver")
        self.assertEqual(dns["refused_count"], 7)
        self.assertEqual(dns["verified_path_count"], 3)
        self.assertEqual(len(dns["target_network_alarms"]), 1)
        self.assertEqual(dns["target_network_alarms"][0]["timestamp"], "2026-09-10T01:45:04")
        self.assertEqual(sum(c["relation"] == "unverified" for c in dns["calls"]), 3)
        self.assertEqual(sum(c["relation"] == "self" for c in dns["calls"]), 1)

    def test_executive_card_separates_direct_hosts_from_all_hosts(self):
        network = next(i for i in self.report["incidents"] if i["kind"] == "network")
        self.assertEqual(len(network["direct_hosts"]), 9)
        self.assertEqual(len(network["hosts"]), 26)
        self.assertEqual(len(network["services"]), 14)
        self.assertEqual(network["alarm_count"], 401)
        known_ids = {a["alarm_id"] for a in self.report["alarms"]}
        self.assertTrue(all(set(c["alarm_ids"]) <= known_ids for c in network["evidence_checks"]))

    def test_uncertain_contract_and_review_cards_keep_accounting(self):
        r = self.report
        ids = {a["alarm_id"] for a in r["alarms"] if a["decision"] == "uncertain"}
        self.assertEqual({a["alarm_id"] for a in r["uncertain"]}, ids)
        reviews = r["review_candidates"]
        self.assertEqual(len(reviews), 3)
        card_ids = [a for c in reviews for a in c["review_alarm_ids"]]
        self.assertEqual(len(card_ids), len(set(card_ids)))
        self.assertTrue(set(card_ids) <= ids)
        self.assertTrue(all(c["confidence"]["level"] == "düşük" for c in reviews))
        self.assertTrue(all(c["action"]["owner"] and c["action"]["status"] for c in reviews))
        self.assertEqual(r["summary"]["total_card_count"], 8)

    def test_owner_roles_follow_root_family_not_equal_criticality(self):
        owners = {i["kind"]: i["action"]["owner"] for i in self.report["incidents"]}
        self.assertEqual(len(set(owners.values())), 5)

    def test_memory_trend_has_three_hosts_and_excludes_low_interleaved_readings(self):
        memory = next(i for i in self.report["incidents"] if i["kind"] == "memory")
        trend = memory["memory_trend"]
        self.assertEqual(len({a["host"] for a in trend}), 3)
        self.assertEqual(len(trend), 24)
        for hostname in {a["host"] for a in trend}:
            values = [a["percent"] for a in trend if a["host"] == hostname]
            self.assertEqual(values, [60,62,64,66,68,70,72,74])

    def test_order_invariance(self):
        with tempfile.TemporaryDirectory() as directory:
            self.fixture_copy(directory)
            path = Path(directory) / "alarms.json"
            rows = json.loads(path.read_text()); random.Random(419).shuffle(rows)
            path.write_text(json.dumps(rows))
            self.assertEqual(self.decision_map(analyze(directory)), self.decision_map(self.report))

    def test_csv_and_json_equivalence(self):
        with tempfile.TemporaryDirectory() as directory:
            self.fixture_copy(directory)
            (Path(directory) / "alarms.json").unlink()
            self.assertEqual(self.decision_map(analyze(directory)), self.decision_map(self.report))

    def test_day_shift_and_id_rename_do_not_change_decisions(self):
        with tempfile.TemporaryDirectory() as directory:
            self.fixture_copy(directory)
            path = Path(directory) / "alarms.json"
            rows = json.loads(path.read_text())
            for a in rows:
                a["timestamp"] = (datetime.fromisoformat(a["timestamp"]) + timedelta(days=400)).isoformat()
                a["alarm_id"] = "REKEY-" + a["alarm_id"]
            path.write_text(json.dumps(rows))
            changed = self.decision_map(analyze(directory))
            self.assertEqual({key.removeprefix("REKEY-"): value for key, value in changed.items()}, self.decision_map(self.report))

    def test_service_rename_does_not_change_assignment(self):
        with tempfile.TemporaryDirectory() as directory:
            self.fixture_copy(directory)
            services = sorted({a["service"] for a in self.report["alarms"]}, key=len, reverse=True)
            for filename in ["alarms.json", "host_inventory.csv", "service_dependencies.csv"]:
                path = Path(directory) / filename; content = path.read_text()
                # Unique neutral names prevent service-name-specific rules from passing.
                for index, service in enumerate(services):
                    content = content.replace(service, f"renamed-{index:03d}")
                path.write_text(content)
            changed = self.decision_map(analyze(directory)); original = self.decision_map(self.report)
            self.assertEqual({k: v[:2] for k, v in changed.items()}, {k: v[:2] for k, v in original.items()})


if __name__ == "__main__":
    unittest.main()
