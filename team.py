"""pages/team.py — the team page. Already works: it shows team.json.

Week 0 task: open team.json, put in your group name, topic, and every member's
name / student id / role / task. Then look at /team. You may also change this file
and templates/team.html to make the page your own.
"""
import json
import os

TITLE = "ทีม"

TITLES = ["นางสาว", "นาย", "นาง", "ว่าที่ร้อยตรี", "Mr.", "Ms.", "Miss"]


def initial_of(name):
    """First letter of the given name, skipping Thai/English titles."""
    name = name.strip()
    for t in TITLES:
        if name.startswith(t):
            name = name[len(t):].strip()
    if name == "":
        return "?"
    return name[0]


def build():
    group = {
        "name": "comten",
        "section": "section 1",
        "topic": "Project Demo",
        "description": "หน้า Team แบบคงที่ ไม่ต้องเปลี่ยนตามข้อมูลภายนอก",
    }

    members = [
        {
            "name": "นางสาวกิตติยา ม่วงอยู่",
            "id": "69130040302",
            "role": "Project Lead(PM)",
            "task": "Page 1",
            "initial": "1",
        },
        {
            "name": "นายกมล เกษียร",
            "id": "69130040049",
            "role": "Backend Dev (Python), Frontend\nDev (HTML/CSS)",
            "task": "page2",
            "initial": "2",
        },
        {
            "name": "นายกิตติศักดิ์ ดวงแก้ว",
            "id": "69130040326",
            "role": "Frontend Dev (HTML/CSS), Backend\nDev (Python)",
            "task": "home + team page",
            "initial": "3",
        },
        {
            "name": "นางสาวกัญญภัส รัตนพิมพ์",
            "id": "69130040195",
            "role": "Data Engineer (data.json + models),\nDevOps (Git/GitHubsetup)",
            "task": "Page3",
            "initial": "4",
        },
    ]
    return {"group": group, "members": members, "count": len(members)}
