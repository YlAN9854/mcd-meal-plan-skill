# 安装与第一次使用

用 Skill 点餐，需要支持 Markdown Skill 和 Streamable HTTP MCP 的 AI 客户端，模型由你在客户端选择。本仓库还提供 Python 命令行工具，方便直接检查连接和查询结果。下面的命令示例使用 Bash 终端。

## 1. 下载项目

可以在 GitHub 页面选择 **Code → Download ZIP**，也可以克隆仓库：

```bash
git clone https://github.com/YlAN9854/mcd-meal-plan-skill.git
cd mcd-meal-plan-skill
```

## 2. 连接麦当劳 MCP

在 [麦当劳 MCP 开放平台](https://open.mcd.cn/mcp)申请个人 Token。服务地址为 `https://mcp.mcd.cn`。

以 [mcp-config.example.json](../mcp-config.example.json)作为客户端配置模板，设置 `MCD_MCP_URL` 和 `MCD_MCP_TOKEN`。环境变量由客户端读取和展开；桌面客户端需要在自己的配置或启动环境中取得这些值。

Token 仅用于你自己的设备。公开仓库、聊天记录和 Issue 中请保留变量名或占位符。

若需要运行命令行工具或生成配置文件，先安装 **Python 3.11+** 和依赖：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

下面的 Bash 命令可以隐藏输入 Token；终端里看不到字符属于正常现象：

```bash
export MCD_MCP_URL=https://mcp.mcd.cn
read -rs -p '请输入麦当劳 MCP Token：' MCD_MCP_TOKEN; printf '\n'
export MCD_MCP_TOKEN
```

如果客户端支持环境变量展开，按模板完成连接即可。如果客户端需要填写完整配置，可以运行：

```bash
python scripts/render_mcp_config.py
```

生成的 `.local/mcp.json` 含个人 Token，只供本机客户端导入。文件权限为 `0600`，目录已加入 Git 忽略列表。文件已存在时，脚本会保留原文件并退出；需要更新时，请先妥善处理旧配置，再重新生成。

## 3. 导入 Skill

按客户端的 Skill 安装方式，导入完整的 [skills/mcd-meal-plan-output](../skills/mcd-meal-plan-output/) 文件夹，并保留 `references/`。

使用能读取本地文件的编码 Agent 时，也可以明确要求它先阅读这个目录下的 `SKILL.md`，再通过已连接的 `mcd-mcp` 完成点餐请求。

告诉助手城市或位置、到店自取或得来速、人数、预算和口味。它会请你选择门店；需要机器可读结果时，可以要求同时输出 `plan.json`，字段见 [输出说明](../skills/mcd-meal-plan-output/references/output.md)。

## 4. 用命令行检查连接

以下命令需要先完成 Python 安装和环境变量配置。脚本直接连接官方服务。

```bash
python scripts/mcd_mcp.py tools
python scripts/mcd_mcp.py call query-nearby-stores --arguments '{"city":"上海","keyword":"人民广场","searchType":2,"beType":1}'
python scripts/read_only_demo.py --city 上海 --keyword 人民广场
```

第一条查看六个可用查询和计价工具；第二条搜索示例位置附近的门店；第三条从营业门店中选一个无需选配的商品，检查菜单、优惠、详情和整单报价。这些命令用于验证接口连接，配餐由 AI 助手按照 Skill 完成。

CLI 只接受这六个查询和计价工具。AI 客户端直接连接官方 MCP 时可能显示更多工具，请将当前任务限定在用餐方案；下单、领券和账户修改属于其他操作。

## 常见问题

| 情况 | 可以怎么处理 |
| --- | --- |
| 提示鉴权失败 | 在官方平台核对 Token，并检查客户端是否读到了环境变量 |
| 临时网络或服务错误 | 稍后重试，保留实际错误信息供本机排查 |
| 示例位置没有营业门店 | 改用合适的城市和公开地标重新查询 |
| 演示没有找到可直接计价的单品 | 用 CLI 查看菜单和商品详情；完整套餐可能需要填写选配参数 |
| 查到了某张券 | 继续核对当前门店、渠道和商品的适用情况 |

原始工具响应可能带有个人券信息，请在本机查看。公开分享时使用经过脱敏的摘要。
