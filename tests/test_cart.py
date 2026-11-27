from decimal import Decimal

import pytest

from cart_app.cart import Cart


@pytest.fixture
def cart():
    return Cart()


# R1: adding items
def test_new_cart_is_empty(cart):
    assert cart.items == {}


def test_add_item_stores_price_and_quantity(cart):
    cart.add_item("mug", "12.50", 2)
    assert cart.items["mug"] == (Decimal("12.50"), 2)


def test_adding_same_item_again_increases_quantity(cart):
    cart.add_item("mug", "12.50", 2)
    cart.add_item("mug", "12.50", 3)
    assert cart.items["mug"] == (Decimal("12.50"), 5)


# R2: input validation (equivalence classes + boundary values)
@pytest.mark.parametrize("bad_price", ["0", "0.00", "-1", "-0.01"])
def test_rejects_non_positive_price(cart, bad_price):
    with pytest.raises(ValueError):
        cart.add_item("mug", bad_price, 1)


def test_accepts_smallest_valid_price(cart):
    cart.add_item("sticker", "0.01", 1)
    assert cart.subtotal() == Decimal("0.01")


@pytest.mark.parametrize("bad_qty", [0, -1, 1.5, "2"])
def test_rejects_invalid_quantity(cart, bad_qty):
    with pytest.raises(ValueError):
        cart.add_item("mug", "12.50", bad_qty)


def test_rejects_unparseable_price(cart):
    with pytest.raises(ValueError):
        cart.add_item("mug", "twelve", 1)


# R3: subtotal
def test_empty_cart_subtotal_is_zero(cart):
    assert cart.subtotal() == Decimal("0.00")


def test_subtotal_sums_price_times_quantity(cart):
    cart.add_item("mug", "12.50", 2)
    cart.add_item("pen", "1.99", 3)
    assert cart.subtotal() == Decimal("30.97")


def test_subtotal_has_no_float_rounding_error(cart):
    cart.add_item("a", "0.10", 1)
    cart.add_item("b", "0.20", 1)
    assert cart.subtotal() == Decimal("0.30")


# R4: removing items
def test_remove_item(cart):
    cart.add_item("mug", "12.50", 2)
    cart.remove_item("mug")
    assert "mug" not in cart.items


def test_remove_unknown_item_raises(cart):
    with pytest.raises(KeyError):
        cart.remove_item("ghost")


# R5: discount codes
def test_no_discount_by_default(cart):
    cart.add_item("mug", "12.50", 2)
    assert cart.discount() == Decimal("0.00")


@pytest.mark.parametrize("code", ["SAVE10", "save10", "Save10"])
def test_save10_takes_ten_percent_and_ignores_case(cart, code):
    cart.add_item("mug", "12.50", 2)  # subtotal 25.00
    cart.apply_code(code)
    assert cart.discount() == Decimal("2.50")


@pytest.mark.parametrize(
    "price, expected_discount",
    [("25.00", Decimal("5.00")), ("25.01", Decimal("5.00"))],
)
def test_flat5_applies_at_or_above_25(cart, price, expected_discount):
    cart.add_item("item", price, 1)
    cart.apply_code("FLAT5")
    assert cart.discount() == expected_discount


def test_flat5_rejected_just_below_threshold(cart):
    cart.add_item("item", "24.99", 1)
    with pytest.raises(ValueError):
        cart.apply_code("FLAT5")


@pytest.mark.parametrize("code", ["", "SAVE100", "FREE", "  "])
def test_unknown_code_rejected(cart, code):
    cart.add_item("mug", "12.50", 2)
    with pytest.raises(ValueError):
        cart.apply_code(code)


def test_new_code_replaces_old_one(cart):
    cart.add_item("item", "100.00", 1)
    cart.apply_code("SAVE10")
    cart.apply_code("FLAT5")
    assert cart.discount() == Decimal("5.00")


def test_flat5_drops_when_items_removed_below_threshold(cart):
    cart.add_item("big", "20.00", 1)
    cart.add_item("small", "10.00", 1)
    cart.apply_code("FLAT5")
    cart.remove_item("big")
    assert cart.discount() == Decimal("0.00")


# R6: total with tax
def test_total_without_tax_or_discount_equals_subtotal(cart):
    cart.add_item("mug", "12.50", 2)
    assert cart.total() == Decimal("25.00")


def test_total_applies_discount_then_tax():
    cart = Cart(tax_rate="0.0725")
    cart.add_item("mug", "12.50", 2)  # 25.00
    cart.apply_code("SAVE10")         # -2.50 -> 22.50
    # tax 22.50 * 0.0725 = 1.63125 -> total 24.13125 -> 24.13
    assert cart.total() == Decimal("24.13")


def test_total_rounds_half_up():
    cart = Cart(tax_rate="0.10")
    cart.add_item("item", "0.05", 1)  # 0.05 + 0.005 tax = 0.055 -> 0.06
    assert cart.total() == Decimal("0.06")


def test_empty_cart_total_is_zero():
    assert Cart(tax_rate="0.0725").total() == Decimal("0.00")


@pytest.mark.parametrize("bad_rate", ["-0.01", "1.01", "abc"])
def test_rejects_invalid_tax_rate(bad_rate):
    with pytest.raises(ValueError):
        Cart(tax_rate=bad_rate)
