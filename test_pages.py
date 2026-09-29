"""test_pages.py — GIVEN, DO NOT EDIT.   Run:  pytest

Four tests: page1, page2, page3 each load (not a "not built yet" page, no TODO left in
their source), and team.json has been filled in.
This is the "pages running" part of check_project.py, in pytest form.
"""
import os

import pytest

import app as webapp

HERE = os.path.dirname(os.path.abspath(__file__))
NOT_BUILT_MARK = "ยังไม่พร้อม"


@pytest.fixture
def client():
    return webapp.app.test_client()


def _source(rel):
    with open(os.path.join(HERE, *rel.split("/")), encoding="utf-8") as f:
        return f.read()


@pytest.mark.parametrize("name", ["page1", "page2", "page3"])
def test_page_loads(client, name):
    r = client.get("/" + name)
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert NOT_BUILT_MARK not in html, f"/{name} is not built yet — see PAGES.md"
    assert "TODO" not in _source("pages/" + name + ".py"), f"pages/{name}.py still has a TODO"
    assert "TODO" not in _source("templates/" + name + ".html"), f"templates/{name}.html still has a TODO"


def test_team_page_filled(client):
    html = client.get("/team").get_data(as_text=True)
    assert "66xxxxxxx" not in html, "team.json still has the placeholder student ids"


def test_group_creation_form_is_visible(client):
    html = client.get("/page1").get_data(as_text=True)
    assert "สร้างกลุ่ม" in html or "Create Group" in html
    assert "ชื่อกลุ่ม" in html
    assert "ชื่อสมาชิก" in html


def test_expense_form_supports_multiple_payers(client):
    html = client.get("/page2").get_data(as_text=True)
    assert "จำนวนเงินรวม" in html
    assert "คนที่ออกเงิน" in html
    assert "เงินที่แต่ละคนออก" in html


def test_create_group_redirects_to_page2(client):
    r = client.post("/page1", data={"group_name": "กลุ่มทดสอบ", "member_names": "คนA\nคนB\nคนC"}, follow_redirects=False)
    assert r.status_code == 302
    assert "/page2" in r.headers.get("Location", "")


def test_expense_amount_must_match_total_payer_amounts(client):
    data = {
        "expense_name": "อาหาร",
        "amount": "500",
        "eater_นิว": "on",
        "eater_กาย": "on",
        "eater_เฟิร์น": "on",
        "payer_นิว": "on",
        "payer_amount_นิว": "300",
        "payer_กาย": "on",
        "payer_amount_กาย": "100",
    }
    r = client.post("/page2", data=data, follow_redirects=False)
    assert r.status_code == 302
    assert "msg=" in r.headers.get("Location", "")


def test_valid_expense_redirects_to_page3(client):
    data = {
        "expense_name": "อาหาร",
        "amount": "500",
        "eater_นิว": "on",
        "eater_กาย": "on",
        "eater_เฟิร์น": "on",
        "payer_นิว": "on",
        "payer_amount_นิว": "300",
        "payer_กาย": "on",
        "payer_amount_กาย": "200",
    }
    r = client.post("/page2", data=data, follow_redirects=False)
    assert r.status_code == 302
    assert "/page3" in r.headers.get("Location", "")
