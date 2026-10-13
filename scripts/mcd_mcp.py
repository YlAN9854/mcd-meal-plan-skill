"""Read-only command-line client for the official McDonald's China MCP server."""
from __future__ import annotations
import argparse
import asyncio
from contextlib import asynccontextmanager
import json
import os
import sys
from urllib.parse import urlsplit
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

READ_ONLY_TOOLS = frozenset({
    'query-nearby-stores', 'query-meals', 'query-meal-detail',
    'query-my-coupons', 'query-store-coupons', 'calculate-price',
})

def connection_settings():
    url = os.environ.get('MCD_MCP_URL', 'https://mcp.mcd.cn')
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname != 'mcp.mcd.cn'
            or parsed.port not in (None, 443) or parsed.username or parsed.password
            or parsed.query or parsed.fragment or parsed.path not in ('', '/')):
        raise ValueError('MCD_MCP_URL must be the official https://mcp.mcd.cn endpoint')
    token = os.environ.get('MCD_MCP_TOKEN', '').strip()
    if not token:
        raise ValueError('Set MCD_MCP_TOKEN in the environment; never put it in a file committed to Git')
    return url, token

@asynccontextmanager
async def connect():
    url, token = connection_settings()
    # A direct connection avoids inheriting an unrelated local proxy or sending credentials to it.
    factory = lambda **kw: httpx.AsyncClient(**kw, trust_env=False, follow_redirects=True)
    async with streamablehttp_client(url, headers={'Authorization': 'Bearer ' + token},
                                    timeout=30, sse_read_timeout=60,
                                    httpx_client_factory=factory) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

async def call_read_only(session, name, arguments):
    if name not in READ_ONLY_TOOLS:
        raise ValueError('This client only exposes menu, store, coupon-query and price tools')
    if not isinstance(arguments, dict):
        raise ValueError('Tool arguments must be a JSON object')
    return await session.call_tool(name, arguments)

def business_payload(result):
    if result.isError:
        raise ValueError('Official MCP returned a tool error')
    structured = getattr(result, 'structuredContent', None)
    if isinstance(structured, dict):
        return structured
    for block in result.content:
        if getattr(block, 'type', None) != 'text':
            continue
        try:
            value = json.loads(block.text)
        except (ValueError, TypeError):
            continue
        if isinstance(value, dict):
            return value
    raise ValueError('Response has no structured JSON payload; inspect it locally with the CLI')

async def run(args):
    # Validate the operation before opening an authenticated connection.
    if args.command == 'call':
        if args.tool not in READ_ONLY_TOOLS:
            raise ValueError('Tool is outside the read-only allowlist')
        if args.arguments_file:
            from pathlib import Path
            arguments = json.loads(Path(args.arguments_file).read_text())
        else:
            arguments = json.loads(args.arguments)
        if not isinstance(arguments, dict):
            raise ValueError('Tool arguments must be a JSON object')
    async with connect() as session:
        if args.command == 'tools':
            response = await session.list_tools()
            data = {'tools': [t.model_dump(mode='json', exclude_none=True)
                              for t in response.tools if t.name in READ_ONLY_TOOLS]}
        else:
            response = await call_read_only(session, args.tool, arguments)
            data = response.model_dump(mode='json', exclude_none=True)
        print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('tools', help='Discover current schemas for the six permitted tools')
    c = sub.add_parser('call', help='Call one permitted read-only tool')
    c.add_argument('tool', choices=sorted(READ_ONLY_TOOLS))
    g = c.add_mutually_exclusive_group()
    g.add_argument('--arguments', default='{}', help='JSON object; never include credentials')
    g.add_argument('--arguments-file', help='Read non-credential tool arguments from a local JSON file')
    args = p.parse_args()
    try:
        asyncio.run(run(args))
    except Exception as error:
        # SDK exceptions may contain transport metadata; do not echo them or credentials.
        print(f'MCP operation failed ({type(error).__name__}). Check the token, connection and tool arguments locally.', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
