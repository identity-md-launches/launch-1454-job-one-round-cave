#!/usr/bin/env python3
"""Offline behavioral checks for explicit unsigned-envelope expectations."""

import contextlib
import io
import unittest

import guard

D = guard.intent.decoder


def baseline():
    return [1, 0, 1000000000, 2000000000, 100000,
            bytes.fromhex(D.ZTO[2:]), 0, bytes.fromhex("18160ddd"), []]


def encode(fields):
    return "0x02" + D.rlp_encode(fields).hex()


def expectations():
    return {"chainId": 1, "nonce": 0, "to": D.ZTO, "value": 0,
            "data": "0x18160ddd", "gasLimit": 100000,
            "maxPriorityFeePerGas": 1000000000, "maxFeePerGas": 2000000000,
            "accessList": []}


class GuardTests(unittest.TestCase):
    def test_synthetic_zto_demo_matches_all_fields(self):
        report = guard.check(D.demo_transaction(), expectations())
        self.assertEqual(report["status"], "matches-expectations")
        self.assertEqual(report["mismatches"], [])
        self.assertEqual(report["inspection"]["destinationLabel"], "ZTO")
        self.assertEqual(report["inspection"]["feeBudget"]["gasFeeCapWei"], "200000000000000")
        self.assertEqual(len([c for c in report["checks"] if c["matched"]]), len(report["checks"]))

    def test_each_exact_field_mutation_is_reported(self):
        cases = {0: (2, "chainId"), 1: (1, "nonce"),
                 4: (100001, "gasLimit"), 5: (bytes.fromhex(guard.intent.IMD[2:]), "to"),
                 6: (1, "value"), 7: (bytes.fromhex("18160ddd00"), "data")}
        for index, (replacement, name) in cases.items():
            with self.subTest(field=name):
                tx = baseline()
                tx[index] = replacement
                report = guard.check(encode(tx), expectations())
                self.assertEqual(report["status"], "mismatch")
                self.assertEqual([m["field"] for m in report["mismatches"]], [name])

    def test_fee_caps_are_upper_bounds_and_priority_order_is_checked(self):
        tx = baseline()
        tx[2], tx[3] = 500000000, 1500000000
        self.assertEqual(guard.check(encode(tx), expectations())["status"], "matches-expectations")
        tx[2], tx[3] = 2000000001, 2000000000
        fields = [m["field"] for m in guard.check(encode(tx), expectations())["mismatches"]]
        self.assertEqual(fields, ["maxPriorityFeePerGas", "priorityWithinFeeCap"])
        tx[2], tx[3] = 1000000000, 3000000000
        self.assertEqual([m["field"] for m in guard.check(encode(tx), expectations())["mismatches"]],
                         ["maxFeePerGas"])

    def test_access_list_must_match_exact_order_and_duplicate_slots(self):
        a = {"address": D.ZTO, "storageKeys": ["0x" + "11" * 32, "0x" + "11" * 32]}
        b = {"address": guard.intent.IMD, "storageKeys": []}
        expected = expectations()
        expected["accessList"] = [a, b]
        tx = baseline()
        tx[8] = [[bytes.fromhex(a["address"][2:]), [bytes.fromhex(s[2:]) for s in a["storageKeys"]]],
                 [bytes.fromhex(b["address"][2:]), []]]
        self.assertEqual(guard.check(encode(tx), expected)["status"], "matches-expectations")
        for mutation in (tx[8][::-1], [tx[8][0], tx[8][1], tx[8][0]],
                         [[tx[8][0][0], tx[8][0][1][:1]], tx[8][1]]):
            changed = list(tx)
            changed[8] = mutation
            self.assertEqual([m["field"] for m in guard.check(encode(changed), expected)["mismatches"]],
                             ["accessList"])

    def test_policy_input_rejects_ambiguity_and_oversize(self):
        for text in ("", "01", "-1", "+1", "0x1", "1.0", "1  ", str(2**256)):
            with self.subTest(number=text), self.assertRaises(ValueError):
                guard.decimal(text)
        for value in ("0x123", "0X" + "12" * 20, "0x" + "zz" * 20):
            with self.assertRaises(ValueError):
                guard.address(value)
        for value in ("18160ddd", "0x123", "0xzz", "0x00 "):
            with self.assertRaises(ValueError):
                guard.hex_data(value)
        for value in ('{"address":"x"}', '[{"address":"x","address":"y","storageKeys":[]}]',
                      '[{"address":"x","storageKeys":[]}]',
                      '[{"address":"0x' + '11'*20 + '","storageKeys":["0x1234"]}]'):
            with self.assertRaises(ValueError):
                guard.expected_access_list(value)

    def test_bad_envelopes_are_rejected_before_any_report(self):
        for value in ("0x01c0", "0x02c0", encode(baseline() + [0, 1, 1]), "0x02zz"):
            with self.assertRaises(ValueError):
                guard.check(value, expectations())

    def test_contract_creation_requires_explicit_creation_destination(self):
        tx = baseline()
        tx[5] = b""
        expected = expectations()
        expected["to"] = guard.destination("creation")
        self.assertEqual(guard.check(encode(tx), expected)["status"], "matches-expectations")
        expected["to"] = D.ZTO
        self.assertEqual([m["field"] for m in guard.check(encode(tx), expected)["mismatches"]],
                         ["to"])

    def test_cli_exit_codes_and_no_partial_json(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(guard.main(["--demo"]), 0)
        self.assertIn('"matches-expectations"', output.getvalue())
        args = [D.demo_transaction(), "--chain-id", "1", "--nonce", "0",
                "--to", D.ZTO, "--value-wei", "0", "--data", "0x18160ddd",
                "--gas-limit", "100000", "--max-priority-fee-per-gas-wei", "1000000000",
                "--max-fee-per-gas-wei", "2000000000"]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(guard.main(args), 0)
            self.assertEqual(guard.main(args[:4] + ["2"] + args[5:]), 1)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            guard.main(["--demo", D.demo_transaction()])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
