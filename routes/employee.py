from datetime import datetime, date, timedelta
from calendar import monthrange
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from models import db, Expense, ExpenseRate
from utils.calculations import calculate_expense

employee_bp = Blueprint("employee", __name__)


def get_rates():
    rates = ExpenseRate.query.first()
    if not rates:
        rates = ExpenseRate()
        db.session.add(rates)
        db.session.commit()
    return rates


def parse_date(value, default=None):
    if not value:
        return default
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return default


@employee_bp.route("/dashboard")
@login_required
def dashboard():
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    base = Expense.query.filter_by(employee_id=current_user.id)

    def total_since(start):
        return base.filter(Expense.expense_date >= start).with_entities(
            func.coalesce(func.sum(Expense.total_amount), 0)
        ).scalar()

    stats = {
        "today": base.filter(Expense.expense_date == today).with_entities(
            func.coalesce(func.sum(Expense.total_amount), 0)).scalar(),
        "week": total_since(week_start),
        "month": total_since(month_start),
        "year": total_since(year_start),
        "total": base.with_entities(func.coalesce(func.sum(Expense.total_amount), 0)).scalar(),
    }

    recent = base.order_by(Expense.expense_date.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        stats=stats,
        recent=recent,
        period_from=month_start,
        period_to=today,
    )


@employee_bp.route("/expenses")
@login_required
def expenses():
    query = Expense.query.filter_by(employee_id=current_user.id)

    search = request.args.get("q", "").strip()
    from_date = parse_date(request.args.get("from_date"))
    to_date = parse_date(request.args.get("to_date"))
    mode = request.args.get("mode", "").strip()

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Expense.reason.ilike(like)) |
            (Expense.from_location.ilike(like)) |
            (Expense.to_location.ilike(like))
        )
    if from_date:
        query = query.filter(Expense.expense_date >= from_date)
    if to_date:
        query = query.filter(Expense.expense_date <= to_date)
    if mode:
        query = query.filter(Expense.mode == mode)

    items = query.order_by(Expense.expense_date.desc()).all()

    summary = {
        "count": len(items),
        "km": sum(e.km or 0 for e in items),
        "food": sum(e.food_amount or 0 for e in items),
        "transport": sum((e.courier_transport_amount or 0) + (e.cng_bus_amount or 0) for e in items),
        "grand_total": sum(e.total_amount or 0 for e in items),
    }

    return render_template("expenses.html", expenses=items, summary=summary,
                            search=search, from_date=from_date, to_date=to_date, mode=mode)


@employee_bp.route("/add-expense", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        rates = get_rates()
        mode = request.form.get("mode", "")
        km = request.form.get("km") or 0
        other_amount = request.form.get("other_amount") or 0
        cng_bus_amount = request.form.get("cng_bus_amount") or 0
        courier_transport_amount = request.form.get("courier_transport_amount") or 0
        food_amount = request.form.get("food_amount") or 0

        calc = calculate_expense(mode, km, other_amount, cng_bus_amount,
                                  courier_transport_amount, food_amount, rates)

        expense = Expense(
            employee_id=current_user.id,
            expense_date=parse_date(request.form.get("expense_date"), date.today()),
            reason=request.form.get("reason", "").strip(),
            mode=mode,
            from_location=request.form.get("from_location", "").strip(),
            to_location=request.form.get("to_location", "").strip(),
            other_amount=float(other_amount or 0),
            cng_bus_amount=float(cng_bus_amount or 0),
            km=float(km or 0),
            courier_transport_amount=float(courier_transport_amount or 0),
            food_amount=float(food_amount or 0),
            km_rate=calc["km_rate"],
            km_amount=calc["km_amount"],
            total_amount=calc["total_amount"],
            notes=request.form.get("notes", "").strip(),
        )
        db.session.add(expense)
        db.session.commit()
        flash("Expense added successfully.", "success")
        return redirect(url_for("employee.expenses"))

    return render_template("add_expense.html", expense=None)


@employee_bp.route("/edit-expense/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.employee_id != current_user.id and not current_user.is_admin:
        flash("You cannot edit this expense.", "danger")
        return redirect(url_for("employee.expenses"))

    if request.method == "POST":
        rates = get_rates()
        mode = request.form.get("mode", "")
        km = request.form.get("km") or 0
        other_amount = request.form.get("other_amount") or 0
        cng_bus_amount = request.form.get("cng_bus_amount") or 0
        courier_transport_amount = request.form.get("courier_transport_amount") or 0
        food_amount = request.form.get("food_amount") or 0

        calc = calculate_expense(mode, km, other_amount, cng_bus_amount,
                                  courier_transport_amount, food_amount, rates)

        expense.expense_date = parse_date(request.form.get("expense_date"), expense.expense_date)
        expense.reason = request.form.get("reason", "").strip()
        expense.mode = mode
        expense.from_location = request.form.get("from_location", "").strip()
        expense.to_location = request.form.get("to_location", "").strip()
        expense.other_amount = float(other_amount or 0)
        expense.cng_bus_amount = float(cng_bus_amount or 0)
        expense.km = float(km or 0)
        expense.courier_transport_amount = float(courier_transport_amount or 0)
        expense.food_amount = float(food_amount or 0)
        expense.km_rate = calc["km_rate"]
        expense.km_amount = calc["km_amount"]
        expense.total_amount = calc["total_amount"]
        expense.notes = request.form.get("notes", "").strip()

        db.session.commit()
        flash("Expense updated successfully.", "success")
        return redirect(url_for("employee.expenses"))

    return render_template("add_expense.html", expense=expense)


@employee_bp.route("/delete-expense/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.employee_id != current_user.id and not current_user.is_admin:
        flash("You cannot delete this expense.", "danger")
        return redirect(url_for("employee.expenses"))

    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", "info")
    return redirect(url_for("employee.expenses"))


@employee_bp.route("/api/calculate-total")
@login_required
def api_calculate_total():
    rates = get_rates()
    calc = calculate_expense(
        request.args.get("mode"),
        request.args.get("km"),
        request.args.get("other_amount"),
        request.args.get("cng_bus_amount"),
        request.args.get("courier_transport_amount"),
        request.args.get("food_amount"),
        rates,
    )
    return jsonify(calc)


@employee_bp.route("/daily-report")
@login_required
def daily_report():
    from_date = parse_date(request.args.get("from_date"), date.today() - timedelta(days=30))
    to_date = parse_date(request.args.get("to_date"), date.today())

    items = Expense.query.filter(
        Expense.employee_id == current_user.id,
        Expense.expense_date >= from_date,
        Expense.expense_date <= to_date,
    ).order_by(Expense.expense_date.asc()).all()

    daily_totals = {}
    for e in items:
        key = e.expense_date.strftime("%d %b")
        daily_totals[key] = daily_totals.get(key, 0) + (e.total_amount or 0)

    summary = {
        "transactions": len(items),
        "km": sum(e.km or 0 for e in items),
        "food": sum(e.food_amount or 0 for e in items),
        "transport": sum((e.courier_transport_amount or 0) + (e.cng_bus_amount or 0) for e in items),
        "grand_total": sum(e.total_amount or 0 for e in items),
    }

    return render_template("daily_report.html", items=items, summary=summary,
                            from_date=from_date, to_date=to_date,
                            chart_labels=list(daily_totals.keys()),
                            chart_values=list(daily_totals.values()))


@employee_bp.route("/monthly-report")
@login_required
def monthly_report():
    month = int(request.args.get("month", date.today().month))
    year = int(request.args.get("year", date.today().year))

    items = Expense.query.filter(
        Expense.employee_id == current_user.id,
        extract("month", Expense.expense_date) == month,
        extract("year", Expense.expense_date) == year,
    ).order_by(Expense.expense_date.asc()).all()

    summary = {
        "total_expenses": sum(e.total_amount or 0 for e in items),
        "km": sum(e.km or 0 for e in items),
        "food": sum(e.food_amount or 0 for e in items),
        "transport": sum(e.courier_transport_amount or 0 for e in items),
        "cng_bus": sum(e.cng_bus_amount or 0 for e in items),
        "other": sum(e.other_amount or 0 for e in items),
    }
    summary["grand_total"] = summary["total_expenses"]

    return render_template("monthly_report.html", items=items, summary=summary,
                            month=month, year=year)


@employee_bp.route("/analytics")
@login_required
def analytics():
    today = date.today()
    year_start = today.replace(month=1, day=1)
    items = Expense.query.filter(
        Expense.employee_id == current_user.id,
        Expense.expense_date >= year_start,
    ).order_by(Expense.expense_date.asc()).all()

    monthly_totals = [0] * 12
    for e in items:
        monthly_totals[e.expense_date.month - 1] += e.total_amount or 0

    category_totals = {
        "Food": sum(e.food_amount or 0 for e in items),
        "Transport/Courier": sum(e.courier_transport_amount or 0 for e in items),
        "CNG/Bus": sum(e.cng_bus_amount or 0 for e in items),
        "Bike/Car KM": sum(e.km_amount or 0 for e in items),
        "Other": sum(e.other_amount or 0 for e in items),
    }

    # Last 30 days of data for the four detail trend charts
    recent_start = today - timedelta(days=30)
    recent_items = [e for e in items if e.expense_date >= recent_start]
    if not recent_items:
        recent_items = items[-30:]

    day_labels = []
    food_series, transport_series, cng_series, km_series = [], [], [], []
    daily = {}
    for e in recent_items:
        key = e.expense_date
        if key not in daily:
            daily[key] = {"food": 0, "transport": 0, "cng": 0, "km": 0}
        daily[key]["food"] += e.food_amount or 0
        daily[key]["transport"] += e.courier_transport_amount or 0
        daily[key]["cng"] += e.cng_bus_amount or 0
        daily[key]["km"] += e.km or 0

    for d in sorted(daily.keys()):
        day_labels.append(d.strftime("%d %b"))
        food_series.append(daily[d]["food"])
        transport_series.append(daily[d]["transport"])
        cng_series.append(daily[d]["cng"])
        km_series.append(daily[d]["km"])

    return render_template("analytics.html",
                            monthly_labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                            monthly_values=monthly_totals,
                            category_labels=list(category_totals.keys()),
                            category_values=list(category_totals.values()),
                            day_labels=day_labels,
                            food_series=food_series,
                            transport_series=transport_series,
                            cng_series=cng_series,
                            km_series=km_series)


@employee_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")
