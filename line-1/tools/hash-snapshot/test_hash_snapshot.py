#!/usr/bin/env python3
"""Offline invariants and hostile-input checks, based on the retained real capture."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import hash_snapshot as tool

EXAMPLE = tool.load_json(Path(__file__).with_name('example-mainnet.json').read_bytes())
ENDPOINT = EXAMPLE['endpoint']


def envelope(result):
    return {'jsonrpc': '2.0', 'id': 1, 'result': result}


class Tests(unittest.TestCase):
    def replay(self, edit=None):
        replies = [EXAMPLE['chain_response'], envelope(EXAMPLE['anchor'])]
        replies += [row['response'] for row in EXAMPLE['observations']]
        replies += [envelope(EXAMPLE['anchor_after'])]
        replies = copy.deepcopy(replies)
        if edit:
            edit(replies)
        calls = []
        def read(method, params):
            calls.append((method, copy.deepcopy(params)))
            return replies[len(calls) - 1]
        return read, calls

    def test_real_offline_observation(self):
        with patch.object(tool, 'public_read') as network:
            summary = tool.inspect(EXAMPLE)
            self.assertEqual(summary['block_number'], str(int(EXAMPLE['anchor']['number'], 16)))
            labels = {row['label']: row for row in summary['calls']}
            self.assertEqual(labels['ZTO-supply']['decoded_uint256'], '1000000000000000000000000000')
            self.assertEqual(labels['ZTO-decimals']['decoded_uint256'], '18')
            self.assertEqual(labels['IMD-decimals']['decoded_uint256'], '18')
            network.assert_not_called()

    def test_all_calls_use_one_hash_and_canonical_flag(self):
        read, calls = self.replay()
        bundle = tool.capture(ENDPOINT, read=read)
        self.assertEqual(len(calls), 7)
        self.assertEqual(calls[0], ('eth_chainId', []))
        self.assertEqual(calls[1], ('eth_getBlockByNumber', ['finalized', False]))
        for method, params in calls[2:6]:
            self.assertEqual(method, 'eth_call')
            self.assertEqual(params[1], {'blockHash': EXAMPLE['anchor']['hash'], 'requireCanonical': True})
            self.assertEqual(set(params[0]), {'to', 'data'})
        self.assertEqual(calls[-1], ('eth_getBlockByNumber', [EXAMPLE['anchor']['number'], False]))
        self.assertEqual(tool.inspect(bundle)['calls'], tool.inspect(EXAMPLE)['calls'])

    def test_wrong_chain_stops_before_anchor_or_calls(self):
        read, calls = self.replay(lambda r: r[0].update(result='0x89'))
        with self.assertRaises(ValueError):
            tool.capture(ENDPOINT, read=read)
        self.assertEqual(len(calls), 1)

    def test_explicit_wrong_number_stops_before_calls(self):
        read, calls = self.replay()
        with self.assertRaises(ValueError):
            tool.capture(ENDPOINT, tag='0x1', read=read)
        self.assertEqual(len(calls), 2)

    def test_explicit_number_roundtrip(self):
        read, _ = self.replay()
        bundle = tool.capture(ENDPOINT, tag=EXAMPLE['anchor']['number'], read=read)
        self.assertEqual(bundle['requested_block'], EXAMPLE['anchor']['number'])
        tool.inspect(bundle)

    def test_reorg_parent_timestamp_or_number_change_rejected(self):
        for field, value in [('hash', EXAMPLE['anchor']['parentHash']), ('parentHash', EXAMPLE['anchor']['hash']),
                             ('timestamp', '0x1'), ('number', '0x1')]:
            read, _ = self.replay(lambda r: r[-1]['result'].update({field: value}))
            with self.subTest(field=field), self.assertRaises(ValueError):
                tool.capture(ENDPOINT, read=read)

    def test_invalid_plan_and_tag_before_network(self):
        bad_calls = [[], tool.DEFAULT_CALLS * 5, [tool.DEFAULT_CALLS[0]] * 2,
                     [{'label': 'x', 'to': tool.ZTO, 'data': '0x1'}],
                     [{'label': 'x', 'to': tool.ZTO, 'data': '0x', 'value': '0x1'}],
                     [{'label': 'x', 'to': tool.ZTO, 'data': '0x' + '11' * (tool.MAX_DATA + 1)}],
                     [{'label': '../outside', 'to': tool.ZTO, 'data': '0x'}]]
        with patch.object(tool, 'public_read') as network:
            for calls in bad_calls:
                with self.subTest(calls=str(calls)[:80]), self.assertRaises(ValueError):
                    tool.capture(ENDPOINT, calls=calls)
            for tag in ('pending', '0x01', '0xA', 'bad', None, []):
                with self.assertRaises(ValueError):
                    tool.capture(ENDPOINT, tag=tag)
            network.assert_not_called()

    def test_hash_reference_tampering_rejected_offline(self):
        for ref in ('latest', EXAMPLE['anchor']['number'], None, {},
                    {'blockHash': EXAMPLE['anchor']['hash'], 'requireCanonical': False},
                    {'blockHash': EXAMPLE['anchor']['hash'], 'requireCanonical': 1},
                    {'blockHash': EXAMPLE['anchor']['parentHash'], 'requireCanonical': True},
                    {'blockHash': EXAMPLE['anchor']['hash'], 'requireCanonical': True, 'blockNumber': '0x1'}):
            b = copy.deepcopy(EXAMPLE)
            b['observations'][0]['params'][1] = ref
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                tool.inspect(b)

    def test_snapshot_context_tampering_rejected(self):
        mutations = [lambda b: b.update(schema='other'), lambda b: b.update(extra=True),
                     lambda b: b.update(requested_block='0x1'), lambda b: b.update(requested_block='pending'),
                     lambda b: b.update(captured_at='2026-02-30T00:00:00Z'),
                     lambda b: b['chain_response'].update(result='0x2'),
                     lambda b: b['anchor'].update(extra=True), lambda b: b.update(anchor=None),
                     lambda b: b.update(observations=[]),
                     lambda b: b['observations'][0].update(method='eth_sendRawTransaction'),
                     lambda b: b['observations'][0]['params'][0].update(value='0x1'),
                     lambda b: b['observations'][1].update(label=b['observations'][0]['label']),
                     lambda b: b.update(endpoint='https://user:password@eth.drpc.org')]
        for mutate in mutations:
            b = copy.deepcopy(EXAMPLE)
            mutate(b)
            with self.assertRaises((ValueError, RuntimeError)):
                tool.inspect(b)

    def test_response_envelope_errors_rejected(self):
        for response in (None, [], {}, {'jsonrpc': '2.0', 'id': True, 'result': '0x'},
                         {'jsonrpc': '2.0', 'id': 2, 'result': '0x'},
                         {'jsonrpc': '2.0', 'id': 1, 'result': '0x', 'error': {}},
                         {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32000, 'message': 'unsupported hash'}},
                         {'jsonrpc': '2.0', 'id': 1, 'result': '0x', 'extra': 1}):
            b = copy.deepcopy(EXAMPLE)
            b['observations'][0]['response'] = response
            with self.assertRaises((ValueError, RuntimeError)):
                tool.inspect(b)

    def test_result_and_abi_bounds(self):
        for result in (None, '0x1', '0xgg', '0x', '0x' + '11' * (tool.MAX_RESULT + 1)):
            b = copy.deepcopy(EXAMPLE)
            b['observations'][0]['response']['result'] = result
            with self.assertRaises(ValueError):
                tool.inspect(b)
        b = copy.deepcopy(EXAMPLE)
        row = next(row for row in b['observations'] if row['label'] == 'ZTO-decimals')
        row['response']['result'] = '0x' + format(256, '064x')
        with self.assertRaises(ValueError):
            tool.inspect(b)

    def test_generic_call_retains_raw_bytes(self):
        b = copy.deepcopy(EXAMPLE)
        b['observations'] = [b['observations'][0]]
        b['observations'][0]['params'][0]['data'] = '0x'
        b['observations'][0]['response']['result'] = '0x1234'
        row = tool.inspect(b)['calls'][0]
        self.assertEqual(row['result'], '0x1234')
        self.assertNotIn('decoded_uint256', row)

    def test_json_duplicate_nonfinite_and_size_rejected(self):
        for raw in (b'{"x":1,"x":2}', b'{"a":{"x":1,"x":2}}', b'NaN', b'Infinity',
                    b' ' * (tool.MAX_INPUT + 1)):
            with self.assertRaises(ValueError):
                tool.load_json(raw)

    def test_combined_bundle_bound(self):
        read, _ = self.replay()
        with patch.object(tool, 'MAX_INPUT', 100):
            with self.assertRaisesRegex(ValueError, 'combined snapshot'):
                tool.capture(ENDPOINT, read=read)

    def test_public_read_rejects_unsafe_requests_before_opener(self):
        with patch.object(tool.urllib.request, 'build_opener') as network:
            for method, params in [('eth_sendRawTransaction', ['0x']), ('eth_gasPrice', []),
                                   ('eth_call', [{'to': tool.ZTO, 'data': '0x'}, 'latest']),
                                   ('eth_call', [{'to': tool.ZTO, 'data': '0x'}, {'blockHash': EXAMPLE['anchor']['hash'], 'requireCanonical': 1}])]:
                with self.assertRaises(ValueError):
                    tool.public_read(ENDPOINT, method, params)
            with self.assertRaises(ValueError):
                tool.public_read('https://user:password@eth.drpc.org', 'eth_chainId', [])
            network.assert_not_called()

    def test_transport_bound_and_duplicate_envelope(self):
        for raw in (b' ' * (tool.rpc.MAX_RESPONSE_BYTES + 1), b'null',
                    b'{"jsonrpc":"2.0","id":1,"result":"0x1","result":"0x2"}'):
            with patch.object(tool.urllib.request, 'build_opener') as network:
                network.return_value.open.return_value.__enter__.return_value.read.return_value = raw
                with self.assertRaises((ValueError, RuntimeError)):
                    tool.public_read(ENDPOINT, 'eth_chainId', [])

    def test_transport_has_header_no_environment_proxy_and_no_redirect(self):
        with patch.object(tool.urllib.request, 'build_opener') as network:
            network.return_value.open.return_value.__enter__.return_value.read.return_value = b'{"jsonrpc":"2.0","id":1,"result":"0x1"}'
            tool.public_read(ENDPOINT, 'eth_chainId', [])
            proxy, redirect = network.call_args.args
            self.assertEqual(proxy.proxies, {})
            self.assertIsInstance(redirect, tool.NoRedirect)
            request = network.return_value.open.call_args.args[0]
            self.assertIn('Pepeolithic-Hash-Snapshot', request.get_header('User-agent'))
            with self.assertRaises(ValueError):
                redirect.redirect_request(request, None, 302, '', {}, 'https://eth.drpc.org')

    def test_rpc_failure_no_number_fallback_or_snapshot(self):
        read, calls = self.replay(lambda r: r.__setitem__(2, {'jsonrpc': '2.0', 'id': 1,
                    'error': {'code': -32602, 'message': 'EIP-1898 unsupported'}}))
        with self.assertRaises(RuntimeError):
            tool.capture(ENDPOINT, read=read)
        self.assertEqual(len(calls), 3)

    def test_cli_offline_and_controlled_failures(self):
        for raw, code in ((json.dumps(EXAMPLE).encode(), 0), (b'null', 1), (b'{', 1),
                          (b'[]', 1), (b'[' * 2000, 1), (b' ' * (tool.MAX_INPUT + 1), 1)):
            out, err = io.StringIO(), io.StringIO()
            with patch.object(sys, 'argv', ['hash-snapshot', 'inspect']), \
                 patch.object(sys, 'stdin', io.TextIOWrapper(io.BytesIO(raw))), \
                 patch.object(tool, 'public_read') as network, \
                 contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(tool.main(), code)
                network.assert_not_called()
                if code:
                    self.assertEqual(out.getvalue(), '')
                    self.assertNotIn('Traceback', err.getvalue())

    def test_cli_capture_failure_emits_no_partial_snapshot(self):
        with patch.object(sys, 'argv', ['hash-snapshot', 'capture', '--rpc', ENDPOINT]), \
             patch.object(tool, 'public_read', side_effect=OSError('provider failed')), \
             contextlib.redirect_stdout(io.StringIO()) as out, \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(tool.main(), 1)
            self.assertEqual(out.getvalue(), '')


if __name__ == '__main__':
    unittest.main(verbosity=2)
