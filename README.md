# 麦当劳点餐决策助手

参赛准备状态：项目与真实接口验证已就绪，报名 Issue 待参赛者确认官方规则和参赛声明后提交。

把“预算、人数、必选项、口味偏好和优惠券”整理成有真实报价依据的用餐方案。通过麦当劳官方 MCP 查询门店、菜单、餐品详情和门店适用优惠，再按完整购物车计价，说明方案是否满足你的要求。

适合有预算约束的个人或多人点餐、到店自取和得来速场景。你可以直接描述需求，例如：

> 上海人民广场附近，到店自取，两个人，预算 60 元，每人一份主食和一杯饮料。先展示门店让我选择，再结合该门店可用优惠给出方案；有无法确认的条件请告诉我。

Skill 会区分硬性要求与偏好，报告可行方案、待澄清信息或有证据的无解原因。探索不充分时会明确证据不足，不把“暂时没找到”说成“没有方案”。最终提供商品、数量、整单报价、约束检查和调用依据，以方案输出结束。

## 安装和使用

需要 Python 3.11+；使用 Skill 还需要一个支持 Markdown Skill 与 Streamable HTTP MCP 的 AI 客户端。模型由你在客户端自行选择。

```bash
git clone https://github.com/YlAN9854/mcd-meal-plan-skill.git
cd mcd-meal-plan-skill
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

1. 在 [麦当劳 MCP 开放平台](https://open.mcd.cn/mcp)申请自己的 Token。
2. 在终端设置 `MCD_MCP_URL=https://mcp.mcd.cn` 和 `MCD_MCP_TOKEN`。不要把 Token 写进仓库、聊天示例或 issue。
3. 将 [mcp-config.example.json](mcp-config.example.json)作为客户端连接配置的模板。模板变量必须由客户端展开；若客户端不支持，可运行 `python scripts/render_mcp_config.py`，将生成的本机 `.local/mcp.json` 导入客户端。该文件含凭据、权限为0600且已被 Git 忽略。
4. 按客户端的 Skill 安装方式导入完整的 [skills/mcd-meal-plan-output](skills/mcd-meal-plan-output/) 目录，保留 `references/`。在具有文件读取能力的编码 Agent 中，也可明确要求读取该目录的 `SKILL.md` 后执行点餐请求。
5. 连接 `mcd-mcp`，提出城市/位置、取餐方式、人数、预算和偏好。按提示选择真实门店；需要机器可读结果时，要求同时输出 `plan.json`，格式见 [输出说明](skills/mcd-meal-plan-output/references/output.md)。

本机保存 Token 可用不会回显输入的 Bash 命令；命令历史只包含变量名：

```bash
export MCD_MCP_URL=https://mcp.mcd.cn
read -rs -p 'MCD MCP Token: ' MCD_MCP_TOKEN; printf '\n'
export MCD_MCP_TOKEN
```

## 先验证真实接口

以下命令直接访问官方 MCP，不需要调用大模型，也不创建订单：

```bash
python scripts/mcd_mcp.py tools
python scripts/mcd_mcp.py call query-nearby-stores --arguments '{"city":"上海","keyword":"人民广场","searchType":2,"beType":1}'
python scripts/read_only_demo.py --city 上海 --keyword 人民广场
```

CLI 只允许六个查询/计价工具；价格与库存会随门店和时间变化。演示从查询结果中选择营业门店及一个无需选配的商品，核验真实整单计价链路；它不运行配餐搜索。标准客户端直接连接官方 MCP 时可能看到更多工具，Skill 的任务范围仍止于方案，不授权下单、领券或账户修改。

## 已有验证

2026-10-13 完成真实 MCP 鉴权、工具发现，以及门店 → 菜单 → 门店优惠 → 商品详情 → 整单计价的5次业务调用。全部返回，取得整数分报价；无大模型调用或账户写操作。公开摘要已移除账户、券、门店及 trace 标识：[live-verification.json](docs/live-verification.json)。

项目来自一次固定模拟场景的 Skill-only 优化。原研究版 C2 在 MiniMax 独立评估中为29/30，空 Skill 基线25/30（10题、每题3次）。当前入口已按真实 MCP 适配，原研究版两份文件完整保存在 [research/c2](research/c2/)，二者版本及成绩范围见 [研究记录](research/README.md)。这些分数属于原研究版；真实入口目前完成工具链路检查，尚无对应的端到端大模型成功率测量。

## 项目文件

- [Skill 正文](skills/mcd-meal-plan-output/SKILL.md)：约束收集、查询、计价、解释和交付步骤。
- [MCP_INTEGRATION.md](MCP_INTEGRATION.md)：实际工具、调用流程与业务价值。
- [docs/ADAPTATION.md](docs/ADAPTATION.md)：从固定研究场景到真实接口的适配说明。
- [CONTEST_DECLARATION.md](CONTEST_DECLARATION.md)：官方原版参赛声明。

项目为独立开发的竞赛作品。餐品、价格、库存与券的适用情况以官方接口实时结果为准；未标注的营养、过敏原或库存信息保持未知。查询成功不等于订单创建或库存锁定。

代码与自编文档按 [MIT License](LICENSE)开放；原版参赛声明单独保留其官方来源。没有 WorkBuddy 开发记录，因此本项目不声明 WorkBuddy 专项资格。
