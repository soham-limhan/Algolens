"""
app/database_problems.py — Curated SQL and database problems with detailed problem statements,
schemas, test cases, and optimal solutions.
"""
from __future__ import annotations
import json


def sql_opt_sol(sql_code: str) -> str:
    """Format optimal SQL solution."""
    return json.dumps({
        "sql": sql_code.strip(),
        "mysql": sql_code.strip(),
    })


DATABASE_PROBLEMS = [
    # ── 1. Combine Two Tables ────────────────────────────────────────────────
    {
        "title": "Combine Two Tables",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": sql_opt_sol(
            """SELECT p.firstName, p.lastName, a.city, a.state
FROM Person p
LEFT JOIN Address a ON p.personId = a.personId;"""
        ),
        "generator_key": "sql_person_address",
        "description": (
            "Table: `Person`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `personId` | int | Primary key for this table. |\n"
            "| `lastName` | varchar | The last name of the person. |\n"
            "| `firstName` | varchar | The first name of the person. |\n\n"
            "Table: `Address`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `addressId` | int | Primary key for this table. |\n"
            "| `personId` | int | Foreign key referencing `Person.personId`. |\n"
            "| `city` | varchar | The city where the person resides. |\n"
            "| `state` | varchar | The state where the person resides. |\n\n"
            "### Problem Statement\n"
            "Write a solution to report the `firstName`, `lastName`, `city`, and `state` of each person in the `Person` table. "
            "If the address of a `personId` is not present in the `Address` table, report `null` instead for `city` and `state`.\n\n"
            "Return the result table in **any order**.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Person table:\n"
            "| personId | lastName | firstName |\n"
            "| :--- | :--- | :--- |\n"
            "| 1 | Wang | Allen |\n"
            "| 2 | Alice | Bob |\n\n"
            "Address table:\n"
            "| addressId | personId | city | state |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| 1 | 2 | New York City | New York |\n"
            "| 2 | 3 | Leetcode | California |\n\n"
            "**Output:**\n"
            "| firstName | lastName | city | state |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| Allen | Wang | null | null |\n"
            "| Bob | Alice | New York City | New York |\n\n"
            "**Explanation:**\n"
            "There is no address in the `Address` table for `personId = 1` (`Allen Wang`), so we report `null` for `city` and `state`.\n\n"
            "<details><summary>💡 Hint</summary>Use a `LEFT JOIN` on `Person.personId = Address.personId` so every row in `Person` is preserved even if it has no matching address row.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Person (personId INT PRIMARY KEY, lastName VARCHAR(50), firstName VARCHAR(50));\n"
                    "INSERT INTO Person VALUES (1, 'Wang', 'Allen'), (2, 'Alice', 'Bob');\n"
                    "CREATE TABLE Address (addressId INT PRIMARY KEY, personId INT, city VARCHAR(50), state VARCHAR(50));\n"
                    "INSERT INTO Address VALUES (1, 2, 'New York City', 'New York'), (2, 3, 'Leetcode', 'California');\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["firstName", "lastName", "city", "state"],
                    "rows": [["Allen", "Wang", None, None], ["Bob", "Alice", "New York City", "New York"]]
                }),
                "comparator_type": "sql_table",
            },
            {
                "input": (
                    "CREATE TABLE Person (personId INT PRIMARY KEY, lastName VARCHAR(50), firstName VARCHAR(50));\n"
                    "INSERT INTO Person VALUES (1, 'Smith', 'John');\n"
                    "CREATE TABLE Address (addressId INT PRIMARY KEY, personId INT, city VARCHAR(50), state VARCHAR(50));\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["firstName", "lastName", "city", "state"],
                    "rows": [["John", "Smith", None, None]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [
            {
                "pattern_type": "missing_left_join",
                "hint_text": "An INNER JOIN will drop persons without addresses. Use a LEFT JOIN from Person to Address."
            }
        ],
    },

    # ── 2. Employees Earning More Than Their Managers ─────────────────────────
    {
        "title": "Employees Earning More Than Their Managers",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": sql_opt_sol(
            """SELECT e.name AS Employee
FROM Employee e
JOIN Employee m ON e.managerId = m.id
WHERE e.salary > m.salary;"""
        ),
        "generator_key": "sql_employee",
        "description": (
            "Table: `Employee`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key for this table. |\n"
            "| `name` | varchar | The employee's name. |\n"
            "| `salary` | int | The employee's salary. |\n"
            "| `managerId` | int | The ID of the employee's manager (referencing `id`), or `null` if no manager. |\n\n"
            "### Problem Statement\n"
            "Write a solution to find the employees who earn **strictly more** than their managers.\n\n"
            "Return the result table with single column `Employee` in **any order**.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Employee table:\n"
            "| id | name | salary | managerId |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| 1 | Joe | 70000 | 3 |\n"
            "| 2 | Henry | 80000 | 4 |\n"
            "| 3 | Sam | 60000 | null |\n"
            "| 4 | Max | 90000 | null |\n\n"
            "**Output:**\n"
            "| Employee |\n"
            "| :--- |\n"
            "| Joe |\n\n"
            "**Explanation:**\n"
            "`Joe` earns 70,000 and his manager `Sam` earns 60,000. `Henry` earns 80,000 while his manager `Max` earns 90,000.\n\n"
            "<details><summary>💡 Hint</summary>Perform a self-join between `Employee e` (employee) and `Employee m` (manager) on `e.managerId = m.id` and filter `WHERE e.salary > m.salary`.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Employee (id INT PRIMARY KEY, name VARCHAR(50), salary INT, managerId INT);\n"
                    "INSERT INTO Employee VALUES (1, 'Joe', 70000, 3), (2, 'Henry', 80000, 4), (3, 'Sam', 60000, NULL), (4, 'Max', 90000, NULL);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["Employee"],
                    "rows": [["Joe"]]
                }),
                "comparator_type": "sql_table",
            },
            {
                "input": (
                    "CREATE TABLE Employee (id INT PRIMARY KEY, name VARCHAR(50), salary INT, managerId INT);\n"
                    "INSERT INTO Employee VALUES (1, 'Alice', 50000, NULL), (2, 'Bob', 40000, 1);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["Employee"],
                    "rows": []
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 3. Duplicate Emails ───────────────────────────────────────────────────
    {
        "title": "Duplicate Emails",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": sql_opt_sol(
            """SELECT email AS Email
FROM Person
GROUP BY email
HAVING COUNT(email) > 1;"""
        ),
        "generator_key": "sql_generic",
        "description": (
            "Table: `Person`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key for this table. |\n"
            "| `email` | varchar | The person's email address. |\n\n"
            "### Problem Statement\n"
            "Write a solution to report all the **duplicate emails**. Note that it's guaranteed that the email field is not `NULL`.\n\n"
            "Return the result table with column name `Email` in **any order**.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Person table:\n"
            "| id | email |\n"
            "| :--- | :--- |\n"
            "| 1 | a@b.com |\n"
            "| 2 | c@d.com |\n"
            "| 3 | a@b.com |\n\n"
            "**Output:**\n"
            "| Email |\n"
            "| :--- |\n"
            "| a@b.com |\n\n"
            "<details><summary>💡 Hint</summary>Group by the `email` column and use the `HAVING COUNT(email) > 1` clause to filter only duplicates.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Person (id INT PRIMARY KEY, email VARCHAR(100));\n"
                    "INSERT INTO Person VALUES (1, 'a@b.com'), (2, 'c@d.com'), (3, 'a@b.com');\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["Email"],
                    "rows": [["a@b.com"]]
                }),
                "comparator_type": "sql_table",
            },
            {
                "input": (
                    "CREATE TABLE Person (id INT PRIMARY KEY, email VARCHAR(100));\n"
                    "INSERT INTO Person VALUES (1, 'john@example.com'), (2, 'bob@example.com');\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["Email"],
                    "rows": []
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 4. Customers Who Never Order ──────────────────────────────────────────
    {
        "title": "Customers Who Never Order",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": sql_opt_sol(
            """SELECT c.name AS Customers
FROM Customers c
LEFT JOIN Orders o ON c.id = o.customerId
WHERE o.id IS NULL;"""
        ),
        "generator_key": "sql_customers_orders",
        "description": (
            "Table: `Customers`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key for this table. |\n"
            "| `name` | varchar | The customer's name. |\n\n"
            "Table: `Orders`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key for this table. |\n"
            "| `customerId` | int | Foreign key referencing `Customers.id`. |\n\n"
            "### Problem Statement\n"
            "Write a solution to find all customers who **never place any orders**.\n\n"
            "Return the result table with single column `Customers` in **any order**.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Customers table:\n"
            "| id | name |\n"
            "| :--- | :--- |\n"
            "| 1 | Joe |\n"
            "| 2 | Henry |\n"
            "| 3 | Sam |\n"
            "| 4 | Max |\n\n"
            "Orders table:\n"
            "| id | customerId |\n"
            "| :--- | :--- |\n"
            "| 1 | 3 |\n"
            "| 2 | 1 |\n\n"
            "**Output:**\n"
            "| Customers |\n"
            "| :--- |\n"
            "| Henry |\n"
            "| Max |\n\n"
            "<details><summary>💡 Hint</summary>Use `LEFT JOIN Orders ON Customers.id = Orders.customerId` and check `WHERE Orders.id IS NULL`, or use `WHERE id NOT IN (SELECT customerId FROM Orders)`.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Customers (id INT PRIMARY KEY, name VARCHAR(50));\n"
                    "INSERT INTO Customers VALUES (1, 'Joe'), (2, 'Henry'), (3, 'Sam'), (4, 'Max');\n"
                    "CREATE TABLE Orders (id INT PRIMARY KEY, customerId INT);\n"
                    "INSERT INTO Orders VALUES (1, 3), (2, 1);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["Customers"],
                    "rows": [["Henry"], ["Max"]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 5. Second Highest Salary ──────────────────────────────────────────────
    {
        "title": "Second Highest Salary",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": sql_opt_sol(
            """SELECT (
    SELECT DISTINCT salary
    FROM Employee
    ORDER BY salary DESC
    LIMIT 1 OFFSET 1
) AS SecondHighestSalary;"""
        ),
        "generator_key": "sql_employee",
        "description": (
            "Table: `Employee`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key for this table. |\n"
            "| `salary` | int | The employee's salary. |\n\n"
            "### Problem Statement\n"
            "Write a solution to find the **second highest distinct salary** from the `Employee` table. "
            "If there is no second highest salary, return `null` (or `NULL` in SQL).\n\n"
            "Return the result table with single column `SecondHighestSalary`.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Employee table:\n"
            "| id | salary |\n"
            "| :--- | :--- |\n"
            "| 1 | 100 |\n"
            "| 2 | 200 |\n"
            "| 3 | 300 |\n\n"
            "**Output:**\n"
            "| SecondHighestSalary |\n"
            "| :--- |\n"
            "| 200 |\n\n"
            "### Example 2\n"
            "**Input:**\n\n"
            "Employee table:\n"
            "| id | salary |\n"
            "| :--- | :--- |\n"
            "| 1 | 100 |\n\n"
            "**Output:**\n"
            "| SecondHighestSalary |\n"
            "| :--- |\n"
            "| null |\n\n"
            "<details><summary>💡 Hint</summary>Wrapping `(SELECT DISTINCT salary FROM Employee ORDER BY salary DESC LIMIT 1 OFFSET 1)` inside a scalar subquery automatically returns `NULL` when the offset is out of range.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Employee (id INT PRIMARY KEY, salary INT);\n"
                    "INSERT INTO Employee VALUES (1, 100), (2, 200), (3, 300);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["SecondHighestSalary"],
                    "rows": [[200]]
                }),
                "comparator_type": "sql_table",
            },
            {
                "input": (
                    "CREATE TABLE Employee (id INT PRIMARY KEY, salary INT);\n"
                    "INSERT INTO Employee VALUES (1, 100);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["SecondHighestSalary"],
                    "rows": [[None]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 6. Department Highest Salary ──────────────────────────────────────────
    {
        "title": "Department Highest Salary",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": sql_opt_sol(
            """SELECT d.name AS Department, e.name AS Employee, e.salary AS Salary
FROM Employee e
JOIN Department d ON e.departmentId = d.id
WHERE (e.departmentId, e.salary) IN (
    SELECT departmentId, MAX(salary)
    FROM Employee
    GROUP BY departmentId
);"""
        ),
        "generator_key": "sql_employee",
        "description": (
            "Table: `Employee`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key for this table. |\n"
            "| `name` | varchar | The employee's name. |\n"
            "| `salary` | int | The employee's salary. |\n"
            "| `departmentId` | int | Foreign key referencing `Department.id`. |\n\n"
            "Table: `Department`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key for this table. |\n"
            "| `name` | varchar | The department's name. |\n\n"
            "### Problem Statement\n"
            "Write a solution to find employees who have the **highest salary** in each of the departments.\n\n"
            "Return the result table with columns `Department`, `Employee`, and `Salary` in **any order**.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Employee table:\n"
            "| id | name | salary | departmentId |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| 1 | Joe | 70000 | 1 |\n"
            "| 2 | Jim | 90000 | 1 |\n"
            "| 3 | Henry | 80000 | 2 |\n"
            "| 4 | Sam | 60000 | 2 |\n"
            "| 5 | Max | 90000 | 1 |\n\n"
            "Department table:\n"
            "| id | name |\n"
            "| :--- | :--- |\n"
            "| 1 | IT |\n"
            "| 2 | Sales |\n\n"
            "**Output:**\n"
            "| Department | Employee | Salary |\n"
            "| :--- | :--- | :--- |\n"
            "| IT | Jim | 90000 |\n"
            "| IT | Max | 90000 |\n"
            "| Sales | Henry | 80000 |\n\n"
            "<details><summary>💡 Hint</summary>Group by `departmentId` to find `MAX(salary)` per department, then join or filter where `(departmentId, salary)` matches the max pair.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Department (id INT PRIMARY KEY, name VARCHAR(50));\n"
                    "INSERT INTO Department VALUES (1, 'IT'), (2, 'Sales');\n"
                    "CREATE TABLE Employee (id INT PRIMARY KEY, name VARCHAR(50), salary INT, departmentId INT);\n"
                    "INSERT INTO Employee VALUES (1, 'Joe', 70000, 1), (2, 'Jim', 90000, 1), (3, 'Henry', 80000, 2), (4, 'Sam', 60000, 2), (5, 'Max', 90000, 1);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["Department", "Employee", "Salary"],
                    "rows": [["IT", "Jim", 90000], ["IT", "Max", 90000], ["Sales", "Henry", 80000]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 7. Rank Scores ────────────────────────────────────────────────────────
    {
        "title": "Rank Scores",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n log n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": sql_opt_sol(
            """SELECT score, DENSE_RANK() OVER (ORDER BY score DESC) AS `rank`
FROM Scores
ORDER BY score DESC;"""
        ),
        "generator_key": "sql_scores",
        "description": (
            "Table: `Scores`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key for this table. |\n"
            "| `score` | decimal | The participant's score. |\n\n"
            "### Problem Statement\n"
            "Write a solution to find the rank of the scores. The ranking should be calculated according to the following rules:\n"
            "- The scores should be ranked from the highest to the lowest.\n"
            "- If there is a tie between two scores, both should have the same ranking.\n"
            "- After a tie, the next ranking number should be the next consecutive integer value (i.e. no holes between ranks).\n\n"
            "Return the result table ordered by `score` in **descending order**.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Scores table:\n"
            "| id | score |\n"
            "| :--- | :--- |\n"
            "| 1 | 3.50 |\n"
            "| 2 | 3.65 |\n"
            "| 3 | 4.00 |\n"
            "| 4 | 3.85 |\n"
            "| 5 | 4.00 |\n"
            "| 6 | 3.65 |\n\n"
            "**Output:**\n"
            "| score | rank |\n"
            "| :--- | :--- |\n"
            "| 4.00 | 1 |\n"
            "| 4.00 | 1 |\n"
            "| 3.85 | 2 |\n"
            "| 3.65 | 3 |\n"
            "| 3.65 | 3 |\n"
            "| 3.50 | 4 |\n\n"
            "<details><summary>💡 Hint</summary>The window function `DENSE_RANK() OVER (ORDER BY score DESC)` computes consecutive ranking without gaps.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Scores (id INT PRIMARY KEY, score DECIMAL(3,2));\n"
                    "INSERT INTO Scores VALUES (1, 3.50), (2, 3.65), (3, 4.00), (4, 3.85), (5, 4.00), (6, 3.65);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["score", "rank"],
                    "rows": [[4.0, 1], [4.0, 1], [3.85, 2], [3.65, 3], [3.65, 3], [3.5, 4]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 8. Consecutive Numbers ────────────────────────────────────────────────
    {
        "title": "Consecutive Numbers",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": sql_opt_sol(
            """SELECT DISTINCT l1.num AS ConsecutiveNums
FROM Logs l1
JOIN Logs l2 ON l1.id = l2.id - 1
JOIN Logs l3 ON l1.id = l3.id - 2
WHERE l1.num = l2.num AND l2.num = l3.num;"""
        ),
        "generator_key": "sql_generic",
        "description": (
            "Table: `Logs`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Auto-increment primary key. |\n"
            "| `num` | varchar | The logged number. |\n\n"
            "### Problem Statement\n"
            "Find all numbers that appear **at least three times consecutively**.\n\n"
            "Return the result table with column name `ConsecutiveNums` in **any order**.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Logs table:\n"
            "| id | num |\n"
            "| :--- | :--- |\n"
            "| 1 | 1 |\n"
            "| 2 | 1 |\n"
            "| 3 | 1 |\n"
            "| 4 | 2 |\n"
            "| 5 | 1 |\n"
            "| 6 | 2 |\n"
            "| 7 | 2 |\n\n"
            "**Output:**\n"
            "| ConsecutiveNums |\n"
            "| :--- |\n"
            "| 1 |\n\n"
            "<details><summary>💡 Hint</summary>Use either `LEAD()` and `LAG()` window functions or join `Logs` to itself three times on `l1.id = l2.id - 1` and `l2.id = l3.id - 1`.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Logs (id INT PRIMARY KEY, num INT);\n"
                    "INSERT INTO Logs VALUES (1, 1), (2, 1), (3, 1), (4, 2), (5, 1), (6, 2), (7, 2);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["ConsecutiveNums"],
                    "rows": [[1]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 9. Department Top Three Salaries ──────────────────────────────────────
    {
        "title": "Department Top Three Salaries",
        "difficulty": "hard",
        "optimal_time_complexity": "O(n log n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": sql_opt_sol(
            """WITH RankedEmployees AS (
    SELECT
        d.name AS Department,
        e.name AS Employee,
        e.salary AS Salary,
        DENSE_RANK() OVER (PARTITION BY e.departmentId ORDER BY e.salary DESC) AS rnk
    FROM Employee e
    JOIN Department d ON e.departmentId = d.id
)
SELECT Department, Employee, Salary
FROM RankedEmployees
WHERE rnk <= 3;"""
        ),
        "generator_key": "sql_employee",
        "description": (
            "Table: `Employee`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key. |\n"
            "| `name` | varchar | Employee name. |\n"
            "| `salary` | int | Employee salary. |\n"
            "| `departmentId` | int | Foreign key referencing `Department.id`. |\n\n"
            "Table: `Department`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key. |\n"
            "| `name` | varchar | Department name. |\n\n"
            "### Problem Statement\n"
            "A company's executives are interested in seeing who earns the most money in each department. "
            "A **high earner** in a department is an employee who has a salary in the **top three unique salaries** for that department.\n\n"
            "Write a solution to find the employees who are high earners in each of the departments.\n\n"
            "Return the result table in **any order**.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Employee table:\n"
            "| id | name | salary | departmentId |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| 1 | Joe | 85000 | 1 |\n"
            "| 2 | Henry | 80000 | 2 |\n"
            "| 3 | Sam | 60000 | 2 |\n"
            "| 4 | Max | 90000 | 1 |\n"
            "| 5 | Janet | 69000 | 1 |\n"
            "| 6 | Randy | 85000 | 1 |\n"
            "| 7 | Will | 70000 | 1 |\n\n"
            "Department table:\n"
            "| id | name |\n"
            "| :--- | :--- |\n"
            "| 1 | IT |\n"
            "| 2 | Sales |\n\n"
            "**Output:**\n"
            "| Department | Employee | Salary |\n"
            "| :--- | :--- | :--- |\n"
            "| IT | Max | 90000 |\n"
            "| IT | Joe | 85000 |\n"
            "| IT | Randy | 85000 |\n"
            "| IT | Will | 70000 |\n"
            "| Sales | Henry | 80000 |\n"
            "| Sales | Sam | 60000 |\n\n"
            "<details><summary>💡 Hint</summary>Use a Common Table Expression (CTE) with `DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC)` and filter `rnk <= 3`.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Department (id INT PRIMARY KEY, name VARCHAR(50));\n"
                    "INSERT INTO Department VALUES (1, 'IT'), (2, 'Sales');\n"
                    "CREATE TABLE Employee (id INT PRIMARY KEY, name VARCHAR(50), salary INT, departmentId INT);\n"
                    "INSERT INTO Employee VALUES (1, 'Joe', 85000, 1), (2, 'Henry', 80000, 2), (3, 'Sam', 60000, 2), (4, 'Max', 90000, 1), (5, 'Janet', 69000, 1), (6, 'Randy', 85000, 1), (7, 'Will', 70000, 1);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["Department", "Employee", "Salary"],
                    "rows": [["IT", "Max", 90000], ["IT", "Joe", 85000], ["IT", "Randy", 85000], ["IT", "Will", 70000], ["Sales", "Henry", 80000], ["Sales", "Sam", 60000]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 10. Delete Duplicate Emails ───────────────────────────────────────────
    {
        "title": "Delete Duplicate Emails",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n^2)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": sql_opt_sol(
            """DELETE p1 FROM Person p1, Person p2
WHERE p1.email = p2.email AND p1.id > p2.id;"""
        ),
        "generator_key": "sql_generic",
        "description": (
            "Table: `Person`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key. |\n"
            "| `email` | varchar | The person's email address. |\n\n"
            "### Problem Statement\n"
            "Write a solution to **delete all duplicate emails**, keeping only one unique email with the smallest `id`.\n\n"
            "For SQL queries, write a `DELETE` statement and not a `SELECT` statement.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Person table:\n"
            "| id | email |\n"
            "| :--- | :--- |\n"
            "| 1 | john@example.com |\n"
            "| 2 | bob@example.com |\n"
            "| 3 | john@example.com |\n\n"
            "**Output:**\n"
            "| id | email |\n"
            "| :--- | :--- |\n"
            "| 1 | john@example.com |\n"
            "| 2 | bob@example.com |\n\n"
            "<details><summary>💡 Hint</summary>In MySQL, you can delete with a self-join: `DELETE p1 FROM Person p1, Person p2 WHERE p1.email = p2.email AND p1.id > p2.id`.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Person (id INT PRIMARY KEY, email VARCHAR(100));\n"
                    "INSERT INTO Person VALUES (1, 'john@example.com'), (2, 'bob@example.com'), (3, 'john@example.com');\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["id", "email"],
                    "rows": [[1, "john@example.com"], [2, "bob@example.com"]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 11. Rising Temperature ────────────────────────────────────────────────
    {
        "title": "Rising Temperature",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n log n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": sql_opt_sol(
            """SELECT w1.id
FROM Weather w1
JOIN Weather w2 ON DATEDIFF(w1.recordDate, w2.recordDate) = 1
WHERE w1.temperature > w2.temperature;"""
        ),
        "generator_key": "sql_weather",
        "description": (
            "Table: `Weather`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key. |\n"
            "| `recordDate` | date | The date of the weather record. |\n"
            "| `temperature` | int | The temperature on that day. |\n\n"
            "### Problem Statement\n"
            "Write a solution to find all dates' `id` with higher temperatures compared to its **previous dates (yesterday)**.\n\n"
            "Return the result table with column `id` in **any order**.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Weather table:\n"
            "| id | recordDate | temperature |\n"
            "| :--- | :--- | :--- |\n"
            "| 1 | 2015-01-01 | 10 |\n"
            "| 2 | 2015-01-02 | 25 |\n"
            "| 3 | 2015-01-03 | 20 |\n"
            "| 4 | 2015-01-04 | 30 |\n\n"
            "**Output:**\n"
            "| id |\n"
            "| :--- |\n"
            "| 2 |\n"
            "| 4 |\n\n"
            "<details><summary>💡 Hint</summary>Join `Weather w1` and `Weather w2` using `DATEDIFF(w1.recordDate, w2.recordDate) = 1` and check `w1.temperature > w2.temperature`.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Weather (id INT PRIMARY KEY, recordDate DATE, temperature INT);\n"
                    "INSERT INTO Weather VALUES (1, '2015-01-01', 10), (2, '2015-01-02', 25), (3, '2015-01-03', 20), (4, '2015-01-04', 30);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["id"],
                    "rows": [[2], [4]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 12. Trips and Users ───────────────────────────────────────────────────
    {
        "title": "Trips and Users",
        "difficulty": "hard",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": sql_opt_sol(
            """SELECT
    t.request_at AS Day,
    ROUND(SUM(CASE WHEN t.status != 'completed' THEN 1.0 ELSE 0.0 END) / COUNT(*), 2) AS `Cancellation Rate`
FROM Trips t
JOIN Users c ON t.client_id = c.users_id AND c.banned = 'No'
JOIN Users d ON t.driver_id = d.users_id AND d.banned = 'No'
WHERE t.request_at BETWEEN '2013-10-01' AND '2013-10-03'
GROUP BY t.request_at;"""
        ),
        "generator_key": "sql_generic",
        "description": (
            "Table: `Trips`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key. |\n"
            "| `client_id` | int | Foreign key referencing `Users.users_id`. |\n"
            "| `driver_id` | int | Foreign key referencing `Users.users_id`. |\n"
            "| `city_id` | int | The city ID. |\n"
            "| `status` | enum | 'completed', 'cancelled_by_driver', 'cancelled_by_client'. |\n"
            "| `request_at` | date | The date of the request. |\n\n"
            "Table: `Users`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `users_id` | int | Primary key. |\n"
            "| `banned` | enum | 'Yes' or 'No'. |\n"
            "| `role` | enum | 'client', 'driver', 'partner'. |\n\n"
            "### Problem Statement\n"
            "The **cancellation rate** is computed by dividing the number of canceled (by client or driver) requests with **unbanned users** by the total number of requests with unbanned users on that day.\n\n"
            "Write a solution to find the cancellation rate of requests with unbanned users (both client and driver must not be banned) each day between `'2013-10-01'` and `'2013-10-03'`.\n\n"
            "Round `Cancellation Rate` to **two decimal points**.\n\n"
            "### Example 1\n"
            "**Output:**\n"
            "| Day | Cancellation Rate |\n"
            "| :--- | :--- |\n"
            "| 2013-10-01 | 0.33 |\n"
            "| 2013-10-02 | 0.00 |\n"
            "| 2013-10-03 | 0.50 |\n\n"
            "<details><summary>💡 Hint</summary>Join `Trips` with `Users` twice: once on `client_id` with `banned = 'No'`, and once on `driver_id` with `banned = 'No'`. Use `SUM(CASE WHEN status != 'completed' THEN 1.0 ELSE 0.0 END) / COUNT(*)`.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Users (users_id INT PRIMARY KEY, banned VARCHAR(10), role VARCHAR(20));\n"
                    "INSERT INTO Users VALUES (1, 'No', 'client'), (2, 'Yes', 'client'), (3, 'No', 'client'), (4, 'No', 'client'), (10, 'No', 'driver'), (11, 'No', 'driver'), (12, 'No', 'driver'), (13, 'No', 'driver');\n"
                    "CREATE TABLE Trips (id INT PRIMARY KEY, client_id INT, driver_id INT, city_id INT, status VARCHAR(50), request_at DATE);\n"
                    "INSERT INTO Trips VALUES (1, 1, 10, 1, 'completed', '2013-10-01'), (2, 2, 11, 1, 'cancelled_by_driver', '2013-10-01'), (3, 3, 12, 6, 'completed', '2013-10-01'), (4, 4, 13, 6, 'cancelled_by_client', '2013-10-01'), (5, 1, 10, 1, 'completed', '2013-10-02'), (6, 3, 11, 6, 'completed', '2013-10-02'), (7, 4, 12, 6, 'completed', '2013-10-02'), (8, 1, 12, 12, 'completed', '2013-10-03'), (9, 3, 10, 12, 'completed', '2013-10-03'), (10, 4, 13, 12, 'cancelled_by_driver', '2013-10-03');\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["Day", "Cancellation Rate"],
                    "rows": [["2013-10-01", 0.33], ["2013-10-02", 0.0], ["2013-10-03", 0.5]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 13. Market Analysis I ─────────────────────────────────────────────────
    {
        "title": "Market Analysis I",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": sql_opt_sol(
            """SELECT
    u.user_id AS buyer_id,
    u.join_date,
    COUNT(o.order_id) AS orders_in_2019
FROM Users u
LEFT JOIN Orders o ON u.user_id = o.buyer_id AND o.order_date LIKE '2019%'
GROUP BY u.user_id, u.join_date;"""
        ),
        "generator_key": "sql_generic",
        "description": (
            "Table: `Users`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `user_id` | int | Primary key. |\n"
            "| `join_date` | date | The date the user registered. |\n"
            "| `favorite_brand` | varchar | The user's favorite brand. |\n\n"
            "Table: `Orders`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `order_id` | int | Primary key. |\n"
            "| `order_date` | date | The date of the order. |\n"
            "| `item_id` | int | Foreign key to `Items`. |\n"
            "| `buyer_id` | int | Foreign key to `Users`. |\n"
            "| `seller_id` | int | Foreign key to `Users`. |\n\n"
            "### Problem Statement\n"
            "Write a solution to find for each user, their join date and the number of orders they made as a **buyer in 2019**.\n\n"
            "Return the result table with columns `buyer_id`, `join_date`, and `orders_in_2019` in **any order**.\n\n"
            "<details><summary>💡 Hint</summary>Use `LEFT JOIN Orders ON Users.user_id = Orders.buyer_id AND YEAR(order_date) = 2019` (or `order_date LIKE '2019%'`) and group by user.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Users (user_id INT PRIMARY KEY, join_date DATE, favorite_brand VARCHAR(50));\n"
                    "INSERT INTO Users VALUES (1, '2018-01-01', 'Lenovo'), (2, '2018-02-09', 'Samsung'), (3, '2018-01-19', 'LG'), (4, '2018-05-21', 'HP');\n"
                    "CREATE TABLE Orders (order_id INT PRIMARY KEY, order_date DATE, item_id INT, buyer_id INT, seller_id INT);\n"
                    "INSERT INTO Orders VALUES (1, '2019-08-01', 4, 1, 2), (2, '2018-08-02', 2, 1, 3), (3, '2019-08-03', 3, 2, 3), (4, '2018-08-04', 1, 4, 2), (5, '2018-08-04', 1, 3, 4), (6, '2019-08-05', 2, 2, 4);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["buyer_id", "join_date", "orders_in_2019"],
                    "rows": [[1, "2018-01-01", 1], [2, "2018-02-09", 2], [3, "2018-01-19", 0], [4, "2018-05-21", 0]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 14. Investments in 2016 ───────────────────────────────────────────────
    {
        "title": "Investments in 2016",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n log n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": sql_opt_sol(
            """SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM Insurance
WHERE tiv_2015 IN (
    SELECT tiv_2015 FROM Insurance GROUP BY tiv_2015 HAVING COUNT(*) > 1
)
AND (lat, lon) IN (
    SELECT lat, lon FROM Insurance GROUP BY lat, lon HAVING COUNT(*) = 1
);"""
        ),
        "generator_key": "sql_generic",
        "description": (
            "Table: `Insurance`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `pid` | int | Primary key. |\n"
            "| `tiv_2015` | float | Total investment value in 2015. |\n"
            "| `tiv_2016` | float | Total investment value in 2016. |\n"
            "| `lat` | float | Latitude of policyholder's city. |\n"
            "| `lon` | float | Longitude of policyholder's city. |\n\n"
            "### Problem Statement\n"
            "Write a solution to report the sum of all total investment values in 2016 `tiv_2016` for all policyholders who:\n"
            "1. have the same `tiv_2015` value as one or more other policyholders, and\n"
            "2. are not located in the same city as any other policyholder (i.e. the `(lat, lon)` attribute pair must be unique).\n\n"
            "Round `tiv_2016` to **two decimal points**.\n\n"
            "<details><summary>💡 Hint</summary>Filter `tiv_2015 IN (SELECT tiv_2015 ... HAVING COUNT(*) > 1)` and `(lat, lon) IN (SELECT lat, lon ... HAVING COUNT(*) = 1)`.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Insurance (pid INT PRIMARY KEY, tiv_2015 FLOAT, tiv_2016 FLOAT, lat FLOAT, lon FLOAT);\n"
                    "INSERT INTO Insurance VALUES (1, 10, 5, 10, 10), (2, 20, 20, 20, 20), (3, 10, 30, 20, 20), (4, 10, 40, 40, 40);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["tiv_2016"],
                    "rows": [[45.0]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },

    # ── 15. Tree Node Classification ──────────────────────────────────────────
    {
        "title": "Tree Node Classification",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": sql_opt_sol(
            """SELECT
    id,
    CASE
        WHEN p_id IS NULL THEN 'Root'
        WHEN id IN (SELECT DISTINCT p_id FROM Tree WHERE p_id IS NOT NULL) THEN 'Inner'
        ELSE 'Leaf'
    END AS type
FROM Tree
ORDER BY id;"""
        ),
        "generator_key": "sql_generic",
        "description": (
            "Table: `Tree`\n\n"
            "| Column Name | Type | Description |\n"
            "| :--- | :--- | :--- |\n"
            "| `id` | int | Primary key. |\n"
            "| `p_id` | int | The parent node ID (`null` if root). |\n\n"
            "### Problem Statement\n"
            "Each node in the tree can be one of three types:\n"
            "- **\"Leaf\"**: if the node is a leaf node (has a parent but no children).\n"
            "- **\"Root\"**: if the node is the root of the tree (no parent).\n"
            "- **\"Inner\"**: if the node is neither a leaf node nor a root node (has both parent and children).\n\n"
            "Write a solution to report the type of each node in the tree.\n\n"
            "Return the result table with columns `id` and `type` in **any order**.\n\n"
            "### Example 1\n"
            "**Input:**\n\n"
            "Tree table:\n"
            "| id | p_id |\n"
            "| :--- | :--- |\n"
            "| 1 | null |\n"
            "| 2 | 1 |\n"
            "| 3 | 1 |\n"
            "| 4 | 2 |\n"
            "| 5 | 2 |\n\n"
            "**Output:**\n"
            "| id | type |\n"
            "| :--- | :--- |\n"
            "| 1 | Root |\n"
            "| 2 | Inner |\n"
            "| 3 | Leaf |\n"
            "| 4 | Leaf |\n"
            "| 5 | Leaf |\n\n"
            "<details><summary>💡 Hint</summary>Use a `CASE` statement checking `p_id IS NULL` for 'Root', `id IN (SELECT p_id FROM Tree WHERE p_id IS NOT NULL)` for 'Inner', and 'Leaf' for others.</details>"
        ),
        "test_cases": [
            {
                "input": (
                    "CREATE TABLE Tree (id INT PRIMARY KEY, p_id INT);\n"
                    "INSERT INTO Tree VALUES (1, NULL), (2, 1), (3, 1), (4, 2), (5, 2);\n"
                ),
                "expected_output": json.dumps({
                    "columns": ["id", "type"],
                    "rows": [[1, "Root"], [2, "Inner"], [3, "Leaf"], [4, "Leaf"], [5, "Leaf"]]
                }),
                "comparator_type": "sql_table",
            },
        ],
        "signatures": [],
    },
]
