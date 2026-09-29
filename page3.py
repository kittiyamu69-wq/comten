"""pages/page3.py — show who owes whom."""
import json
import os

import storage

TITLE = "สรุปค่าใช้จ่าย"

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAM_FILE = os.path.join(HERE, "team.json")
GROUP_STATE_FILE = os.path.join(HERE, "group_state.json")


def _load_group_state():
    try:
        with open(GROUP_STATE_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"group_name": "", "members": []}
    if not isinstance(data, dict):
        data = {"group_name": "", "members": []}
    return {"group_name": data.get("group_name") or "", "members": data.get("members") or []}


def _load_team():
    try:
        with open(TEAM_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"group": {"name": "กลุ่มค่าใช้จ่าย"}, "members": []}
    return data


def build():
    state = _load_group_state()
    team_data = _load_team()
    names = state.get("members") or [m.get("name") for m in team_data.get("members") or [] if m.get("name")]
    if not names:
        names = ["นิว", "กาย", "เฟิร์น"]
    group = team_data.get("group") or {}
    if state.get("group_name"):
        group = {**group, "name": state["group_name"]}

    raw_expenses = storage.load()
    expenses = raw_expenses if isinstance(raw_expenses, list) else []
    expense_summary = []
    for expense in expenses:
        expense_summary.append({
            "name": expense.get("name") or "ค่าใช้จ่าย",
            "amount": float(expense.get("amount") or 0),
        })

    paid = {name: 0.0 for name in names}
    due = {name: 0.0 for name in names}
    total_spent = 0.0

    for expense in expenses:
        amount = float(expense.get("amount") or 0)
        total_spent += amount
        eaters = expense.get("eaters") or names
        if not eaters:
            eaters = names
        per_person = amount / max(len(eaters), 1)
        for name in names:
            if name in eaters:
                due[name] += per_person

        for payer in expense.get("payers") or []:
            name = payer.get("name") if isinstance(payer, dict) else payer
            if name in paid:
                paid[name] += float(payer.get("amount") if isinstance(payer, dict) else 0)

    member_rows = []
    balances = {}
    for name in names:
        net = paid[name] - due[name]
        balances[name] = net
        if net > 0:
            status = "ต้องได้รับ"
        elif net < 0:
            status = "ต้องจ่าย"
        else:
            status = "สมดุล"

        expense_list = []
        for expense in expenses:
            expense_name = expense.get("name") or "ค่าใช้จ่าย"
            eaters = expense.get("eaters") or names
            if name in eaters:
                share = float(expense.get("amount") or 0) / max(len(eaters), 1)
                expense_list.append({
                    "name": expense_name,
                    "amount": round(share, 2),
                    "type": "ส่วนแบ่ง",
                })
            for payer in expense.get("payers") or []:
                payer_name = payer.get("name") if isinstance(payer, dict) else payer
                if payer_name != name:
                    continue
                payer_amount = float(payer.get("amount") if isinstance(payer, dict) else 0)
                expense_list.append({
                    "name": expense_name,
                    "amount": round(payer_amount, 2),
                    "type": "จ่ายแล้ว",
                })

        member_rows.append({
            "name": name,
            "paid": paid[name],
            "due": due[name],
            "net": net,
            "status": status,
            "expense_list": expense_list,
        })

    debtors = [{"name": name, "amount": abs(value)} for name, value in balances.items() if value < 0]
    creditors = [{"name": name, "amount": value} for name, value in balances.items() if value > 0]
    settlements = []
    debtor_index = 0
    creditor_index = 0

    reason_names = []
    for expense in expenses:
        name = expense.get("name") or "ค่าใช้จ่าย"
        if name not in reason_names:
            reason_names.append(name)

    while debtor_index < len(debtors) and creditor_index < len(creditors):
        debtor = debtors[debtor_index]
        creditor = creditors[creditor_index]
        amount = min(debtor["amount"], creditor["amount"])
        if amount > 0.01:
            settlements.append({
                "from": debtor["name"],
                "to": creditor["name"],
                "amount": round(amount, 2),
                "reason": ", ".join(reason_names) if reason_names else "ค่าใช้จ่าย",
            })
        debtor["amount"] -= amount
        creditor["amount"] -= amount

        if debtor["amount"] <= 0.01:
            debtor_index += 1
        if creditor["amount"] <= 0.01:
            creditor_index += 1

    return {
        "group": group,
        "members": member_rows,
        "settlements": settlements,
        "expenses": expenses,
        "expense_summary": expense_summary,
        "total_spent": total_spent,
        "member_count": len(names),
    }


def handle(form):
    action = (form.get("action") or "").strip()
    if action != "delete":
        return ""

    try:
        delete_index = int(form.get("delete_index", ""))
    except (TypeError, ValueError):
        return "รายการที่ลบไม่ถูกต้อง"

    records = storage.load()
    if not isinstance(records, list):
        records = []

    if 0 <= delete_index < len(records):
        del records[delete_index]
        storage.save(records)
        return "ลบรายการสำเร็จ"

    return "ไม่พบรายการที่ต้องการลบ"
