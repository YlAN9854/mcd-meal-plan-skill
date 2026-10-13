---
name: mcd-meal-plan-output
description: "Fill every field of the McDonald’s MCP meal-plan result written to /workspace/plan.json for the chosen status (ready / infeasible / needs_clarification / service_unavailable): plan.schema.json fixes the structure, and the task’s output contract defines what each status requires of those fields. Key rule: minimum_total_cents stays null unless the status is infeasible with reason budget_infeasible."
whenToUse: "The task asks for a 用餐方案 / meal plan that must be saved to /workspace/plan.json and validated against plan.schema.json — including tasks that should end in needs_clarification, service_unavailable, or infeasible. Decide the status from the task inputs and tool responses; a successful query or whole-cart pricing is not a precondition for these outcomes."
---

# MCP meal plan: write plan.json to the per-status contract

`plan.json` describes the outcome state of the task. The values that are valid for one `status` are
wrong for another, so pick the status first, then fill every field exactly for that status.
`plan.schema.json` fixes the structure — the 10 required fields and `additionalProperties: false` —
while the task’s output contract assigns the per-status semantics of those fields. Everything below
restates that public contract and the schema.

## The state-dependent field: `minimum_total_cents`

`minimum_total_cents` is meaningful only for a budget-infeasible outcome. Set it to an integer
**only** when `status` is `infeasible` **and** the reason is `budget_infeasible` (it then holds the
cheapest whole-cart total that still satisfies every other constraint). In **every other** case set
it to `null` — including:

- `ready`: leave it `null` even though you have a real `total_cents`. **Do not copy `total_cents`
  into `minimum_total_cents`.**
- `needs_clarification`, `service_unavailable`, and `infeasible` from `no_available_combination`:
  always `null`.

## Step 1 — choose the status

- `needs_clarification`: the user did not state the order mode (取餐方式: 到店自取 pickup vs 得来速
  drive-through). Do not assume one. Emit this even if a plan would otherwise be feasible; it can be
  decided before any query, because every store/menu/pricing tool already requires a `beType`.
- `service_unavailable`: a whole-cart `calculate-price` call returns `PRICE_SERVICE_UNAVAILABLE`,
  which the contract defines as persistently unavailable for this session. That explicit response is
  sufficient — no fixed number of attempts is required. A `PRICE_SERVICE_RETRYABLE` is transient —
  retry it; do not declare the session unavailable from a retryable error.
- `infeasible`: no plan can satisfy all constraints. Distinguish `budget_infeasible` (a combination
  exists under all non-budget constraints but the cheapest still exceeds budget) from
  `no_available_combination` (stock / variety / preference rules out every assignment). Never reduce
  quantity or relax a stated preference just to reach feasibility.
- `ready`: a combination satisfies store, channel, budget, variety, quantity, tags and each diner.

## Step 2 — fill every field for that status

| Field | `ready` | `infeasible` (budget) | `infeasible` (no combo) | `needs_clarification` | `service_unavailable` |
|---|---|---|---|---|---|
| `items` | chosen products | `[]` | `[]` | `[]` | `[]` |
| `total_cents` | whole-cart `price` (int cents) | `null` | `null` | `null` | `null` |
| `minimum_total_cents` | **`null`** | cheapest cart (int cents) | **`null`** | **`null`** | **`null`** |
| `be_type` | `1` pickup / `5` drive-through | requested mode | requested mode | **`null`** | requested mode |
| `missing_fields` | `[]` | `[]` | `[]` | `["be_type"]` | `[]` |
| `reason_codes` | `[]` base (+ Step 3 events) | `["budget_infeasible"]` (+ Step 3 events) | `["no_available_combination"]` (+ Step 3 events) | `["missing_order_mode"]` (+ Step 3 events) | `["price_service_unavailable"]` (+ Step 3 events) |
| `store_code` | selected store code | selected store code | selected store code | selected store code | selected store code |
| `message` | non-empty user summary | non-empty | non-empty | non-empty | non-empty |

For `ready`, `total_cents` must equal the `price` of **one successful whole-cart `calculate-price`**
for exactly the listed items + quantities + coupons. Never sum several per-item quotes as a
substitute for a whole-cart quote. Reordering items or merging/splitting quantities of the same
product+coupon is fine. Each coupon is used once, discounts one matching product, and is not stacked
on the same item; multiple units of one product may each use a different coupon.

For `infeasible` from budget, `minimum_total_cents` is the quoted price of the cheapest whole cart
that satisfies every constraint except budget (applicable coupons allowed). A
`no_available_combination` outcome needs no cart quote at all — its amounts stay `null`; do not
fabricate a quote for it.

## Step 3 — `reason_codes`: base reason plus real events

`reason_codes` = the base reason of the chosen status (Step 2 table; `ready` has none) **plus** any
of the following events — but only events that genuinely occurred in this task. Report each event
that occurred, under whichever status the plan ends in, and add none that did not occur.

- `coupon_not_applicable`: a coupon the user named does not apply to the chosen store/channel.
- `preferred_item_unavailable`: an item the user expressed a priority or preference for is sold
  out. Both conditions must hold: the user independently prioritized that item — judge this from
  the request's meaning, not from fixed wording — and the observed data shows it unavailable. A
  hard requirement is a different predicate from a preference: an item that is only required (a
  mandated item, category, tag, or quantity, with or without a no-substitution condition) is not
  thereby "preferred", so its unavailability alone feeds the feasibility decision (e.g.
  `no_available_combination`) and never creates this event — though a failed hard requirement can
  still coexist with a separately expressed priority event. The event never depends on
  substitution being allowed: a prioritized item the user refused to replace still raises it.
  Whether or not the event is reported changes nothing about feasibility — every hard requirement
  and no-substitution condition stays binding. Keep a preferred item if still sellable;
  substitute only within what the user allowed.

The base reasons (`budget_infeasible`, `no_available_combination`, `missing_order_mode`,
`price_service_unavailable`) stay tied to their status as in Steps 1–2 and do not appear under
other statuses.

## Step 4 — `evidence_refs`: real traceIds bound to each obligation

Copy `traceId` values returned by the tools in this run; never invent one. Bind each obligation to
the specific response that supports it:

- `ready` and both `infeasible` outcomes: reference the selected store+channel menu.
- `ready`: also reference the one successful whole-cart quote behind `total_cents`.
- `budget_infeasible`: also reference the minimum whole-cart quote reported as
  `minimum_total_cents`. `no_available_combination` requires no cart quote — do not fabricate one.
- A coupon used, a coupon explained as inapplicable, or a budget-infeasibility proof: also
  reference the store coupon query (`query-store-coupons`).
- `service_unavailable`: reference the response(s) that reported persistent unavailability.
- `needs_clarification` may have no calls.

## Final checklist before writing `plan.json`

1. `status` matches the situation (Step 1), and every field is filled for that status (Step 2).
2. `minimum_total_cents` is an integer **only** for `infeasible`+`budget_infeasible`; otherwise `null`.
3. Amount obligations are state-dependent: for `ready`, `total_cents` equals one successful
   whole-cart quote for the exact `items`; for `budget_infeasible`, `minimum_total_cents` equals the
   quoted minimum cart; every other amount is `null`. Amounts are integer cents.
4. `reason_codes` lists the status base reason plus only the events that occurred; `missing_fields`
   is `["be_type"]` only when clarifying.
5. `evidence_refs` are real returned `traceId`s, bound per obligation as in Step 4.
6. All 10 required fields present, no extra keys; `message` non-empty; file is valid JSON.

## Channel values, amounts, and error taxonomy

For the pickup vs drive-through `beType`/`beCode` values, the amount units, and the
`PRICE_SERVICE_*` / `COUPON_MISMATCH` error meanings, see
[references/mcp-tools.md](references/mcp-tools.md). The tool schemas from `tools/list` stay
authoritative for argument names; take store codes, product codes, coupon IDs, and search inputs
from the task statement and the actual tool responses.
