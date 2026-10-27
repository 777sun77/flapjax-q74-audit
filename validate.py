"""Offline consistency checks on the published evidence (no RPC required)."""
import json
from decimal import Decimal, localcontext
from pathlib import Path

def main():
 d=json.load(open('results.json'));a=json.load(open('logs_nodereal.json'));b=json.load(open('logs_nownodes.json'))
 assert a==b
 ts=d['transfers'];assert len(a)==len(ts)==d['transfer_count']
 assert len({t['recipient']for t in ts})==d['distinct_recipients']
 assert len({(t['tx_hash'],t['log_index'])for t in ts})==len(ts)
 with localcontext()as ctx:
  ctx.prec=100
  assert sum(Decimal(t['amount'])for t in ts)==Decimal(d['total'])
  assert Decimal(d['total'])*10**18==int(d['total_raw'])
  assert sum(Decimal(g['total'])for g in d['groups'])==Decimal(d['total'])
 assert all(d['first_block']<=t['block']<=d['last_block']for t in ts)
 bounds=d['boundaries'];assert bounds[0]['timestamp']<bounds[1]['timestamp']==1792990800
 assert bounds[2]['timestamp']==1793077199<bounds[3]['timestamp']
 fs=d['first_funders'];assert len(fs)==len({t['recipient']for t in ts}|{d['treasury']})
 for f in fs:
  if 'funder'not in f:
   assert f['snapshot_state']=={'balance':0,'nonce':0}
   continue
  assert f['before']=={'balance':0,'nonce':0}
  assert f['receipt_status']=='0x1'
  first=f['first_block_incoming_traces'][0]
  assert first['from']==f['funder']and first['tx_hash']==f['tx_hash']and first['value_wei']==f['value_wei']
  assert Path(f'traces/{f["block"]}.json').exists()
 assert len(d['groups'])==d['group_count']
 assert sum(len(g['recipients'])for g in d['groups'])==d['distinct_recipients']
 assert len(d['unexplained_transfers'])==len(ts)
 page=Path('README.md').read_text()
 for t in ts:assert t['tx_hash']in page and t['amount']in page and t['recipient']in page
 for f in fs:
  if 'tx_hash'in f:assert f['tx_hash']in page
 assert page.rstrip().endswith('Auditor handle: 777sun77 (Taskmarket agent). Payout BSC wallet: 0x0cFe6b3D0B3CFcc95cdf793d8f99829E23aEdE2d')
 print(f'PASS: {len(ts)} transfers, {d["distinct_recipients"]} recipients, {d["total"]} FLAPJAX; blocks {d["first_block"]}–{d["last_block"]}; {d["group_count"]} provisional groups, {d["unresolved_recipient_count"]} unresolved first funders.')
if __name__=='__main__':main()
