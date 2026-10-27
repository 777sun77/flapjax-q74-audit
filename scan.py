import requests,json,time,os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone,timedelta
RPCS=['https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3','https://public-bsc.nownodes.io']
TOKEN='0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df'; TREASURY='0x7c34e9e21ee28a49ff0b84b61774119e6633359f'
TOPIC='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
def rpc(m,p,u=RPCS[0]):
 for i in range(5):
  try:
   r=requests.post(u,json={'jsonrpc':'2.0','id':1,'method':m,'params':p},timeout=45).json()
   if 'result'in r:return r['result']
   raise RuntimeError(str(r))
  except Exception:
   if i==4:raise
   time.sleep(1)
def block(b,full=False,u=RPCS[0]):return rpc('eth_getBlockByNumber',[hex(b),full],u)
def stamp(b):return int(block(b)['timestamp'],16)
def times(t):return {'utc':datetime.fromtimestamp(t,timezone.utc).isoformat(),'cot':datetime.fromtimestamp(t,timezone(timedelta(hours=-5))).isoformat()}
def dec(n):return f'{n//10**18}.{n%10**18:018d}'
def lower_bound(t,latest):
 lo,hi=max(0,latest-5_000_000),latest
 if stamp(lo)>=t:raise RuntimeError('Target predates bracket; widen search range on a node serving older headers')
 while lo<hi:
  m=(lo+hi)//2
  if stamp(m)<t:lo=m+1
  else:hi=m
 return lo
if __name__=='__main__':
 latest=int(rpc('eth_blockNumber',[]),16)
 start=int(datetime(2026,10,26,5,tzinfo=timezone.utc).timestamp());end=start+86400
 assert stamp(latest)>=end
 s=lower_bound(start,latest);e=lower_bound(end,latest)-1
 bounds=[{'block':b,'timestamp':stamp(b),**times(stamp(b))}for b in [s-1,s,e,e+1]]
 print('bounds',bounds,flush=True)
 def logs(u):
  def chunk(b):return rpc('eth_getLogs',[{'address':TOKEN,'fromBlock':hex(b),'toBlock':hex(min(e,b+4999)),'topics':[TOPIC,'0x'+'0'*24+TREASURY[2:]]}],u)
  with ThreadPoolExecutor(12)as ex:return sorted([l for ls in ex.map(chunk,range(s,e+1,5000))for l in ls],key=lambda l:(int(l['blockNumber'],16),int(l['logIndex'],16)))
 a=logs(RPCS[1]);json.dump(a,open('logs_nownodes.json','w'),indent=2);print('nownodes logs',len(a),flush=True)
 b=logs(RPCS[0]);json.dump(b,open('logs_nodereal.json','w'),indent=2);assert a==b
 for x in bounds:assert int(block(x['block'],u=RPCS[1])['timestamp'],16)==x['timestamp']
 def detail(l):
  bn=int(l['blockNumber'],16);tx=rpc('eth_getTransactionByHash',[l['transactionHash']]);addr='0x'+l['topics'][2][-40:];code=rpc('eth_getCode',[addr,hex(bn)])
  return {'tx_hash':l['transactionHash'],'block':bn,'log_index':int(l['logIndex'],16),**times(stamp(bn)),'recipient':addr,'amount_raw':str(int(l['data'],16)),'amount':dec(int(l['data'],16)),'tx_sender':tx['from'],'recipient_code':code,'is_contract':code!='0x','raw_log':l}
 with ThreadPoolExecutor(6)as ex:transfers=list(ex.map(detail,a))
 out={'token':TOKEN,'treasury':TREASURY,'rpcs':RPCS,'first_block':s,'last_block':e,'boundaries':bounds,'logs_crosscheck_equal':True,'transfers':transfers,'total_raw':str(sum(int(t['amount_raw'])for t in transfers))}
 out['total']=dec(int(out['total_raw']));out['distinct_recipients']=len(set(t['recipient']for t in transfers))
 json.dump(out,open('results.json','w'),indent=2)
 print('total',out['total'],'transfers',len(transfers),'recipients',out['distinct_recipients'],flush=True)
