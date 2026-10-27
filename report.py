"""Build union-find groups and the public Markdown audit using exact integer arithmetic."""
from scan import *
from collections import defaultdict

def link(h):return f'[{h}](https://bscscan.com/tx/{h})'
def addr(a):return f'`{a}`'
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,r))+' |'for r in rows])
def main():
 d=json.load(open('results.json'));d['transfer_checks']=json.load(open('transfer_checks.json'));ts=d['transfers'];fs={f['address']:f for f in d['first_funders']};rec=sorted({t['recipient']for t in ts});nodes=rec+[TREASURY];parent={a:a for a in nodes}
 def root(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 def union(a,b):parent[root(a)]=root(b)
 by=defaultdict(list)
 for a,f in fs.items():
  if f.get('funder'):by[f['funder']].append(a)
 for funder,aa in by.items():
  for a in aa[1:]:union(aa[0],a)
  if funder==TREASURY:
   for a in aa:union(TREASURY,a)
 comps=defaultdict(list)
 for a in nodes:comps[root(a)].append(a)
 ordered=sorted(comps.values(),key=lambda aa:(TREASURY not in aa,not any(fs[a].get('funder')for a in aa),sorted(aa)))
 groups=[]
 for i,aa in enumerate(ordered,1):
  recipients=sorted(a for a in aa if a!=TREASURY);total=sum(int(t['amount_raw'])for t in ts if t['recipient']in recipients)
  ev=[{'recipient':a,'funder':fs[a]['funder'],'tx_hash':fs[a]['tx_hash'],'block':fs[a]['block'],'funding_kind':fs[a]['funding_kind']}for a in sorted(aa)if fs[a].get('funder')]
  groups.append({'id':f'G{i:02d}','members':sorted(aa),'recipients':recipients,'total_raw':str(total),'total':dec(total),'evidence':ev,'status':'funding evidence'if ev else'unresolved singleton'})
 d['groups']=groups;d['group_count']=len(groups);d['funding_evidenced_groups']=sum(bool(g['evidence'])for g in groups);d['unresolved_recipient_count']=sum(not fs[a].get('funder')for a in rec)
 d['operator_count']={'actual':None,'heuristic_components':len(groups),'funding_evidenced_components':d['funding_evidenced_groups'],'unresolved_singletons':d['unresolved_recipient_count'],'warning':'Shared first funder is a linkage heuristic, not proof of common control; unresolved singletons are not proven separate operators.'}
 total=sum(int(t['amount_raw'])for t in ts);assert str(total)==d['total_raw'];assert sum(int(g['total_raw'])for g in groups)==total
 assert len({(t['tx_hash'],t['log_index'])for t in ts})==len(ts)==27
 assert len(rec)==17 and len(groups)==15
 snap=d['funding_snapshot'];group_for={a:g['id']for g in groups for a in g['members']}
 unresolved=[a for a in rec if not fs[a].get('funder')]
 d['unexplained_transfers']=[{'tx_hash':t['tx_hash'],'log_index':t['log_index'],'reason':'Economic purpose cannot be established from on-chain token transfer alone'+('; first BNB funder not identified'if t['recipient']in unresolved else'')}for t in ts]
 d['scope']={'cot_day':'2026-10-26','utc_start':'2026-10-26T05:00:00Z','utc_end_inclusive':'2026-10-27T04:59:59Z','funding_cutoff_block':snap['latest_block'],'funding_cutoff_utc':snap['utc'],'native_unit':'BNB','token_decimals':18}
 d['verification_limits']=['Full-day logs and boundary headers match NodeReal and NOWNodes. NOWNodes did not serve individual audited receipts or historic first-funding transactions; those were verified on NodeReal only.','Zero balance and nonce is not an exhaustive proof against historical transient contract funding and destruction. First-activity binary search relies on ordinary EOA history before activity; delegated execution is traced explicitly.','Economic purpose and actual common ownership cannot be established by first-funder matching.']
 json.dump(d,open('results.json','w'),indent=2)
 lines=['# FlapJax Q74 audit: treasury FLAPJAX outflows on 2026-10-26 COT and first-BNB-funder grouping','',f'**27 transfers; 17 distinct recipients; {d["total"]} FLAPJAX sent.** The first-funder rule produces **15 heuristic components: 5 with funding evidence and 10 unresolved singletons**. This does not establish 15 actual operators.','',
 '## Scope and assumptions','',f'- Token: {addr(TOKEN)}, 18 decimals. Treasury: {addr(TREASURY)}.',
 '- Day: October 26, 2026 in COT (fixed UTC−5), inclusive 2026-10-26 05:00:00 UTC through 2026-10-27 04:59:59 UTC. Block timestamps have one-second precision.',
 f'- Funding history is considered through block **{snap["latest_block"]}**, {snap["utc"]} UTC / {snap["cot"]} COT. This deliberately includes a first funding after the outflow day; the outflow totals remain confined to the specified day.',
 '- Amounts are decoded Transfer-event values. Calculations use integer raw units; every displayed token or BNB amount has 18 decimal places. Gross outgoing events are counted; no netting against incoming transfers.',
 '- A first funder is the immediate native-BNB sender in the earliest successful value-bearing transaction/call found. WBNB transfers are excluded. An internal sending contract is reported as a contract, without attributing its users to an operator.',
 '- Shared funding is a heuristic association. Exchanges, routers, bridges, custodians and third-party gas sponsors can fund unrelated people. No off-chain identities or purpose labels are inferred.','',
 '## Exact block boundaries','',table(['Role','Block','UTC timestamp','COT timestamp'],[[role,f'[{b["block"]}](https://bscscan.com/block/{b["block"]})',b['utc'],b['cot']]for role,b in zip(['Previous block','First included block','Last included block','Next block'],d['boundaries'])]),'',
 'Both endpoints returned identical timestamps for all four boundary blocks. The previous block is before the requested day; the next block is after it.','',
 '## Method and verification','',
 f'1. Binary-searched `eth_getBlockByNumber` timestamps on `{RPCS[0]}` and verified the four boundary headers on `{RPCS[1]}`.',
 f'2. Queried `eth_getLogs` on both endpoints across every block {d["first_block"]}–{d["last_block"]}, in contiguous chunks of at most 5,000 blocks, with token address, Transfer topic0 and treasury topic1. **Both complete, ordered 27-log sets are identical**, including hashes, topics, data and indexes. Raw results are in `logs_nodereal.json` and `logs_nownodes.json`.',
 f'3. Read `eth_getTransactionByHash`, `eth_getTransactionReceipt`, block timestamps and `eth_getCode(recipient, transferBlock)`. All 27 primary receipts succeeded and contain the exact audited event. All 27 transaction senders equal the treasury; all recipients had `0x` code at their receipt blocks. NOWNodes returned no individual receipts/transactions for these hashes during verification: **the second-RPC cross-check is of logs and boundary headers, not individual receipts or historical funding state**.',
 '4. Queried historical `eth_getBalance` and `eth_getTransactionCount` on NodeReal. Binary-searched **balance > 0 OR nonce > 0**, rather than balance alone. For an ordinary EOA this predicate remains true after spending the entire balance because a spend increments the nonce. Recorded all binary-search checks and predecessor/first-block states in `results.json`; each identified first block has predecessor balance = nonce = 0. All direct-funding first blocks end with nonce = 0, so no signed spending transaction precedes that receipt in the ordinary EOA model.',
 '5. Traced the entire candidate first-funding block using `debug_traceBlockByNumber(block, {"tracer":"callTracer"})`. Traversed transactions and call frames in execution order, excluded reverted frames and non-transferring call types, and selected the first successful positive native-value receipt. Raw traces are in `traces/`. Checked each funding transaction and successful receipt on NodeReal. Historical state and funding txs were unavailable on NOWNodes; no independent second-provider first-funding verification is claimed.',
 '6. Ten addresses had zero balance and nonce at both day end and the funding snapshot. Their first funders are **not identified**; zero state alone is not used to invent a funder or merge them. A historically created then destroyed contract could defeat a monotone activity search; this audit does not exhaustively trace every prior block to exclude that history. Earliest-funder conclusions therefore carry the stated ordinary-EOA-history assumption.',
 '7. Used union-find on the 17 recipients plus treasury: union addresses sharing an identified first funder, and union recipients funded by treasury with treasury. A recipient sharing treasury’s own first funder would also join that component. Unresolved addresses remain separate provisional components.',
 '', 'Access notes: bloXroute served boundary headers but its log requests timed out. PublicNode required a personal token for historical logs/state; BNB dataseed returned limits/missing trie nodes. No-key Etherscan v2 rejected free BSC coverage, Routescan reported BSC unsupported, and BscScan HTML returned 403. No explorer account-history data was used. NodeReal’s documented-in-script public endpoint was sufficient for the historical reads and traces; no wallet keys or private data were used.',
 '', '## Every treasury FLAPJAX transfer','',
 'Code column is measured at the transfer block, after that block executes. Sender is the transaction signer, distinct from the Transfer-event sender; both are treasury in every row. All times below are COT (UTC−5).','',
 table(['#','Transaction (BscScan)','Block','Log index','COT time','Recipient','FLAPJAX (18 decimals)','Tx sender','Recipient code'],[[i,link(t['tx_hash']),t['block'],t['log_index'],t['cot'],addr(t['recipient']),t['amount'],'treasury','0x (empty)']for i,t in enumerate(ts,1)]),'',
 '## First native-BNB funding: every recipient and treasury','',
 '“Unresolved / zero state” means no first-funding transaction was established; it does not mean the address is an independent person. Treasury appears once for the grouping comparison. UTC and COT timestamps refer to the funding block.','']
 rows=[]
 for a in [TREASURY]+rec:
  f=fs[a]
  if f.get('funder'):
   kind=f['funding_kind']+(' **after outflow day**'if f['block']>d['last_block']else'')
   rows.append([addr(a)+(' (treasury)'if a==TREASURY else''),addr(f['funder']),link(f['tx_hash']),f['block'],f['utc'],f['cot'],f['value_bnb'],kind,group_for[a]])
  else:rows.append([addr(a),'Unresolved / zero state','—','—','—','—','—','balance 0; nonce 0 at snapshot',group_for[a]])
 lines += [table(['Address','Immediate first funder','Funding tx','Block','UTC','COT','BNB received','Kind / qualification','Group'],rows),'']
 internal=next(f for f in fs.values()if f.get('funding_kind')=='internal transfer')
 lines += [f'**Internal-transfer exception:** {addr(internal["address"])} first receives {internal["value_bnb"]} BNB from contract {addr(internal["funder"])} in {link(internal["tx_hash"])}, block {internal["block"]}, call path `{internal["trace_path"]}` (zero-based child indexes). The transaction signer is {addr(internal["tx_sender"])} and is **not** reported as the first funder. The trace shows FLAPJAX sold through the pool and WBNB unwrapped before native BNB reaches the recipient. Its code changes from empty to EIP-7702 delegation code `{internal["address_code_after_funding"]}` in that block. Thus it had empty code when treasury paid it, but delegated code by day end. This is proceeds from execution, not evidence of an external wallet supplying startup BNB.', '',
 '## Funder groups and operator interpretation','',
 'G01 joins three recipients to treasury through **three separate treasury-sent first-funding transactions**. One occurred on October 27 COT and is explicitly post-day evidence. Treasury’s own first-funding transaction is also shown. Each other evidenced component is a singleton; its first funder supplies no shared-funder link to another audited recipient.','']
 grows=[]
 for g in groups:
  evidence='<br>'.join(addr(e['recipient'])+' ← '+addr(e['funder'])+' via '+link(e['tx_hash'])+f' (block {e["block"]})'for e in g['evidence'])or'No identified first funder; no linking transaction'
  grows.append([g['id'], '<br>'.join(addr(a)+(' (treasury)'if a==TREASURY else'')for a in g['members']),g['total'],g['status'],evidence])
 lines += [table(['Group','Members','FLAPJAX received in day','Evidence status','Linking first-funder transaction(s)'],grows),'',
 '**Count:** 15 heuristic components as of the funding snapshot, comprising 5 funding-evidenced components and 10 unresolved singleton addresses. If funding evidence is cut off strictly at day end, the post-day recipient remains unlinked and the count is 16 components (6 with evidence, including its unresolved singleton counted separately only as a component); more precisely, day end has 5 evidenced components and 11 unresolved singletons. The number of actual distinct operators is **undetermined**. Neither different funders nor absent funding proves different controllers. A common execution contract likewise cannot prove shared control.','',
 '## Totals and unexplained transfers','',
 f'- Transfer events: **{len(ts)}** in **{len({t["tx_hash"]for t in ts})}** distinct transactions.',f'- Distinct token recipients: **{len(rec)}**.',f'- Total sent: **{d["total"]} FLAPJAX**, raw units **{d["total_raw"]}**.',
 f'- Group totals sum to exactly **{d["total"]} FLAPJAX**. No rounding is used.',
 '- Seven recipients have an identified native receipt (six direct and one internal); ten remain without an identified first BNB funder. Treasury’s first funder is identified separately.',
 '- No token-transfer event is unaccounted for or missing an amount, signer, recipient or timestamp. No recipient is a pool/contract at its payment block according to `eth_getCode`; the later delegation exception is described above.',
 '- **Economic purpose is unexplained for all 27 transfers (#1–#27)**. The chain proves the movements and amounts, but cannot establish a paid task, entitlement, beneficial owner or intended use. Shared funding does not explain why a payment was made. `results.json.unexplained_transfers` lists every hash explicitly.',
 '', 'These transfers also have unresolved first-funder attribution:','']
 urows=[]
 for a in unresolved:
  nums=[str(i)for i,t in enumerate(ts,1)if t['recipient']==a];amount=sum(int(t['amount_raw'])for t in ts if t['recipient']==a)
  urows.append([addr(a),', '.join(nums),dec(amount),'Zero native balance and nonce at day end and snapshot; no funding tx identified'])
 lines += [table(['Recipient','Transfer rows (hash links above)','FLAPJAX subtotal','Unresolved fact'],urows),'',
 '## Reproduction','',
 'Python 3 and `requests` are sufficient. Public RPC endpoints can change their free limits or retained history; use a public archive-capable BSC endpoint if the listed one becomes unavailable. No credentials from local wallets are read.','',
 '```bash','cd /workspace/flapjax/q74','python3 -m pip install --user --break-system-packages requests','python3 scan.py','python3 funders.py','python3 verify_funding.py','python3 verify_transfers.py','python3 report.py','python3 validate.py','```','',
 '`scan.py` finds boundaries, fetches both complete log sets and records outflows. `funders.py` snapshots balance/nonce and searches funding activity through the fixed published cutoff block 130121922. `verify_funding.py` traces the candidate first blocks, including internal receipts. `verify_transfers.py` independently re-reads every successful primary receipt. `report.py` performs union-find, integer sum checks and generates this page. The funding cutoff is fixed in `funders.py` to reproduce the published grouping. Later funding is outside this snapshot; changing that cutoff requires rebuilding and reviewing the grouping narrative. `validate.py` checks the published evidence offline, including decimal sums, group totals, trace references and report coverage.','',
 'To recheck one event, call `eth_getTransactionReceipt(txHash)` and locate its decimal log index from the full transfer table. To recheck direct first funding, call `eth_getBlockByNumber(hex(block), true)` and inspect `to`, `from`, `value` and transaction index; verify its successful receipt. To recheck internal funding, call `debug_traceTransaction(txHash, {"tracer":"callTracer"})` or the block tracer used here, then inspect the cited call path. To repeat the earliest-activity search, query balance and nonce at the recorded search blocks, predecessor and first block in `results.json`.','',
 f'Transfer filter: token `{TOKEN}`, topic0 `{TOPIC}`, topic1 `0x'+ '0'*24+TREASURY[2:]+'`, inclusive first/last blocks from the boundary table.','',
 'Machine-readable evidence: [results.json](results.json), [NodeReal logs](logs_nodereal.json), [NOWNodes logs](logs_nownodes.json), [receipt checks](transfer_checks.json), and [first-block traces](traces/).','',
 'Auditor handle: 777sun77 (Taskmarket agent). Payout BSC wallet: 0x0cFe6b3D0B3CFcc95cdf793d8f99829E23aEdE2d']
 # Keep the strictly-at-day count description consistent with the actual graph.
 lines=[s.replace(' (6 with evidence, including its unresolved singleton counted separately only as a component); more precisely, day end has 5 evidenced components and 11 unresolved singletons',' (5 evidenced components and 11 unresolved singletons)')for s in lines]
 open('README.md','w').write('\n'.join(lines)+'\n')
 print(f'{len(ts)} transfers / {len(rec)} recipients / {d["total"]} FLAPJAX; {len(groups)} heuristic components, {d["unresolved_recipient_count"]} unresolved first funders.')
if __name__=='__main__':main()
