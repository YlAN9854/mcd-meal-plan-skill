"""Verify real store/menu/coupon-query/price access without an LLM or order creation."""
import argparse
import hashlib
import asyncio
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from mcd_mcp import connect, call_read_only, business_payload, READ_ONLY_TOOLS

async def demo(args):
    calls = []
    async def request(session, name, arguments):
        result = await call_read_only(session, name, arguments)
        data = business_payload(result)
        calls.append({'tool': name, 'tool_error': bool(result.isError),
                      'has_server_trace_id': bool(data.get('traceId'))})
        return data
    async with connect() as session:
        listed = await session.list_tools()
        available = {t.name for t in listed.tools}
        assert READ_ONLY_TOOLS <= available, 'Required read-only tool missing'
        stores = await request(session, 'query-nearby-stores',
                               {'city': args.city, 'keyword': args.keyword, 'searchType': 2, 'beType': 1})
        options = stores.get('data', [])
        if not isinstance(options, list):
            raise ValueError('Unexpected store response shape')
        open_stores = [s for s in options if s.get('businessStatus') is True and s.get('storeCode')]
        if not open_stores:
            raise ValueError('No currently open pickup store found at this demonstration location')
        channel = {'storeCode': open_stores[0]['storeCode'], 'orderType': 1, 'beType': 1}
        menu = await request(session, 'query-meals', channel)
        coupons = await request(session, 'query-store-coupons', channel)
        if not isinstance(coupons.get('data'), list):
            raise ValueError('Unexpected coupon response shape; no successful coupon-query claim')
        meals = (menu.get('data') or {}).get('meals') or {}
        if not isinstance(meals, dict):
            raise ValueError('Unexpected menu response shape')
        choices = []
        for code, meal in meals.items():
            try:
                price = Decimal(str(meal.get('currentPrice', '')))
            except InvalidOperation:
                continue
            if price.is_finite() and price > 0:
                choices.append((price, code, meal))
        quoted = None
        for _, code, meal in sorted(choices, key=lambda v:(v[0],v[1]))[:5]:
            detail = await request(session, 'query-meal-detail', {**channel, 'code': code})
            product = detail.get('data') or {}
            # This transport smoke test chooses only a simple unmodified single product.
            if product.get('rounds') or (product.get('modification') or {}).get('items'):
                continue
            quoted = await request(session, 'calculate-price',
                                   {**channel, 'items': [{'productCode': code, 'quantity': 1}]})
            amount = (quoted.get('data') or {}).get('price')
            if isinstance(amount, int) and not isinstance(amount, bool) and amount >= 0:
                break
            quoted = None
        if quoted is None:
            raise ValueError('Could not obtain a valid quote for an unmodified product within this bounded demo')
        result = {'tested_utc': datetime.now(timezone.utc).isoformat(),
                  'endpoint': 'https://mcp.mcd.cn',
                  'kind': 'real_mcp_read_only_transport_smoke',
                  'client_sha256': hashlib.sha256(Path(__file__).with_name('mcd_mcp.py').read_bytes()).hexdigest(),
                  'demo_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'discovered_tool_count': len(available),
                  'permitted_tools_present': sorted(READ_ONLY_TOOLS),
                  'calls': calls, 'business_tool_calls': len(calls),
                  'quote_received': True, 'quote_amount_type': 'integer_cents',
                  'actor_model_calls': 0, 'account_mutation_calls': 0,
                  'personal_data_published': False,
                  'scope': 'Actual authenticated read-only tool calls, not an LLM end-to-end Skill evaluation. No store/coupon/account/trace identifiers or raw responses included.'}
        if args.summary_out:
            Path(args.summary_out).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps(result, ensure_ascii=False, indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--city', required=True)
    p.add_argument('--keyword', required=True, help='A public demonstration location, not your home address')
    p.add_argument('--summary-out')
    args=p.parse_args()
    try:
        asyncio.run(demo(args))
    except Exception as error:
        print(json.dumps({'passed':False,'error_type':type(error).__name__,
                          'detail':'No success claim; raw responses and exceptions withheld. Inspect locally with the read-only CLI.'}))
        return 1
    return 0

if __name__=='__main__':
    raise SystemExit(main())
