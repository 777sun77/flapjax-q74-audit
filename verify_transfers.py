"""Recheck every audited event against successful receipts and transaction fields."""
from scan import *
from concurrent.futures import ThreadPoolExecutor

def verify(t):
 h=t['tx_hash'];r=rpc('eth_getTransactionReceipt',[h]);tx=rpc('eth_getTransactionByHash',[h]);r2=rpc('eth_getTransactionReceipt',[h],RPCS[1]);tx2=rpc('eth_getTransactionByHash',[h],RPCS[1])
 assert r['status']=='0x1' and int(r['blockNumber'],16)==t['block']
 assert tx['from'].lower()==t['tx_sender'].lower()==TREASURY
 l=[l for l in r['logs']if int(l['logIndex'],16)==t['log_index']];assert len(l)==1
 assert all(l[0][k]==t['raw_log'][k]for k in ['address','topics','data','transactionHash','blockNumber','blockHash','logIndex'])
 out={'tx_hash':h,'primary_receipt':'success; event matches','second_rpc_receipt':'unavailable'if r2 is None else'matched','second_rpc_transaction':'unavailable'if tx2 is None else'matched'}
 if r2 is not None:assert r2['status']==r['status'] and r2['logs']==r['logs']
 if tx2 is not None:assert all(tx[k]==tx2[k]for k in ['hash','from','to','value','input','blockNumber'])
 return out
if __name__=='__main__':
 d=json.load(open('results.json'))
 with ThreadPoolExecutor(6)as ex:checks=list(ex.map(verify,d['transfers']))
 json.dump(checks,open('transfer_checks.json','w'),indent=2)
 print('Verified',len(checks),'successful transfer receipts; second RPC receipts',sum(c['second_rpc_receipt']=='matched'for c in checks),flush=True)
