"""Trace candidate first-funding blocks to distinguish direct funding from internal proceeds."""
from funders import *
from concurrent.futures import ThreadPoolExecutor
os.makedirs('traces',exist_ok=True)
def walk(c,path=(),failed=False):
 failed=failed or bool(c.get('error'))
 yield c,path,failed
 for i,cc in enumerate(c.get('calls',[])):yield from walk(cc,path+(i,),failed)
def verify(f):
 if 'candidate_first_block'not in f:return f
 b=f['candidate_first_block'];a=f['address'];p=f'traces/{b}.json'
 if os.path.exists(p):tr=json.load(open(p))
 else:
  tr=rpc('debug_traceBlockByNumber',[hex(b),{'tracer':'callTracer'}]);json.dump(tr,open(p,'w'),indent=2)
 incoming=[]
 for idx,txtrace in enumerate(tr):
  txh=txtrace.get('txHash');root=txtrace.get('result',txtrace)
  for c,path,failed in walk(root):
   if c.get('to','').lower()==a and int(c.get('value','0x0'),16)>0 and not failed and c.get('type')not in ['DELEGATECALL','STATICCALL','CALLCODE']:
    incoming.append({'tx_hash':txh,'tx_order_in_block':idx,'trace_path':list(path),'from':c['from'].lower(),'to':a,'value_wei':str(int(c['value'],16)),'value_bnb':dec(int(c['value'],16)),'type':c.get('type')})
 f['first_block_incoming_traces']=incoming
 if not incoming:f['status']='unresolved: no successful native transfer in candidate block trace';return f
 first=incoming[0];tx=rpc('eth_getTransactionByHash',[first['tx_hash']]);receipt=rpc('eth_getTransactionReceipt',[first['tx_hash']]);assert receipt['status']=='0x1'
 f.update({'funder':first['from'],'tx_hash':first['tx_hash'],'block':b,'value_wei':first['value_wei'],'value_bnb':first['value_bnb'],'trace_path':first['trace_path'],'funding_kind':'internal transfer'if first['trace_path']else'direct transaction','tx_sender':tx['from'],'receipt_status':receipt['status'],'funding_transaction':tx})
 f['funder_code_at_funding']=rpc('eth_getCode',[f['funder'],hex(b)])
 f['address_code_before_funding']=rpc('eth_getCode',[a,hex(b-1)])
 f['address_code_after_funding']=rpc('eth_getCode',[a,hex(b)])
 f['status']='verified candidate first native receipt; '+f['funding_kind']
 f['earliest_history_basis']='Binary search balance>0 OR nonce>0; zero balance and nonce at predecessor; trace entire candidate block in transaction/execution order. Ordinary EOA assumption before activity; historical contract destruction is not exhaustively excluded.'
 print(a,b,first['from'],f['funding_kind'],first['value_bnb'],flush=True)
 return f
if __name__=='__main__':
 d=json.load(open('results.json'));fs=d['first_funders']
 with ThreadPoolExecutor(4)as ex:fs=list(ex.map(verify,fs))
 d['first_funders']=fs;d['funding_snapshot']=json.load(open('account_states.json'));json.dump(d,open('results.json','w'),indent=2)
