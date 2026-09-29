"""Expense model for the group expense tracker."""


class ExpenseItem:
    def __init__(self, name, amount, people=None):
        self.name = name
        self.amount = float(amount)
        self.people = people or []

    def describe(self):
        people_text = ", ".join(self.people) if self.people else "ทุกคน"
        return f"{self.name} จ่ายรวม {self.amount:.2f} บาท สำหรับ {people_text}"

    def total_per_person(self):
        if not self.people:
            return self.amount
        return self.amount / len(self.people)
