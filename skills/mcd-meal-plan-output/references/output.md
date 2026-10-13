# 可选结构化输出

普通使用先给可读方案。需要 `plan.json` 时使用以下字段；本格式属于提交版应用输出，不是麦当劳官方接口，也不是原研究版评分契约。

| 字段 | 内容 |
| --- | --- |
| status | ready / needs_clarification / infeasible / service_unavailable / incomplete |
| store_code | 实际门店编码；未确定时null |
| be_type | 自取1、得来速5；未确定时null |
| items | 可行方案的商品、数量、已核实优惠与配置；其他结果为[] |
| total_cents | 可行方案的整单实时报价，整数分；其他结果null |
| minimum_total_cents | 仅已证明预算无解时填可证实的最低整单报价；其余null |
| missing_fields | 必要的未确定信息名称；没有则[] |
| reason_codes | 本次状态/事件的简短机器可读标签，必须有对应事实 |
| evidence_refs | 对象列表，含tool、server_trace_id（无则null）、source_locator（客户端可定位结果，无则null）、supports；不伪造标识 |
| message | 给用户的简明结果、证据范围和未解决事项 |

金额一律为整数分，未知金额不填0。未完成搜索时用incomplete，不能仅因当前几个方案超预算就填infeasible或最低价。工具返回了报价也不代表已经下单。需要澄清时直接列问题，无需先造一套商品方案。
