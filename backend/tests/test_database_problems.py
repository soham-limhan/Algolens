"""
tests/test_database_problems.py — Comprehensive tests for MySQL/SQL Sandbox,
DataGrid comparators, and Database Problems.
"""
import json
import pytest
from app.sandbox.executor import CompiledSubmission, SandboxLimits
from app.services.correctness import compare_output
from app.database_problems import DATABASE_PROBLEMS


def test_sql_sandbox_basic_execution():
    """Verify that CompiledSubmission can execute SQL queries on SQLite with MySQL emulation."""
    setup_sql = """
    CREATE TABLE Person (personId INT, lastName VARCHAR(50), firstName VARCHAR(50));
    INSERT INTO Person VALUES (1, 'Wang', 'Allen'), (2, 'Alice', 'Bob');
    """
    query_sql = "SELECT firstName, lastName FROM Person ORDER BY personId ASC;"
    
    submission = CompiledSubmission(
        source_code=query_sql,
        language="mysql",
    )
    
    result = submission.run(stdin_data=setup_sql, limits=SandboxLimits(wall_timeout_s=5))
    assert not result.timed_out
    assert result.exit_code == 0
    assert result.stderr == ""
    
    # Parse structured JSON output
    data = json.loads(result.stdout)
    assert data["type"] == "sql_table"
    assert [c.lower() for c in data["columns"]] == ["firstname", "lastname"]
    assert data["rows"] == [["Allen", "Wang"], ["Bob", "Alice"]]


def test_sql_sandbox_mysql_functions():
    """Verify MySQL compatibility functions: IF, CONCAT, MOD, DATEDIFF."""
    setup_sql = """
    CREATE TABLE Items (id INT, price INT, created_at VARCHAR(20));
    INSERT INTO Items VALUES (1, 100, '2023-01-01'), (2, 50, '2023-01-05');
    """
    query_sql = """
    SELECT 
        id,
        IF(price > 60, 'Expensive', 'Cheap') AS tag,
        CONCAT('Item-', id) AS code,
        DATEDIFF('2023-01-10', created_at) AS days_ago
    FROM Items
    ORDER BY id ASC;
    """
    
    submission = CompiledSubmission(
        source_code=query_sql,
        language="sql",
    )
    
    result = submission.run(stdin_data=setup_sql, limits=SandboxLimits(wall_timeout_s=5))
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert len(data["rows"]) == 2
    assert data["rows"][0] == [1, "Expensive", "Item-1", 9]
    assert data["rows"][1] == [2, "Cheap", "Item-2", 5]


def test_sql_comparator_matching():
    """Verify that _sql_table comparator matches column-normalized, order-insensitive table outputs."""
    actual = json.dumps({
        "type": "sql_table",
        "columns": ["firstName", "lastName", "city", "state"],
        "rows": [
            ["Bob", "Alice", "New York City", "New York"],
            ["Allen", "Wang", None, None]
        ]
    })
    
    expected = json.dumps({
        "type": "sql_table",
        "columns": ["firstname", "lastname", "city", "state"],
        "rows": [
            ["Allen", "Wang", None, None],
            ["Bob", "Alice", "New York City", "New York"]
        ]
    })
    
    assert compare_output("sql_table", expected, actual) is True
    assert compare_output("sql", expected, actual) is True


def test_sql_comparator_mismatch():
    """Verify that _sql_table comparator correctly fails when outputs differ."""
    actual = json.dumps({
        "type": "sql_table",
        "columns": ["firstName", "lastName"],
        "rows": [["Allen", "Wang"]]
    })
    
    expected = json.dumps({
        "type": "sql_table",
        "columns": ["firstName", "lastName"],
        "rows": [["Allen", "Smith"]]
    })
    
    assert compare_output("sql_table", expected, actual) is False


def test_database_problems_structure():
    """Verify all 15 curated database problems contain required metadata, solutions and test cases."""
    assert len(DATABASE_PROBLEMS) == 15
    for prob in DATABASE_PROBLEMS:
        assert prob["title"]
        assert prob["difficulty"] in ("easy", "medium", "hard")
        assert prob["generator_key"].startswith("sql_")
        assert len(prob["test_cases"]) >= 1
        for tc in prob["test_cases"]:
            assert "CREATE TABLE" in tc["input"]
            assert tc["comparator_type"] in ("sql_table", "sql")
            exp_data = json.loads(tc["expected_output"])
            assert "columns" in exp_data
            assert "rows" in exp_data
