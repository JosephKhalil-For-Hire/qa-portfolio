# Plan: Shopping Cart Pricing (test-first)

## Goal
A small, well-tested pricing module for an online store cart, built red/green/refactor
to show core QA skills: requirements → test cases → automation → CI.

## Requirements (the "spec" the tests check)
1. **R1 Add items.** Name, unit price, quantity. Adding the same name again increases its quantity.
2. **R2 Validation.** Price must be greater than 0 and quantity a whole number ≥ 1. Anything else raises `ValueError`.
3. **R3 Subtotal.** Sum of price × quantity, as exact money (`Decimal`, 2 places).
4. **R4 Remove.** Remove an item by name. Removing an unknown item raises `KeyError`.
5. **R5 Discount codes** (one per cart, case-insensitive):
   - `SAVE10`: 10% off the subtotal.
   - `FLAT5`: $5 off, only when subtotal ≥ $25.00. Below that it raises `ValueError`.
   - Unknown code: `ValueError`.
6. **R6 Total.** (subtotal − discount) + tax at the cart's tax rate, rounded half-up to cents. Never below $0.

## Test design
| Technique | Where |
|---|---|
| Equivalence partitioning | valid vs. invalid prices/quantities, known vs. unknown codes |
| Boundary values | price 0 / 0.01, qty 0 / 1, FLAT5 at $24.99 / $25.00 |
| Negative tests | bad input, removing missing items, bad codes |
| Parametrized tests | `pytest.mark.parametrize` tables |
| Fixtures | a reusable empty cart |

## Steps
1. RED: test R1 → watch fail → GREEN: minimal Cart.
2. RED: tests R2 → fail → GREEN: validation.
3. RED: tests R3/R4 → fail → GREEN.
4. RED: tests R5/R6 → fail → GREEN → refactor.
5. README + GitHub Actions running pytest on push/PR.
