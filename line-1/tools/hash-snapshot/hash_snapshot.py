#!/usr/bin/env python3
"""Capture bounded eth_call observations at one canonical Ethereum block hash."""
import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path
import re
import sys
import urllib.request

SOURCE = Path(__file__).resolve().parents[1] / 'rpc-snapshot' / 'rpc_snapshot.py'
SPEC = importlib.util.spec_from_file_location('hash_snapshot_rpc', SOURCE)
rpc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rpc)
SCHEMA = 'ethereum-hash-snapshot/1'
MAX_INPUT = 1024 * 1024
MAX_CALLS = 16
MAX_DATA = 4096
MAX_RESULT = 65536
ZTO = '0xd782bdea4ef02a0bd391eb9089470c8080f0a68e'
IMD = '0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7'
TOKENS = {ZTO: 'ZTO', IMD: 'IMD'}
DEFAULT_CALLS = [
    {'label': token + '-supply', 'to': address, 'data': '0x18160ddd'}
    for address, token in TOKENS.items()
] + [
    {'label': token + '-decimals', 'to': address, 'data': '0x313ce567'}
    for address, token in TOKENS.items()
]
LIMITS = ('Provider observations only: hash references and requireCanonical are not '
          'cryptographic proof, independent corroboration or verified finality. The '
          'provider must implement EIP-1898 honestly. No fallback to block numbers.')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('non-finite JSON value')


def load_json(raw):
    if len(raw) > MAX_INPUT:
        raise ValueError('input exceeds 1 MiB')
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)


def check_calls(calls):
    if not isinstance(calls, list) or not 1 <= len(calls) <= MAX_CALLS:
        raise ValueError('expected 1 to 16 call descriptions')
    labels = set()
    for call in calls:
        if not isinstance(call, dict) or set(call) != {'label', 'to', 'data'}:
            raise ValueError('a call must contain only label, to and data')
        label = call['label']
        if not isinstance(label, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', label):
            raise ValueError('invalid call label')
        if label in labels:
            raise ValueError('duplicate call label')
        labels.add(label)
        rpc.validate_request('eth_call', [{'to': call['to'], 'data': call['data']}, 'latest'])
        if len(call['data']) > 2 + MAX_DATA * 2:
            raise ValueError('call data exceeds 4096 bytes')
    return calls


def quantity(value):
    return isinstance(value, str) and bool(re.fullmatch(r'0x(?:0|[1-9a-f][0-9a-f]{0,63})', value))


def identity(block):
    if not isinstance(block, dict):
        raise ValueError('missing block object')
    if not quantity(block.get('number')) or not quantity(block.get('timestamp')):
        raise ValueError('invalid block number or timestamp')
    for key in ('hash', 'parentHash'):
        if not rpc.hex_data(block.get(key), 32):
            raise ValueError('invalid block hash')
    return {key: block[key] for key in ('number', 'hash', 'parentHash', 'timestamp')}


def response_result(response):
    result = rpc.validate_response(response)
    if set(response) != {'jsonrpc', 'id', 'result'}:
        raise ValueError('unexpected JSON-RPC response fields')
    return result


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('RPC redirects are refused')


def public_read(endpoint, method, params):
    # EIP-1898 is the only extension to the ancestor's explicit request policy.
    rpc.validate_endpoint(endpoint)
    if method == 'eth_call':
        if not isinstance(params, list) or len(params) != 2:
            raise ValueError('invalid eth_call parameter count')
        rpc.validate_request(method, [params[0], 'latest'])
        ref = params[1]
        if (not isinstance(ref, dict) or set(ref) != {'blockHash', 'requireCanonical'}
                or not rpc.hex_data(ref['blockHash'], 32) or ref['requireCanonical'] is not True):
            raise ValueError('canonical block-hash reference required')
        if len(params[0].get('data', '0x')) > 2 + MAX_DATA * 2:
            raise ValueError('call data exceeds 4096 bytes')
    else:
        rpc.validate_request(method, params)
        if method not in {'eth_chainId', 'eth_getBlockByNumber'}:
            raise ValueError('method outside hash-snapshot read policy')
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode()
    request = urllib.request.Request(endpoint, data=body, headers={
        'Content-Type': 'application/json', 'User-Agent': 'Pepeolithic-Hash-Snapshot/1.0'})
    # Do not discover proxies from environment variables; no redirects to other endpoints.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=20) as response:
        raw = response.read(rpc.MAX_RESPONSE_BYTES + 1)
    if len(raw) > rpc.MAX_RESPONSE_BYTES:
        raise ValueError('RPC response exceeds 4 MiB')
    response = json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)
    response_result(response)
    return response


def capture(endpoint, tag='finalized', calls=None, read=None):
    rpc.validate_endpoint(endpoint)
    if not rpc.block_tag(tag) or tag == 'pending':
        raise ValueError('stable block tag or explicit number required')
    if tag.startswith('0x') and not quantity(tag):
        raise ValueError('canonical block number required')
    calls = check_calls(DEFAULT_CALLS if calls is None else calls)
    read = read or (lambda method, params: public_read(endpoint, method, params))
    chain = read('eth_chainId', [])
    if response_result(chain) != '0x1':
        raise ValueError('Ethereum mainnet chain ID 0x1 required')
    anchor = identity(response_result(read('eth_getBlockByNumber', [tag, False])))
    if tag.startswith('0x') and anchor['number'] != tag:
        raise ValueError('provider returned wrong requested block number')
    ref = {'blockHash': anchor['hash'], 'requireCanonical': True}
    observations = []
    for call in calls:
        params = [{'to': call['to'], 'data': call['data']}, dict(ref)]
        response = read('eth_call', params)
        observations.append({'label': call['label'], 'method': 'eth_call',
                             'params': params, 'response': response})
        validate_observation(observations[-1], ref)
    after = identity(response_result(read('eth_getBlockByNumber', [anchor['number'], False])))
    if anchor != after:
        raise ValueError('block identity changed; discard capture')
    bundle = {'schema': SCHEMA, 'endpoint': endpoint,
              'captured_at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
              'requested_block': tag, 'chain_response': chain, 'anchor': anchor,
              'anchor_after': after, 'observations': observations}
    inspect(bundle)
    if len(json.dumps(bundle, indent=2, sort_keys=True).encode()) + 1 > MAX_INPUT:
        raise ValueError('combined snapshot exceeds 1 MiB')
    return bundle


def validate_observation(row, ref):
    if not isinstance(row, dict) or set(row) != {'label', 'method', 'params', 'response'}:
        raise ValueError('invalid observation fields')
    if row['method'] != 'eth_call' or not isinstance(row['params'], list) or len(row['params']) != 2:
        raise ValueError('only hash-pinned eth_call observations supported')
    if row['params'][1] != ref or row['params'][1].get('requireCanonical') is not True:
        raise ValueError('observation is not pinned to the canonical anchor hash')
    call = row['params'][0]
    if not isinstance(call, dict) or set(call) != {'to', 'data'}:
        raise ValueError('invalid call fields')
    check_calls([{'label': row['label'], **call}])
    result = response_result(row['response'])
    if not rpc.hex_data(result) or len(result) > 2 + MAX_RESULT * 2:
        raise ValueError('call result must be hex bytes at most 64 KiB')
    summary = {'label': row['label'], 'to': call['to'], 'data': call['data'], 'result': result}
    token = TOKENS.get(call['to'].lower())
    if token and call['data'] in {'0x18160ddd', '0x313ce567'}:
        if not rpc.hex_data(result, 32):
            raise ValueError('known token call requires one ABI word')
        value = int(result, 16)
        if call['data'] == '0x313ce567' and value > 255:
            raise ValueError('decimals result is outside uint8')
        summary.update(token=token, decoded_uint256=str(value),
                       meaning='totalSupply base units' if call['data'] == '0x18160ddd' else 'decimals')
    return summary


def inspect(bundle):
    expected = {'schema', 'endpoint', 'captured_at', 'requested_block', 'chain_response',
                'anchor', 'anchor_after', 'observations'}
    if not isinstance(bundle, dict) or set(bundle) != expected or bundle['schema'] != SCHEMA:
        raise ValueError('invalid snapshot schema or fields')
    rpc.validate_endpoint(bundle['endpoint'])
    stamp = bundle['captured_at']
    if not isinstance(stamp, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', stamp):
        raise ValueError('canonical UTC capture time required')
    dt.datetime.strptime(stamp, '%Y-%m-%dT%H:%M:%SZ')
    if response_result(bundle['chain_response']) != '0x1':
        raise ValueError('Ethereum mainnet chain ID 0x1 required')
    anchor = identity(bundle['anchor'])
    if set(bundle['anchor']) != set(anchor) or bundle['anchor_after'] != anchor:
        raise ValueError('invalid or changed block identity')
    tag = bundle['requested_block']
    if not rpc.block_tag(tag) or tag == 'pending':
        raise ValueError('invalid requested block')
    if tag.startswith('0x') and tag != anchor['number']:
        raise ValueError('requested block differs from anchor')
    rows = bundle['observations']
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_CALLS:
        raise ValueError('expected 1 to 16 observations')
    ref = {'blockHash': anchor['hash'], 'requireCanonical': True}
    summaries = [validate_observation(row, ref) for row in rows]
    if len({row['label'] for row in summaries}) != len(summaries):
        raise ValueError('duplicate observation label')
    return {'schema': SCHEMA + '-summary', 'chain_id': '1', 'endpoint': bundle['endpoint'],
            'captured_at': stamp, 'block_number': str(int(anchor['number'], 16)),
            'block_hash': anchor['hash'], 'calls': summaries, 'evidence_limits': LIMITS}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    cap = sub.add_parser('capture', help='read-only network capture; JSON to stdout')
    cap.add_argument('--rpc', required=True, help='worker relay or credential-free public HTTPS')
    cap.add_argument('--block', default='finalized')
    cap.add_argument('--calls-stdin', action='store_true', help='read call descriptions from stdin')
    sub.add_parser('inspect', help='offline, snapshot on stdin')
    sub.add_parser('demo', help='offline inspection of retained real ZTO/IMD observations')
    args = parser.parse_args()
    try:
        if args.command == 'capture':
            calls = load_json(sys.stdin.buffer.read(MAX_INPUT + 1)) if args.calls_stdin else None
            output = capture(args.rpc, args.block, calls)
        else:
            raw = ((Path(__file__).resolve().parent / 'example-mainnet.json').read_bytes()
                   if args.command == 'demo' else sys.stdin.buffer.read(MAX_INPUT + 1))
            output = inspect(load_json(raw))
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (ValueError, TypeError, KeyError, RuntimeError, OSError, RecursionError):
        print('hash-snapshot: invalid input, inconsistent evidence, or RPC failure; no snapshot emitted',
              file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
