import unittest,time,datetime
import fundinglens
class LiveSourceTests(unittest.TestCase):
    def kraken_payload(self):return {'result':'success','serverTime':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tickers':[{'symbol':'PF_XBTUSD','relativeFundingRate':'0.00001','fundingRate':'999','openInterest':'20','suspended':False}]}
    def deribit_payload(self):return {'testnet':False,'result':[{'instrument_name':'BTC-PERPETUAL','funding_8h':'0.0002','open_interest':'2000','creation_timestamp':time.time()*1000}]}
    def test_kraken_uses_relative_not_absolute(self):self.assertEqual(fundinglens.kraken(self.kraken_payload(),'BTC')['illustrative_8h_decimal'],'0.00008')
    def test_deribit_oi_is_usd(self):self.assertEqual(fundinglens.deribit(self.deribit_payload(),'BTC')['oi_usd'],'2000')
    def test_kraken_unknown_oi_conversion_not_guessed(self):self.assertIsNone(fundinglens.kraken(self.kraken_payload(),'BTC')['oi_usd'])
    def test_no_mixed_contract_ranking(self):
        d=fundinglens.snapshot(fetch=lambda u:self.kraken_payload() if 'kraken' in u else self.deribit_payload());self.assertEqual(len(d['rows']),2);self.assertEqual(d['ranking'],[])
    def test_unavailable_source_no_fixture_fallback(self):
        def fail(u):raise TimeoutError('injected timeout')
        d=fundinglens.snapshot(fetch=fail);self.assertEqual(len(d['errors']),2);self.assertEqual(d['rows'],[])
    def test_suspended_instrument_rejected(self):
        d=self.kraken_payload();d['tickers'][0]['suspended']=True
        with self.assertRaises(ValueError):fundinglens.kraken(d,'BTC')
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):fundinglens.number('NaN')
    def test_testnet_not_reported_as_live(self):
        d=self.deribit_payload();d['testnet']=True
        with self.assertRaises(ValueError):fundinglens.deribit(d,'BTC')
if __name__=='__main__':unittest.main(verbosity=2)
