"""pages/page2.py — add an expense to the group."""
import json
import os
import re
from urllib.parse import urlencode

import storage

TITLE = "เพิ่มค่าใช้จ่าย"

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


def _safe_name(name):
    text = str(name).strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^0-9A-Za-zก-๙_]", "_", text)
    return text.strip("_") or "member"


def _member_names():
    state = _load_group_state()
    names = state.get("members") or []
    if names:
        return names
    data = _load_team()
    members = data.get("members") or []
    names = [m.get("name") for m in members if m.get("name")]
    return names or ["นิว", "กาย", "เฟิร์น"]


def _redirect_with_error(form, message):
    params = {}
    for key, value in form.items():
        if key in {"expense_name", "amount"} or key.startswith("eater_") or key.startswith("payer_") or key.startswith("payer_amount_"):
            if isinstance(value, (list, tuple)):
                value = value[0] if value else ""
            if value not in (None, ""):
                params[key] = str(value)
    params["msg"] = message
    return {"redirect": "/page2?" + urlencode(params)}


def build(query=None):
    q = query or {}
    names = _member_names()
    error_msg = q.get("msg", "")
    state = _load_group_state()
    group_name = state.get("group_name") or _load_team().get("group", {}).get("name", "กลุ่มค่าใช้จ่าย")
    return {
        "members": names,
        "group_name": group_name,
        "default_name": q.get("expense_name", "ค่าอาหาร"),
        "default_amount": q.get("amount", ""),
        "query": q,
        "error_msg": error_msg,
    }


def handle(form):
    names = _member_names()
    item_name = (form.get("expense_name") or "ค่าใช้จ่าย").strip() or "ค่าใช้จ่าย"
    amount = float(form.get("amount") or 0)
    if amount <= 0:
        amount = 0.0

    eater_keys = [key for key in form.keys() if key.startswith("eater_") and form.get(key) in ("on", "true", "1", "yes")]
    eaters = []
    for key in eater_keys:
        member_name = key[len("eater_"):].replace("_", " ").strip()
        if member_name:
            eaters.append(member_name)
    if not eaters:
        eaters = names

    selected_payers = []
    payer_amounts = []
    for key, value in form.items():
        if key.startswith("payer_") and key not in {"payer_"}:
            member_name = key[len("payer_"):].replace("_", " ").strip()
            if form.get(key) in ("on", "true", "1", "yes"):
                selected_payers.append(member_name or key)
                payer_value = form.get(f"payer_amount_{key[len('payer_'):]}")
                try:
                    payer_amount = float(payer_value or 0)
                except ValueError:
                    payer_amount = 0.0
                payer_amounts.append({"name": member_name or key, "amount": payer_amount})

    if not selected_payers:
        selected_payers = [names[0]] if names else ["สมาชิก 1"]
        payer_amounts = [{"name": selected_payers[0], "amount": amount}]

    expense = {
        "name": item_name,
        "amount": amount,
        "eaters": eaters,
        "payers": payer_amounts,
    }
    records = storage.load()
    if not isinstance(records, list):
        records = []
    records.append(expense)
    storage.save(records)
    return {"redirect": "/page3", "msg": "บันทึกค่าใช้จ่ายแล้ว"}
