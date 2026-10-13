# 需要 `plan.json` 时怎么写

日常使用先给用户可读方案。用户需要 `plan.json` 时，按下表整理；这是提交版的应用输出格式。

| 字段 | 填写内容 |
| --- | --- |
| `status` | `ready` / `needs_clarification` / `infeasible` / `service_unavailable` / `incomplete` |
| `store_code` | 实际门店编码，未确定时为 `null` |
| `be_type` | 到店自取为 `1`，得来速为 `5`，未确定时为 `null` |
| `items` | 可行方案的商品、数量、已核实优惠和配置；其他结果为 `[]` |
| `total_cents` | 可行方案的整单实时报价，单位为整数分；其他结果为 `null` |
| `minimum_total_cents` | 仅在已证明预算无解时，填写有依据的最低整单报价；其余为 `null` |
| `missing_fields` | 尚未确定的必要信息名称；没有则填 `[]` |
| `reason_codes` | 状态和实际事件的简短标签，每项都应有对应事实 |
| `evidence_refs` | 依据列表，每项包含 `tool`、`server_trace_id`、`source_locator` 和 `supports` |
| `message` | 给用户的简明结果、已检查范围和未解决事项 |

`evidence_refs` 中的 `server_trace_id` 填服务实际返回的 trace；没有则为 `null`。`source_locator` 填客户端可定位的本次调用结果；没有则为 `null`。`supports` 说明这条查询支持哪个结论。所有引用均须真实。

金额使用整数分，未知金额保持 `null`。搜索尚未完成时使用 `incomplete`，说明已经查过的组合和待查内容；无解和最低价的结论需要充分依据。

需要澄清时直接列出问题，商品清单保持为空。查询和报价完成后，任务结束于方案输出，实际点餐仍由用户在官方渠道完成。
