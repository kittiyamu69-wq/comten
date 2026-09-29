"""pages/page1.py — Create group and member list."""
import json
import os

import storage

TITLE = "สร้างกลุ่ม"

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


def _save_group_state(data):
    with open(GROUP_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_team():
    try:
        with open(TEAM_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"group": {"name": "กลุ่มค่าใช้จ่าย", "section": "Section 01", "topic": "จัดการค่าใช้จ่ายกลุ่ม", "description": ""}, "members": []}
    if not isinstance(data, dict):
        data = {"group": {"name": "กลุ่มค่าใช้จ่าย", "section": "Section 01", "topic": "จัดการค่าใช้จ่ายกลุ่ม", "description": ""}, "members": []}
    return data


def _save_team(data):
    with open(TEAM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _parse_member_names(value):
    if value is None:
        return []
    if isinstance(value, list):
        entries = value
    elif isinstance(value, str):
        entries = value.replace("\r", "\n").split("\n")
        if "," in value and "\n" not in value:
            entries = [part.strip() for part in value.split(",")]
    else:
        entries = [str(value)]

    names = []
    for entry in entries:
        if isinstance(entry, list):
            names.extend(_parse_member_names(entry))
            continue
        name = str(entry).strip()
        if name and name.lower() != "undefined":
            names.append(name)
    cleaned = []
    seen = set()
    for name in names:
        key = name.casefold()
        if key not in seen:
            seen.add(key)
            cleaned.append(name)
    return cleaned


def build():
    state = _load_group_state()
    team_data = _load_team()
    names = state.get("members") or [m.get("name") for m in (team_data.get("members") or []) if m.get("name")]
    members = [{"name": name} for name in names]
    group = team_data.get("group") or {}
    return {
        "group": group,
        "members": members,
        "member_count": len(members),
        "group_name": state.get("group_name") or group.get("name") or "กลุ่มค่าใช้จ่าย",
    }


def handle(form):
    group_name = (form.get("group_name") or form.get("name") or "กลุ่มค่าใช้จ่าย").strip()
    if not group_name:
        group_name = "กลุ่มค่าใช้จ่าย"

    names = _parse_member_names(form.get("member_names") or form.get("members") or form.get("member_name") or [])
    if not names:
        names = [member.get("name", "") for member in _load_team().get("members", []) if member.get("name")]
    if not names:
        names = ["นิว", "กาย", "เฟิร์น"]

    _save_group_state({"group_name": group_name, "members": names})
    storage.save([])
    return {"redirect": "/page2", "msg": "สร้างกลุ่มเรียบร้อยแล้ว"}
