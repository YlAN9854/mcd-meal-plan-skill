# MCP 工具使用参考

服务地址为 `https://mcp.mcd.cn`，使用 Streamable HTTP。客户端通过 `Authorization: Bearer ...` 发送个人 Token。

以下说明根据 2026-10-13 核对的到店场景整理。调用时，以当前 `tools/list` 返回的参数和业务说明为准。

## 六个常用工具

| 工具 | 用途 |
| --- | --- |
| `query-nearby-stores` | 按用户位置查门店；使用 `searchType=2`，配合 `city` 和 `keyword` |
| `query-meals` | 查询所选门店和取餐方式下的菜单、商品编码与参考价 |
| `query-meal-detail` | 查看套餐组成、默认选配和特调参数 |
| `query-my-coupons` | 查询用户拥有的券，实际使用前仍需核对门店和渠道 |
| `query-store-coupons` | 查询指定门店和渠道适用的券，以及对应商品 |
| `calculate-price` | 按完整商品清单、数量、优惠和配置核对整单价格 |

按位置查门店时显式传入 `searchType=2`，避免使用默认的收藏餐厅查询。

## 取餐方式

- 到店自取：`orderType=1`、`beType=1`，不传 `beCode`。
- 得来速：`orderType=1`、`beType=5`，携带门店查询返回、且与该门店配对的 `beCode`。
- 预约：按当前 schema 填写 `reservationDate`。

当前 Skill 支持到店自取和得来速。外送地址与团餐需要相应的业务接入流程。

## 价格与商品配置

`query-meals` 的 `currentPrice` 为字符串参考价；`calculate-price.data.price` 为整数分。最终金额采用同一门店、同一份商品清单和配置的整单报价。

数量、套餐 `roundList`、特调 `modification`、券 `couponId/couponCode` 和其他费用，均按实时 schema 与返回结果处理。

## 错误和个人信息

遇到 `COUPON_MISMATCH` 等参数问题时，先核对商品、券 ID 和取餐方式。错误含义尚不明确时保留未知，按真实返回继续排查；研究环境中的模拟错误码只适用于对应模拟场景。

响应可能包含个人券信息，只用于当前用户请求。公开日志和示例使用脱敏内容。

参考：[麦当劳官方接入指南](https://github.com/M-China/mcd-mcp-server)。
