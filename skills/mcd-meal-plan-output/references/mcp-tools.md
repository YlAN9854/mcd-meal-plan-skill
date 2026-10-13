# 官方 MCP 接入与工具参考

服务为 `https://mcp.mcd.cn`，Streamable HTTP，凭据由客户端通过 `Authorization: Bearer ...` 注入。以当前 `tools/list` 返回的参数和业务说明为准；本文件记录2026-10-13核对的到店场景。

| 工具 | 用途 |
| --- | --- |
| query-nearby-stores | 按用户位置搜索到店/得来速门店；`searchType=2` 配合 `city`、`keyword`，避免默认查询收藏 |
| query-meals | 获取所选门店与渠道的菜单、商品编码和参考价格 |
| query-meal-detail | 查看套餐组成、默认选配和特调参数 |
| query-my-coupons | 查询用户拥有的券；不证明特定门店和渠道可用 |
| query-store-coupons | 查询指定门店与渠道适用的券和商品关联 |
| calculate-price | 对完整商品、数量、券和配置计算整单价格 |

到店自取使用 `orderType=1, beType=1`，不传 `beCode`；得来速使用 `orderType=1, beType=5`，携带门店查询返回且与该门店配对的 `beCode`。预约时按 schema 传 `reservationDate`。当前 Skill 范围是这两种取餐方式，外送地址与团餐流程需要相应的另一套业务接入。

`query-meals` 的 `currentPrice` 是字符串参考价；`calculate-price.data.price` 是整数分。数量、套餐 `roundList`、特调 `modification`、券 `couponId/couponCode` 及其他费用以实时 schema 和响应为准。不得用不同配置或不同门店的报价拼接出本单价格。

对 `COUPON_MISMATCH` 等参数问题，核对当前商品、券ID和渠道后再判断。没有可靠的业务错误分类时保持未知，不强套研究场景中定义的 `PRICE_SERVICE_RETRYABLE` 或 `PRICE_SERVICE_UNAVAILABLE` 语义。

参考：[官方接入指南](https://github.com/M-China/mcd-mcp-server)。响应可能包含个人券信息，仅用于当前用户任务，不进入公开日志或示例。
