"""
app/problems_data/sql_generators.py — Scaled input generators for SQL and database benchmarks.
"""
from __future__ import annotations
import random


def generate_sql_employee(n: int, seed: int) -> str:
    """Generate DDL and n rows for Employee and Department tables."""
    rng = random.Random(seed)
    lines = [
        "DROP TABLE IF EXISTS Employee;",
        "DROP TABLE IF EXISTS Department;",
        "CREATE TABLE Department (id INT PRIMARY KEY, name VARCHAR(50));",
        "CREATE TABLE Employee (id INT PRIMARY KEY, name VARCHAR(50), salary INT, departmentId INT);",
        "INSERT INTO Department VALUES (1, 'IT'), (2, 'Sales'), (3, 'HR'), (4, 'Engineering');",
    ]
    
    first_names = ["Joe", "Henry", "Sam", "Max", "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]
    batch_values = []
    for i in range(1, n + 1):
        name = f"{rng.choice(first_names)}_{i}"
        salary = rng.randint(30000, 150000)
        dept_id = rng.choice([1, 2, 3, 4, None])
        dept_val = str(dept_id) if dept_id is not None else "NULL"
        batch_values.append(f"({i}, '{name}', {salary}, {dept_val})")
        if len(batch_values) >= 500:
            lines.append(f"INSERT INTO Employee VALUES {', '.join(batch_values)};")
            batch_values = []
    if batch_values:
        lines.append(f"INSERT INTO Employee VALUES {', '.join(batch_values)};")
    
    return "\n".join(lines)


def generate_sql_person_address(n: int, seed: int) -> str:
    """Generate DDL and n rows for Person and Address tables."""
    rng = random.Random(seed)
    lines = [
        "DROP TABLE IF EXISTS Person;",
        "DROP TABLE IF EXISTS Address;",
        "CREATE TABLE Person (personId INT PRIMARY KEY, lastName VARCHAR(50), firstName VARCHAR(50));",
        "CREATE TABLE Address (addressId INT PRIMARY KEY, personId INT, city VARCHAR(50), state VARCHAR(50));",
    ]
    
    first_names = ["Allen", "Bob", "Alice", "John", "Emma", "Olivia", "James", "William"]
    last_names = ["Wang", "Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson"]
    cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]
    states = ["New York", "California", "Illinois", "Texas", "Arizona", "Pennsylvania"]

    p_values = []
    a_values = []
    for i in range(1, n + 1):
        fn = rng.choice(first_names)
        ln = rng.choice(last_names)
        p_values.append(f"({i}, '{ln}', '{fn}')")
        if rng.random() > 0.3:  # 70% have address
            city = rng.choice(cities)
            state = rng.choice(states)
            a_values.append(f"({i}, {i}, '{city}', '{state}')")
            
        if len(p_values) >= 500:
            lines.append(f"INSERT INTO Person VALUES {', '.join(p_values)};")
            p_values = []
        if len(a_values) >= 500:
            lines.append(f"INSERT INTO Address VALUES {', '.join(a_values)};")
            a_values = []
            
    if p_values:
        lines.append(f"INSERT INTO Person VALUES {', '.join(p_values)};")
    if a_values:
        lines.append(f"INSERT INTO Address VALUES {', '.join(a_values)};")

    return "\n".join(lines)


def generate_sql_customers_orders(n: int, seed: int) -> str:
    """Generate DDL and n rows for Customers and Orders tables."""
    rng = random.Random(seed)
    lines = [
        "DROP TABLE IF EXISTS Customers;",
        "DROP TABLE IF EXISTS Orders;",
        "CREATE TABLE Customers (id INT PRIMARY KEY, name VARCHAR(50));",
        "CREATE TABLE Orders (id INT PRIMARY KEY, customerId INT);",
    ]
    names = ["Joe", "Henry", "Sam", "Max", "Alice", "Bob", "Charlie", "David"]
    c_values = []
    o_values = []
    order_id = 1
    for i in range(1, n + 1):
        c_values.append(f"({i}, '{rng.choice(names)}_{i}')")
        if rng.random() > 0.4:
            for _ in range(rng.randint(1, 3)):
                o_values.append(f"({order_id}, {i})")
                order_id += 1
        if len(c_values) >= 500:
            lines.append(f"INSERT INTO Customers VALUES {', '.join(c_values)};")
            c_values = []
        if len(o_values) >= 500:
            lines.append(f"INSERT INTO Orders VALUES {', '.join(o_values)};")
            o_values = []
    if c_values:
        lines.append(f"INSERT INTO Customers VALUES {', '.join(c_values)};")
    if o_values:
        lines.append(f"INSERT INTO Orders VALUES {', '.join(o_values)};")
    return "\n".join(lines)


def generate_sql_scores(n: int, seed: int) -> str:
    """Generate DDL and n rows for Scores table."""
    rng = random.Random(seed)
    lines = [
        "DROP TABLE IF EXISTS Scores;",
        "CREATE TABLE Scores (id INT PRIMARY KEY, score DECIMAL(3,2));",
    ]
    batch = []
    for i in range(1, n + 1):
        score = round(rng.uniform(3.0, 4.0), 2)
        batch.append(f"({i}, {score})")
        if len(batch) >= 500:
            lines.append(f"INSERT INTO Scores VALUES {', '.join(batch)};")
            batch = []
    if batch:
        lines.append(f"INSERT INTO Scores VALUES {', '.join(batch)};")
    return "\n".join(lines)


def generate_sql_weather(n: int, seed: int) -> str:
    """Generate DDL and n rows for Weather table with dates and temperatures."""
    from datetime import date, timedelta
    rng = random.Random(seed)
    lines = [
        "DROP TABLE IF EXISTS Weather;",
        "CREATE TABLE Weather (id INT PRIMARY KEY, recordDate DATE, temperature INT);",
    ]
    base_date = date(2023, 1, 1)
    batch = []
    for i in range(1, n + 1):
        curr_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        temp = rng.randint(-10, 40)
        batch.append(f"({i}, '{curr_date}', {temp})")
        if len(batch) >= 500:
            lines.append(f"INSERT INTO Weather VALUES {', '.join(batch)};")
            batch = []
    if batch:
        lines.append(f"INSERT INTO Weather VALUES {', '.join(batch)};")
    return "\n".join(lines)


def generate_sql_generic(n: int, seed: int) -> str:
    """Generic SQL scaled generator."""
    return generate_sql_employee(n, seed)
