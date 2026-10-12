#!/usr/bin/env python3
"""Offline regressions using dated real ZTO logs and explicitly mocked RPC replies."""
import contextlib
import copy
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import transfer_window as window


FIXTURE = json.loads(Path(__file__).with_name('observed_logs.json').read_text())
LOGS = FIXTURE['logs']
FIRST = int(LOGS[0]['blockNumber'], 16)
LAST = int(LOGS[-1]['blockNumber'], 16)


class TransferTests(unittest.TestCase):
    def validate(self, logs):
        return window.validate_logs(logs, 18, window.TOKENS['zto'], FIRST, LAST)

    def test_real_logs_exact_values_sort_and_deduplication(self):
        transfers, duplicates = self.validate([LOGS[1], LOGS[0], copy.deepcopy(LOGS[0])])
        self.assertEqual(duplicates, 1)
        self.assertEqual(len(transfers), 2)
        for item, raw in zip(transfers, LOGS):
            self.assertEqual(item['raw_value'], str(int(raw['data'], 16)))
            self.assertEqual(item['block_hash'], raw['blockHash'])
            self.assertEqual(item['transaction_hash'], raw['transactionHash'])
        self.assertEqual(transfers[0]['value'], '485416.666666666666666667')

    def test_gathering_findings_and_malformed_fields_are_rejected(self):
        variants = [
            {'address': window.TOKENS['imd']},
            {'topics': [LOGS[0]['blockHash']] + LOGS[0]['topics'][1:]},
            {'blockNumber': hex(FIRST - 1)}, {'blockNumber': hex(LAST + 1)},
            {'removed': True}, {'removed': None}, {'removed': 0},
            {'data': '0x1'}, {'data': '0x' + 'f' * 66},
            {'data': '0x' + 'g' * 64}, {'data': '-0x1'},
            {'topics': LOGS[0]['topics'][:1] + ['0x' + 'g' * 64] + LOGS[0]['topics'][2:]},
            {'topics': LOGS[0]['topics'][:1] + ['0x1' + '0' * 63] + LOGS[0]['topics'][2:]},
            {'topics': LOGS[0]['topics'] + [LOGS[0]['blockHash']]},
            {'blockHash': None}, {'transactionHash': '0x1'},
            {'transactionIndex': '0x00'}, {'logIndex': '-0x1'},
            {'logIndex': '0x01'}, {'blockNumber': True},
        ]
        for changes in variants:
            with self.subTest(changes=changes), self.assertRaises(window.RpcError):
                log = copy.deepcopy(LOGS[0])
                log.update(changes)
                self.validate([log])
        for bad in (None, {}, 'logs', [None], [1], [[]]):
            with self.subTest(bad=bad), self.assertRaises(window.RpcError):
                self.validate(bad)

    def test_conflicting_duplicate_and_block_identity(self):
        for changes in ({'data': LOGS[1]['data']},
                        {'transactionHash': LOGS[1]['transactionHash']},
                        {'blockHash': LOGS[1]['blockHash']}):
            other = copy.deepcopy(LOGS[0])
            other.update(changes)
            with self.subTest(changes=changes), self.assertRaises(window.RpcError):
                self.validate([LOGS[0], other])

    def test_exact_unit_rendering(self):
        self.assertEqual(window.display_units(1, 18), '0.000000000000000001')
        self.assertEqual(window.display_units(10**18, 18), '1')
        self.assertEqual(window.display_units(0, 255), '0')
        self.assertEqual(window.display_units(2**256 - 1, 0), str(2**256 - 1))

    def test_address_summary_is_exact_and_self_transfer_is_both_directions(self):
        first = window.decode_log(LOGS[0], 18, window.TOKENS['zto'], FIRST, LAST)
        second = copy.deepcopy(first)
        second['from'] = first['to']
        second['to'] = first['to']
        second['raw_value'] = '7'
        summary = window.address_summary([first, second], first['to'], 18)
        self.assertEqual(summary['incoming_transfer_count'], 2)
        self.assertEqual(summary['outgoing_transfer_count'], 1)
        self.assertEqual(summary['matching_transfer_count'], 2)
        self.assertEqual(summary['received_raw'], str(int(first['raw_value']) + 7))
        self.assertEqual(summary['sent_raw'], '7')
        self.assertEqual(summary['net_raw'], first['raw_value'])

    def test_address_argument_is_strict(self):
        valid = '0xAbCd' + '0' * 36
        self.assertEqual(window.address(valid), valid.lower())
        for bad in ('0x' + '0' * 39, '0x' + 'g' * 40, 'alice', '', None):
            with self.subTest(bad=bad), self.assertRaises(window.argparse.ArgumentTypeError):
                window.address(bad)

    def test_decimal_and_hex_block_arguments(self):
        self.assertEqual(window.parse_block('010'), 10)
        self.assertEqual(window.parse_block('0x10'), 16)
        with self.assertRaises(window.argparse.ArgumentTypeError):
            window.parse_block(str(2**256))

    def test_limit_does_not_truncate(self):
        with patch.object(window, 'MAX_LOGS', 1), self.assertRaises(window.RpcError):
            self.validate(LOGS)


class CaptureTests(unittest.TestCase):
    def capture(self, chain='0x1', logs=None, changed=None, decimals=None, head=None, extra_args=None):
        calls = []
        seen = {}
        # Block numbers/hashes are taken from observed logs. These minimal header
        # replies simulate transport; they are not captured block-header evidence.
        anchors = {int(log['blockNumber'], 16): log['blockHash'] for log in LOGS}

        def fake_rpc(endpoint, method, params):
            calls.append((method, copy.deepcopy(params)))
            if method == 'eth_chainId': return chain
            if method == 'eth_blockNumber': return hex(LAST if head is None else head)
            if method == 'eth_call': return decimals if decimals is not None else '0x' + format(18, '064x')
            if method == 'eth_getLogs': return copy.deepcopy(LOGS if logs is None else logs)
            if method == 'eth_getBlockByNumber':
                number = int(params[0], 16)
                seen[number] = seen.get(number, 0) + 1
                block_hash = anchors[number]
                if changed == number and seen[number] > 1:
                    block_hash = anchors[FIRST if number == LAST else LAST]
                return {'number': hex(number), 'hash': block_hash}
            raise AssertionError('unexpected method: ' + method)

        output = io.StringIO()
        with patch.object(window, 'rpc', fake_rpc), contextlib.redirect_stdout(output):
            window.main(['--from-block', str(FIRST), '--to-block', str(LAST)] + (extra_args or []))
        return json.loads(output.getvalue()), calls

    def test_capture_pins_decimals_and_retains_evidence(self):
        result, calls = self.capture()
        self.assertEqual(result['chain_id'], 1)
        self.assertEqual(result['schema_version'], 3)
        self.assertEqual(result['raw_logs'], LOGS)
        self.assertEqual(result['transfer_count'], 2)
        self.assertEqual(result['decimals_block'], LAST)
        self.assertEqual([params[-1] for method, params in calls if method == 'eth_call'], [hex(LAST)])
        self.assertEqual(sum(method == 'eth_getBlockByNumber' for method, _ in calls), 4)

    def test_capture_optionally_emits_only_a_bounded_address_summary(self):
        selected = '0x' + LOGS[0]['topics'][2][-40:]
        result, _ = self.capture(extra_args=['--address', selected.upper().replace('0X', '0x')])
        summary = result['address_window_summary']
        self.assertEqual(summary['address'], selected)
        self.assertEqual(summary['matching_transfer_count'], 1)
        self.assertIn('not a token balance', summary['scope'])

    def test_empty_result_is_success_but_invalid_or_wrong_chain_is_error(self):
        result, _ = self.capture(logs=[])
        self.assertEqual(result['transfer_count'], 0)
        self.assertEqual(result['raw_logs'], [])
        for kwargs in ({'chain': '0x2'}, {'logs': {}}, {'decimals': '0x12'},
                       {'decimals': '0x' + format(256, '064x')}, {'head': FIRST}):
            with self.subTest(kwargs=kwargs), self.assertRaises(window.RpcError):
                self.capture(**kwargs)

    def test_reorg_at_either_boundary_is_error(self):
        for number in (FIRST, LAST):
            with self.subTest(number=number), self.assertRaises(window.RpcError):
                self.capture(changed=number)

    def test_boundary_log_hash_mismatch_is_error(self):
        logs = copy.deepcopy(LOGS)
        logs[0]['blockHash'] = logs[1]['blockHash']
        with self.assertRaises(window.RpcError): self.capture(logs=logs)

    def test_invalid_cli_ranges_do_not_network(self):
        for args in (['--latest-window', '0'], ['--latest-window', '2001'],
                     ['--from-block', '1'], ['--from-block', '-1', '--to-block', '2'],
                     ['--from-block', '2', '--to-block', '1'],
                     ['--from-block', '0', '--to-block', '2000']):
            with self.subTest(args=args), patch.object(window, 'rpc') as rpc:
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    window.main(args)
                rpc.assert_not_called()


class TransportTests(unittest.TestCase):
    def reply(self, payload):
        class Reply:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, limit): return json.dumps(payload).encode()
        return Reply()

    def test_invalid_envelopes_are_controlled_errors(self):
        for payload in (None, [], 3, {'result': []},
                        {'jsonrpc': '2.0', 'id': True, 'result': []},
                        {'jsonrpc': '2.0', 'id': 2, 'result': []},
                        {'jsonrpc': '2.0', 'id': 1},
                        {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32000}}):
            with self.subTest(payload=payload), patch.object(window.urllib.request, 'urlopen', return_value=self.reply(payload)):
                with self.assertRaises(window.RpcError):
                    window.rpc(window.DEFAULT_RPC, 'eth_getLogs', [])

    def test_valid_envelope_user_agent_and_read_method(self):
        with patch.object(window.urllib.request, 'urlopen', return_value=self.reply({'jsonrpc': '2.0', 'id': 1, 'result': '0x1'})) as opener:
            self.assertEqual(window.rpc(window.DEFAULT_RPC, 'eth_chainId', []), '0x1')
            request = opener.call_args.args[0]
            self.assertEqual(request.get_header('User-agent'), window.USER_AGENT)
            self.assertEqual(json.loads(request.data)['method'], 'eth_chainId')

    def test_exact_loopback_mainnet_relay_uses_same_readonly_transport(self):
        relay = 'http://127.0.0.1:44117/rpc/1'
        with patch.object(window.urllib.request, 'urlopen', return_value=self.reply({'jsonrpc': '2.0', 'id': 1, 'result': '0x1'})) as opener:
            self.assertEqual(window.rpc(relay, 'eth_chainId', []), '0x1')
            request = opener.call_args.args[0]
            self.assertEqual(request.full_url, relay)
            self.assertEqual(request.get_header('User-agent'), window.USER_AGENT)
        with patch.object(window.urllib.request, 'urlopen') as opener:
            with self.assertRaises(window.RpcError):
                window.rpc(relay, 'eth_sendRawTransaction', [])
            opener.assert_not_called()

    def test_response_limit_and_network_error(self):
        with patch.object(window, 'MAX_RESPONSE_BYTES', 1), patch.object(window.urllib.request, 'urlopen', return_value=self.reply({})):
            with self.assertRaises(window.RpcError): window.rpc(window.DEFAULT_RPC, 'eth_chainId', [])
        with patch.object(window.urllib.request, 'urlopen', side_effect=OSError('offline')):
            with self.assertRaises(window.RpcError): window.rpc(window.DEFAULT_RPC, 'eth_chainId', [])

    def test_nonread_methods_and_credential_endpoints_never_network(self):
        with patch.object(window.urllib.request, 'urlopen') as opener:
            with self.assertRaises(window.RpcError): window.rpc(window.DEFAULT_RPC, 'not_a_read', [])
            for endpoint in ('file:///workspace/data', 'http://example.org',
                             'http://127.0.0.1:44117/rpc/56',
                             'http://127.0.0.1:44117/other',
                             'http://127.0.0.1/rpc/1',
                             'http://localhost:44117/rpc/1',
                             'http://127.0.0.1:44117/rpc/1?key=value',
                             'https://user:password@example.org', 'https://example.org?key=value'):
                with self.subTest(endpoint=endpoint), self.assertRaises(window.RpcError):
                    window.rpc(endpoint, 'eth_chainId', [])
            opener.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
