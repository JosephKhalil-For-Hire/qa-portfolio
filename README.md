# Shopping Cart Pricing: a test-first QA project

A small Python pricing module for an online store cart (items, discount codes, sales tax), built **test-first**: every behavior had a failing pytest test before any code was written. It is checked automatically by GitHub Actions on every push.

## What this project shows
- **Requirements to test cases:** a written spec ([PLAN.md](PLAN.md), R1–R6) with every rule covered by tests.
- **Test design techniques:**
  - *Equivalence partitioning:* valid vs. invalid prices, quantities, codes and tax rates.
  - *Boundary value analysis:* price `0` / `0.01`, quantity `0` / `1`, the `FLAT5` threshold at `$24.99` / `$25.00` / `$25.01`, tax rate `-0.01` / `1.01`.
  - *Negative testing:* bad input, removing missing items, unknown codes.
  - *Rounding edge cases:* `0.10 + 0.20 == 0.30` (no float error), half-up rounding to cents.
- **pytest features:** fixtures, `parametrize` tables, `pytest.raises`.
- **CI:** GitHub Actions runs the suite on Python 3.11, 3.12 and 3.13.

## Rules under test
| ID | Rule |
|---|---|
| R1 | Add items; adding the same item again increases its quantity |
| R2 | Price > 0 and quantity a whole number ≥ 1, otherwise `ValueError` |
| R3 | Subtotal = Σ price × qty, exact to the cent |
| R4 | Remove by name; unknown item raises `KeyError` |
| R5 | `SAVE10` = 10% off; `FLAT5` = $5 off at subtotal ≥ $25; codes ignore case; unknown codes rejected |
| R6 | Total = (subtotal − discount) + tax, rounded half-up, never below $0 |

## Run it
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -e ".[test]"
pytest -v
```

## How it was built (red → green → refactor)
1. Wrote the R1 tests and watched them fail (`Cart` didn't exist), then wrote the minimum code to pass.
2. Added 15 R2–R4 tests, all failing, then added validation, `subtotal()` and `remove_item()`.
3. Added 20 R5–R6 tests, all failing, then added discount codes, tax and rounding.

Result: **38 tests, all passing.**

## Project layout
```
src/cart_app/cart.py   the code under test
tests/test_cart.py     the test suite
PLAN.md                spec and test design
.github/workflows/     CI
```
