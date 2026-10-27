"""Find first native funding via monotone account-activity predicate, retaining evidence.
For an ordinary EOA, (balance > 0 OR nonce > 0) remains true after first
funding even if it later spends its entire balance. Contract histories require
traces and are explicitly not certified by this search.
"""
from scan import *
from concurrent.futures import ThreadPoolExecutor

def state(a,b,u=RPCS[0]):
 return {'balance':int(rpc('eth_getBalance',[a,hex(b)],u),16),'nonce':int(rpc('eth_getTransactionCount',[a,hex(b)],u),16)}
def active(s):return s['balance']>0 or s['nonce']>0

def find(a,last):
 print('search',a,flush=True)
 lo,hi=0,last;checks=[]
 s0=state(a,0);se=state(a,last)
 if active(s0):return {'address':a,'status':'unresolved: funded at genesis','genesis_state':s0}
 if not active(se):return {'address':a,'status':'unresolved: zero balance and nonce at funding snapshot','genesis_state':s0,'snapshot_state':se,'end_state':se,'code_at_funding_snapshot':rpc('eth_getCode',[a,hex(last)])}
 while lo<hi:
  m=(lo+hi)//2;s=state(a,m);checks.append({'block':m,**s})
  if active(s):hi=m
  else:lo=m+1
 b=lo;before=state(a,b-1);after=state(a,b);code=rpc('eth_getCode',[a,hex(last)])
 out={'address':a,'candidate_first_block':b,'before':before,'after':after,'search_checks':checks,'code_at_audit_end':code}
 assert not active(before) and active(after)
 raw=block(b,True)
 if raw is None:out['status']='unresolved: candidate block unavailable';return out
 out.update(times(int(raw['timestamp'],16)))
 matches=[t for t in raw['transactions']if (t.get('to')or'').lower()==a and int(t['value'],16)>0]
 if matches:
  t=min(matches,key=lambda t:int(t['transactionIndex'],16));receipt=rpc('eth_getTransactionReceipt',[t['hash']])
  out.update({'funder':t['from'].lower(),'tx_hash':t['hash'],'block':b,'value_wei':str(int(t['value'],16)),'value_bnb':dec(int(t['value'],16)),'transaction_index':int(t['transactionIndex'],16),'receipt_status':receipt.get('status'),'transaction':t})
  out['status']='direct funding; ordinary-EOA earliest-activity search' if code=='0x' else 'candidate direct funding; contract history requires traces'
 else:
  out['status']='unresolved: internal funding or same-block activity; trace required'
  out['block_transactions']=raw['transactions']
 # Independently verify exact before/after states, funding tx and timestamp.
 other={}
 try:
  other={'before':state(a,b-1,RPCS[1]),'after':state(a,b,RPCS[1])}
  assert other['before']==before and other['after']==after
 except RuntimeError as exc:other={'historical_state_unavailable':str(exc)}
 if matches:
  tt=rpc('eth_getTransactionByHash',[out['tx_hash']],RPCS[1])
  if tt is None:other['funding_tx']='unavailable on second RPC'
  else:
   assert all(tt[k]==t[k]for k in ['hash','from','to','value','blockNumber','transactionIndex'])
   other['funding_tx']='matched'
  rr=rpc('eth_getTransactionReceipt',[out['tx_hash']],RPCS[1])
  if rr is None:other['funding_receipt']='unavailable on second RPC'
  else:assert rr['status']==receipt['status']=='0x1';other['funding_receipt']='matched success'
 out['second_rpc_crosscheck']=other
 print('found',a,b,out.get('funder'),out['status'],flush=True)
 return out
if __name__=='__main__':
 d=json.load(open('results.json'));addrs=sorted(set(t['recipient']for t in d['transfers'])|{TREASURY})
 # Fixed publication cutoff keeps reproduction independent of later funding.
 latest=130121922
 assert int(rpc('eth_blockNumber',[]),16)>=latest
 def snapshots(a):return {'address':a,'audit_end':state(a,d['last_block']),'latest':state(a,latest)}
 with ThreadPoolExecutor(5)as ex:states=list(ex.map(snapshots,addrs))
 snapshot={'latest_block':latest,**times(stamp(latest)),'states':states}
 json.dump(snapshot,open('account_states.json','w'),indent=2)
 def safe(a):
  try:return find(a,latest)
  except Exception as e:return {'address':a,'status':'unresolved: RPC failure','error':str(e)}
 with ThreadPoolExecutor(5)as ex:funders=list(ex.map(safe,addrs))
 d['first_funders']=funders;d['funding_snapshot']=snapshot
 json.dump(d,open('results.json','w'),indent=2)
