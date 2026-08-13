import math


def apply_rounding(value, mode="nearest"):
    if mode == "up":
        return math.ceil(value)
    if mode == "down":
        return math.floor(value)
    if mode == "none":
        return round(value, 2)
    # nearest (default) - round-half-up, e.g. 58.50 -> 59
    return math.floor(value + 0.5)


def get_km_rate(mode, rates):
    """rates -> ExpenseRate row"""
    mode = (mode or "").lower()
    if mode == "bike":
        return rates.bike_rate
    if mode == "car":
        return rates.car_rate
    # bus / train / auto / cab / other -> no automatic KM costing,
    # CNG/Bus field is used instead. Fallback to "other vehicle" rate
    # only if the user explicitly logs KM for an uncovered mode.
    return 0


def calculate_expense(mode, km, other_amount, cng_bus_amount, courier_transport_amount,
                       food_amount, rates):
    km = float(km or 0)
    other_amount = float(other_amount or 0)
    cng_bus_amount = float(cng_bus_amount or 0)
    courier_transport_amount = float(courier_transport_amount or 0)
    food_amount = float(food_amount or 0)

    km_rate = get_km_rate(mode, rates)
    km_amount_raw = km * km_rate
    km_amount = apply_rounding(km_amount_raw, rates.rounding) if km_rate else 0

    total = other_amount + cng_bus_amount + courier_transport_amount + food_amount + km_amount

    return {
        "km_rate": km_rate,
        "km_amount": km_amount,
        "total_amount": round(total, 2),
    }
