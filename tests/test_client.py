import asyncio
import json
import os
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import mcd_mcp
from render_mcp_config import write_local_config

class Tests(unittest.TestCase):
    def test_default_endpoint_and_required_token(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError): mcd_mcp.connection_settings()
        with patch.dict(os.environ, {'MCD_MCP_TOKEN':'test-only-placeholder'}, clear=True):
            self.assertEqual(mcd_mcp.connection_settings(), ('https://mcp.mcd.cn','test-only-placeholder'))

    def test_token_cannot_be_sent_to_nonofficial_url(self):
        for url in ['http://mcp.mcd.cn','https://mcp.mcd.cn.evil.test','https://mcp.mcd.cn@evil.test',
                    'https://evil.test','https://mcp.mcd.cn/?token=x','https://mcp.mcd.cn:444',
                    'https://mcp.mcd.cn/other','https://user:pass@mcp.mcd.cn']:
            with self.subTest(url=url), patch.dict(os.environ, {'MCD_MCP_URL':url,'MCD_MCP_TOKEN':'test-only-placeholder'}, clear=True):
                with self.assertRaises(ValueError):mcd_mcp.connection_settings()

    def test_write_tools_rejected_before_session_call(self):
        class Session:
            async def call_tool(self,*args):raise AssertionError('must never reach remote call')
        for name in ['create-order','cancel-order','auto-bind-coupons','draw-lottery','delivery-create-address']:
            with self.subTest(tool=name), self.assertRaises(ValueError):
                asyncio.run(mcd_mcp.call_read_only(Session(),name,{}))

    def test_read_only_call_keeps_arguments(self):
        class Session:
            async def call_tool(self,name,args):return name,args
        args={'storeCode':'example-not-real','orderType':1,'beType':1}
        self.assertEqual(asyncio.run(mcd_mcp.call_read_only(Session(),'query-meals',args)),('query-meals',args))
        with self.assertRaises(ValueError):asyncio.run(mcd_mcp.call_read_only(Session(),'query-meals',[]))

    def test_structured_and_text_responses(self):
        data={'data':{'price':100},'traceId':'synthetic-test-only'}
        for result in [SimpleNamespace(isError=False,structuredContent=data,content=[]),
                       SimpleNamespace(isError=False,structuredContent=None,content=[SimpleNamespace(type='text',text=json.dumps(data))])]:
            self.assertEqual(mcd_mcp.business_payload(result),data)
        with self.assertRaises(ValueError):mcd_mcp.business_payload(SimpleNamespace(isError=True))
        with self.assertRaises(ValueError):mcd_mcp.business_payload(SimpleNamespace(isError=False,structuredContent=None,content=[]))

    def test_private_config_exclusive_and_mode(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ,{'MCD_MCP_TOKEN':'test-only-placeholder'},clear=True):
            result=write_local_config(root)
            self.assertEqual(result.stat().st_mode&0o777,0o600)
            self.assertEqual(json.loads(result.read_text())['mcpServers']['mcd-mcp']['headers']['Authorization'],'Bearer test-only-placeholder')
            with self.assertRaises(FileExistsError):write_local_config(root)

    def test_private_config_rejects_symlink_directory(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as other, patch.dict(os.environ,{'MCD_MCP_TOKEN':'test-only-placeholder'},clear=True):
            (Path(root)/'.local').symlink_to(other,target_is_directory=True)
            with self.assertRaises(ValueError):write_local_config(root)
            self.assertEqual(list(Path(other).iterdir()),[])

if __name__=='__main__':unittest.main()
