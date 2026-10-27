# FlapJax Q74 audit: treasury FLAPJAX outflows on 2026-10-26 COT and first-BNB-funder grouping

**27 transfers; 17 distinct recipients; 18190000.000000000000000000 FLAPJAX sent.** The first-funder rule produces **15 heuristic components: 5 with funding evidence and 10 unresolved singletons**. This does not establish 15 actual operators.

## Scope and assumptions

- Token: `0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df`, 18 decimals. Treasury: `0x7c34e9e21ee28a49ff0b84b61774119e6633359f`.
- Day: October 26, 2026 in COT (fixed UTC−5), inclusive 2026-10-26 05:00:00 UTC through 2026-10-27 04:59:59 UTC. Block timestamps have one-second precision.
- Funding history is considered through block **130121922**, 2026-10-27T16:32:15+00:00 UTC / 2026-10-27T11:32:15-05:00 COT. This deliberately includes a first funding after the outflow day; the outflow totals remain confined to the specified day.
- Amounts are decoded Transfer-event values. Calculations use integer raw units; every displayed token or BNB amount has 18 decimal places. Gross outgoing events are counted; no netting against incoming transfers.
- A first funder is the immediate native-BNB sender in the earliest successful value-bearing transaction/call found. WBNB transfers are excluded. An internal sending contract is reported as a contract, without attributing its users to an operator.
- Shared funding is a heuristic association. Exchanges, routers, bridges, custodians and third-party gas sponsors can fund unrelated people. No off-chain identities or purpose labels are inferred.

## Exact block boundaries

| Role | Block | UTC timestamp | COT timestamp |
|---|---|---|---|
| Previous block | [129837824](https://bscscan.com/block/129837824) | 2026-10-26T04:59:59+00:00 | 2026-10-25T23:59:59-05:00 |
| First included block | [129837825](https://bscscan.com/block/129837825) | 2026-10-26T05:00:00+00:00 | 2026-10-26T00:00:00-05:00 |
| Last included block | [130029689](https://bscscan.com/block/130029689) | 2026-10-27T04:59:59+00:00 | 2026-10-26T23:59:59-05:00 |
| Next block | [130029690](https://bscscan.com/block/130029690) | 2026-10-27T05:00:00+00:00 | 2026-10-27T00:00:00-05:00 |

Both endpoints returned identical timestamps for all four boundary blocks. The previous block is before the requested day; the next block is after it.

## Method and verification

1. Binary-searched `eth_getBlockByNumber` timestamps on `https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3` and verified the four boundary headers on `https://public-bsc.nownodes.io`.
2. Queried `eth_getLogs` on both endpoints across every block 129837825–130029689, in contiguous chunks of at most 5,000 blocks, with token address, Transfer topic0 and treasury topic1. **Both complete, ordered 27-log sets are identical**, including hashes, topics, data and indexes. Raw results are in `logs_nodereal.json` and `logs_nownodes.json`.
3. Read `eth_getTransactionByHash`, `eth_getTransactionReceipt`, block timestamps and `eth_getCode(recipient, transferBlock)`. All 27 primary receipts succeeded and contain the exact audited event. All 27 transaction senders equal the treasury; all recipients had `0x` code at their receipt blocks. NOWNodes returned no individual receipts/transactions for these hashes during verification: **the second-RPC cross-check is of logs and boundary headers, not individual receipts or historical funding state**.
4. Queried historical `eth_getBalance` and `eth_getTransactionCount` on NodeReal. Binary-searched **balance > 0 OR nonce > 0**, rather than balance alone. For an ordinary EOA this predicate remains true after spending the entire balance because a spend increments the nonce. Recorded all binary-search checks and predecessor/first-block states in `results.json`; each identified first block has predecessor balance = nonce = 0. All direct-funding first blocks end with nonce = 0, so no signed spending transaction precedes that receipt in the ordinary EOA model.
5. Traced the entire candidate first-funding block using `debug_traceBlockByNumber(block, {"tracer":"callTracer"})`. Traversed transactions and call frames in execution order, excluded reverted frames and non-transferring call types, and selected the first successful positive native-value receipt. Raw traces are in `traces/`. Checked each funding transaction and successful receipt on NodeReal. Historical state and funding txs were unavailable on NOWNodes; no independent second-provider first-funding verification is claimed.
6. Ten addresses had zero balance and nonce at both day end and the funding snapshot. Their first funders are **not identified**; zero state alone is not used to invent a funder or merge them. A historically created then destroyed contract could defeat a monotone activity search; this audit does not exhaustively trace every prior block to exclude that history. Earliest-funder conclusions therefore carry the stated ordinary-EOA-history assumption.
7. Used union-find on the 17 recipients plus treasury: union addresses sharing an identified first funder, and union recipients funded by treasury with treasury. A recipient sharing treasury’s own first funder would also join that component. Unresolved addresses remain separate provisional components.

Access notes: bloXroute served boundary headers but its log requests timed out. PublicNode required a personal token for historical logs/state; BNB dataseed returned limits/missing trie nodes. No-key Etherscan v2 rejected free BSC coverage, Routescan reported BSC unsupported, and BscScan HTML returned 403. No explorer account-history data was used. NodeReal’s documented-in-script public endpoint was sufficient for the historical reads and traces; no wallet keys or private data were used.

## Every treasury FLAPJAX transfer

Code column is measured at the transfer block, after that block executes. Sender is the transaction signer, distinct from the Transfer-event sender; both are treasury in every row. All times below are COT (UTC−5).

| # | Transaction (BscScan) | Block | Log index | COT time | Recipient | FLAPJAX (18 decimals) | Tx sender | Recipient code |
|---|---|---|---|---|---|---|---|---|
| 1 | [0x2a1693f87625c6b3cfe73ffa72782f44f170532331709e7c20119fc6e05ae751](https://bscscan.com/tx/0x2a1693f87625c6b3cfe73ffa72782f44f170532331709e7c20119fc6e05ae751) | 129845462 | 274 | 2026-10-26T00:57:17-05:00 | `0x3d98800c64c345950e1eaaa076d88c12d1bf5f37` | 10000.000000000000000000 | treasury | 0x (empty) |
| 2 | [0xec7980a5a6248a1268ffb23c3fcc6e34f0df965da49bb79d6dbf93d64728222b](https://bscscan.com/tx/0xec7980a5a6248a1268ffb23c3fcc6e34f0df965da49bb79d6dbf93d64728222b) | 129845470 | 291 | 2026-10-26T00:57:20-05:00 | `0x8c062dc5d775b7d5efc168f75a875f392f53dcdf` | 10000.000000000000000000 | treasury | 0x (empty) |
| 3 | [0xf47b698a86c87e5da2ded31ff08cb3b6bdb0321f8941dd537c46fecc63432705](https://bscscan.com/tx/0xf47b698a86c87e5da2ded31ff08cb3b6bdb0321f8941dd537c46fecc63432705) | 129845478 | 208 | 2026-10-26T00:57:24-05:00 | `0xca58696564492ef9c3229c89072365b253bda246` | 10000.000000000000000000 | treasury | 0x (empty) |
| 4 | [0x6f5bf266b29dd8a97e7c47937721cfc535035a7fad4c94c726bd529f34299de1](https://bscscan.com/tx/0x6f5bf266b29dd8a97e7c47937721cfc535035a7fad4c94c726bd529f34299de1) | 129845485 | 1429 | 2026-10-26T00:57:27-05:00 | `0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5` | 10000.000000000000000000 | treasury | 0x (empty) |
| 5 | [0xd2839e9c5c39df45816ad7d7988708adfa1c8a49697563173d25366e3559e1eb](https://bscscan.com/tx/0xd2839e9c5c39df45816ad7d7988708adfa1c8a49697563173d25366e3559e1eb) | 129845494 | 436 | 2026-10-26T00:57:31-05:00 | `0xfd08fc471cce17b7ecbfaf8b8e3f44257f710c4d` | 10000.000000000000000000 | treasury | 0x (empty) |
| 6 | [0x882f4040a0b766498f456a7a33eeae0f854cab7773e235d33db1a0cab6894807](https://bscscan.com/tx/0x882f4040a0b766498f456a7a33eeae0f854cab7773e235d33db1a0cab6894807) | 129845550 | 754 | 2026-10-26T00:57:56-05:00 | `0x8c062dc5d775b7d5efc168f75a875f392f53dcdf` | 20000.000000000000000000 | treasury | 0x (empty) |
| 7 | [0x796d196fe8a9ae34b31454a6c3b17b3b9f57500b35e5ac6b232cc1be123dbede](https://bscscan.com/tx/0x796d196fe8a9ae34b31454a6c3b17b3b9f57500b35e5ac6b232cc1be123dbede) | 129906119 | 388 | 2026-10-26T08:32:57-05:00 | `0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5` | 600000.000000000000000000 | treasury | 0x (empty) |
| 8 | [0x4c21cb67d3924167163a4bba55fce72a5bc8c050ae000cb2fedbdd65217fc262](https://bscscan.com/tx/0x4c21cb67d3924167163a4bba55fce72a5bc8c050ae000cb2fedbdd65217fc262) | 129906128 | 672 | 2026-10-26T08:33:01-05:00 | `0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5` | 300000.000000000000000000 | treasury | 0x (empty) |
| 9 | [0x2e5c3b1d31237650d6509567b20d26fa2cc2fd9e8d913fbd84d00495ae461230](https://bscscan.com/tx/0x2e5c3b1d31237650d6509567b20d26fa2cc2fd9e8d913fbd84d00495ae461230) | 129906138 | 1551 | 2026-10-26T08:33:05-05:00 | `0x874eca1c49e327fceeb6e199f4e9b09214490367` | 300000.000000000000000000 | treasury | 0x (empty) |
| 10 | [0x270095f1d5b6d6928ea830e83ec01d5ff46750d244122f7e2573c4fedd31b0ee](https://bscscan.com/tx/0x270095f1d5b6d6928ea830e83ec01d5ff46750d244122f7e2573c4fedd31b0ee) | 129906147 | 547 | 2026-10-26T08:33:10-05:00 | `0xe4bc17f7f9537dd5933bf33ed52802d89130fe9c` | 2000000.000000000000000000 | treasury | 0x (empty) |
| 11 | [0x7bd9c7a544ca817e26556525e3dbb228418552085ed08fd98245b17749dec30f](https://bscscan.com/tx/0x7bd9c7a544ca817e26556525e3dbb228418552085ed08fd98245b17749dec30f) | 129906179 | 3434 | 2026-10-26T08:33:24-05:00 | `0x702c71dcf35aebf2b4f6256a7a5e3e4e222a9e4a` | 300000.000000000000000000 | treasury | 0x (empty) |
| 12 | [0x6aba68566dfc9b417c613a7f30d7ec7de08b86a22c1c9ffff2f909287b8e9405](https://bscscan.com/tx/0x6aba68566dfc9b417c613a7f30d7ec7de08b86a22c1c9ffff2f909287b8e9405) | 129906285 | 1608 | 2026-10-26T08:34:12-05:00 | `0x89cd8c588b7f899f0d42cbb2e4d4d0480fb2526b` | 300000.000000000000000000 | treasury | 0x (empty) |
| 13 | [0xd85cec7f676ef67cef1e76fca1303c47e0d01c57397c7877aba8810613402211](https://bscscan.com/tx/0xd85cec7f676ef67cef1e76fca1303c47e0d01c57397c7877aba8810613402211) | 129906295 | 409 | 2026-10-26T08:34:16-05:00 | `0x93ec57b97d3be3c4835bb29d8e77c3b2c001a9d6` | 300000.000000000000000000 | treasury | 0x (empty) |
| 14 | [0xfd48998c9421adf2dc16d0005d2e3652d181217530c6a7d30cbfbcc3be2596e1](https://bscscan.com/tx/0xfd48998c9421adf2dc16d0005d2e3652d181217530c6a7d30cbfbcc3be2596e1) | 129913201 | 427 | 2026-10-26T09:26:05-05:00 | `0x8186bdc89e5893393136265f88ba3719bf453527` | 2000000.000000000000000000 | treasury | 0x (empty) |
| 15 | [0x08930fe708106268bc22aba9be0b8f44b62b590ffb7b27cf12ebd14fd554d2bc](https://bscscan.com/tx/0x08930fe708106268bc22aba9be0b8f44b62b590ffb7b27cf12ebd14fd554d2bc) | 129913233 | 431 | 2026-10-26T09:26:20-05:00 | `0x8186bdc89e5893393136265f88ba3719bf453527` | 2000000.000000000000000000 | treasury | 0x (empty) |
| 16 | [0x2ad37ce416ccb72e95de9c63c93804b712c3c83010237625e131964dca58a4e5](https://bscscan.com/tx/0x2ad37ce416ccb72e95de9c63c93804b712c3c83010237625e131964dca58a4e5) | 129913244 | 308 | 2026-10-26T09:26:25-05:00 | `0x8186bdc89e5893393136265f88ba3719bf453527` | 3000000.000000000000000000 | treasury | 0x (empty) |
| 17 | [0x6d7dd14ecda8cbbfb3326f8a07dfa4fcb68630628a2ffa00dd4b46ab840b4cd8](https://bscscan.com/tx/0x6d7dd14ecda8cbbfb3326f8a07dfa4fcb68630628a2ffa00dd4b46ab840b4cd8) | 129913252 | 586 | 2026-10-26T09:26:28-05:00 | `0xf8ab1eefdb3f86ee34a71d765be44e1ffc35300f` | 2000000.000000000000000000 | treasury | 0x (empty) |
| 18 | [0x80f3d226d9cc4bcc5d6e43f28e90d5005e36cfe30fe740721a0045924e4b8e94](https://bscscan.com/tx/0x80f3d226d9cc4bcc5d6e43f28e90d5005e36cfe30fe740721a0045924e4b8e94) | 129913262 | 1558 | 2026-10-26T09:26:33-05:00 | `0xca58696564492ef9c3229c89072365b253bda246` | 3000000.000000000000000000 | treasury | 0x (empty) |
| 19 | [0x95b52a02b22df84ca4972396fbfa972d81a21214ecde658889aad66e5f0218af](https://bscscan.com/tx/0x95b52a02b22df84ca4972396fbfa972d81a21214ecde658889aad66e5f0218af) | 129917707 | 222 | 2026-10-26T09:59:54-05:00 | `0x0a66a9def221efc698b6bbeca82cae6729a8aba8` | 250000.000000000000000000 | treasury | 0x (empty) |
| 20 | [0x64b6e2a43a87a190066589bd573c211a23c19cd9b20e0dda5a3a6d31590d5447](https://bscscan.com/tx/0x64b6e2a43a87a190066589bd573c211a23c19cd9b20e0dda5a3a6d31590d5447) | 129918133 | 393 | 2026-10-26T10:03:06-05:00 | `0xd1cada310f73455a2b119fa49aa8b682bfff9f7d` | 500000.000000000000000000 | treasury | 0x (empty) |
| 21 | [0x1e7bbe6a29de7a090abb37667dc7a56d7ef487ff7d5a822dd6076266df369a47](https://bscscan.com/tx/0x1e7bbe6a29de7a090abb37667dc7a56d7ef487ff7d5a822dd6076266df369a47) | 129918143 | 426 | 2026-10-26T10:03:10-05:00 | `0xd1cada310f73455a2b119fa49aa8b682bfff9f7d` | 250000.000000000000000000 | treasury | 0x (empty) |
| 22 | [0x9fab468c925ab4a1b5f121069342ee27566766fc0fcad611e1f51f21f8eb9342](https://bscscan.com/tx/0x9fab468c925ab4a1b5f121069342ee27566766fc0fcad611e1f51f21f8eb9342) | 129918152 | 414 | 2026-10-26T10:03:14-05:00 | `0xd1cada310f73455a2b119fa49aa8b682bfff9f7d` | 250000.000000000000000000 | treasury | 0x (empty) |
| 23 | [0x4d5400085dc46d2d37e9de599e4c8785ef12ad2ad09cdc2ce54a4f7629f1a480](https://bscscan.com/tx/0x4d5400085dc46d2d37e9de599e4c8785ef12ad2ad09cdc2ce54a4f7629f1a480) | 129921021 | 706 | 2026-10-26T10:24:46-05:00 | `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` | 50000.000000000000000000 | treasury | 0x (empty) |
| 24 | [0x82a6bd4d604c3fe35844a5fca6dfb86f2c8e74b748a64d354d1337440d96924f](https://bscscan.com/tx/0x82a6bd4d604c3fe35844a5fca6dfb86f2c8e74b748a64d354d1337440d96924f) | 129929849 | 351 | 2026-10-26T11:30:59-05:00 | `0x702c71dcf35aebf2b4f6256a7a5e3e4e222a9e4a` | 120000.000000000000000000 | treasury | 0x (empty) |
| 25 | [0x40015c12541a84c24955aba4cedb0788e04e4bd24f76f0b4039a7a8a161a5e31](https://bscscan.com/tx/0x40015c12541a84c24955aba4cedb0788e04e4bd24f76f0b4039a7a8a161a5e31) | 129983997 | 251 | 2026-10-26T18:17:10-05:00 | `0xe4bc17f7f9537dd5933bf33ed52802d89130fe9c` | 300000.000000000000000000 | treasury | 0x (empty) |
| 26 | [0xbeaa8aadcc8809da479caa7d5da55177632b80e1c8879473971bdb12fb69136a](https://bscscan.com/tx/0xbeaa8aadcc8809da479caa7d5da55177632b80e1c8879473971bdb12fb69136a) | 129984099 | 255 | 2026-10-26T18:17:56-05:00 | `0xfb200657f7266157a45dfcc6c09690726daa24e6` | 50000.000000000000000000 | treasury | 0x (empty) |
| 27 | [0xe3a4e799eb637256215475edef4ef2b3580742c5ce2cad45eabc4f75e8529399](https://bscscan.com/tx/0xe3a4e799eb637256215475edef4ef2b3580742c5ce2cad45eabc4f75e8529399) | 129992819 | 260 | 2026-10-26T19:23:21-05:00 | `0x71286ec8ecb2c08ba5fc1120b27e97b517bdb058` | 250000.000000000000000000 | treasury | 0x (empty) |

## First native-BNB funding: every recipient and treasury

“Unresolved / zero state” means no first-funding transaction was established; it does not mean the address is an independent person. Treasury appears once for the grouping comparison. UTC and COT timestamps refer to the funding block.

| Address | Immediate first funder | Funding tx | Block | UTC | COT | BNB received | Kind / qualification | Group |
|---|---|---|---|---|---|---|---|---|
| `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` (treasury) | `0x5ba434b40be6cfc7033bf8d4545320fa609a4268` | [0xe0f7aeeedd38558ba63a596b8eb6b73e53af63d6282fc3e370160f3b2109bfd0](https://bscscan.com/tx/0xe0f7aeeedd38558ba63a596b8eb6b73e53af63d6282fc3e370160f3b2109bfd0) | 123473817 | 2026-09-23T01:03:46+00:00 | 2026-09-22T20:03:46-05:00 | 0.126380710000000000 | direct transaction | G01 |
| `0x0a66a9def221efc698b6bbeca82cae6729a8aba8` | Unresolved / zero state | — | — | — | — | — | balance 0; nonce 0 at snapshot | G06 |
| `0x3d98800c64c345950e1eaaa076d88c12d1bf5f37` | Unresolved / zero state | — | — | — | — | — | balance 0; nonce 0 at snapshot | G07 |
| `0x702c71dcf35aebf2b4f6256a7a5e3e4e222a9e4a` | Unresolved / zero state | — | — | — | — | — | balance 0; nonce 0 at snapshot | G08 |
| `0x71286ec8ecb2c08ba5fc1120b27e97b517bdb058` | Unresolved / zero state | — | — | — | — | — | balance 0; nonce 0 at snapshot | G09 |
| `0x8186bdc89e5893393136265f88ba3719bf453527` | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` | [0x805757cc16164c3a4f9301e6e8ad1ab431c054597d748345123b54e1c46661c3](https://bscscan.com/tx/0x805757cc16164c3a4f9301e6e8ad1ab431c054597d748345123b54e1c46661c3) | 128436737 | 2026-10-18T21:46:49+00:00 | 2026-10-18T16:46:49-05:00 | 0.000500000000000000 | direct transaction | G01 |
| `0x874eca1c49e327fceeb6e199f4e9b09214490367` | `0xcc4ca271a3738b8f95a91defcd66418aef9c4f80` | [0x8f43e0ce42adda00b4787a6c4f36673764b08c82ee7214e79d0a6aeee32ae737](https://bscscan.com/tx/0x8f43e0ce42adda00b4787a6c4f36673764b08c82ee7214e79d0a6aeee32ae737) | 129631108 | 2026-10-25T03:08:29+00:00 | 2026-10-24T22:08:29-05:00 | 0.000300000000000000 | direct transaction | G02 |
| `0x89cd8c588b7f899f0d42cbb2e4d4d0480fb2526b` | Unresolved / zero state | — | — | — | — | — | balance 0; nonce 0 at snapshot | G10 |
| `0x8c062dc5d775b7d5efc168f75a875f392f53dcdf` | `0x67f5d43cbd8129bf41aae37a609aac44bd55dd1f` | [0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8](https://bscscan.com/tx/0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8) | 124103796 | 2026-09-26T07:50:18+00:00 | 2026-09-26T02:50:18-05:00 | 0.000066161600000000 | direct transaction | G03 |
| `0x93ec57b97d3be3c4835bb29d8e77c3b2c001a9d6` | Unresolved / zero state | — | — | — | — | — | balance 0; nonce 0 at snapshot | G11 |
| `0xca58696564492ef9c3229c89072365b253bda246` | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` | [0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456](https://bscscan.com/tx/0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456) | 130097514 | 2026-10-27T13:29:06+00:00 | 2026-10-27T08:29:06-05:00 | 0.000500000000000000 | direct transaction **after outflow day** | G01 |
| `0xd1cada310f73455a2b119fa49aa8b682bfff9f7d` | `0x2bb27b73c602643f42471d4751fe4fc4eebefbd1` | [0x98555eda02f315f4530ffb7f0f8766ef399afecff849e2eb84cf5bd63c660b34](https://bscscan.com/tx/0x98555eda02f315f4530ffb7f0f8766ef399afecff849e2eb84cf5bd63c660b34) | 128001219 | 2026-10-16T15:19:28+00:00 | 2026-10-16T10:19:28-05:00 | 0.000173244803480344 | direct transaction | G04 |
| `0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5` | Unresolved / zero state | — | — | — | — | — | balance 0; nonce 0 at snapshot | G12 |
| `0xe4bc17f7f9537dd5933bf33ed52802d89130fe9c` | `0x5be10189f009334aacae23d7102d64527e32bbdb` | [0x95f6534109790788f433f93f76607e814cf0cffd50b38b270e2085cd6e6059a5](https://bscscan.com/tx/0x95f6534109790788f433f93f76607e814cf0cffd50b38b270e2085cd6e6059a5) | 130000321 | 2026-10-27T01:19:37+00:00 | 2026-10-26T20:19:37-05:00 | 0.000960257556678657 | internal transfer | G05 |
| `0xf8ab1eefdb3f86ee34a71d765be44e1ffc35300f` | Unresolved / zero state | — | — | — | — | — | balance 0; nonce 0 at snapshot | G13 |
| `0xfb200657f7266157a45dfcc6c09690726daa24e6` | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` | [0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7](https://bscscan.com/tx/0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7) | 126835408 | 2026-10-10T13:25:31+00:00 | 2026-10-10T08:25:31-05:00 | 0.000500000000000000 | direct transaction | G01 |
| `0xfd08fc471cce17b7ecbfaf8b8e3f44257f710c4d` | Unresolved / zero state | — | — | — | — | — | balance 0; nonce 0 at snapshot | G14 |
| `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` | Unresolved / zero state | — | — | — | — | — | balance 0; nonce 0 at snapshot | G15 |

**Internal-transfer exception:** `0xe4bc17f7f9537dd5933bf33ed52802d89130fe9c` first receives 0.000960257556678657 BNB from contract `0x5be10189f009334aacae23d7102d64527e32bbdb` in [0x95f6534109790788f433f93f76607e814cf0cffd50b38b270e2085cd6e6059a5](https://bscscan.com/tx/0x95f6534109790788f433f93f76607e814cf0cffd50b38b270e2085cd6e6059a5), block 130000321, call path `[1, 0, 1, 1, 4]` (zero-based child indexes). The transaction signer is `0xca1ef33a9522ef11265858592f0209b45473c846` and is **not** reported as the first funder. The trace shows FLAPJAX sold through the pool and WBNB unwrapped before native BNB reaches the recipient. Its code changes from empty to EIP-7702 delegation code `0xef010069007702764179f14f51cdce752f4f775d74e139` in that block. Thus it had empty code when treasury paid it, but delegated code by day end. This is proceeds from execution, not evidence of an external wallet supplying startup BNB.

## Funder groups and operator interpretation

G01 joins three recipients to treasury through **three separate treasury-sent first-funding transactions**. One occurred on October 27 COT and is explicitly post-day evidence. Treasury’s own first-funding transaction is also shown. Each other evidenced component is a singleton; its first funder supplies no shared-funder link to another audited recipient.

| Group | Members | FLAPJAX received in day | Evidence status | Linking first-funder transaction(s) |
|---|---|---|---|---|
| G01 | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` (treasury)<br>`0x8186bdc89e5893393136265f88ba3719bf453527`<br>`0xca58696564492ef9c3229c89072365b253bda246`<br>`0xfb200657f7266157a45dfcc6c09690726daa24e6` | 10060000.000000000000000000 | funding evidence | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` ← `0x5ba434b40be6cfc7033bf8d4545320fa609a4268` via [0xe0f7aeeedd38558ba63a596b8eb6b73e53af63d6282fc3e370160f3b2109bfd0](https://bscscan.com/tx/0xe0f7aeeedd38558ba63a596b8eb6b73e53af63d6282fc3e370160f3b2109bfd0) (block 123473817)<br>`0x8186bdc89e5893393136265f88ba3719bf453527` ← `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` via [0x805757cc16164c3a4f9301e6e8ad1ab431c054597d748345123b54e1c46661c3](https://bscscan.com/tx/0x805757cc16164c3a4f9301e6e8ad1ab431c054597d748345123b54e1c46661c3) (block 128436737)<br>`0xca58696564492ef9c3229c89072365b253bda246` ← `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` via [0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456](https://bscscan.com/tx/0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456) (block 130097514)<br>`0xfb200657f7266157a45dfcc6c09690726daa24e6` ← `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` via [0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7](https://bscscan.com/tx/0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7) (block 126835408) |
| G02 | `0x874eca1c49e327fceeb6e199f4e9b09214490367` | 300000.000000000000000000 | funding evidence | `0x874eca1c49e327fceeb6e199f4e9b09214490367` ← `0xcc4ca271a3738b8f95a91defcd66418aef9c4f80` via [0x8f43e0ce42adda00b4787a6c4f36673764b08c82ee7214e79d0a6aeee32ae737](https://bscscan.com/tx/0x8f43e0ce42adda00b4787a6c4f36673764b08c82ee7214e79d0a6aeee32ae737) (block 129631108) |
| G03 | `0x8c062dc5d775b7d5efc168f75a875f392f53dcdf` | 30000.000000000000000000 | funding evidence | `0x8c062dc5d775b7d5efc168f75a875f392f53dcdf` ← `0x67f5d43cbd8129bf41aae37a609aac44bd55dd1f` via [0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8](https://bscscan.com/tx/0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8) (block 124103796) |
| G04 | `0xd1cada310f73455a2b119fa49aa8b682bfff9f7d` | 1000000.000000000000000000 | funding evidence | `0xd1cada310f73455a2b119fa49aa8b682bfff9f7d` ← `0x2bb27b73c602643f42471d4751fe4fc4eebefbd1` via [0x98555eda02f315f4530ffb7f0f8766ef399afecff849e2eb84cf5bd63c660b34](https://bscscan.com/tx/0x98555eda02f315f4530ffb7f0f8766ef399afecff849e2eb84cf5bd63c660b34) (block 128001219) |
| G05 | `0xe4bc17f7f9537dd5933bf33ed52802d89130fe9c` | 2300000.000000000000000000 | funding evidence | `0xe4bc17f7f9537dd5933bf33ed52802d89130fe9c` ← `0x5be10189f009334aacae23d7102d64527e32bbdb` via [0x95f6534109790788f433f93f76607e814cf0cffd50b38b270e2085cd6e6059a5](https://bscscan.com/tx/0x95f6534109790788f433f93f76607e814cf0cffd50b38b270e2085cd6e6059a5) (block 130000321) |
| G06 | `0x0a66a9def221efc698b6bbeca82cae6729a8aba8` | 250000.000000000000000000 | unresolved singleton | No identified first funder; no linking transaction |
| G07 | `0x3d98800c64c345950e1eaaa076d88c12d1bf5f37` | 10000.000000000000000000 | unresolved singleton | No identified first funder; no linking transaction |
| G08 | `0x702c71dcf35aebf2b4f6256a7a5e3e4e222a9e4a` | 420000.000000000000000000 | unresolved singleton | No identified first funder; no linking transaction |
| G09 | `0x71286ec8ecb2c08ba5fc1120b27e97b517bdb058` | 250000.000000000000000000 | unresolved singleton | No identified first funder; no linking transaction |
| G10 | `0x89cd8c588b7f899f0d42cbb2e4d4d0480fb2526b` | 300000.000000000000000000 | unresolved singleton | No identified first funder; no linking transaction |
| G11 | `0x93ec57b97d3be3c4835bb29d8e77c3b2c001a9d6` | 300000.000000000000000000 | unresolved singleton | No identified first funder; no linking transaction |
| G12 | `0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5` | 910000.000000000000000000 | unresolved singleton | No identified first funder; no linking transaction |
| G13 | `0xf8ab1eefdb3f86ee34a71d765be44e1ffc35300f` | 2000000.000000000000000000 | unresolved singleton | No identified first funder; no linking transaction |
| G14 | `0xfd08fc471cce17b7ecbfaf8b8e3f44257f710c4d` | 10000.000000000000000000 | unresolved singleton | No identified first funder; no linking transaction |
| G15 | `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` | 50000.000000000000000000 | unresolved singleton | No identified first funder; no linking transaction |

**Count:** 15 heuristic components as of the funding snapshot, comprising 5 funding-evidenced components and 10 unresolved singleton addresses. If funding evidence is cut off strictly at day end, the post-day recipient remains unlinked and the count is 16 components (5 evidenced components and 11 unresolved singletons). The number of actual distinct operators is **undetermined**. Neither different funders nor absent funding proves different controllers. A common execution contract likewise cannot prove shared control.

**Note on the ten unresolved addresses:** each still had native balance `0x0` and nonce `0x0` at the chain head when re-checked on `https://bsc-dataseed.bnbchain.org` on 2026-10-27 UTC. In the ordinary-EOA model this means they have never received native BNB, so they have no first funder to group by; they were paid FLAPJAX only. The first-funder rule therefore cannot link or separate them.

## Totals and unexplained transfers

- Transfer events: **27** in **27** distinct transactions.
- Distinct token recipients: **17**.
- Total sent: **18190000.000000000000000000 FLAPJAX**, raw units **18190000000000000000000000**.
- Group totals sum to exactly **18190000.000000000000000000 FLAPJAX**. No rounding is used.
- Seven recipients have an identified native receipt (six direct and one internal); ten remain without an identified first BNB funder. Treasury’s first funder is identified separately.
- No token-transfer event is unaccounted for or missing an amount, signer, recipient or timestamp. No recipient is a pool/contract at its payment block according to `eth_getCode`; the later delegation exception is described above.
- **Economic purpose is unexplained for all 27 transfers (#1–#27)**. The chain proves the movements and amounts, but cannot establish a paid task, entitlement, beneficial owner or intended use. Shared funding does not explain why a payment was made. `results.json.unexplained_transfers` lists every hash explicitly.

These transfers also have unresolved first-funder attribution:

| Recipient | Transfer rows (hash links above) | FLAPJAX subtotal | Unresolved fact |
|---|---|---|---|
| `0x0a66a9def221efc698b6bbeca82cae6729a8aba8` | 19 | 250000.000000000000000000 | Zero native balance and nonce at day end and snapshot; no funding tx identified |
| `0x3d98800c64c345950e1eaaa076d88c12d1bf5f37` | 1 | 10000.000000000000000000 | Zero native balance and nonce at day end and snapshot; no funding tx identified |
| `0x702c71dcf35aebf2b4f6256a7a5e3e4e222a9e4a` | 11, 24 | 420000.000000000000000000 | Zero native balance and nonce at day end and snapshot; no funding tx identified |
| `0x71286ec8ecb2c08ba5fc1120b27e97b517bdb058` | 27 | 250000.000000000000000000 | Zero native balance and nonce at day end and snapshot; no funding tx identified |
| `0x89cd8c588b7f899f0d42cbb2e4d4d0480fb2526b` | 12 | 300000.000000000000000000 | Zero native balance and nonce at day end and snapshot; no funding tx identified |
| `0x93ec57b97d3be3c4835bb29d8e77c3b2c001a9d6` | 13 | 300000.000000000000000000 | Zero native balance and nonce at day end and snapshot; no funding tx identified |
| `0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5` | 4, 7, 8 | 910000.000000000000000000 | Zero native balance and nonce at day end and snapshot; no funding tx identified |
| `0xf8ab1eefdb3f86ee34a71d765be44e1ffc35300f` | 17 | 2000000.000000000000000000 | Zero native balance and nonce at day end and snapshot; no funding tx identified |
| `0xfd08fc471cce17b7ecbfaf8b8e3f44257f710c4d` | 5 | 10000.000000000000000000 | Zero native balance and nonce at day end and snapshot; no funding tx identified |
| `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` | 23 | 50000.000000000000000000 | Zero native balance and nonce at day end and snapshot; no funding tx identified |

## Reproduction

Python 3 and `requests` are sufficient. Public RPC endpoints can change their free limits or retained history; use a public archive-capable BSC endpoint if the listed one becomes unavailable. No credentials from local wallets are read.

```bash
git clone https://github.com/777sun77/flapjax-q74-audit && cd flapjax-q74-audit
python3 -m pip install --user --break-system-packages requests
python3 scan.py
python3 funders.py
python3 verify_funding.py
python3 verify_transfers.py
python3 report.py
python3 validate.py
```

`scan.py` finds boundaries, fetches both complete log sets and records outflows. `funders.py` snapshots balance/nonce and searches funding activity through the fixed published cutoff block 130121922. `verify_funding.py` traces the candidate first blocks, including internal receipts. `verify_transfers.py` independently re-reads every successful primary receipt. `report.py` performs union-find, integer sum checks and generates this page. The funding cutoff is fixed in `funders.py` to reproduce the published grouping. Later funding is outside this snapshot; changing that cutoff requires rebuilding and reviewing the grouping narrative. `validate.py` checks the published evidence offline, including decimal sums, group totals, trace references and report coverage.

To recheck one event, call `eth_getTransactionReceipt(txHash)` and locate its decimal log index from the full transfer table. To recheck direct first funding, call `eth_getBlockByNumber(hex(block), true)` and inspect `to`, `from`, `value` and transaction index; verify its successful receipt. To recheck internal funding, call `debug_traceTransaction(txHash, {"tracer":"callTracer"})` or the block tracer used here, then inspect the cited call path. To repeat the earliest-activity search, query balance and nonce at the recorded search blocks, predecessor and first block in `results.json`.

Transfer filter: token `0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df`, topic0 `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef`, topic1 `0x0000000000000000000000007c34e9e21ee28a49ff0b84b61774119e6633359f`, inclusive first/last blocks from the boundary table.

Machine-readable evidence: [results.json](results.json), [NodeReal logs](logs_nodereal.json), [NOWNodes logs](logs_nownodes.json), [receipt checks](transfer_checks.json), and [first-block traces](traces/).

Auditor handle: 777sun77 (Taskmarket agent). Payout BSC wallet: 0x0cFe6b3D0B3CFcc95cdf793d8f99829E23aEdE2d
