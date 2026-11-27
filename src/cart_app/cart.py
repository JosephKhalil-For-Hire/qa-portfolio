"""Shopping cart pricing: items, discount codes and tax, using exact money math."""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

CENT = Decimal("0.01")
ZERO = Decimal("0.00")
FLAT5_MINIMUM = Decimal("25.00")


def _to_decimal(value, what):
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"not a valid {what}: {value!r}") from None
    if not amount.is_finite():
        raise ValueError(f"not a valid {what}: {value!r}")
    return amount


def _round(amount):
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


class Cart:
    def __init__(self, tax_rate="0"):
        rate = _to_decimal(tax_rate, "tax rate")
        if not 0 <= rate <= 1:
            raise ValueError("tax rate must be between 0 and 1")
        self.tax_rate = rate
        self.items = {}
        self.code = None

    def add_item(self, name, unit_price, quantity):
        price = _to_decimal(unit_price, "price")
        if price <= 0:
            raise ValueError("price must be greater than 0")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise ValueError("quantity must be a whole number of at least 1")
        _, current_qty = self.items.get(name, (price, 0))
        self.items[name] = (price, current_qty + quantity)

    def remove_item(self, name):
        if name not in self.items:
            raise KeyError(name)
        del self.items[name]

    def subtotal(self):
        total = sum((price * qty for price, qty in self.items.values()), Decimal("0"))
        return _round(total)

    def apply_code(self, code):
        normalized = str(code).strip().upper()
        if normalized == "SAVE10":
            self.code = normalized
        elif normalized == "FLAT5":
            if self.subtotal() < FLAT5_MINIMUM:
                raise ValueError(f"FLAT5 needs a subtotal of at least ${FLAT5_MINIMUM}")
            self.code = normalized
        else:
            raise ValueError(f"unknown discount code: {code!r}")

    def discount(self):
        subtotal = self.subtotal()
        if self.code == "SAVE10":
            return _round(subtotal * Decimal("0.10"))
        if self.code == "FLAT5" and subtotal >= FLAT5_MINIMUM:
            return Decimal("5.00")
        return ZERO

    def total(self):
        taxable = max(self.subtotal() - self.discount(), ZERO)
        return _round(taxable * (1 + self.tax_rate))
