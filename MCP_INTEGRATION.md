# 麦当劳 MCP 接入说明

实际使用官方远程服务 `https://mcp.mcd.cn`，通过 Streamable HTTP 连接，Token 仅从用户运行环境注入。官方指南：[M-China/mcd-mcp-server](https://github.com/M-China/mcd-mcp-server)。

## 调用流程与价值

1. `query-nearby-stores`：使用用户明确的城市、位置和取餐渠道选择真实门店。
2. `query-meals` / `query-meal-detail`：读取当前菜单、编码、套餐组成和选配，供模型结合预算与人数规划。
3. `query-store-coupons`：核验门店/渠道可用优惠。`query-my-coupons` 仅在需要查看用户资产或指定券时使用，不能用它替代适用性检查。
4. `calculate-price`：对候选整单核验实际金额，避免参考价、优惠叠加或元/分换算造成错误。
5. Skill 汇总方案、约束和调用依据；有真实traceId时保留它与对应结论的联系。

应用保留从研究版迁移出的状态判断、硬性要求与偏好区分、证据关联和输出自检。真实接口可能没有某些合成属性或固定错误码，无法确认的内容保持未知。所有业务标识从工具返回提取。

## 可独立运行的入口

`scripts/mcd_mcp.py` 使用官方 MCP Python SDK，支持工具发现与六项查询/计价工具，传输层拒绝其他工具；端点限制为官方域名。`scripts/read_only_demo.py` 依次验证门店、菜单、门店券、单品详情和报价，不调用大模型、不下单、不改变账户。正常 Skill 执行由用户选择的 AI 客户端完成。

2026-10-13 的真实验证已成功，公开证据：[docs/live-verification.json](docs/live-verification.json)。该摘要只披露工具名、成功和报价类型，未发布响应原文、账户信息、券ID、门店/trace标识或凭据。此次验证是实时接口链路检查，不代表完整自然语言配餐的成功率。

## 配置

`mcp-config.example.json` 只含环境变量占位符。支持变量展开的客户端可直接引用；其他客户端使用本机生成的 `.local/mcp.json`。凭据文件不进入版本控制。仓库未使用真实账户数据作为测试夹具。
