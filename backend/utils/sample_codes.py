"""Curated sample Python programs for CodeMate AI demonstrations and learning.

Each sample showcases realistic beginner anti-patterns:
- Cryptic variable names
- Missing docstrings
- Mutable default arguments
- Deeply nested conditions
- Unused imports and bare exceptions
"""

from typing import Dict, List


SAMPLE_PROGRAMS: Dict[str, Dict[str, str]] = {
    "Student Grade Calculator": {
        "description": "Calculates student scores, averages, and letter grades. Contains poor naming (x, y, s), missing docstrings, and redundant conditionals.",
        "code": '''import math

def calc(g, w=None):
    # calculates the weighted score
    t = 0
    wt = 0
    for i in range(len(g)):
        if w != None:
            t = t + g[i] * w[i]
            wt = wt + w[i]
        else:
            t = t + g[i]
            wt = wt + 1
    res = t / wt
    return res

def get_letter(s):
    if s >= 90:
        return 'A'
    else:
        if s >= 80:
            return 'B'
        else:
            if s >= 70:
                return 'C'
            else:
                if s >= 60:
                    return 'D'
                else:
                    return 'F'

def Process_Students(data):
    out = {}
    for k in data:
        scores = data[k]
        avg = calc(scores)
        grade = get_letter(avg)
        out[k] = {"average": avg, "grade": grade}
    return out

# Sample run
students = {
    "Alice": [88, 92, 79, 95],
    "Bob": [65, 70, 58, 62],
    "Charlie": [95, 98, 92, 100]
}

report = Process_Students(students)
print("Student Report:", report)
'''
    },
    "Inventory Store Manager": {
        "description": "Demonstrates mutable default arguments (items=[]), long functions, and deep nesting.",
        "code": '''def manage_inventory(action, item_name=None, qty=0, price=0.0, store_items=[]):
    # Manages a store inventory
    if action == "add":
        found = False
        for item in store_items:
            if item["name"] == item_name:
                item["qty"] = item["qty"] + qty
                item["price"] = price
                found = True
                break
        if not found:
            store_items.append({"name": item_name, "qty": qty, "price": price})
        return store_items
    elif action == "remove":
        for item in store_items:
            if item["name"] == item_name:
                if item["qty"] >= qty:
                    item["qty"] = item["qty"] - qty
                    return True
                else:
                    print("Error: insufficient stock!")
                    return False
        return False
    elif action == "total_value":
        total = 0.0
        for item in store_items:
            if item["qty"] > 0:
                if item["price"] > 0:
                    total = total + (item["qty"] * item["price"])
        return total
    else:
        print("Unknown action")
        return None

# Test runs
store = manage_inventory("add", "Notebook", 10, 2.50)
manage_inventory("add", "Pen", 50, 1.20, store)
total = manage_inventory("total_value", store_items=store)
print("Total store inventory value:", total)
'''
    },
    "Text Analyzer & Word Counter": {
        "description": "Features unused imports (sys, math), bare except clause, non-snake_case functions, and magic numbers.",
        "code": '''import sys
import os
import math
import string

def ProcessText(RAW_TEXT, min_len=3):
    # cleans and counts words
    try:
        words = RAW_TEXT.split()
        d = {}
        for w in words:
            # strip punctuation
            clean = ""
            for c in w:
                if c not in string.punctuation:
                    clean = clean + c.lower()
            if len(clean) >= min_len:
                if clean in d:
                    d[clean] = d[clean] + 1
                else:
                    d[clean] = 1
        
        # find top 5 words
        sorted_words = sorted(d.items(), key=lambda item: item[1], reverse=True)
        top = sorted_words[:5]
        return {"counts": d, "top_5": top, "total_counted": len(d)}
    except:
        print("Something went wrong while processing text")
        return None

sample_paragraph = """
Python is an easy to learn, powerful programming language. 
Python has efficient high-level data structures and a simple but effective approach to object-oriented programming. 
Python elegant syntax and dynamic typing make it an ideal language for scripting.
"""

result = ProcessText(sample_paragraph)
print("Analysis:", result)
'''
    },
    "Bank Account System": {
        "description": "Basic object-oriented class without encapsulation, missing type hints, missing docstrings, and unvalidated operations.",
        "code": '''class bank_account:
    def __init__(self, owner, balance=0.0):
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amt):
        if amt > 0:
            self.balance = self.balance + amt
            self.history.append("deposit: " + str(amt))
            return True
        return False

    def withdraw(self, amt):
        if amt > 0:
            if self.balance >= amt:
                self.balance = self.balance - amt
                self.history.append("withdraw: " + str(amt))
                return True
        return False

    def get_summary(self):
        s = "Account owner: " + self.owner + ", Current Balance: " + str(self.balance)
        return s

acc = bank_account("Jordan", 500.0)
acc.deposit(150.0)
acc.withdraw(75.0)
print(acc.get_summary())
'''
    },
    "Math & Prime Utilities": {
        "description": "Recursive Fibonacci with potential stack overflow, inefficient prime checker, and cryptic variable names.",
        "code": '''def fib(n):
    # calculates fibonacci recursively
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)

def is_prime(num):
    if num <= 1:
        return False
    # checks every number up to num
    for i in range(2, num):
        if (num % i) == 0:
            return False
    return True

def get_primes_in_range(start, end):
    lst = []
    for x in range(start, end + 1):
        if is_prime(x):
            lst.append(x)
    return lst

print("10th Fibonacci number:", fib(10))
print("Primes between 10 and 50:", get_primes_in_range(10, 50))
'''
    }
}


def get_sample_names() -> List[str]:
    """Return list of available sample program titles."""
    return list(SAMPLE_PROGRAMS.keys())


def get_sample_code(name: str) -> str:
    """Return the source code for a given sample name."""
    sample = SAMPLE_PROGRAMS.get(name)
    return sample["code"] if sample else ""


def get_sample_description(name: str) -> str:
    """Return the description for a given sample name."""
    sample = SAMPLE_PROGRAMS.get(name)
    return sample["description"] if sample else ""
