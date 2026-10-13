# Skill-only 研究来源

原研究版 C2 的两份 Markdown 原样保存在 `c2/`，用于溯源和方法讨论。它依赖固定合成场景和专门的 `plan.json` 契约；日常使用从根目录 `skills/mcd-meal-plan-output/` 安装提交版。

原研究固定工具/场景、runtime、评分及执行限制，仅新增或修改 Markdown Skill。开发集16题，每题R=3；同一harness先在 Kimi `kimi-for-coding` 与 MiniMax `MiniMax-M3.1-Flash-Preview` 两模型上测量。公开开发汇总如下：

| 版本 | Kimi | MiniMax |
| --- | --- | --- |
| 空Skill基线 | 13/48 | 42/48 |
| C1 | 45/48 | 43/48 |
| C2 | 48/48 | 47/48 |

开发汇总采用经授权、明确标记的事后超时评分分析：两次MiniMax超时在核验停止和原程序评分后计入原reward=0，未重跑Actor或修改原失败记录。原执行并发1。不能把这些结果视为事前登记的全新开发比较。

随后锁定C2，由独立角色在10道未用于优化的题上进行最终MiniMax评估，R=3、并发2、有效Actor180秒。基线25/30，C2 29/30，差4/30；两边无超时、错误或恢复。最终标准在看留出结果前确定：C2均值≥0.75且不低于基线。没有依据留出结果修复或重选。10题各重复3次不等于30道独立题，也不证明比赛综合能力或统计显著性。

目标累计376个Actor Trial：2接入、288正式开发、26取消前恢复、60最终评估。程序评分，无临时LLM judge；独立Pi审查与Actor分开记账。

C2 Engine content_hash：`24398d8ae7a197a7229d34bd84807e8fc5355593baf663173d93a8df474f5c4a`（原候选完整文件与runtime的身份，不能由这里只含Skill的子集复算）。

- `c2/SKILL.md` SHA256：`49e7664bf47974908821b26f6ff066f0207f031599497bfcd4d19015ce217ece`
- `c2/references/mcp-tools.md` SHA256：`af7a4d6bec065c91165217a9e1de812178b0dd17d2cfdf5441b581f50a160a48`

提交版为真实MCP做了明确适配，改动见 [ADAPTATION.md](../docs/ADAPTATION.md)。原研究分数只属于上述冻结原件；提交版尚未重新做端到端模型评测。私有verifier、答案、留出题、用户账户数据、模型凭据与完整实验状态不包含在此公开仓库。
