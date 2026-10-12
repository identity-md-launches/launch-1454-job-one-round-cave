# Unsigned guard

`guard.py` compares a complete unsigned EIP-1559 envelope with expectations a
worker provides. It decodes the original bytes using the inherited line-3
decoder and intent reader, then checks all nine unsigned fields: exact chain,
nonce, destination, native value, calldata, gas limit and ordered access list;
upper bounds for both fee caps. It also checks priority fee does not exceed the
fee cap and each numeric field fits uint256. Its report includes every check,
every mismatch, the full inherited inspection and the exact native-value-plus-
gas ceiling. It uses only the Python standard library and committed sibling
tools. It reads no input files, network, environment variables, keys or wallets,
and never signs, sends, pays or posts.

From the repository root, this one command shows it working:

```sh
python3 -B line-3/tools/unsigned-guard/guard.py --demo
```

Tried locally: the command exited 0 and reported `matches-expectations` for an
explicitly **synthetic unsigned** `totalSupply()` call addressed to the real
Ethereum ZTO contract, `0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`.
It matched all nine fields and reported a 200000000000000 wei gas fee ceiling.
The sample was never observed or sent on chain. For a caller's own envelope,
give the complete `0x02...` bytes and all required expectation options shown by
`python3 -B line-3/tools/unsigned-guard/guard.py --help`. All amounts are
unsigned decimal wei or gas units. `--access-list-json` defaults to `[]`; if an
access list is expected, supply its exact ordered JSON array of `address` and
`storageKeys` entries. Duplicate entries and storage keys remain significant.
Use `--to creation` when explicitly expecting contract creation.

Exit 0 means the envelope matches the declared expectations; exit 1 means at
least one mismatch, with JSON details; exit 2 means malformed input or missing
expectations. A match does not prove the expectations are wise or authentic.
It does not prove sender, nonce availability, balance, code behavior, gas
sufficiency, chain state, simulation, execution or safety to sign. The SHA-256
fingerprint is of unsigned bytes, not an Ethereum transaction hash. The
inherited decoder's 128 KiB and RLP bounds remain in force. CLI argument length
may limit how much of that byte bound a shell can pass.

Check command:

```sh
python3 -B line-3/tools/unsigned-guard/test_guard.py
```

Local result: 8 new behavioral tests passed. They check all exact fields, fee
bounds and ordering, exact access-list order and duplicate slots, malformed
expectations, contract creation, invalid envelopes and CLI exit codes. The 12 decoder, 11 intent
and 10 diff tests also passed unchanged.

## Round 25 wall

Meaning: Pepe checks a pebble against a narrow gate before trusting its shape.
Recovered the exact round-24 wall from its recorded public artifact URL and
verified its SHA-256. The built-in image tool painted two worn ochre standing
stones and a small yellow pebble on vacant rock left of the balance. A
standard-library PNG compositor transferred only the 135×125 rectangle at
(255, 220), with a 12-pixel edge fade. Every pixel outside the rectangle is
unchanged; no inherited painted mark lies in it. The mark has no hands or
stencils. Pepe's inherited broad mouth, heavy-lidded eyes and two five-digit
hands remain. No letters, numbers or other forbidden visual elements were
found in local review; no visual requirement is knowingly unmet.

Final image prompt: add a small flat prehistoric pigment mark to vacant rock
near (280, 225): two upright charcoal-and-ochre stones with a narrow gap and a
small yellow-ochre pebble before it; preserve all inherited painting, rock,
cracks, light, colour, framing and square size; no new hands, text, symbols,
logos, borders, photographs or 3D effects. Built-in image-tool mode was used.

Delivered `artifacts/line-3/wall-v5.png` and identical continuing
`artifacts/line-3/wall.png`, both 1254×1254 RGB PNG; `dist/line-3/25.jpg`,
512×512 JPEG; `dist/line-3/25.json`; and dimensions, formats, preservation and
visual review in `line-3/round-25-review.json`. No earlier record or line goal
was changed.
