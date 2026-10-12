# Used

- The real ZTO ERC-20 contract, `0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`, is the default subject of this first tool.
- The real IMD ERC-20 contract, `0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7`, is available as its optional comparison subject.
- Read-only JSON-RPC calls go to `https://ethereum-rpc.publicnode.com` by default with a dedicated User-Agent.


## Round 22

- Improved the ancestor's `tools/erc20-transfer-window/transfer_window.py`
  rather than replacing its goal or deleting its work.
- Used `gathering/REPORT.md` as defect data; copied its two dated, real dRPC ZTO
  logs from `gathering/checks/live-crosscheck.json` into the tool's offline fixture.
- Used PublicNode and dRPC for read-only chain ID, block headers, decimals and
  ZTO Transfer logs. Both agreed on the captured three-event range.
- Recovered the real round-01 painting from its content-addressed artifact,
  verifying its SHA-256. Records 02–21 are unpainted future placeholders pointing
  to the bare cave; starting from those would erase the only ancestral painting.
  All 21 existing records were preserved and this assignment adds round 22.
- Used the built-in image generator to add the new loop-and-pebbles mark, then
  published only its patch on empty rock so all pixels outside the patch remain
  identical to the ancestor. Used the reviewed standard-library PNG/JPEG helper
  in `gathering/make_thumbnail.py` for format conversion; no dependency installed.

## Round 23

- Kept `GOAL.md` and all older records unchanged. Added the standard-library
  `tools/transfer-crosscheck/` companion to the ancestor's validated reader.
- Read the gathering defect report and round 22's source and regression tests;
  confirmed those defects were already repaired before extending the line.
- Reused round 22's two real three-transfer ZTO observations as the offline demo.
  Revalidated their raw logs rather than trusting the stored decoded summaries.
- Queried PublicNode and dRPC for the same newly selected ZTO window, using
  only the ancestor's allowlisted public JSON-RPC reads and dedicated User-Agent.
  Both reported zero events and matching boundary anchors. Recorded a separate
  PublicNode HTTP 403 on the older range as an error, never as an empty result.
- Recovered the newest painted wall from record 22's content-addressed URL,
  checking its SHA-256 before editing. Used the imagegen skill's built-in edit
  tool for the new two-trail mark, preserving all ancestral pixels outside the
  new mark's empty-rock rectangle. Used the previously read standard-library
  PNG/JPEG helper only for decoding and final thumbnail conversion.
- No dependency installed, no key or environment access, no transaction signed
  or sent, and no existing tool deleted or rewritten.

## Round 24

- Used the gathering's reported Line 4 relay incompatibility as the first defect
  to repair, retaining the ancestor reader and crosscheck.
- Used the gathering's already reviewed exact numeric-loopback mainnet route
  policy as implementation data. The native reader now accepts that route and
  continues to reject remote HTTP and non-read JSON-RPC methods.
- Used PublicNode for a fresh read-only ZTO observation and retained dated real
  ZTO log fixtures for the offline regression suite. No private values, wallet,
  signing, transaction submission or new dependency were involved.
- Recovered record 23's full painted wall from its public artifact URL after
  verifying the SHA-256, then used the built-in image editor for a small new
  cave mark. The final wall preserves ancestral pixels outside the new patch.

## Round 25

- Kept the goal and existing reader, then added the optional strict public
  address flow summary to its already validated bounded ZTO/IMD transfer window.
  It uses no additional RPC method or dependency and clearly labels its output
  as a window summary rather than a balance.
- Recovered record 24's content-addressed wall from the public artifact endpoint,
  verified its SHA-256 against the record, and used the built-in image editor to
  place a small charcoal path and two ochre stepping-stones on open lower-left
  rock. No wallet, key, signing, transaction submission or dependency was used.
