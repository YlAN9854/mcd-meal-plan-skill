# MCP tool reference for the meal-planning bench

Concise grounding for the state-dependent `plan.json` output: channel values, amount units, and the
pricing/coupon error meanings. The tool schemas returned by `tools/list` stay authoritative for
argument names and shapes. Take every identifier from the task statement and the actual tool
responses — the store-search city and keyword, `storeCode`, product codes, and coupon IDs are task
inputs, not reusable constants. The fixed endpoint is `http://mcp:8000/mcp`; the client only
forwards requests. Every tool response carries a `traceId` you can cite in `evidence_refs`.

## Channel values (be_type)

- 到店自取 (pickup): `orderType=1`, `beType=1`, and **do not** pass `beCode`.
- 得来速 (drive-through): `orderType=1`, `beType=5`, and pass the `beCode` returned for that store.
- `be_type` in the plan is `1` for pickup, `5` for drive-through.

## Amounts

Menu `currentPrice`/`originalPrice` are yuan strings (e.g. `"15.00"`) and are only reference prices.
The authoritative total is the `calculate-price` response `price` in integer cents (1 元 = 100 分).
Never report a menu amount as the final quote. Only for `ready` does `total_cents` come from one
successful whole-cart quote; every other status keeps `total_cents` `null` as the main Skill
status table requires.

## Error taxonomy

- `PRICE_SERVICE_RETRYABLE`: transient failure for this attempt — retry `calculate-price`. Do not
  conclude the session is unavailable from a retryable error.
- `PRICE_SERVICE_UNAVAILABLE`: pricing is persistently unavailable for this session. That explicit
  response is sufficient — no fixed number of attempts is required. Finish with
  `status=service_unavailable`, empty `items`, `null` amounts, reason `price_service_unavailable`,
  and cite the `traceId` of the response that reported persistent unavailability.
- `COUPON_MISMATCH` (e.g. 券码或餐品不匹配 / 使用券码时须提供券ID): the call must pass the matching
  `couponId` for that product. Fix the call and retry; conclude `coupon_not_applicable` only when
  the store-coupon query (`query-store-coupons`) shows the coupon does not apply to the chosen
  store/channel — a malformed call does not prove inapplicability, and coupons listed by
  `query-my-coupons` are not store/channel-validated, so ownership alone does not establish
  applicability.
