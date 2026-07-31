"""
tests/test_multi_sandbox.py — Unit tests for multi-language sandbox executor (Python, Java, C++, C, JavaScript).
"""
from __future__ import annotations

import shutil
import pytest
from app.sandbox.executor import CompiledSubmission, SandboxLimits


def test_python_submission_execution():
    code = "import sys\nprint('hello python from stdin:', sys.stdin.read().strip())"
    cs = CompiledSubmission(code, language="python")
    assert not cs.compilation_error, cs.compiler_output

    res = cs.run(stdin_data="test_input\n")
    assert res.exit_code == 0
    assert "hello python from stdin: test_input" in res.stdout.strip()
    cs.cleanup()


def test_python_syntax_error():
    code = "this is not valid python code syntax !!!"
    cs = CompiledSubmission(code, language="python")
    assert cs.compilation_error
    assert cs.compiler_output != ""
    cs.cleanup()


def test_java_submission_execution():
    code = """
import java.util.*;
public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println(a + b);
    }
}
"""
    cs = CompiledSubmission(code, language="java")
    if shutil.which("javac"):
        assert not cs.compilation_error, cs.compiler_output
        res = cs.run(stdin_data="5 10\n")
        assert res.exit_code == 0
        assert res.stdout.strip() == "15"
    else:
        assert cs.compilation_error
    cs.cleanup()


def test_javascript_submission_execution():
    if not shutil.which("node"):
        pytest.skip("node not found on PATH")

    code = """
const fs = require('fs');
const input = fs.readFileSync(0, 'utf-8').trim();
console.log('JS input:', input);
"""
    cs = CompiledSubmission(code, language="javascript")
    assert not cs.compilation_error, cs.compiler_output

    res = cs.run(stdin_data="hello js\n")
    assert res.exit_code == 0
    assert "JS input: hello js" in res.stdout.strip()
    cs.cleanup()


def test_cpp_submission_execution():
    compiler = shutil.which("g++") or shutil.which("clang++")
    if not compiler:
        pytest.skip("g++/clang++ compiler not found on PATH")

    code = """
#include <iostream>
using namespace std;
int main() {
    int x;
    if (cin >> x) {
        cout << "CPP double: " << (x * 2) << endl;
    }
    return 0;
}
"""
    cs = CompiledSubmission(code, language="cpp")
    assert not cs.compilation_error, cs.compiler_output

    res = cs.run(stdin_data="21\n")
    assert res.exit_code == 0
    assert "CPP double: 42" in res.stdout.strip()
    cs.cleanup()


def test_c_submission_execution():
    compiler = shutil.which("gcc") or shutil.which("clang")
    if not compiler:
        pytest.skip("gcc/clang compiler not found on PATH")

    code = """
#include <stdio.h>
int main() {
    int val;
    if (scanf("%d", &val) == 1) {
        printf("C res: %d\\n", val + 100);
    }
    return 0;
}
"""
    cs = CompiledSubmission(code, language="c")
    assert not cs.compilation_error, cs.compiler_output

    res = cs.run(stdin_data="50\n")
    assert res.exit_code == 0
    assert "C res: 150" in res.stdout.strip()
    cs.cleanup()


def test_unsupported_language():
    cs = CompiledSubmission("print(1)", language="brainfuck")
    assert cs.compilation_error
    assert "Unsupported language" in cs.compiler_output
    cs.cleanup()
