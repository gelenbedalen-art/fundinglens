"""Read-only public venue data. No account, trading API, wallet or fixture fallback."""
import json,time,urllib.request,datetime
from decimal import Decimal,InvalidOperation
from concurrent.futures import ThreadPoolExecutor

KRAKEN='https://futures.kraken.com/derivatives/api/v3/tickers'
DERIBIT='https://www.deribit.com/api/v2/public/get_book_summary_by_instrument?instrument_name='

def number(value,positive=False):
    if value is None or type(value) is bool: raise ValueError('missing or invalid number')
    try: n=Decimal(str(value))
    except InvalidOperation: raise ValueError('invalid number')
    if not n.is_finite() or (positive and n<=0): raise ValueError('nonfinite or nonpositive number')
    return n

def kraken(payload,asset):
    symbol='PF_'+('XBT' if asset=='BTC' else 'ETH')+'USD'
    if payload.get('result')!='success': raise ValueError('Kraken upstream error')
    row=next(r for r in payload['tickers'] if r.get('symbol')==symbol)
    rate=number(row['relativeFundingRate']); oi=number(row['openInterest']); stamp=datetime.datetime.fromisoformat(payload['serverTime'].replace('Z','+00:00')).timestamp()
    if row.get('suspended'): raise ValueError('instrument suspended')
    return dict(venue='Kraken',asset=asset,symbol=symbol,contract='linear multi-collateral USD perpetual',funding_kind='current_hourly_rate',rate_decimal=str(rate),native_interval_hours=1,illustrative_8h_decimal=str(rate*8),oi_native=str(oi),oi_native_unit='native contract size; USD conversion not asserted',oi_usd=None,source_timestamp=stamp,timestamp_semantics='API response serverTime; not last-trade time or per-field observation guarantee',source_url=KRAKEN,source_field='relativeFundingRate',raw=row,notes=['8h figure is a constant-rate illustration, not settled 8h funding.','Absolute fundingRate is not a percentage and is not used as one.'])

def deribit(payload,asset):
    if payload.get('error') or payload.get('testnet') is True: raise ValueError('Deribit error or testnet response')
    symbol=asset+'-PERPETUAL'; row=next(r for r in payload['result'] if r.get('instrument_name')==symbol)
    rate=number(row['funding_8h']); oi=number(row['open_interest'])
    return dict(venue='Deribit',asset=asset,symbol=symbol,contract='inverse USD perpetual',funding_kind='projected_accumulated_8h',rate_decimal=str(rate),native_interval_hours=8,illustrative_8h_decimal=str(rate),oi_native=str(oi),oi_native_unit='USD',oi_usd=str(oi),source_timestamp=float(row['creation_timestamp'])/1000,timestamp_semantics='book summary creation_timestamp; not a settled funding timestamp',source_url=DERIBIT+symbol,source_field='funding_8h',raw=row,notes=['Projected/accumulated 8h funding is not a completed settlement.','Inverse and linear contracts are not directly ranked together.'])

def snapshot(asset='BTC',fetch=None):
    if asset not in ('BTC','ETH'): raise ValueError('unsupported asset')
    def get(url):
        req=urllib.request.Request(url,headers={'Accept':'application/json','User-Agent':'FundingLens/0.2 (read-only public market data)'})
        with urllib.request.urlopen(req,timeout=10) as r:
            raw=r.read(2000000)
            return json.loads(raw,parse_float=str)
    get=fetch or get
    def run(item):
        venue,url,parse=item
        try:
            data=get(url); r=parse(data,asset); r['fetched_at']=time.time()
            age=r['fetched_at']-r['source_timestamp']; r['source_age_seconds']=round(age,3)
            r['freshness']='fresh' if -5<=age<=120 else 'stale_or_future'
            r['comparable']=False;r['exclusion_reason']='different_funding_semantics_and_contract_types'
            if r['freshness']!='fresh': r['exclusion_reason']+=';stale_or_future'
            return {'row':r}
        except Exception as e:return {'error':{'venue':venue,'source_url':url,'message':str(e),'fixture_fallback':False}}
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(run,[('Kraken',KRAKEN,kraken),('Deribit',DERIBIT+asset+'-PERPETUAL',deribit)]))
    return dict(mode='LIVE PUBLIC API — NO FIXTURE FALLBACK',asset=asset,rows=[r['row'] for r in results if 'row' in r],errors=[r['error'] for r in results if 'error' in r],ranking=[],status='cross_venue_ranking_withheld',reason='Kraken hourly current funding and Deribit accumulated/projected funding are different contracts and measures; do not infer executable yield.',generated_at=time.time())


if __name__ == '__main__':
    import sys
    asset = sys.argv[1] if len(sys.argv) > 1 else 'BTC'
    print(json.dumps(snapshot(asset), indent=2))
