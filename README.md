# Business Logic Vulnerabilities

Business logic vulnerabilities are flaws in an application’s **intended workflow** rather than in its underlying technology (e.g., not “SQL injection” or “XSS” by itself). They happen when an attacker can **abuse legitimate features** in unexpected ways to gain an advantage: bypass restrictions, manipulate prices, skip steps, or trigger states the system should never allow.

Unlike classic technical bugs, business logic issues usually come from:
- Missing or incorrect **server-side validation**
- Trusting **client-controlled** data (price, role, discount, quantity, status)
- Weak enforcement of **process rules** (order of steps, limits, approvals)
- Bad assumptions about “normal” user behavior

## Why they matter
Business logic vulnerabilities can cause real-world impact:
- Unauthorized purchases or refunds (price/discount tampering)
- Account takeover paths through flawed recovery/verification flows
- Access control bypass via workflow manipulation (IDOR + logic)
- Abuse of credits, coupons, loyalty points, or rate limits
- Skipping payment, bypassing approvals, or duplicating transactions

These issues are often **high severity** because they directly affect money, authorization, or trust — and they may not be caught by automated scanners.

## Common examples
- **Price tampering:** server accepts a `price` parameter from the client.
- **Quantity/limit bypass:** buying more than allowed by changing request fields.
- **Coupon stacking:** applying discounts in unintended combinations.
- **Race conditions:** double-spending balance by sending parallel requests.
- **Step skipping:** calling `/checkout` without completing required steps.

## How to test (high-level)
1. Map the intended workflow (happy path).
2. Identify trust boundaries (what the server should compute vs. what the client sends).
3. Replay requests and mutate parameters:
   - price, quantity, role, status, discount, productId, userId
4. Try reordering steps, repeating steps, or skipping steps.
5. Test concurrency (two requests at once) for double actions.

## Key defensive principles
- Validate **everything** server-side (including price and totals).
- Enforce workflow state transitions (a finite-state model helps).
- Use idempotency keys for critical actions (payments, refunds).
- Apply strict authorization checks on every request.
- Log and monitor abnormal sequences and repeated actions.

---

> This repository focuses on understanding, documenting, and demonstrating business logic vulnerabilities with clear workflows, reproducible steps, and practical remediation guidance.
