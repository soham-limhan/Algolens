"""
app/seed.py — Idempotent seed script for the AlgoLens problem bank.

Run with: python -m app.seed

Idempotent: safe to re-run — checks for existing rows by title, updates description,
optimal solutions (Python, Java, JavaScript, C++), test cases, and signatures.
"""
from __future__ import annotations

import json
import logging
import sys

from app.db.database import Base, SessionLocal, engine
from app.models import InefficiencySignature, Problem, TestCase  # noqa: F401 — registers all models
from app.database_problems import DATABASE_PROBLEMS

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def opt_sol(python_code: str, java_code: str = "", js_code: str = "", cpp_code: str = "") -> str:
    """Format optimal solutions into a JSON object with language keys."""
    res = {"python": python_code.strip()}
    if java_code:
        res["java"] = java_code.strip()
    if js_code:
        res["javascript"] = js_code.strip()
    if cpp_code:
        res["cpp"] = cpp_code.strip()
    return json.dumps(res)


# ── Problem definitions ───────────────────────────────────────────────────────

PROBLEMS = [
    {
        "title": "Minimum Number of Pushes to Type Word I",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    lines = sys.stdin.read().split()
    if not lines:
        return
    word = lines[0].strip()

    res = 0
    for i, _ in enumerate(word):
        res += (i // 8) + 1
    print(res)

if __name__ == '__main__':
    main()""",
            """import java.util.Scanner;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNext()) return;
        String word = sc.next();
        int res = 0;
        for (int i = 0; i < word.length(); i++) {
            res += (i / 8) + 1;
        }
        System.out.println(res);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/);
    if (!input || input.length === 0 || !input[0]) return;
    const word = input[0];
    let res = 0;
    for (let i = 0; i < word.length; i++) {
        res += Math.floor(i / 8) + 1;
    }
    console.log(res);
}

main();""",
            """#include <iostream>
#include <string>
using namespace std;

int main() {
    string word;
    if (!(cin >> word)) return 0;
    int res = 0;
    for (int i = 0; i < (int)word.length(); i++) {
        res += (i / 8) + 1;
    }
    cout << res << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "You are given a string `word` containing distinct lowercase English letters.\n\n"
            "Telephone keypads have keys numbered `2` through `9` (8 keys total) mapped to distinct collections of letters. "
            "You can map each letter of `word` to any key. Each key can be pressed 1, 2, 3, or 4 times to type the mapped letters assigned to it.\n\n"
            "Your goal is to map the letters to the 8 keys such that the total number of key pushes needed to type `word` is **minimized**.\n\n"
            "### Example 1:\n"
            "- **Input:** `abcde`\n"
            "- **Output:** `5`\n"
            "- **Explanation:** We map 'a', 'b', 'c', 'd', 'e' each as the first letter of keys 2, 3, 4, 5, 6. Each letter requires 1 press. Total = 1 + 1 + 1 + 1 + 1 = 5.\n\n"
            "### Example 2:\n"
            "- **Input:** `xycdefgh`\n"
            "- **Output:** `8`\n"
            "- **Explanation:** There are 8 distinct letters. We can map all 8 letters as the 1st position on each of the 8 available keys (keys 2-9). Total pushes = 8 * 1 = 8.\n\n"
            "### Constraints:\n"
            "- `1 <= word.length <= 26`\n"
            "- `word` consists of lowercase English letters.\n"
            "- All letters in `word` are distinct.\n\n"
            "### Input / Output Format:\n"
            "- **Input:** A single line containing the string `word`.\n"
            "- **Output:** A single integer representing the minimum number of key pushes.\n\n"
            "<details><summary>💡 Hint 1</summary>Since there are 8 distinct keys (2 through 9), the first 8 letters can each be placed at position 1 (cost = 1 push).</details>\n"
            "<details><summary>💡 Hint 2</summary>The next 8 letters (indices 8 to 15) must be placed at position 2 on the keys (cost = 2 pushes each), and so on.</details>\n"
            "<details><summary>💡 Hint 3</summary>For letter at index `i` (0-indexed), the cost is `(i // 8) + 1` pushes.</details>"
        ),
        "test_cases": [
            {"input": "abcde\n", "expected_output": "5", "comparator_type": "exact"},
            {"input": "xycdefgh\n", "expected_output": "8", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Two Sum",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:n+1]]
    target = int(input_data[n+1])

    # Hash Map for O(n) lookup
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            res = sorted([seen[complement], i])
            print(f"{res[0]} {res[1]}")
            return
        seen[num] = i

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        int target = sc.nextInt();

        // Hash Map for O(n) time lookup
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < n; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                System.out.println(map.get(complement) + " " + i);
                return;
            }
            map.put(nums[i], i);
        }
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const nums = input.slice(1, n + 1);
    const target = input[n + 1];

    const seen = new Map();
    for (let i = 0; i < n; i++) {
        const complement = target - nums[i];
        if (seen.has(complement)) {
            const idx1 = seen.get(complement);
            const res = [idx1, i].sort((a, b) => a - b);
            console.log(`${res[0]} ${res[1]}`);
            return;
        }
        seen.set(nums[i], i);
    }
}

main();""",
            """#include <iostream>
#include <vector>
#include <unordered_map>
#include <algorithm>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> nums(n);
    for (int i = 0; i < n; i++) cin >> nums[i];
    int target;
    cin >> target;

    unordered_map<int, int> seen;
    for (int i = 0; i < n; i++) {
        int complement = target - nums[i];
        if (seen.count(complement)) {
            cout << seen[complement] << " " << i << endl;
            return 0;
        }
        seen[nums[i]] = i;
    }
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given an array of integers `nums` and an integer `target`, return the **indices of the two numbers** such that they add up to `target`.\n\n"
            "You may assume that each input would have **exactly one solution**, and you may not use the same element twice. You can return the answer in any order (indices printed space-separated).\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 4`, `nums = [2, 7, 11, 15]`, `target = 9`\n"
            "- **Output:** `0 1`\n"
            "- **Explanation:** Because `nums[0] + nums[1] == 2 + 7 == 9`, we return `0 1`.\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 3`, `nums = [3, 2, 4]`, `target = 6`\n"
            "- **Output:** `1 2`\n"
            "- **Explanation:** `nums[1] + nums[2] == 2 + 4 == 6`, so the indices are `1 2`.\n\n"
            "### Example 3:\n"
            "- **Input:** `n = 2`, `nums = [3, 3]`, `target = 6`\n"
            "- **Output:** `0 1`\n"
            "- **Explanation:** `nums[0] + nums[1] == 3 + 3 == 6`.\n\n"
            "### Constraints:\n"
            "- `2 <= nums.length <= 10^5`\n"
            "- `-10^9 <= nums[i] <= 10^9`\n"
            "- `-10^9 <= target <= 10^9`\n"
            "- **Only one valid answer exists.**\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n` (number of elements)\n"
            "- **Line 2:** `n` space-separated integers representing `nums`\n"
            "- **Line 3:** Integer `target`\n"
            "- **Output:** Two space-separated indices (e.g. `0 1`)\n\n"
            "<details><summary>💡 Hint 1</summary>A brute-force approach compares all pairs with nested loops in O(n²) time. Can you do it faster using additional memory?</details>\n"
            "<details><summary>💡 Hint 2</summary>When inspecting number `x`, what you really need to find is `complement = target - x`. Can a Hash Map look up whether `complement` was already visited in O(1) time?</details>\n"
            "<details><summary>💡 Hint 3</summary>Iterate through `nums` once. For each element `nums[i]`, check if `target - nums[i]` is in your hash map. If yes, you found the pair. If not, insert `nums[i]: i` into the map.</details>"
        ),
        "test_cases": [
            {"input": "4\n2 7 11 15\n9\n", "expected_output": "0 1", "comparator_type": "sorted"},
            {"input": "3\n3 2 4\n6\n",     "expected_output": "1 2", "comparator_type": "sorted"},
            {"input": "2\n3 3\n6\n",       "expected_output": "0 1", "comparator_type": "sorted"},
            {"input": "5\n1 5 3 8 2\n3\n", "expected_output": "0 4", "comparator_type": "sorted"},
        ],
        "signatures": [
            {
                "pattern_type": "nested_loop_lookup",
                "hint_text": (
                    "Your solution scans the array with a nested loop to find a matching pair. "
                    "Each element causes a full inner scan — O(n²) overall. "
                    "Consider a single pass with a HashMap: for each element, check if its "
                    "complement (target − current) is already stored."
                ),
            }
        ],
    },
    {
        "title": "Add Two Numbers",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    lines = sys.stdin.read().strip().split('\\n')
    if len(lines) < 2:
        return
    l1 = list(map(int, lines[0].split()))
    l2 = list(map(int, lines[1].split()))

    i, j, carry = 0, 0, 0
    res = []
    while i < len(l1) or j < len(l2) or carry:
        v1 = l1[i] if i < len(l1) else 0
        v2 = l2[j] if j < len(l2) else 0
        total = v1 + v2 + carry
        res.append(total % 10)
        carry = total // 10
        i += 1
        j += 1

    print(" ".join(map(str, res)))

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextLine()) return;
        String[] l1 = sc.nextLine().trim().split("\\\\s+");
        String[] l2 = sc.nextLine().trim().split("\\\\s+");

        int i = 0, j = 0, carry = 0;
        List<String> res = new ArrayList<>();
        while (i < l1.length || j < l2.length || carry > 0) {
            int v1 = i < l1.length ? Integer.parseInt(l1[i]) : 0;
            int v2 = j < l2.length ? Integer.parseInt(l2[j]) : 0;
            int total = v1 + v2 + carry;
            res.add(String.valueOf(total % 10));
            carry = total / 10;
            i++; j++;
        }
        System.out.println(String.join(" ", res));
    }
}""",
            """const fs = require('fs');

function main() {
    const lines = fs.readFileSync(0, 'utf-8').trim().split('\\n');
    if (lines.length < 2) return;
    const l1 = lines[0].trim().split(/\\s+/).map(Number);
    const l2 = lines[1].trim().split(/\\s+/).map(Number);

    let i = 0, j = 0, carry = 0;
    const res = [];
    while (i < l1.length || j < l2.length || carry > 0) {
        const v1 = i < l1.length ? l1[i] : 0;
        const v2 = j < l2.length ? l2[j] : 0;
        const total = v1 + v2 + carry;
        res.push(total % 10);
        carry = Math.floor(total / 10);
        i++;
        j++;
    }
    console.log(res.join(' '));
}

main();""",
            """#include <iostream>
#include <vector>
#include <string>
#include <sstream>
using namespace std;

int main() {
    string line1, line2;
    if (!getline(cin, line1) || !getline(cin, line2)) return 0;
    stringstream ss1(line1), ss2(line2);
    vector<int> l1, l2;
    int val;
    while (ss1 >> val) l1.push_back(val);
    while (ss2 >> val) l2.push_back(val);

    int i = 0, j = 0, carry = 0;
    vector<int> res;
    while (i < (int)l1.size() || j < (int)l2.size() || carry) {
        int v1 = (i < (int)l1.size()) ? l1[i] : 0;
        int v2 = (j < (int)l2.size()) ? l2[j] : 0;
        int total = v1 + v2 + carry;
        res.push_back(total % 10);
        carry = total / 10;
        i++; j++;
    }
    for (int k = 0; k < (int)res.size(); k++) {
        cout << res[k] << (k + 1 == (int)res.size() ? "" : " ");
    }
    cout << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "You are given two non-empty sequences representing two non-negative integers. "
            "The digits are stored in **reverse order**, and each position contains a single digit. "
            "Add the two numbers and return the sum as a reversed sequence of digits.\n\n"
            "You may assume the two numbers do not contain any leading zero, except the number 0 itself.\n\n"
            "### Example 1:\n"
            "- **Input:**\n"
            "  `2 4 3` (represents 342)\n"
            "  `5 6 4` (represents 465)\n"
            "- **Output:** `7 0 8`\n"
            "- **Explanation:** `342 + 465 = 807`. In reverse order: `[7, 0, 8]`.\n\n"
            "### Example 2:\n"
            "- **Input:**\n"
            "  `0`\n"
            "  `0`\n"
            "- **Output:** `0`\n"
            "- **Explanation:** `0 + 0 = 0`.\n\n"
            "### Example 3:\n"
            "- **Input:**\n"
            "  `9 9 9`\n"
            "  `1`\n"
            "- **Output:** `0 0 0 1`\n"
            "- **Explanation:** `999 + 1 = 1000`. Reversed: `[0, 0, 0, 1]`.\n\n"
            "### Constraints:\n"
            "- The number of digits in each list is in the range `[1, 100]`.\n"
            "- `0 <= digit <= 9`\n"
            "- It is guaranteed that the list represents a number that does not have leading zeros.\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Space-separated digits for first number\n"
            "- **Line 2:** Space-separated digits for second number\n"
            "- **Output:** Space-separated digits of the result\n\n"
            "<details><summary>💡 Hint 1</summary>Since the numbers are already in reverse order (least significant digit first), you can add digits from left to right simulating column addition.</details>\n"
            "<details><summary>💡 Hint 2</summary>Keep track of the `carry` across iterations: `sum = digit1 + digit2 + carry`, new digit is `sum % 10`, and new carry is `sum // 10`.</details>\n"
            "<details><summary>💡 Hint 3</summary>Don't forget to handle the case where a remaining `carry > 0` after both input lists have been fully traversed (e.g. 99 + 1).</details>"
        ),
        "test_cases": [
            {"input": "2 4 3\n5 6 4\n", "expected_output": "7 0 8", "comparator_type": "exact"},
            {"input": "0\n0\n", "expected_output": "0", "comparator_type": "exact"},
            {"input": "9 9 9\n1\n", "expected_output": "0 0 0 1", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    s = sys.stdin.read().rstrip('\\r\\n')
    char_map = {}
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        if char in char_map and char_map[char] >= left:
            left = char_map[char] + 1
        char_map[char] = right
        max_len = max(max_len, right - left + 1)
    print(max_len)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.hasNextLine() ? sc.nextLine() : "";
        Map<Character, Integer> map = new HashMap<>();
        int left = 0, maxLen = 0;
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            if (map.containsKey(c) && map.get(c) >= left) {
                left = map.get(c) + 1;
            }
            map.put(c, right);
            maxLen = Math.max(maxLen, right - left + 1);
        }
        System.out.println(maxLen);
    }
}""",
            """const fs = require('fs');

function main() {
    const s = fs.readFileSync(0, 'utf-8').replace(/[\\r\\n]+$/, '');
    const charMap = new Map();
    let left = 0, maxLen = 0;
    for (let right = 0; right < s.length; right++) {
        const char = s[right];
        if (charMap.has(char) && charMap.get(char) >= left) {
            left = charMap.get(char) + 1;
        }
        charMap.set(char, right);
        maxLen = Math.max(maxLen, right - left + 1);
    }
    console.log(maxLen);
}

main();""",
            """#include <iostream>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

int main() {
    string s;
    if (!getline(cin, s)) return 0;
    unordered_map<char, int> char_map;
    int left = 0, max_len = 0;
    for (int right = 0; right < (int)s.length(); right++) {
        if (char_map.count(s[right]) && char_map[s[right]] >= left) {
            left = char_map[s[right]] + 1;
        }
        char_map[s[right]] = right;
        max_len = max(max_len, right - left + 1);
    }
    cout << max_len << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given a string `s`, find the **length of the longest substring** without repeating characters.\n\n"
            "A **substring** is a contiguous non-empty sequence of characters within a string.\n\n"
            "### Example 1:\n"
            "- **Input:** `abcabcbb`\n"
            "- **Output:** `3`\n"
            "- **Explanation:** The answer is `\"abc\"`, with the length of 3.\n\n"
            "### Example 2:\n"
            "- **Input:** `bbbbb`\n"
            "- **Output:** `1`\n"
            "- **Explanation:** The answer is `\"b\"`, with the length of 1.\n\n"
            "### Example 3:\n"
            "- **Input:** `pwwkew`\n"
            "- **Output:** `3`\n"
            "- **Explanation:** The answer is `\"wke\"`, with the length of 3. Note that the answer must be a substring, `\"pwke\"` is a subsequence and not a substring.\n\n"
            "### Constraints:\n"
            "- `0 <= s.length <= 5 * 10^4`\n"
            "- `s` consists of English letters, digits, symbols and spaces.\n\n"
            "### Input / Output Format:\n"
            "- **Input:** A single string `s`\n"
            "- **Output:** Integer representing the maximum length\n\n"
            "<details><summary>💡 Hint 1</summary>Use the sliding window technique with two pointers `left` and `right` defining the current substring window.</details>\n"
            "<details><summary>💡 Hint 2</summary>Store the most recent index of each character in a Hash Map. When a duplicate is seen at `right`, advance `left` to `map[char] + 1`.</details>\n"
            "<details><summary>💡 Hint 3</summary>Make sure you only update `left` forward (i.e. `left = max(left, last_seen_index + 1)`) so you don't rewind the window.</details>"
        ),
        "test_cases": [
            {"input": "abcabcbb\n", "expected_output": "3", "comparator_type": "exact"},
            {"input": "bbbbb\n", "expected_output": "1", "comparator_type": "exact"},
            {"input": "pwwkew\n", "expected_output": "3", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Median of Two Sorted Arrays",
        "difficulty": "hard",
        "optimal_time_complexity": "O(log n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    lines = sys.stdin.read().strip().split('\\n')
    if not lines:
        return
    nums1 = list(map(int, lines[0].split())) if lines[0].strip() else []
    nums2 = list(map(int, lines[1].split())) if len(lines) > 1 and lines[1].strip() else []

    merged = sorted(nums1 + nums2)
    n = len(merged)
    if n % 2 == 1:
        print(float(merged[n // 2]))
    else:
        print((merged[n // 2 - 1] + merged[n // 2]) / 2.0)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<Integer> list = new ArrayList<>();
        if (sc.hasNextLine()) {
            String l1 = sc.nextLine().trim();
            if (!l1.isEmpty()) for (String s : l1.split("\\\\s+")) list.add(Integer.parseInt(s));
        }
        if (sc.hasNextLine()) {
            String l2 = sc.nextLine().trim();
            if (!l2.isEmpty()) for (String s : l2.split("\\\\s+")) list.add(Integer.parseInt(s));
        }
        Collections.sort(list);
        int n = list.size();
        if (n % 2 == 1) {
            System.out.println((double)list.get(n / 2));
        } else {
            System.out.println((list.get(n / 2 - 1) + list.get(n / 2)) / 2.0);
        }
    }
}""",
            """const fs = require('fs');

function main() {
    const lines = fs.readFileSync(0, 'utf-8').trim().split('\\n');
    const nums1 = lines[0] ? lines[0].trim().split(/\\s+/).filter(Boolean).map(Number) : [];
    const nums2 = lines[1] ? lines[1].trim().split(/\\s+/).filter(Boolean).map(Number) : [];
    const merged = [...nums1, ...nums2].sort((a, b) => a - b);
    const n = merged.length;
    if (n % 2 === 1) {
        console.log(merged[Math.floor(n / 2)].toFixed(1));
    } else {
        console.log(((merged[n / 2 - 1] + merged[n / 2]) / 2).toFixed(1));
    }
}

main();""",
            """#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <iomanip>
using namespace std;

int main() {
    string l1, l2;
    vector<int> nums;
    if (getline(cin, l1)) {
        stringstream ss(l1);
        int val;
        while (ss >> val) nums.push_back(val);
    }
    if (getline(cin, l2)) {
        stringstream ss(l2);
        int val;
        while (ss >> val) nums.push_back(val);
    }
    sort(nums.begin(), nums.end());
    int n = nums.size();
    cout << fixed << setprecision(1);
    if (n % 2 == 1) {
        cout << (double)nums[n / 2] << endl;
    } else {
        cout << (nums[n / 2 - 1] + nums[n / 2]) / 2.0 << endl;
    }
    return 0;
}"""
        ),
        "generator_key": "binary_search",
        "description": (
            "Given two sorted arrays `nums1` and `nums2` of size `m` and `n` respectively, return the **median** of the two sorted arrays.\n\n"
            "The overall run time complexity should be `O(log (m+n))`.\n\n"
            "### Example 1:\n"
            "- **Input:**\n"
            "  `1 3`\n"
            "  `2`\n"
            "- **Output:** `2.0`\n"
            "- **Explanation:** merged array = `[1, 2, 3]` and median is `2.0`.\n\n"
            "### Example 2:\n"
            "- **Input:**\n"
            "  `1 2`\n"
            "  `3 4`\n"
            "- **Output:** `2.5`\n"
            "- **Explanation:** merged array = `[1, 2, 3, 4]` and median is `(2 + 3) / 2 = 2.5`.\n\n"
            "### Constraints:\n"
            "- `nums1.length == m`, `nums2.length == n`\n"
            "- `0 <= m <= 1000`, `0 <= n <= 1000`, `1 <= m + n <= 2000`\n"
            "- `-10^6 <= nums1[i], nums2[i] <= 10^6`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Space-separated sorted integers for `nums1`\n"
            "- **Line 2:** Space-separated sorted integers for `nums2`\n"
            "- **Output:** Decimal median (e.g. `2.0` or `2.5`)\n\n"
            "<details><summary>💡 Hint 1</summary>The naive merge is O(m+n). To achieve O(log(min(m, n))), use binary search on the partition index of the smaller array.</details>\n"
            "<details><summary>💡 Hint 2</summary>We want to partition both arrays into left and right halves such that every element in left is <= every element in right, and total elements on the left equals total elements on the right.</details>"
        ),
        "test_cases": [
            {"input": "1 3\n2\n", "expected_output": "2.0", "comparator_type": "numeric_tolerance"},
            {"input": "1 2\n3 4\n", "expected_output": "2.5", "comparator_type": "numeric_tolerance"},
        ],
        "signatures": [],
    },
    {
        "title": "Longest Palindromic Substring",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n^2)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    s = sys.stdin.read().strip()
    if not s:
        return

    def expand(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return s[left + 1:right]

    res = ""
    for i in range(len(s)):
        p1 = expand(i, i)
        p2 = expand(i, i + 1)
        if len(p1) > len(res): res = p1
        if len(p2) > len(res): res = p2

    print(res)

if __name__ == '__main__':
    main()""",
            """import java.util.Scanner;

public class Solution {
    private static String expand(String s, int left, int right) {
        while (left >= 0 && right < s.length() && s.charAt(left) == s.charAt(right)) {
            left--;
            right++;
        }
        return s.substring(left + 1, right);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNext()) return;
        String s = sc.next();
        String res = "";
        for (int i = 0; i < s.length(); i++) {
            String p1 = expand(s, i, i);
            String p2 = expand(s, i, i + 1);
            if (p1.length() > res.length()) res = p1;
            if (p2.length() > res.length()) res = p2;
        }
        System.out.println(res);
    }
}""",
            """const fs = require('fs');

function main() {
    const s = fs.readFileSync(0, 'utf-8').trim();
    if (!s) return;

    function expand(left, right) {
        while (left >= 0 && right < s.length && s[left] === s[right]) {
            left--;
            right++;
        }
        return s.substring(left + 1, right);
    }

    let res = '';
    for (let i = 0; i < s.length; i++) {
        const p1 = expand(i, i);
        const p2 = expand(i, i + 1);
        if (p1.length > res.length) res = p1;
        if (p2.length > res.length) res = p2;
    }
    console.log(res);
}

main();""",
            """#include <iostream>
#include <string>
using namespace std;

string expand(const string& s, int left, int right) {
    while (left >= 0 && right < (int)s.length() && s[left] == s[right]) {
        left--;
        right++;
    }
    return s.substr(left + 1, right - left - 1);
}

int main() {
    string s;
    if (!(cin >> s)) return 0;
    string res = "";
    for (int i = 0; i < (int)s.length(); i++) {
        string p1 = expand(s, i, i);
        string p2 = expand(s, i, i + 1);
        if (p1.length() > res.length()) res = p1;
        if (p2.length() > res.length()) res = p2;
    }
    cout << res << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given a string `s`, return the **longest palindromic substring** in `s`.\n\n"
            "A string is palindromic if it reads the same forward and backward.\n\n"
            "### Example 1:\n"
            "- **Input:** `babad`\n"
            "- **Output:** `bab` (or `aba`)\n"
            "- **Explanation:** `\"bab\"` and `\"aba\"` are both valid answers with length 3.\n\n"
            "### Example 2:\n"
            "- **Input:** `cbbd`\n"
            "- **Output:** `bb`\n"
            "- **Explanation:** `\"bb\"` is the longest palindrome with length 2.\n\n"
            "### Constraints:\n"
            "- `1 <= s.length <= 1000`\n"
            "- `s` consists of only digits and English letters.\n\n"
            "### Input / Output Format:\n"
            "- **Input:** A single string `s`\n"
            "- **Output:** The longest palindromic substring string\n\n"
            "<details><summary>💡 Hint 1</summary>A palindrome mirrors around its center. A string of length N has `2N - 1` possible centers (single characters or spaces between characters).</details>\n"
            "<details><summary>💡 Hint 2</summary>For each center, expand outward left and right as long as characters match: `expandAroundCenter(i, i)` for odd length and `expandAroundCenter(i, i+1)` for even length.</details>"
        ),
        "test_cases": [
            {"input": "babad\n", "expected_output": "bab", "comparator_type": "exact"},
            {"input": "cbbd\n", "expected_output": "bb", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Zigzag Conversion",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    lines = sys.stdin.read().strip().split('\\n')
    if not lines:
        return
    s = lines[0].strip()
    num_rows = int(lines[1].strip()) if len(lines) > 1 else 1

    if num_rows == 1 or num_rows >= len(s):
        print(s)
        return

    rows = [''] * num_rows
    curr_row = 0
    going_down = False

    for char in s:
        rows[curr_row] += char
        if curr_row == 0 or curr_row == num_rows - 1:
            going_down = not going_down
        curr_row += 1 if going_down else -1

    print(''.join(rows))

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextLine()) return;
        String s = sc.nextLine().trim();
        int numRows = sc.hasNextInt() ? sc.nextInt() : 1;

        if (numRows == 1 || numRows >= s.length()) {
            System.out.println(s);
            return;
        }

        StringBuilder[] rows = new StringBuilder[numRows];
        for (int i = 0; i < numRows; i++) rows[i] = new StringBuilder();

        int currRow = 0;
        boolean goingDown = false;
        for (char c : s.toCharArray()) {
            rows[currRow].append(c);
            if (currRow == 0 || currRow == numRows - 1) goingDown = !goingDown;
            currRow += goingDown ? 1 : -1;
        }

        StringBuilder res = new StringBuilder();
        for (StringBuilder sb : rows) res.append(sb);
        System.out.println(res.toString());
    }
}""",
            """const fs = require('fs');

function main() {
    const lines = fs.readFileSync(0, 'utf-8').trim().split('\\n');
    if (!lines || !lines[0]) return;
    const s = lines[0].trim();
    const numRows = lines[1] ? parseInt(lines[1].trim(), 10) : 1;

    if (numRows === 1 || numRows >= s.length) {
        console.log(s);
        return;
    }

    const rows = Array.from({ length: numRows }, () => '');
    let currRow = 0;
    let goingDown = false;

    for (const char of s) {
        rows[currRow] += char;
        if (currRow === 0 || currRow === numRows - 1) goingDown = !goingDown;
        currRow += goingDown ? 1 : -1;
    }

    console.log(rows.join(''));
}

main();""",
            """#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
    string s;
    if (!getline(cin, s)) return 0;
    int numRows = 1;
    cin >> numRows;

    if (numRows == 1 || numRows >= (int)s.length()) {
        cout << s << endl;
        return 0;
    }

    vector<string> rows(numRows);
    int currRow = 0;
    bool goingDown = false;

    for (char c : s) {
        rows[currRow] += c;
        if (currRow == 0 || currRow == numRows - 1) goingDown = !goingDown;
        currRow += goingDown ? 1 : -1;
    }

    string res = "";
    for (const string& row : rows) res += row;
    cout << res << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "The string `\"PAYPALISHIRING\"` is written in a zigzag pattern on a given number of rows like this:\n\n"
            "```\n"
            "P   A   H   N\n"
            "A P L S I I G\n"
            "Y   I   R\n"
            "```\n\n"
            "And then read line by line: `\"PAHNAPLSIIGYIR\"`.\n\n"
            "Write the code that will take a string and make this conversion given a number of rows.\n\n"
            "### Example 1:\n"
            "- **Input:**\n"
            "  `PAYPALISHIRING`\n"
            "  `3`\n"
            "- **Output:** `PAHNAPLSIIGYIR`\n\n"
            "### Example 2:\n"
            "- **Input:**\n"
            "  `PAYPALISHIRING`\n"
            "  `4`\n"
            "- **Output:** `PINALSIGYAHRPI`\n\n"
            "### Constraints:\n"
            "- `1 <= s.length <= 1000`\n"
            "- `s` consists of English letters (lower-case and upper-case), ',' and '.'.\n"
            "- `1 <= numRows <= 1000`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** String `s`\n"
            "- **Line 2:** Integer `numRows`\n"
            "- **Output:** Formatted zigzag string\n\n"
            "<details><summary>💡 Hint 1</summary>Simulate the process using a list of `numRows` string builders or lists.</details>\n"
            "<details><summary>💡 Hint 2</summary>Keep a `currRow` pointer and a boolean `goingDown`. Flip direction whenever you hit row 0 or row `numRows - 1`.</details>"
        ),
        "test_cases": [
            {"input": "PAYPALISHIRING\n3\n", "expected_output": "PAHNAPLSIIGYIR", "comparator_type": "exact"},
            {"input": "PAYPALISHIRING\n4\n", "expected_output": "PINALSIGYAHRPI", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Reverse Integer",
        "difficulty": "medium",
        "optimal_time_complexity": "O(log n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    s = sys.stdin.read().strip()
    if not s:
        return
    val = int(s)
    sign = -1 if val < 0 else 1
    rev = int(str(abs(val))[::-1]) * sign
    if rev < -2**31 or rev > 2**31 - 1:
        print(0)
    else:
        print(rev)

if __name__ == '__main__':
    main()""",
            """import java.util.Scanner;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextLong()) return;
        long val = sc.nextLong();
        long rev = 0;
        int sign = val < 0 ? -1 : 1;
        val = Math.abs(val);

        while (val > 0) {
            rev = rev * 10 + val % 10;
            val /= 10;
        }
        rev *= sign;
        if (rev < Integer.MIN_VALUE || rev > Integer.MAX_VALUE) {
            System.out.println(0);
        } else {
            System.out.println(rev);
        }
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim();
    if (!input) return;
    const val = parseInt(input, 10);
    const sign = val < 0 ? -1 : 1;
    const rev = parseInt(Math.abs(val).toString().split('').reverse().join(''), 10) * sign;
    if (rev < -(2**31) || rev > 2**31 - 1) {
        console.log(0);
    } else {
        console.log(rev);
    }
}

main();""",
            """#include <iostream>
#include <climits>
#include <cmath>
using namespace std;

int main() {
    long long val;
    if (!(cin >> val)) return 0;
    long long rev = 0;
    int sign = val < 0 ? -1 : 1;
    val = abs(val);
    while (val > 0) {
        rev = rev * 10 + val % 10;
        val /= 10;
    }
    rev *= sign;
    if (rev < INT_MIN || rev > INT_MAX) cout << 0 << endl;
    else cout << rev << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given a signed 32-bit integer `x`, return `x` with its digits reversed.\n\n"
            "If reversing `x` causes the value to go outside the signed 32-bit integer range `[-2^31, 2^31 - 1]`, then return `0`.\n\n"
            "### Example 1:\n"
            "- **Input:** `123`\n"
            "- **Output:** `321`\n\n"
            "### Example 2:\n"
            "- **Input:** `-123`\n"
            "- **Output:** `-321`\n\n"
            "### Example 3:\n"
            "- **Input:** `120`\n"
            "- **Output:** `21`\n\n"
            "### Constraints:\n"
            "- `-2^31 <= x <= 2^31 - 1`\n\n"
            "### Input / Output Format:\n"
            "- **Input:** Integer `x`\n"
            "- **Output:** Reversed integer, or `0` on overflow\n\n"
            "<details><summary>💡 Hint 1</summary>You can extract digits from right to left using modulo 10: `pop = x % 10` and `x //= 10`.</details>\n"
            "<details><summary>💡 Hint 2</summary>Be careful to check if the accumulated value exceeds `2^31 - 1` or `-2^31` before returning.</details>"
        ),
        "test_cases": [
            {"input": "123\n", "expected_output": "321", "comparator_type": "exact"},
            {"input": "-123\n", "expected_output": "-321", "comparator_type": "exact"},
            {"input": "120\n", "expected_output": "21", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "String to Integer (atoi)",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    s = sys.stdin.read().rstrip('\\r\\n')
    s = s.lstrip()
    if not s:
        print(0)
        return

    sign = 1
    idx = 0
    if s[0] == '-':
        sign = -1
        idx += 1
    elif s[0] == '+':
        idx += 1

    res = 0
    while idx < len(s) and s[idx].isdigit():
        res = res * 10 + int(s[idx])
        idx += 1

    res *= sign
    INT_MIN, INT_MAX = -2**31, 2**31 - 1
    if res < INT_MIN: res = INT_MIN
    if res > INT_MAX: res = INT_MAX
    print(res)

if __name__ == '__main__':
    main()""",
            """import java.util.Scanner;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.hasNextLine() ? sc.nextLine() : "";
        s = s.trim();
        if (s.isEmpty()) {
            System.out.println(0);
            return;
        }

        int sign = 1, idx = 0;
        if (s.charAt(0) == '-') { sign = -1; idx++; }
        else if (s.charAt(0) == '+') { idx++; }

        long res = 0;
        while (idx < s.length() && Character.isDigit(s.charAt(idx))) {
            res = res * 10 + (s.charAt(idx) - '0');
            if (sign == 1 && res > Integer.MAX_VALUE) { System.out.println(Integer.MAX_VALUE); return; }
            if (sign == -1 && -res < Integer.MIN_VALUE) { System.out.println(Integer.MIN_VALUE); return; }
            idx++;
        }
        System.out.println((int)(res * sign));
    }
}""",
            """const fs = require('fs');

function main() {
    let s = fs.readFileSync(0, 'utf-8').trimStart();
    if (!s) {
        console.log(0);
        return;
    }

    let sign = 1, idx = 0;
    if (s[0] === '-') { sign = -1; idx++; }
    else if (s[0] === '+') { idx++; }

    let res = 0;
    while (idx < s.length && s[idx] >= '0' && s[idx] <= '9') {
        res = res * 10 + (s.charCodeAt(idx) - 48);
        idx++;
    }

    res *= sign;
    const INT_MIN = -(2**31), INT_MAX = 2**31 - 1;
    if (res < INT_MIN) res = INT_MIN;
    if (res > INT_MAX) res = INT_MAX;
    console.log(res);
}

main();""",
            """#include <iostream>
#include <string>
#include <climits>
using namespace std;

int main() {
    string s;
    if (!getline(cin, s)) { cout << 0 << endl; return 0; }
    int i = 0, n = s.length();
    while (i < n && s[i] == ' ') i++;
    if (i == n) { cout << 0 << endl; return 0; }

    int sign = 1;
    if (s[i] == '-') { sign = -1; i++; }
    else if (s[i] == '+') { i++; }

    long long res = 0;
    while (i < n && isdigit(s[i])) {
        res = res * 10 + (s[i] - '0');
        if (sign == 1 && res > INT_MAX) { cout << INT_MAX << endl; return 0; }
        if (sign == -1 && -res < INT_MIN) { cout << INT_MIN << endl; return 0; }
        i++;
    }
    cout << res * sign << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Implement the `myAtoi(string s)` function, which converts a string to a 32-bit signed integer.\n\n"
            "The algorithm for `myAtoi(string s)` is as follows:\n"
            "1. **Whitespace:** Ignore any leading whitespace (`\" \"`).\n"
            "2. **Signedness:** Check if the next character is `'-'` or `'+'`. Default is positive.\n"
            "3. **Conversion:** Read the integer by skipping leading zeros until a non-digit character is encountered.\n"
            "4. **Rounding:** If the integer is out of the 32-bit signed integer range `[-2^31, 2^31 - 1]`, clamp it to the boundary.\n\n"
            "### Example 1:\n"
            "- **Input:** `42`\n"
            "- **Output:** `42`\n\n"
            "### Example 2:\n"
            "- **Input:** `   -042`\n"
            "- **Output:** `-42`\n\n"
            "### Example 3:\n"
            "- **Input:** `1337c0d3`\n"
            "- **Output:** `1337`\n\n"
            "### Constraints:\n"
            "- `0 <= s.length <= 200`\n"
            "- `s` consists of English letters (lower-case and upper-case), digits (`0-9`), `' '`, `'+'`, `'-'`, and `'.'`. \n\n"
            "### Input / Output Format:\n"
            "- **Input:** A string `s`\n"
            "- **Output:** Parsed and clamped 32-bit integer\n\n"
            "<details><summary>💡 Hint 1</summary>Trim leading whitespace first. Then look for an optional `+` or `-` sign.</details>\n"
            "<details><summary>💡 Hint 2</summary>Accumulate digits: `res = res * 10 + digit`. Stop at the first non-digit character.</details>\n"
            "<details><summary>💡 Hint 3</summary>Clamp the final signed result between `[-2147483648, 2147483647]`.</details>"
        ),
        "test_cases": [
            {"input": "42\n", "expected_output": "42", "comparator_type": "exact"},
            {"input": "   -042\n", "expected_output": "-42", "comparator_type": "exact"},
            {"input": "1337c0d3\n", "expected_output": "1337", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Palindrome Number",
        "difficulty": "easy",
        "optimal_time_complexity": "O(log n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    s = sys.stdin.read().strip()
    if not s:
        return
    print("true" if s == s[::-1] else "false")

if __name__ == '__main__':
    main()""",
            """import java.util.Scanner;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNext()) return;
        String s = sc.next();
        String rev = new StringBuilder(s).reverse().toString();
        System.out.println(s.equals(rev) ? "true" : "false");
    }
}""",
            """const fs = require('fs');

function main() {
    const s = fs.readFileSync(0, 'utf-8').trim();
    if (!s) return;
    const rev = s.split('').reverse().join('');
    console.log(s === rev ? 'true' : 'false');
}

main();""",
            """#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    string s;
    if (!(cin >> s)) return 0;
    string rev = s;
    reverse(rev.begin(), rev.end());
    cout << (s == rev ? "true" : "false") << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given an integer `x`, return `true` if `x` is a **palindrome**, and `false` otherwise.\n\n"
            "An integer is a palindrome when it reads the same forward and backward (e.g. `121` is a palindrome, while `123` is not).\n\n"
            "### Example 1:\n"
            "- **Input:** `121`\n"
            "- **Output:** `true`\n"
            "- **Explanation:** `121` reads as `121` from left to right and from right to left.\n\n"
            "### Example 2:\n"
            "- **Input:** `-121`\n"
            "- **Output:** `false`\n"
            "- **Explanation:** From left to right, it reads `-121`. From right to left, it becomes `121-`. Therefore it is not a palindrome.\n\n"
            "### Example 3:\n"
            "- **Input:** `10`\n"
            "- **Output:** `false`\n"
            "- **Explanation:** Reads `01` from right to left.\n\n"
            "### Constraints:\n"
            "- `-2^31 <= x <= 2^31 - 1`\n\n"
            "### Input / Output Format:\n"
            "- **Input:** Integer `x`\n"
            "- **Output:** `true` or `false`\n\n"
            "<details><summary>💡 Hint 1</summary>Negative numbers can never be palindromes because the negative sign is only at the front.</details>\n"
            "<details><summary>💡 Hint 2</summary>You can reverse the second half of the number and compare it with the first half without converting to string.</details>"
        ),
        "test_cases": [
            {"input": "121\n", "expected_output": "true", "comparator_type": "exact"},
            {"input": "-121\n", "expected_output": "false", "comparator_type": "exact"},
            {"input": "10\n", "expected_output": "false", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Regular Expression Matching",
        "difficulty": "hard",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    lines = sys.stdin.read().strip().split('\\n')
    if not lines:
        return
    s = lines[0].strip()
    p = lines[1].strip() if len(lines) > 1 else ""

    memo = {}
    def dp(i, j):
        if (i, j) in memo:
            return memo[(i, j)]
        if j == len(p):
            res = i == len(s)
        else:
            first_match = i < len(s) and (p[j] == s[i] or p[j] == '.')
            if j + 1 < len(p) and p[j + 1] == '*':
                res = dp(i, j + 2) or (first_match and dp(i + 1, j))
            else:
                res = first_match and dp(i + 1, j + 1)
        memo[(i, j)] = res
        return res

    print("true" if dp(0, 0) else "false")

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.hasNextLine() ? sc.nextLine().trim() : "";
        String p = sc.hasNextLine() ? sc.nextLine().trim() : "";

        boolean[][] dp = new boolean[s.length() + 1][p.length() + 1];
        dp[s.length()][p.length()] = true;

        for (int i = s.length(); i >= 0; i--) {
            for (int j = p.length() - 1; j >= 0; j--) {
                boolean firstMatch = (i < s.length() && (p.charAt(j) == s.charAt(i) || p.charAt(j) == '.'));
                if (j + 1 < p.length() && p.charAt(j + 1) == '*') {
                    dp[i][j] = dp[i][j + 2] || (firstMatch && dp[i + 1][j]);
                } else {
                    dp[i][j] = firstMatch && dp[i + 1][j + 1];
                }
            }
        }
        System.out.println(dp[0][0] ? "true" : "false");
    }
}""",
            """const fs = require('fs');

function main() {
    const lines = fs.readFileSync(0, 'utf-8').trim().split('\\n');
    const s = lines[0] ? lines[0].trim() : '';
    const p = lines[1] ? lines[1].trim() : '';

    const memo = new Map();
    function dp(i, j) {
        const key = `${i},${j}`;
        if (memo.has(key)) return memo.get(key);
        if (j === p.length) return i === s.length;

        const firstMatch = i < s.length && (p[j] === s[i] || p[j] === '.');
        let res = false;
        if (j + 1 < p.length && p[j + 1] === '*') {
            res = dp(i, j + 2) || (firstMatch && dp(i + 1, j));
        } else {
            res = firstMatch && dp(i + 1, j + 1);
        }
        memo.set(key, res);
        return res;
    }
    console.log(dp(0, 0) ? 'true' : 'false');
}

main();""",
            """#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
    string s = "", p = "";
    getline(cin, s);
    getline(cin, p);

    int m = s.length(), n = p.length();
    vector<vector<bool>> dp(m + 1, vector<bool>(n + 1, false));
    dp[m][n] = true;

    for (int i = m; i >= 0; i--) {
        for (int j = n - 1; j >= 0; j--) {
            bool firstMatch = (i < m && (p[j] == s[i] || p[j] == '.'));
            if (j + 1 < n && p[j + 1] == '*') {
                dp[i][j] = dp[i][j + 2] || (firstMatch && dp[i + 1][j]);
            } else {
                dp[i][j] = firstMatch && dp[i + 1][j + 1];
            }
        }
    }
    cout << (dp[0][0] ? "true" : "false") << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given an input string `s` and a pattern `p`, implement regular expression matching with support for `'.'` and `'*'`. \n\n"
            "- `'.'` Matches any single character.\n"
            "- `'*'` Matches **zero or more** of the preceding element.\n\n"
            "The matching should cover the **entire** input string (not partial).\n\n"
            "### Example 1:\n"
            "- **Input:** `s = \"aa\"`, `p = \"a\"`\n"
            "- **Output:** `false`\n"
            "- **Explanation:** `\"a\"` does not match the entire string `\"aa\"`.\n\n"
            "### Example 2:\n"
            "- **Input:** `s = \"aa\"`, `p = \"a*\"`\n"
            "- **Output:** `true`\n"
            "- **Explanation:** `'*'` means zero or more of the preceding element, `'a'`. Therefore, by repeating `'a'` once, it becomes `\"aa\"`.\n\n"
            "### Example 3:\n"
            "- **Input:** `s = \"ab\"`, `p = \".*\"`\n"
            "- **Output:** `true`\n"
            "- **Explanation:** `\".*\"` means \"zero or more (`*`) of any character (`.`)\".\n\n"
            "### Constraints:\n"
            "- `1 <= s.length <= 20`\n"
            "- `1 <= p.length <= 20`\n"
            "- `s` contains only lowercase English letters.\n"
            "- `p` contains only lowercase English letters, `'.'`, and `'*'`. \n"
            "- It is guaranteed for each appearance of the character `'*'`, there will be a previous valid character to match.\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** String `s`\n"
            "- **Line 2:** Pattern `p`\n"
            "- **Output:** `true` or `false`\n\n"
            "<details><summary>💡 Hint 1</summary>Use Dynamic Programming / Memoization. Let `dp(i, j)` represent whether `s[i:]` matches `p[j:]`.</details>\n"
            "<details><summary>💡 Hint 2</summary>If `p[j+1] == '*'`: we can either ignore the `*` clause (`dp(i, j+2)`) or use it if `s[i]` matches `p[j]` (`dp(i+1, j)`).</details>"
        ),
        "test_cases": [
            {"input": "aa\na\n", "expected_output": "false", "comparator_type": "exact"},
            {"input": "aa\na*\n", "expected_output": "true", "comparator_type": "exact"},
            {"input": "ab\n.*", "expected_output": "true", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Container With Most Water",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    heights = [int(x) for x in input_data[1:n+1]]

    # Two-pointer approach: O(n) time, O(1) space
    left, right = 0, n - 1
    max_area = 0
    while left < right:
        area = min(heights[left], heights[right]) * (right - left)
        max_area = max(max_area, area)
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1

    print(max_area)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[] height = new int[n];
        for (int i = 0; i < n; i++) height[i] = sc.nextInt();

        // Two-pointer approach for O(n) time, O(1) space
        int left = 0, right = n - 1;
        int maxArea = 0;
        while (left < right) {
            int area = Math.min(height[left], height[right]) * (right - left);
            maxArea = Math.max(maxArea, area);
            if (height[left] < height[right]) left++;
            else right--;
        }
        System.out.println(maxArea);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const heights = input.slice(1, n + 1);

    let left = 0, right = n - 1;
    let maxArea = 0;
    while (left < right) {
        const area = Math.min(heights[left], heights[right]) * (right - left);
        if (area > maxArea) maxArea = area;
        if (heights[left] < heights[right]) left++;
        else right--;
    }
    console.log(maxArea);
}

main();""",
            """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> heights(n);
    for (int i = 0; i < n; i++) cin >> heights[i];

    int left = 0, right = n - 1;
    int maxArea = 0;
    while (left < right) {
        int area = min(heights[left], heights[right]) * (right - left);
        maxArea = max(maxArea, area);
        if (heights[left] < heights[right]) left++;
        else right--;
    }
    cout << maxArea << endl;
    return 0;
}"""
        ),
        "generator_key": "container_with_most_water",
        "description": (
            "You are given an integer array `height` of length `n`. There are `n` vertical lines drawn such that the two endpoints of the `i-th` line are `(i, 0)` and `(i, height[i])`.\n\n"
            "Find two lines that together with the x-axis form a container, such that the container contains the **most water**.\n\n"
            "Return the **maximum amount of water** a container can store. (Notice that you may not slant the container).\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 9`, `height = [1, 8, 6, 2, 5, 4, 8, 3, 7]`\n"
            "- **Output:** `49`\n"
            "- **Explanation:** The vertical lines are represented by array `[1,8,6,2,5,4,8,3,7]`. The max area is between index 1 (height 8) and index 8 (height 7), area = min(8, 7) * (8 - 1) = 7 * 7 = 49.\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 2`, `height = [1, 1]`\n"
            "- **Output:** `1`\n"
            "- **Explanation:** Area = min(1, 1) * (1 - 0) = 1.\n\n"
            "### Constraints:\n"
            "- `n == height.length`\n"
            "- `2 <= n <= 10^5`\n"
            "- `0 <= height[i] <= 10^4`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n`\n"
            "- **Line 2:** `n` space-separated integers representing `height`\n"
            "- **Output:** Integer representing maximum water volume\n\n"
            "<details><summary>💡 Hint 1</summary>A brute force check of all pairs is O(n²). Can we shrink the search space greedily using two pointers?</details>\n"
            "<details><summary>💡 Hint 2</summary>Place `left = 0` and `right = n - 1`. The area is limited by `min(height[left], height[right])`.</details>\n"
            "<details><summary>💡 Hint 3</summary>To have a chance at finding a larger area with a smaller width, we must move the pointer pointing to the shorter line inward.</details>"
        ),
        "test_cases": [
            {"input": "9\n1 8 6 2 5 4 8 3 7\n", "expected_output": "49", "comparator_type": "exact"},
            {"input": "2\n1 1\n",                "expected_output": "1",  "comparator_type": "exact"},
            {"input": "4\n4 3 2 4\n",            "expected_output": "16", "comparator_type": "exact"},
        ],
        "signatures": [
            {
                "pattern_type": "nested_loop_lookup",
                "hint_text": (
                    "Checking every pair of lines is O(n²). The two-pointer technique does "
                    "this in O(n): start with pointers at both ends, compute the current area, "
                    "then move the pointer on the shorter side inward."
                ),
            }
        ],
    },
    {
        "title": "Integer to Roman",
        "difficulty": "medium",
        "optimal_time_complexity": "O(1)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    val = int(sys.stdin.read().strip())
    mapping = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
    ]
    res = []
    for num, sym in mapping:
        while val >= num:
            res.append(sym)
            val -= num
    print("".join(res))

if __name__ == '__main__':
    main()""",
            """import java.util.Scanner;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int val = sc.nextInt();
        int[] nums = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};
        String[] syms = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"};

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < nums.length; i++) {
            while (val >= nums[i]) {
                sb.append(syms[i]);
                val -= nums[i];
            }
        }
        System.out.println(sb.toString());
    }
}""",
            """const fs = require('fs');

function main() {
    let val = parseInt(fs.readFileSync(0, 'utf-8').trim(), 10);
    if (isNaN(val)) return;
    const mapping = [
        [1000, "M"], [900, "CM"], [500, "D"], [400, "CD"],
        [100, "C"], [90, "XC"], [50, "L"], [40, "XL"],
        [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]
    ];
    let res = '';
    for (const [num, sym] of mapping) {
        while (val >= num) {
            res += sym;
            val -= num;
        }
    }
    console.log(res);
}

main();""",
            """#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
    int val;
    if (!(cin >> val)) return 0;
    vector<pair<int, string>> mapping = {
        {1000, "M"}, {900, "CM"}, {500, "D"}, {400, "CD"},
        {100, "C"}, {90, "XC"}, {50, "L"}, {40, "XL"},
        {10, "X"}, {9, "IX"}, {5, "V"}, {4, "IV"}, {1, "I"}
    };
    string res = "";
    for (auto& p : mapping) {
        while (val >= p.first) {
            res += p.second;
            val -= p.first;
        }
    }
    cout << res << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Seven different symbols represent Roman numerals with the following values:\n\n"
            "| Symbol | Value |\n"
            "|---|---|\n"
            "| I | 1 |\n"
            "| V | 5 |\n"
            "| X | 10 |\n"
            "| L | 50 |\n"
            "| C | 100 |\n"
            "| D | 500 |\n"
            "| M | 1000 |\n\n"
            "Roman numerals are formed by appending the conversions of decimal place values from highest to lowest. Subtractive forms include: IV (4), IX (9), XL (40), XC (90), CD (400), CM (900).\n\n"
            "Given an integer `num`, convert it to a Roman numeral string.\n\n"
            "### Example 1:\n"
            "- **Input:** `3749`\n"
            "- **Output:** `MMMDCCXLIX`\n"
            "- **Explanation:** `3000 = MMM`, `700 = DCC`, `40 = XL`, `9 = IX`.\n\n"
            "### Example 2:\n"
            "- **Input:** `58`\n"
            "- **Output:** `LVIII`\n"
            "- **Explanation:** `50 = L`, `8 = VIII`.\n\n"
            "### Example 3:\n"
            "- **Input:** `1994`\n"
            "- **Output:** `MCMXCIV`\n"
            "- **Explanation:** `1000 = M`, `900 = CM`, `90 = XC`, `4 = IV`.\n\n"
            "### Constraints:\n"
            "- `1 <= num <= 3999`\n\n"
            "### Input / Output Format:\n"
            "- **Input:** A single integer `num`\n"
            "- **Output:** Roman numeral string\n\n"
            "<details><summary>💡 Hint 1</summary>Create an ordered table of values and symbols including the subtractive forms (1000: M, 900: CM, 500: D, 400: CD, ..., 1: I).</details>\n"
            "<details><summary>💡 Hint 2</summary>Iterate from largest to smallest value: while `num >= value`, append symbol and subtract value from `num`.</details>"
        ),
        "test_cases": [
            {"input": "3749\n", "expected_output": "MMMDCCXLIX", "comparator_type": "exact"},
            {"input": "58\n", "expected_output": "LVIII", "comparator_type": "exact"},
            {"input": "1994\n", "expected_output": "MCMXCIV", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Roman to Integer",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    s = sys.stdin.read().strip()
    mapping = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    res = 0
    for i in range(len(s)):
        if i + 1 < len(s) and mapping[s[i]] < mapping[s[i+1]]:
            res -= mapping[s[i]]
        else:
            res += mapping[s[i]]
    print(res)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNext()) return;
        String s = sc.next();
        Map<Character, Integer> map = Map.of(
            'I', 1, 'V', 5, 'X', 10, 'L', 50, 'C', 100, 'D', 500, 'M', 1000
        );
        int res = 0;
        for (int i = 0; i < s.length(); i++) {
            int cur = map.get(s.charAt(i));
            if (i + 1 < s.length() && cur < map.get(s.charAt(i + 1))) {
                res -= cur;
            } else {
                res += cur;
            }
        }
        System.out.println(res);
    }
}""",
            """const fs = require('fs');

function main() {
    const s = fs.readFileSync(0, 'utf-8').trim();
    if (!s) return;
    const map = { I: 1, V: 5, X: 10, L: 50, C: 100, D: 500, M: 1000 };
    let res = 0;
    for (let i = 0; i < s.length; i++) {
        const cur = map[s[i]];
        const next = i + 1 < s.length ? map[s[i + 1]] : 0;
        if (cur < next) res -= cur;
        else res += cur;
    }
    console.log(res);
}

main();""",
            """#include <iostream>
#include <string>
#include <unordered_map>
using namespace std;

int main() {
    string s;
    if (!(cin >> s)) return 0;
    unordered_map<char, int> map = {
        {'I', 1}, {'V', 5}, {'X', 10}, {'L', 50}, {'C', 100}, {'D', 500}, {'M', 1000}
    };
    int res = 0;
    for (int i = 0; i < (int)s.length(); i++) {
        if (i + 1 < (int)s.length() && map[s[i]] < map[s[i + 1]]) {
            res -= map[s[i]];
        } else {
            res += map[s[i]];
        }
    }
    cout << res << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Roman numerals are represented by seven different symbols: `I` (1), `V` (5), `X` (10), `L` (50), `C` (100), `D` (500), `M` (1000).\n\n"
            "Usually, numerals are written largest to smallest from left to right. However, if a smaller numeral appears before a larger one, it represents subtraction (e.g., `IV` is `4`, `IX` is `9`, `XL` is `40`, `XC` is `90`, `CD` is `400`, `CM` is `900`).\n\n"
            "Given a roman numeral string `s`, convert it to an integer.\n\n"
            "### Example 1:\n"
            "- **Input:** `III`\n"
            "- **Output:** `3`\n"
            "- **Explanation:** `III = 3`.\n\n"
            "### Example 2:\n"
            "- **Input:** `LVIII`\n"
            "- **Output:** `58`\n"
            "- **Explanation:** `L = 50, V= 5, III = 3`.\n\n"
            "### Example 3:\n"
            "- **Input:** `MCMXCIV`\n"
            "- **Output:** `1994`\n"
            "- **Explanation:** `M = 1000, CM = 900, XC = 90 and IV = 4`.\n\n"
            "### Constraints:\n"
            "- `1 <= s.length <= 15`\n"
            "- `s` contains only the characters `('I', 'V', 'X', 'L', 'C', 'D', 'M')`.\n"
            "- It is guaranteed that `s` is a valid roman numeral in the range `[1, 3999]`.\n\n"
            "### Input / Output Format:\n"
            "- **Input:** Roman numeral string `s`\n"
            "- **Output:** Integer value\n\n"
            "<details><summary>💡 Hint 1</summary>If current character's value is less than next character's value (e.g. `I` before `V`), subtract its value.</details>\n"
            "<details><summary>💡 Hint 2</summary>Otherwise, add its value to total sum.</details>"
        ),
        "test_cases": [
            {"input": "III\n", "expected_output": "3", "comparator_type": "exact"},
            {"input": "LVIII\n", "expected_output": "58", "comparator_type": "exact"},
            {"input": "MCMXCIV\n", "expected_output": "1994", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "3Sum",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n^2)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:n+1]]

    nums.sort()
    res = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                res.append(f"{nums[i]} {nums[left]} {nums[right]}")
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1

    for triplet in res:
        print(triplet)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();

        Arrays.sort(nums);
        for (int i = 0; i < n - 2; i++) {
            if (i > 0 && nums[i] == nums[i - 1]) continue;
            int left = i + 1, right = n - 1;
            while (left < right) {
                int sum = nums[i] + nums[left] + nums[right];
                if (sum < 0) left++;
                else if (sum > 0) right--;
                else {
                    System.out.println(nums[i] + " " + nums[left] + " " + nums[right]);
                    while (left < right && nums[left] == nums[left + 1]) left++;
                    while (left < right && nums[right] == nums[right - 1]) right--;
                    left++;
                    right--;
                }
            }
        }
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const nums = input.slice(1, n + 1).sort((a, b) => a - b);

    for (let i = 0; i < n - 2; i++) {
        if (i > 0 && nums[i] === nums[i - 1]) continue;
        let left = i + 1, right = n - 1;
        while (left < right) {
            const sum = nums[i] + nums[left] + nums[right];
            if (sum < 0) left++;
            else if (sum > 0) right--;
            else {
                console.log(`${nums[i]} ${nums[left]} ${nums[right]}`);
                while (left < right && nums[left] === nums[left + 1]) left++;
                while (left < right && nums[right] === nums[right - 1]) right--;
                left++;
                right--;
            }
        }
    }
}

main();""",
            """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> nums(n);
    for (int i = 0; i < n; i++) cin >> nums[i];

    sort(nums.begin(), nums.end());
    for (int i = 0; i < n - 2; i++) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        int left = i + 1, right = n - 1;
        while (left < right) {
            int total = nums[i] + nums[left] + nums[right];
            if (total < 0) left++;
            else if (total > 0) right--;
            else {
                cout << nums[i] << " " << nums[left] << " " << nums[right] << endl;
                while (left < right && nums[left] == nums[left + 1]) left++;
                while (left < right && nums[right] == nums[right - 1]) right--;
                left++;
                right--;
            }
        }
    }
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given an integer array `nums`, return all the triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.\n\n"
            "Notice that the solution set must not contain duplicate triplets.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 6`, `nums = [-1, 0, 1, 2, -1, -4]`\n"
            "- **Output:**\n"
            "  `-1 -1 2`\n"
            "  `-1 0 1`\n"
            "- **Explanation:** `nums[0] + nums[1] + nums[2] = (-1) + 0 + 1 = 0`.\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 3`, `nums = [0, 1, 1]`\n"
            "- **Output:** (empty / no triplets)\n\n"
            "### Constraints:\n"
            "- `3 <= nums.length <= 3000`\n"
            "- `-10^5 <= nums[i] <= 10^5`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n` (number of elements)\n"
            "- **Line 2:** `n` space-separated integers\n"
            "- **Output:** Space-separated triplets line by line\n\n"
            "<details><summary>💡 Hint 1</summary>Sort the input array to easily skip duplicate values and use two pointers.</details>\n"
            "<details><summary>💡 Hint 2</summary>Iterate through `nums`. For each element `nums[i]`, find two numbers in `nums[i+1:]` that sum to `-nums[i]`.</details>"
        ),
        "test_cases": [
            {"input": "6\n-1 0 1 2 -1 -4\n", "expected_output": "-1 -1 2\n-1 0 1", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "3Sum Closest",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n^2)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:n+1]]
    target = int(input_data[n+1])

    nums.sort()
    closest_sum = nums[0] + nums[1] + nums[2]

    for i in range(len(nums) - 2):
        left, right = i + 1, len(nums) - 1
        while left < right:
            curr_sum = nums[i] + nums[left] + nums[right]
            if abs(curr_sum - target) < abs(closest_sum - target):
                closest_sum = curr_sum

            if curr_sum < target:
                left += 1
            elif curr_sum > target:
                right -= 1
            else:
                print(closest_sum)
                return

    print(closest_sum)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        int target = sc.nextInt();

        Arrays.sort(nums);
        int closestSum = nums[0] + nums[1] + nums[2];

        for (int i = 0; i < n - 2; i++) {
            int left = i + 1, right = n - 1;
            while (left < right) {
                int currSum = nums[i] + nums[left] + nums[right];
                if (Math.abs(currSum - target) < Math.abs(closestSum - target)) {
                    closestSum = currSum;
                }
                if (currSum < target) {
                    left++;
                } else if (currSum > target) {
                    right--;
                } else {
                    System.out.println(closestSum);
                    return;
                }
            }
        }
        System.out.println(closestSum);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const nums = input.slice(1, n + 1).sort((a, b) => a - b);
    const target = input[n + 1];

    let closestSum = nums[0] + nums[1] + nums[2];

    for (let i = 0; i < n - 2; i++) {
        let left = i + 1, right = n - 1;
        while (left < right) {
            const currSum = nums[i] + nums[left] + nums[right];
            if (Math.abs(currSum - target) < Math.abs(closestSum - target)) {
                closestSum = currSum;
            }
            if (currSum < target) left++;
            else if (currSum > target) right--;
            else {
                console.log(closestSum);
                return;
            }
        }
    }
    console.log(closestSum);
}

main();""",
            """#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> nums(n);
    for (int i = 0; i < n; i++) cin >> nums[i];
    int target;
    cin >> target;

    sort(nums.begin(), nums.end());
    int closestSum = nums[0] + nums[1] + nums[2];

    for (int i = 0; i < n - 2; i++) {
        int left = i + 1, right = n - 1;
        while (left < right) {
            int currSum = nums[i] + nums[left] + nums[right];
            if (abs(currSum - target) < abs(closestSum - target)) {
                closestSum = currSum;
            }
            if (currSum < target) left++;
            else if (currSum > target) right--;
            else {
                cout << closestSum << endl;
                return 0;
            }
        }
    }
    cout << closestSum << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given an integer array `nums` of length `n` and an integer `target`, find three integers in `nums` such that the sum is **closest to target**.\n\n"
            "Return the **sum of the three integers**.\n\n"
            "You may assume that each input would have **exactly one solution**.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 4`, `nums = [-1, 2, 1, -4]`, `target = 1`\n"
            "- **Output:** `2`\n"
            "- **Explanation:** The sum that is closest to the target is `2` (`-1 + 2 + 1 = 2`).\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 3`, `nums = [0, 0, 0]`, `target = 1`\n"
            "- **Output:** `0`\n"
            "- **Explanation:** The sum that is closest to the target is `0` (`0 + 0 + 0 = 0`).\n\n"
            "### Example 3:\n"
            "- **Input:** `n = 3`, `nums = [0, 1, 2]`, `target = 0`\n"
            "- **Output:** `3`\n"
            "- **Explanation:** The closest sum to 0 is `3` (`0 + 1 + 2 = 3`).\n\n"
            "### Constraints:\n"
            "- `3 <= nums.length <= 500`\n"
            "- `-1000 <= nums[i] <= 1000`\n"
            "- `-10^4 <= target <= 10^4`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n` (number of elements)\n"
            "- **Line 2:** `n` space-separated integers representing `nums`\n"
            "- **Line 3:** Integer `target`\n"
            "- **Output:** The closest sum (integer)\n\n"
            "<details><summary>💡 Hint 1</summary>Sort the array first in ascending order so you can use the two-pointer technique.</details>\n"
            "<details><summary>💡 Hint 2</summary>Iterate through each element `nums[i]` as the first number, and use two pointers (`left = i + 1`, `right = n - 1`) to explore sums.</details>\n"
            "<details><summary>💡 Hint 3</summary>Compute `current_sum = nums[i] + nums[left] + nums[right]`. If `abs(current_sum - target) < abs(closest_sum - target)`, update `closest_sum`. If `current_sum < target`, increment `left`; otherwise decrement `right`.</details>"
        ),
        "test_cases": [
            {"input": "4\n-1 2 1 -4\n1\n", "expected_output": "2", "comparator_type": "exact"},
            {"input": "3\n0 0 0\n1\n",     "expected_output": "0", "comparator_type": "exact"},
            {"input": "3\n0 1 2\n0\n",     "expected_output": "3", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Valid Parentheses",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    s = sys.stdin.read().strip()
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                print("false")
                return
        else:
            stack.append(char)
    print("true" if not stack else "false")

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.hasNext() ? sc.next() : "";
        Stack<Character> stack = new Stack<>();
        for (char c : s.toCharArray()) {
            if (c == '(') stack.push(')');
            else if (c == '{') stack.push('}');
            else if (c == '[') stack.push(']');
            else if (stack.isEmpty() || stack.pop() != c) {
                System.out.println("false");
                return;
            }
        }
        System.out.println(stack.isEmpty() ? "true" : "false");
    }
}""",
            """const fs = require('fs');

function main() {
    const s = fs.readFileSync(0, 'utf-8').trim();
    const stack = [];
    const mapping = { ')': '(', '}': '{', ']': '[' };
    for (const char of s) {
        if (mapping[char]) {
            const top = stack.length ? stack.pop() : '#';
            if (mapping[char] !== top) {
                console.log('false');
                return;
            }
        } else {
            stack.push(char);
        }
    }
    console.log(stack.length === 0 ? 'true' : 'false');
}

main();""",
            """#include <iostream>
#include <string>
#include <stack>
using namespace std;

int main() {
    string s;
    if (!(cin >> s)) { cout << "true" << endl; return 0; }
    stack<char> st;
    for (char c : s) {
        if (c == '(') st.push(')');
        else if (c == '{') st.push('}');
        else if (c == '[') st.push(']');
        else {
            if (st.empty() || st.top() != c) {
                cout << "false" << endl;
                return 0;
            }
            st.pop();
        }
    }
    cout << (st.empty() ? "true" : "false") << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.\n\n"
            "An input string is valid if:\n"
            "1. Open brackets must be closed by the same type of brackets.\n"
            "2. Open brackets must be closed in the correct order.\n"
            "3. Every close bracket has a corresponding open bracket of the same type.\n\n"
            "### Example 1:\n"
            "- **Input:** `()`\n"
            "- **Output:** `true`\n\n"
            "### Example 2:\n"
            "- **Input:** `()[]{}`\n"
            "- **Output:** `true`\n\n"
            "### Example 3:\n"
            "- **Input:** `(]`\n"
            "- **Output:** `false`\n\n"
            "### Constraints:\n"
            "- `1 <= s.length <= 10^4`\n"
            "- `s` consists of parentheses only `'()[]{}'`.\n\n"
            "### Input / Output Format:\n"
            "- **Input:** A single string `s`\n"
            "- **Output:** `true` or `false`\n\n"
            "<details><summary>💡 Hint 1</summary>Use a Stack data structure to keep track of expected matching closing brackets.</details>\n"
            "<details><summary>💡 Hint 2</summary>When you see an opening bracket, push its corresponding closing bracket onto the stack. When you see a closing bracket, verify that it matches `stack.pop()`.</details>"
        ),
        "test_cases": [
            {"input": "()\n", "expected_output": "true", "comparator_type": "exact"},
            {"input": "()[]{}\n", "expected_output": "true", "comparator_type": "exact"},
            {"input": "(]\n", "expected_output": "false", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Merge Two Sorted Lists",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    lines = sys.stdin.read().strip().split('\\n')
    if not lines:
        return
    l1 = list(map(int, lines[0].split())) if lines[0].strip() else []
    l2 = list(map(int, lines[1].split())) if len(lines) > 1 and lines[1].strip() else []

    res = []
    i, j = 0, 0
    while i < len(l1) and j < len(l2):
        if l1[i] <= l2[j]:
            res.append(l1[i])
            i += 1
        else:
            res.append(l2[j])
            j += 1
    res.extend(l1[i:])
    res.extend(l2[j:])
    print(" ".join(map(str, res)))

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<Integer> l1 = new ArrayList<>();
        List<Integer> l2 = new ArrayList<>();
        if (sc.hasNextLine()) {
            String s = sc.nextLine().trim();
            if (!s.isEmpty()) for (String v : s.split("\\\\s+")) l1.add(Integer.parseInt(v));
        }
        if (sc.hasNextLine()) {
            String s = sc.nextLine().trim();
            if (!s.isEmpty()) for (String v : s.split("\\\\s+")) l2.add(Integer.parseInt(v));
        }

        int i = 0, j = 0;
        List<String> res = new ArrayList<>();
        while (i < l1.size() && j < l2.size()) {
            if (l1.get(i) <= l2.get(j)) res.add(String.valueOf(l1.get(i++)));
            else res.add(String.valueOf(l2.get(j++)));
        }
        while (i < l1.size()) res.add(String.valueOf(l1.get(i++)));
        while (j < l2.size()) res.add(String.valueOf(l2.get(j++)));

        System.out.println(String.join(" ", res));
    }
}""",
            """const fs = require('fs');

function main() {
    const lines = fs.readFileSync(0, 'utf-8').trim().split('\\n');
    const l1 = lines[0] ? lines[0].trim().split(/\\s+/).filter(Boolean).map(Number) : [];
    const l2 = lines[1] ? lines[1].trim().split(/\\s+/).filter(Boolean).map(Number) : [];

    const res = [];
    let i = 0, j = 0;
    while (i < l1.length && j < l2.length) {
        if (l1[i] <= l2[j]) res.push(l1[i++]);
        else res.push(l2[j++]);
    }
    while (i < l1.length) res.push(l1[i++]);
    while (j < l2.length) res.push(l2[j++]);
    console.log(res.join(' '));
}

main();""",
            """#include <iostream>
#include <vector>
#include <string>
#include <sstream>
using namespace std;

int main() {
    string s1, s2;
    vector<int> l1, l2;
    if (getline(cin, s1)) {
        stringstream ss(s1);
        int v; while (ss >> v) l1.push_back(v);
    }
    if (getline(cin, s2)) {
        stringstream ss(s2);
        int v; while (ss >> v) l2.push_back(v);
    }
    vector<int> res;
    int i = 0, j = 0;
    while (i < (int)l1.size() && j < (int)l2.size()) {
        if (l1[i] <= l2[j]) res.push_back(l1[i++]);
        else res.push_back(l2[j++]);
    }
    while (i < (int)l1.size()) res.push_back(l1[i++]);
    while (j < (int)l2.size()) res.push_back(l2[j++]);

    for (int k = 0; k < (int)res.size(); k++) {
        cout << res[k] << (k + 1 == (int)res.size() ? "" : " ");
    }
    cout << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "You are given the heads of two sorted lists `list1` and `list2`.\n\n"
            "Merge the two lists into one **sorted** list. The list should be made by splicing together the nodes of the first two lists.\n\n"
            "Return the head of the merged sorted list.\n\n"
            "### Example 1:\n"
            "- **Input:**\n"
            "  `1 2 4`\n"
            "  `1 3 4`\n"
            "- **Output:** `1 1 2 3 4 4`\n\n"
            "### Example 2:\n"
            "- **Input:**\n"
            "  ` ` (empty)\n"
            "  `0`\n"
            "- **Output:** `0`\n\n"
            "### Constraints:\n"
            "- The number of nodes in both lists is in the range `[0, 50]`.\n"
            "- `-100 <= Node.val <= 100`\n"
            "- Both `list1` and `list2` are sorted in non-decreasing order.\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Space-separated numbers for list 1\n"
            "- **Line 2:** Space-separated numbers for list 2\n"
            "- **Output:** Space-separated sorted numbers\n\n"
            "<details><summary>💡 Hint 1</summary>Use a two-pointer approach comparing the current elements of both sorted lists.</details>"
        ),
        "test_cases": [
            {"input": "1 2 4\n1 3 4\n", "expected_output": "1 1 2 3 4 4", "comparator_type": "exact"},
            {"input": "\n0\n", "expected_output": "0", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Best Time to Buy and Sell Stock",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    prices = [int(x) for x in input_data[1:n+1]]

    min_price = float('inf')
    max_profit = 0
    for price in prices:
        if price < min_price:
            min_price = price
        elif price - min_price > max_profit:
            max_profit = price - min_price

    print(max_profit)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int minPrice = Integer.MAX_VALUE;
        int maxProfit = 0;
        for (int i = 0; i < n; i++) {
            int price = sc.nextInt();
            if (price < minPrice) minPrice = price;
            else if (price - minPrice > maxProfit) maxProfit = price - minPrice;
        }
        System.out.println(maxProfit);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const prices = input.slice(1, n + 1);

    let minPrice = Infinity;
    let maxProfit = 0;
    for (let i = 0; i < n; i++) {
        if (prices[i] < minPrice) minPrice = prices[i];
        else if (prices[i] - minPrice > maxProfit) maxProfit = prices[i] - minPrice;
    }
    console.log(maxProfit);
}

main();""",
            """#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    int minPrice = INT_MAX;
    int maxProfit = 0;
    for (int i = 0; i < n; i++) {
        int price;
        cin >> price;
        if (price < minPrice) minPrice = price;
        else if (price - minPrice > maxProfit) maxProfit = price - minPrice;
    }
    cout << maxProfit << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "You are given an array `prices` where `prices[i]` is the price of a given stock on the `i-th` day.\n\n"
            "You want to maximize your profit by choosing a **single day** to buy one stock and choosing a **different day in the future** to sell that stock.\n\n"
            "Return the **maximum profit** you can achieve from this transaction. If you cannot achieve any profit, return `0`.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 6`, `prices = [7, 1, 5, 3, 6, 4]`\n"
            "- **Output:** `5`\n"
            "- **Explanation:** Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6 - 1 = 5.\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 5`, `prices = [7, 6, 4, 3, 1]`\n"
            "- **Output:** `0`\n"
            "- **Explanation:** In this case, no transactions are done and the max profit = 0.\n\n"
            "### Constraints:\n"
            "- `1 <= prices.length <= 10^5`\n"
            "- `0 <= prices[i] <= 10^4`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n` (number of days)\n"
            "- **Line 2:** `n` space-separated integers representing `prices`\n"
            "- **Output:** Maximum profit integer\n\n"
            "<details><summary>💡 Hint 1</summary>Keep track of the minimum stock price seen so far as you iterate through the list.</details>\n"
            "<details><summary>💡 Hint 2</summary>For each day, the maximum profit if selling today is `prices[i] - min_price_so_far`.</details>"
        ),
        "test_cases": [
            {"input": "6\n7 1 5 3 6 4\n", "expected_output": "5", "comparator_type": "exact"},
            {"input": "5\n7 6 4 3 1\n",   "expected_output": "0", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Valid Palindrome",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    s = sys.stdin.read().strip()
    filtered = [c.lower() for c in s if c.isalnum()]
    print("true" if filtered == filtered[::-1] else "false")

if __name__ == '__main__':
    main()""",
            """import java.util.Scanner;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.hasNextLine() ? sc.nextLine() : "";
        int left = 0, right = s.length() - 1;
        while (left < right) {
            while (left < right && !Character.isLetterOrDigit(s.charAt(left))) left++;
            while (left < right && !Character.isLetterOrDigit(s.charAt(right))) right--;
            if (Character.toLowerCase(s.charAt(left)) != Character.toLowerCase(s.charAt(right))) {
                System.out.println("false");
                return;
            }
            left++;
            right--;
        }
        System.out.println("true");
    }
}""",
            """const fs = require('fs');

function main() {
    const s = fs.readFileSync(0, 'utf-8');
    let left = 0, right = s.length - 1;
    function isAlnum(c) {
        const code = c.charCodeAt(0);
        return (code >= 48 && code <= 57) || (code >= 65 && code <= 90) || (code >= 97 && code <= 122);
    }
    while (left < right) {
        while (left < right && !isAlnum(s[left])) left++;
        while (left < right && !isAlnum(s[right])) right--;
        if (s[left].toLowerCase() !== s[right].toLowerCase()) {
            console.log('false');
            return;
        }
        left++;
        right--;
    }
    console.log('true');
}

main();""",
            """#include <iostream>
#include <string>
#include <cctype>
using namespace std;

int main() {
    string s;
    if (!getline(cin, s)) { cout << "true" << endl; return 0; }
    int left = 0, right = (int)s.length() - 1;
    while (left < right) {
        while (left < right && !isalnum(s[left])) left++;
        while (left < right && !isalnum(s[right])) right--;
        if (tolower(s[left]) != tolower(s[right])) {
            cout << "false" << endl;
            return 0;
        }
        left++;
        right--;
    }
    cout << "true" << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "A phrase is a **palindrome** if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers.\n\n"
            "Given a string `s`, return `true` if it is a palindrome, or `false` otherwise.\n\n"
            "### Example 1:\n"
            "- **Input:** `A man, a plan, a canal: Panama`\n"
            "- **Output:** `true`\n"
            "- **Explanation:** `\"amanaplanacanalpanama\"` is a palindrome.\n\n"
            "### Example 2:\n"
            "- **Input:** `race a car`\n"
            "- **Output:** `false`\n"
            "- **Explanation:** `\"raceacar\"` is not a palindrome.\n\n"
            "### Constraints:\n"
            "- `1 <= s.length <= 2 * 10^5`\n"
            "- `s` consists only of printable ASCII characters.\n\n"
            "### Input / Output Format:\n"
            "- **Input:** A single string line `s`\n"
            "- **Output:** `true` or `false`\n\n"
            "<details><summary>💡 Hint 1</summary>Use two pointers (`left = 0`, `right = len - 1`), skipping any characters that are not alphanumeric (`isalnum()`).</details>"
        ),
        "test_cases": [
            {"input": "A man, a plan, a canal: Panama\n", "expected_output": "true", "comparator_type": "exact"},
            {"input": "race a car\n", "expected_output": "false", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Maximum Subarray",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:n+1]]

    max_so_far = nums[0]
    current_max = nums[0]
    for num in nums[1:]:
        current_max = max(num, current_max + num)
        max_so_far = max(max_so_far, current_max)

    print(max_so_far)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();

        long maxSoFar = nums[0];
        long currentMax = nums[0];
        for (int i = 1; i < n; i++) {
            currentMax = Math.max((long)nums[i], currentMax + nums[i]);
            maxSoFar = Math.max(maxSoFar, currentMax);
        }
        System.out.println(maxSoFar);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const nums = input.slice(1, n + 1);

    let maxSoFar = nums[0];
    let currentMax = nums[0];
    for (let i = 1; i < n; i++) {
        currentMax = Math.max(nums[i], currentMax + nums[i]);
        maxSoFar = Math.max(maxSoFar, currentMax);
    }
    console.log(maxSoFar);
}

main();""",
            """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> nums(n);
    for (int i = 0; i < n; i++) cin >> nums[i];

    long long maxSoFar = nums[0];
    long long currentMax = nums[0];
    for (int i = 1; i < n; i++) {
        currentMax = max((long long)nums[i], currentMax + nums[i]);
        maxSoFar = max(maxSoFar, currentMax);
    }
    cout << maxSoFar << endl;
    return 0;
}"""
        ),
        "generator_key": "maximum_subarray",
        "description": (
            "Given an integer array `nums`, find the subarray with the **largest sum**, and return its sum.\n\n"
            "A **subarray** is a contiguous non-empty sequence of elements within an array.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 9`, `nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]`\n"
            "- **Output:** `6`\n"
            "- **Explanation:** The subarray `[4, -1, 2, 1]` has the largest sum `6`.\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 1`, `nums = [1]`\n"
            "- **Output:** `1`\n"
            "- **Explanation:** The subarray `[1]` has the largest sum `1`.\n\n"
            "### Example 3:\n"
            "- **Input:** `n = 5`, `nums = [5, 4, -1, 7, 8]`\n"
            "- **Output:** `23`\n"
            "- **Explanation:** The subarray `[5, 4, -1, 7, 8]` has the largest sum `23`.\n\n"
            "### Constraints:\n"
            "- `1 <= nums.length <= 10^5`\n"
            "- `-10^4 <= nums[i] <= 10^4`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n` (number of elements)\n"
            "- **Line 2:** `n` space-separated integers\n"
            "- **Output:** Maximum subarray sum (integer)\n\n"
            "<details><summary>💡 Hint 1</summary>Try Kadane's Algorithm: maintain the maximum subarray sum ending at the current position.</details>\n"
            "<details><summary>💡 Hint 2</summary>At each element `num`, decide whether to add `num` to the previous subarray (`current_max + num`) or start a fresh subarray at `num` (`num`).</details>"
        ),
        "test_cases": [
            {"input": "9\n-2 1 -3 4 -1 2 1 -5 4\n", "expected_output": "6",  "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Merge Intervals",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n log n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    intervals = []
    idx = 1
    for _ in range(n):
        intervals.append([int(input_data[idx]), int(input_data[idx+1])])
        idx += 2

    intervals.sort(key=lambda x: x[0])
    merged = []
    for interval in intervals:
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])

    for start, end in merged:
        print(f"{start} {end}")

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[][] intervals = new int[n][2];
        for (int i = 0; i < n; i++) {
            intervals[i][0] = sc.nextInt();
            intervals[i][1] = sc.nextInt();
        }

        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
        List<int[]> merged = new ArrayList<>();
        for (int[] interval : intervals) {
            if (merged.isEmpty() || merged.get(merged.size() - 1)[1] < interval[0]) {
                merged.add(interval);
            } else {
                merged.get(merged.size() - 1)[1] = Math.max(merged.get(merged.size() - 1)[1], interval[1]);
            }
        }

        for (int[] interval : merged) {
            System.out.println(interval[0] + " " + interval[1]);
        }
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const intervals = [];
    let idx = 1;
    for (let i = 0; i < n; i++) {
        intervals.push([input[idx], input[idx + 1]]);
        idx += 2;
    }

    intervals.sort((a, b) => a[0] - b[0]);
    const merged = [];
    for (const interval of intervals) {
        if (merged.length === 0 || merged[merged.length - 1][1] < interval[0]) {
            merged.push(interval);
        } else {
            merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], interval[1]);
        }
    }

    for (const [start, end] of merged) {
        console.log(`${start} ${end}`);
    }
}

main();""",
            """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<pair<int, int>> intervals(n);
    for (int i = 0; i < n; i++) {
        cin >> intervals[i].first >> intervals[i].second;
    }

    sort(intervals.begin(), intervals.end());
    vector<pair<int, int>> merged;
    for (const auto& interval : intervals) {
        if (merged.empty() || merged.back().second < interval.first) {
            merged.push_back(interval);
        } else {
            merged.back().second = max(merged.back().second, interval.second);
        }
    }

    for (const auto& p : merged) {
        cout << p.first << " " << p.second << endl;
    }
    return 0;
}"""
        ),
        "generator_key": "merge_intervals",
        "description": (
            "Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals, and return an array of the **non-overlapping intervals** that cover all the intervals in the input.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 4`, `intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]`\n"
            "- **Output:**\n"
            "  `1 6`\n"
            "  `8 10`\n"
            "  `15 18`\n"
            "- **Explanation:** Since intervals `[1, 3]` and `[2, 6]` overlap, merge them into `[1, 6]`.\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 2`, `intervals = [[1, 4], [4, 5]]`\n"
            "- **Output:** `1 5`\n"
            "- **Explanation:** Intervals `[1, 4]` and `[4, 5]` are considered overlapping.\n\n"
            "### Constraints:\n"
            "- `1 <= intervals.length <= 10^4`\n"
            "- `intervals[i].length == 2`\n"
            "- `0 <= start_i <= end_i <= 10^4`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n` (number of intervals)\n"
            "- **Next `n` pairs:** `start` and `end` on new lines or space separated\n"
            "- **Output:** Merged intervals line by line (e.g. `start end`)\n\n"
            "<details><summary>💡 Hint 1</summary>Sort the intervals by their start times first.</details>\n"
            "<details><summary>💡 Hint 2</summary>Iterate through the sorted intervals. If current interval's start is <= the previous interval's end, merge them by setting `prev.end = max(prev.end, curr.end)`.</details>"
        ),
        "test_cases": [
            {
                "input": "4\n1 3\n2 6\n8 10\n15 18\n",
                "expected_output": "1 6\n8 10\n15 18",
                "comparator_type": "exact",
            },
        ],
        "signatures": [],
    },
    {
        "title": "Climbing Stairs",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])

    if n <= 2:
        print(n)
        return

    first, second = 1, 2
    for _ in range(3, n + 1):
        first, second = second, first + second

    print(second)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();

        if (n <= 2) {
            System.out.println(n);
            return;
        }

        long first = 1, second = 2;
        for (int i = 3; i <= n; i++) {
            long third = first + second;
            first = second;
            second = third;
        }
        System.out.println(second);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];

    if (n <= 2) {
        console.log(n);
        return;
    }

    let first = 1, second = 2;
    for (let i = 3; i <= n; i++) {
        const third = first + second;
        first = second;
        second = third;
    }
    console.log(second);
}

main();""",
            """#include <iostream>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    if (n <= 2) { cout << n << endl; return 0; }

    long long first = 1, second = 2;
    for (int i = 3; i <= n; i++) {
        long long third = first + second;
        first = second;
        second = third;
    }
    cout << second << endl;
    return 0;
}"""
        ),
        "generator_key": "climbing_stairs",
        "description": (
            "You are climbing a staircase. It takes `n` steps to reach the top.\n\n"
            "Each time you can either climb `1` or `2` steps. In how many distinct ways can you climb to the top?\n\n"
            "### Example 1:\n"
            "- **Input:** `2`\n"
            "- **Output:** `2`\n"
            "- **Explanation:** There are two ways to climb to the top:\n"
            "  1. 1 step + 1 step\n"
            "  2. 2 steps\n\n"
            "### Example 2:\n"
            "- **Input:** `3`\n"
            "- **Output:** `3`\n"
            "- **Explanation:** There are three ways to climb to the top:\n"
            "  1. 1 step + 1 step + 1 step\n"
            "  2. 1 step + 2 steps\n"
            "  3. 2 steps + 1 step\n\n"
            "### Constraints:\n"
            "- `1 <= n <= 45`\n\n"
            "### Input / Output Format:\n"
            "- **Input:** A single integer `n`\n"
            "- **Output:** Integer representing total distinct combinations\n\n"
            "<details><summary>💡 Hint 1</summary>To reach step `n`, you could have arrived from step `n-1` (by taking 1 step) or from step `n-2` (by taking 2 steps).</details>\n"
            "<details><summary>💡 Hint 2</summary>Recurrence: `ways(n) = ways(n-1) + ways(n-2)`. This matches the Fibonacci sequence!</details>\n"
            "<details><summary>💡 Hint 3</summary>Use 2 variables to compute the answer in O(n) time and O(1) space instead of recursion.</details>"
        ),
        "test_cases": [
            {"input": "2\n",  "expected_output": "2",  "comparator_type": "exact"},
            {"input": "3\n",  "expected_output": "3",  "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Reverse Linked List",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    s = sys.stdin.read().strip()
    if not s:
        return
    vals = s.split()
    print(" ".join(vals[::-1]))

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<String> list = new ArrayList<>();
        while (sc.hasNext()) {
            list.add(sc.next());
        }
        Collections.reverse(list);
        System.out.println(String.join(" ", list));
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).filter(Boolean);
    console.log(input.reverse().join(' '));
}

main();""",
            """#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    vector<string> vals;
    string v;
    while (cin >> v) vals.push_back(v);
    reverse(vals.begin(), vals.end());
    for (int i = 0; i < (int)vals.size(); i++) {
        cout << vals[i] << (i + 1 == (int)vals.size() ? "" : " ");
    }
    cout << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given the `head` of a singly linked list, reverse the list, and return the reversed list.\n\n"
            "### Example 1:\n"
            "- **Input:** `1 2 3 4 5`\n"
            "- **Output:** `5 4 3 3 2 1`\n\n"
            "### Example 2:\n"
            "- **Input:** `1 2`\n"
            "- **Output:** `2 1`\n\n"
            "### Constraints:\n"
            "- The number of nodes in the list is in the range `[0, 5000]`.\n"
            "- `-5000 <= Node.val <= 5000`\n\n"
            "### Input / Output Format:\n"
            "- **Input:** Space-separated integers representing linked list values\n"
            "- **Output:** Space-separated integers representing reversed linked list values\n\n"
            "<details><summary>💡 Hint 1</summary>Maintain three pointers: `prev`, `curr`, and `next`. While `curr` is not null, point `curr.next` to `prev` and move forward.</details>"
        ),
        "test_cases": [
            {"input": "1 2 3 4 5\n", "expected_output": "5 4 3 2 1", "comparator_type": "exact"},
            {"input": "1 2\n", "expected_output": "2 1", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Contains Duplicate",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:n+1]]

    seen = set()
    for num in nums:
        if num in seen:
            print("true")
            return
        seen.add(num)
    print("false")

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        Set<Integer> seen = new HashSet<>();
        for (int i = 0; i < n; i++) {
            int num = sc.nextInt();
            if (seen.contains(num)) {
                System.out.println("true");
                return;
            }
            seen.add(num);
        }
        System.out.println("false");
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const nums = input.slice(1, n + 1);

    const seen = new Set();
    for (let i = 0; i < n; i++) {
        if (seen.has(nums[i])) {
            console.log('true');
            return;
        }
        seen.add(nums[i]);
    }
    console.log('false');
}

main();""",
            """#include <iostream>
#include <vector>
#include <unordered_set>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    unordered_set<int> seen;
    for (int i = 0; i < n; i++) {
        int num;
        cin >> num;
        if (seen.count(num)) {
            cout << "true" << endl;
            return 0;
        }
        seen.insert(num);
    }
    cout << "false" << endl;
    return 0;
}"""
        ),
        "generator_key": "contains_duplicate",
        "description": (
            "Given an integer array `nums`, return `true` if any value appears **at least twice** in the array, and return `false` if every element is distinct.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 4`, `nums = [1, 2, 3, 1]`\n"
            "- **Output:** `true`\n"
            "- **Explanation:** The element 1 occurs at the indices 0 and 3.\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 3`, `nums = [1, 2, 3]`\n"
            "- **Output:** `false`\n"
            "- **Explanation:** All elements are distinct.\n\n"
            "### Example 3:\n"
            "- **Input:** `n = 10`, `nums = [1, 1, 1, 3, 3, 4, 3, 2, 4, 2]`\n"
            "- **Output:** `true`\n\n"
            "### Constraints:\n"
            "- `1 <= nums.length <= 10^5`\n"
            "- `-10^9 <= nums[i] <= 10^9`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n` (number of elements)\n"
            "- **Line 2:** `n` space-separated integers\n"
            "- **Output:** `true` or `false`\n\n"
            "<details><summary>💡 Hint 1</summary>A brute force nested loop takes O(n²). Can you use a Hash Set to track seen numbers in O(n) time?</details>\n"
            "<details><summary>💡 Hint 2</summary>Alternatively, sorting the array takes O(n log n) time and O(1) extra space, after which duplicate elements will be adjacent.</details>"
        ),
        "test_cases": [
            {"input": "4\n1 2 3 1\n",   "expected_output": "true",  "comparator_type": "exact"},
            {"input": "3\n1 2 3\n",     "expected_output": "false", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Product of Array Except Self",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:n+1]]

    res = [1] * n
    prefix = 1
    for i in range(n):
        res[i] = prefix
        prefix *= nums[i]

    suffix = 1
    for i in range(n - 1, -1, -1):
        res[i] *= suffix
        suffix *= nums[i]

    print(" ".join(map(str, res)))

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();

        int[] res = new int[n];
        int prefix = 1;
        for (int i = 0; i < n; i++) {
            res[i] = prefix;
            prefix *= nums[i];
        }
        int suffix = 1;
        for (int i = n - 1; i >= 0; i--) {
            res[i] *= suffix;
            suffix *= nums[i];
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append(res[i]).append(i + 1 == n ? "" : " ");
        }
        System.out.println(sb.toString());
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const nums = input.slice(1, n + 1);

    const res = new Array(n).fill(1);
    let prefix = 1;
    for (let i = 0; i < n; i++) {
        res[i] = prefix;
        prefix *= nums[i];
    }
    let suffix = 1;
    for (let i = n - 1; i >= 0; i--) {
        res[i] *= suffix;
        suffix *= nums[i];
    }
    console.log(res.join(' '));
}

main();""",
            """#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> nums(n);
    for (int i = 0; i < n; i++) cin >> nums[i];

    vector<int> res(n, 1);
    int prefix = 1;
    for (int i = 0; i < n; i++) {
        res[i] = prefix;
        prefix *= nums[i];
    }
    int suffix = 1;
    for (int i = n - 1; i >= 0; i--) {
        res[i] *= suffix;
        suffix *= nums[i];
    }

    for (int i = 0; i < n; i++) {
        cout << res[i] << (i + 1 == n ? "" : " ");
    }
    cout << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given an integer array `nums`, return an array `answer` such that `answer[i]` is equal to the product of all the elements of `nums` except `nums[i]`.\n\n"
            "The product of any prefix or suffix of `nums` is guaranteed to fit in a **32-bit** integer.\n\n"
            "You must write an algorithm that runs in `O(n)` time and without using the division operation.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 4`, `nums = [1, 2, 3, 4]`\n"
            "- **Output:** `24 12 8 6`\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 5`, `nums = [-1, 1, 0, -3, 3]`\n"
            "- **Output:** `0 0 9 0 0`\n\n"
            "### Constraints:\n"
            "- `2 <= nums.length <= 10^5`\n"
            "- `-30 <= nums[i] <= 30`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n`\n"
            "- **Line 2:** `n` space-separated integers\n"
            "- **Output:** Space-separated product integers\n\n"
            "<details><summary>💡 Hint 1</summary>The product except `nums[i]` is equal to `(prefix product of elements before i) * (suffix product of elements after i)`.</details>\n"
            "<details><summary>💡 Hint 2</summary>Compute prefix products in a left-to-right pass, and multiply suffix products in a right-to-left pass.</details>"
        ),
        "test_cases": [
            {"input": "4\n1 2 3 4\n", "expected_output": "24 12 8 6", "comparator_type": "exact"},
            {"input": "5\n-1 1 0 -3 3\n", "expected_output": "0 0 9 0 0", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Valid Anagram",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    lines = sys.stdin.read().splitlines()
    if len(lines) < 2:
        return
    s, t = lines[0].strip(), lines[1].strip()

    if len(s) != len(t):
        print("false")
        return

    counts = [0] * 26
    for char_s, char_t in zip(s, t):
        counts[ord(char_s) - 97] += 1
        counts[ord(char_t) - 97] -= 1

    print("true" if all(c == 0 for c in counts) else "false")

if __name__ == '__main__':
    main()""",
            """import java.util.Scanner;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNext()) return;
        String s = sc.next();
        String t = sc.next();

        if (s.length() != t.length()) {
            System.out.println("false");
            return;
        }

        int[] count = new int[26];
        for (int i = 0; i < s.length(); i++) {
            count[s.charAt(i) - 'a']++;
            count[t.charAt(i) - 'a']--;
        }

        for (int c : count) {
            if (c != 0) {
                System.out.println("false");
                return;
            }
        }
        System.out.println("true");
    }
}""",
            """const fs = require('fs');

function main() {
    const lines = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/);
    if (lines.length < 2) return;
    const s = lines[0], t = lines[1];

    if (s.length !== t.length) {
        console.log('false');
        return;
    }

    const count = new Array(26).fill(0);
    for (let i = 0; i < s.length; i++) {
        count[s.charCodeAt(i) - 97]++;
        count[t.charCodeAt(i) - 97]--;
    }

    console.log(count.every(c => c === 0) ? 'true' : 'false');
}

main();""",
            """#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
    string s, t;
    if (!(cin >> s >> t)) return 0;
    if (s.length() != t.length()) {
        cout << "false" << endl;
        return 0;
    }
    vector<int> counts(26, 0);
    for (int i = 0; i < (int)s.length(); i++) {
        counts[s[i] - 'a']++;
        counts[t[i] - 'a']--;
    }
    for (int c : counts) {
        if (c != 0) {
            cout << "false" << endl;
            return 0;
        }
    }
    cout << "true" << endl;
    return 0;
}"""
        ),
        "generator_key": "valid_anagram",
        "description": (
            "Given two strings `s` and `t`, return `true` if `t` is an **anagram** of `s`, and `false` otherwise.\n\n"
            "An **anagram** is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.\n\n"
            "### Example 1:\n"
            "- **Input:** `s = \"anagram\"`, `t = \"nagaram\"`\n"
            "- **Output:** `true`\n\n"
            "### Example 2:\n"
            "- **Input:** `s = \"rat\"`, `t = \"car\"`\n"
            "- **Output:** `false`\n\n"
            "### Constraints:\n"
            "- `1 <= s.length, t.length <= 5 * 10^4`\n"
            "- `s` and `t` consist of lowercase English letters.\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** String `s`\n"
            "- **Line 2:** String `t`\n"
            "- **Output:** `true` or `false`\n\n"
            "<details><summary>💡 Hint 1</summary>If lengths of `s` and `t` are different, they cannot be anagrams.</details>\n"
            "<details><summary>💡 Hint 2</summary>Since input only contains lowercase English letters, a fixed array of size 26 can count frequencies in O(n) time and O(1) space.</details>"
        ),
        "test_cases": [
            {"input": "anagram\nnagaram\n", "expected_output": "true",  "comparator_type": "exact"},
            {"input": "rat\ncar\n",         "expected_output": "false", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Group Anagrams",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n log n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys
from collections import defaultdict

def main():
    words = sys.stdin.read().split()
    if not words:
        return
    groups = defaultdict(list)
    for w in words:
        key = "".join(sorted(w))
        groups[key].append(w)

    for key in sorted(groups.keys()):
        print(" ".join(groups[key]))

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        Map<String, List<String>> map = new TreeMap<>();
        while (sc.hasNext()) {
            String w = sc.next();
            char[] chars = w.toCharArray();
            Arrays.sort(chars);
            String key = new String(chars);
            map.computeIfAbsent(key, k -> new ArrayList<>()).add(w);
        }
        for (List<String> group : map.values()) {
            System.out.println(String.join(" ", group));
        }
    }
}""",
            """const fs = require('fs');

function main() {
    const words = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).filter(Boolean);
    const map = new Map();
    for (const w of words) {
        const key = w.split('').sort().join('');
        if (!map.has(key)) map.set(key, []);
        map.get(key).push(w);
    }
    const keys = Array.from(map.keys()).sort();
    for (const key of keys) {
        console.log(map.get(key).join(' '));
    }
}

main();""",
            """#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <algorithm>
using namespace std;

int main() {
    map<string, vector<string>> groups;
    string w;
    while (cin >> w) {
        string key = w;
        sort(key.begin(), key.end());
        groups[key].push_back(w);
    }
    for (const auto& p : groups) {
        for (int i = 0; i < (int)p.second.size(); i++) {
            cout << p.second[i] << (i + 1 == (int)p.second.size() ? "" : " ");
        }
        cout << endl;
    }
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given an array of strings `strs`, group the **anagrams** together. You can return the answer in any order.\n\n"
            "An **anagram** is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.\n\n"
            "### Example 1:\n"
            "- **Input:** `eat tea tan ate nat bat`\n"
            "- **Output:**\n"
            "  `bat`\n"
            "  `nat tan`\n"
            "  `ate eat tea`\n\n"
            "### Constraints:\n"
            "- `1 <= strs.length <= 10^4`\n"
            "- `0 <= strs[i].length <= 100`\n"
            "- `strs[i]` consists of lowercase English letters.\n\n"
            "### Input / Output Format:\n"
            "- **Input:** Space-separated words\n"
            "- **Output:** Space-separated grouped anagrams per line\n\n"
            "<details><summary>💡 Hint 1</summary>Two words are anagrams if and only if their sorted string representations are identical.</details>\n"
            "<details><summary>💡 Hint 2</summary>Use a Hash Map with the sorted word as the key and a list of original words as the value.</details>"
        ),
        "test_cases": [
            {"input": "eat tea tan ate nat bat\n", "expected_output": "bat\nnat tan\nate eat tea", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Binary Search",
        "difficulty": "easy",
        "optimal_time_complexity": "O(log n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:n+1]]
    target = int(input_data[n+1])

    left, right = 0, n - 1
    result = -1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            result = mid
            break
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    print(result)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        int target = sc.nextInt();

        int left = 0, right = n - 1;
        int result = -1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) {
                result = mid;
                break;
            } else if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        System.out.println(result);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const nums = input.slice(1, n + 1);
    const target = input[n + 1];

    let left = 0, right = n - 1;
    let result = -1;
    while (left <= right) {
        const mid = Math.floor(left + (right - left) / 2);
        if (nums[mid] === target) {
            result = mid;
            break;
        } else if (nums[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    console.log(result);
}

main();""",
            """#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> nums(n);
    for (int i = 0; i < n; i++) cin >> nums[i];
    int target;
    cin >> target;

    int left = 0, right = n - 1;
    int result = -1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) {
            result = mid;
            break;
        } else if (nums[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    cout << result << endl;
    return 0;
}"""
        ),
        "generator_key": "binary_search",
        "description": (
            "Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`.\n\n"
            "If `target` exists, then return its **index**. Otherwise, return `-1`.\n\n"
            "You must write an algorithm with `O(log n)` runtime complexity.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 6`, `nums = [-1, 0, 3, 5, 9, 12]`, `target = 9`\n"
            "- **Output:** `4`\n"
            "- **Explanation:** `9` exists in `nums` and its index is `4`.\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 6`, `nums = [-1, 0, 3, 5, 9, 12]`, `target = 2`\n"
            "- **Output:** `-1`\n"
            "- **Explanation:** `2` does not exist in `nums` so return `-1`.\n\n"
            "### Constraints:\n"
            "- `1 <= nums.length <= 10^4`\n"
            "- `-10^4 < nums[i], target < 10^4`\n"
            "- All the integers in `nums` are unique.\n"
            "- `nums` is sorted in ascending order.\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n` (array size)\n"
            "- **Line 2:** `n` space-separated sorted integers\n"
            "- **Line 3:** Integer `target`\n"
            "- **Output:** Index of `target` or `-1`\n\n"
            "<details><summary>💡 Hint 1</summary>Since the array is sorted, we can divide the search space in half at each step.</details>\n"
            "<details><summary>💡 Hint 2</summary>Compute `mid = (left + right) // 2`. If `nums[mid] < target`, discard the left half (`left = mid + 1`). Otherwise discard right half (`right = mid - 1`).</details>"
        ),
        "test_cases": [
            {"input": "6\n-1 0 3 5 9 12\n9\n",  "expected_output": "4",  "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Search in Rotated Sorted Array",
        "difficulty": "medium",
        "optimal_time_complexity": "O(log n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:n+1]]
    target = int(input_data[n+1])

    left, right = 0, n - 1
    res = -1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            res = mid
            break

        # Check if left half is sorted
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else: # Right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    print(res)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        int target = sc.nextInt();

        int left = 0, right = n - 1, res = -1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) { res = mid; break; }
            if (nums[left] <= nums[mid]) {
                if (nums[left] <= target && target < nums[mid]) right = mid - 1;
                else left = mid + 1;
            } else {
                if (nums[mid] < target && target <= nums[right]) left = mid + 1;
                else right = mid - 1;
            }
        }
        System.out.println(res);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const nums = input.slice(1, n + 1);
    const target = input[n + 1];

    let left = 0, right = n - 1, res = -1;
    while (left <= right) {
        const mid = Math.floor(left + (right - left) / 2);
        if (nums[mid] === target) { res = mid; break; }
        if (nums[left] <= nums[mid]) {
            if (nums[left] <= target && target < nums[mid]) right = mid - 1;
            else left = mid + 1;
        } else {
            if (nums[mid] < target && target <= nums[right]) left = mid + 1;
            else right = mid - 1;
        }
    }
    console.log(res);
}

main();""",
            """#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> nums(n);
    for (int i = 0; i < n; i++) cin >> nums[i];
    int target;
    cin >> target;

    int left = 0, right = n - 1, res = -1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) { res = mid; break; }
        if (nums[left] <= nums[mid]) {
            if (nums[left] <= target && target < nums[mid]) right = mid - 1;
            else left = mid + 1;
        } else {
            if (nums[mid] < target && target <= nums[right]) left = mid + 1;
            else right = mid - 1;
        }
    }
    cout << res << endl;
    return 0;
}"""
        ),
        "generator_key": "binary_search",
        "description": (
            "There is an integer array `nums` sorted in ascending order (with distinct values).\n\n"
            "Prior to being passed to your function, `nums` is possibly rotated at an unknown pivot index `k` (`1 <= k < nums.length`).\n\n"
            "Given the array `nums` after the possible rotation and an integer `target`, return the index of `target` if it is in `nums`, or `-1` if it is not in `nums`.\n\n"
            "You must write an algorithm with `O(log n)` runtime complexity.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 7`, `nums = [4, 5, 6, 7, 0, 1, 2]`, `target = 0`\n"
            "- **Output:** `4`\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 7`, `nums = [4, 5, 6, 7, 0, 1, 2]`, `target = 3`\n"
            "- **Output:** `-1`\n\n"
            "### Constraints:\n"
            "- `1 <= nums.length <= 5000`\n"
            "- `-10^4 <= nums[i] <= 10^4`\n"
            "- All values of `nums` are unique.\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n`\n"
            "- **Line 2:** `n` space-separated integers\n"
            "- **Line 3:** Integer `target`\n"
            "- **Output:** Index integer or `-1`\n\n"
            "<details><summary>💡 Hint 1</summary>At least one half of the rotated array (`[left, mid]` or `[mid, right]`) is always strictly sorted.</details>\n"
            "<details><summary>💡 Hint 2</summary>Determine which half is sorted, then check if `target` falls within the boundary of that sorted half to pick which direction to search.</details>"
        ),
        "test_cases": [
            {"input": "7\n4 5 6 7 0 1 2\n0\n", "expected_output": "4", "comparator_type": "exact"},
            {"input": "7\n4 5 6 7 0 1 2\n3\n", "expected_output": "-1", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Daily Temperatures",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    temps = [int(x) for x in input_data[1:n+1]]

    res = [0] * n
    stack = []  # pairs of (index, temp)

    for i, t in enumerate(temps):
        while stack and t > stack[-1][1]:
            prev_idx, _ = stack.pop()
            res[prev_idx] = i - prev_idx
        stack.append((i, t))

    print(" ".join(map(str, res)))

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[] temps = new int[n];
        for (int i = 0; i < n; i++) temps[i] = sc.nextInt();

        int[] res = new int[n];
        Stack<Integer> stack = new Stack<>();
        for (int i = 0; i < n; i++) {
            while (!stack.isEmpty() && temps[i] > temps[stack.peek()]) {
                int prev = stack.pop();
                res[prev] = i - prev;
            }
            stack.push(i);
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append(res[i]).append(i + 1 == n ? "" : " ");
        }
        System.out.println(sb.toString());
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const temps = input.slice(1, n + 1);

    const res = new Array(n).fill(0);
    const stack = [];
    for (let i = 0; i < n; i++) {
        while (stack.length > 0 && temps[i] > temps[stack[stack.length - 1]]) {
            const prev = stack.pop();
            res[prev] = i - prev;
        }
        stack.push(i);
    }
    console.log(res.join(' '));
}

main();""",
            """#include <iostream>
#include <vector>
#include <stack>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> temps(n);
    for (int i = 0; i < n; i++) cin >> temps[i];

    vector<int> res(n, 0);
    stack<int> st;
    for (int i = 0; i < n; i++) {
        while (!st.empty() && temps[i] > temps[st.top()]) {
            int prev = st.top();
            st.pop();
            res[prev] = i - prev;
        }
        st.push(i);
    }
    for (int i = 0; i < n; i++) {
        cout << res[i] << (i + 1 == n ? "" : " ");
    }
    cout << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given an array of integers `temperatures` represents the daily temperatures, return an array `answer` such that `answer[i]` is the number of days you have to wait after the `i-th` day to get a warmer temperature. If there is no future day for which this is possible, keep `answer[i] == 0` instead.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 8`, `temperatures = [73, 74, 75, 71, 69, 72, 76, 73]`\n"
            "- **Output:** `1 1 4 2 1 1 0 0`\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 4`, `temperatures = [30, 40, 50, 60]`\n"
            "- **Output:** `1 1 1 0`\n\n"
            "### Constraints:\n"
            "- `1 <= temperatures.length <= 10^5`\n"
            "- `30 <= temperatures[i] <= 100`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n`\n"
            "- **Line 2:** `n` space-separated temperatures\n"
            "- **Output:** Space-separated wait days\n\n"
            "<details><summary>💡 Hint 1</summary>Use a Monotonic Decreasing Stack storing indices of days.</details>\n"
            "<details><summary>💡 Hint 2</summary>When a warmer temperature appears, pop indices from the stack and compute `answer[prev_idx] = curr_idx - prev_idx`.</details>"
        ),
        "test_cases": [
            {"input": "8\n73 74 75 71 69 72 76 73\n", "expected_output": "1 1 4 2 1 1 0 0", "comparator_type": "exact"},
            {"input": "4\n30 40 50 60\n", "expected_output": "1 1 1 0", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "House Robber",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:n+1]]

    rob1, rob2 = 0, 0
    for n in nums:
        temp = max(n + rob1, rob2)
        rob1 = rob2
        rob2 = temp
    print(rob2)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int rob1 = 0, rob2 = 0;
        for (int i = 0; i < n; i++) {
            int val = sc.nextInt();
            int temp = Math.max(val + rob1, rob2);
            rob1 = rob2;
            rob2 = temp;
        }
        System.out.println(rob2);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const nums = input.slice(1, n + 1);

    let rob1 = 0, rob2 = 0;
    for (const num of nums) {
        const temp = Math.max(num + rob1, rob2);
        rob1 = rob2;
        rob2 = temp;
    }
    console.log(rob2);
}

main();""",
            """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    int rob1 = 0, rob2 = 0;
    for (int i = 0; i < n; i++) {
        int val; cin >> val;
        int temp = max(val + rob1, rob2);
        rob1 = rob2;
        rob2 = temp;
    }
    cout << rob2 << endl;
    return 0;
}"""
        ),
        "generator_key": "climbing_stairs",
        "description": (
            "You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed, the only constraint stopping you from robbing each of them is that adjacent houses have security systems connected and **it will automatically contact the police if two adjacent houses were broken into on the same night**.\n\n"
            "Given an integer array `nums` representing the amount of money of each house, return the **maximum amount of money** you can rob tonight without alerting the police.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 4`, `nums = [1, 2, 3, 1]`\n"
            "- **Output:** `4`\n"
            "- **Explanation:** Rob house 1 (money = 1) and then rob house 3 (money = 3). Total = 1 + 3 = 4.\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 5`, `nums = [2, 7, 9, 3, 1]`\n"
            "- **Output:** `12`\n"
            "- **Explanation:** Rob house 1 (money = 2), house 3 (money = 9) and house 5 (money = 1). Total = 2 + 9 + 1 = 12.\n\n"
            "### Constraints:\n"
            "- `1 <= nums.length <= 100`\n"
            "- `0 <= nums[i] <= 400`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n`\n"
            "- **Line 2:** `n` space-separated integers\n"
            "- **Output:** Maximum money robbed integer\n\n"
            "<details><summary>💡 Hint 1</summary>At house `i`, you have two choices: rob house `i` (adding `nums[i]` to `dp[i-2]`) or skip house `i` (keeping `dp[i-1]`).</details>\n"
            "<details><summary>💡 Hint 2</summary>Recurrence: `dp[i] = max(nums[i] + dp[i-2], dp[i-1])`. Can be computed with 2 variables in O(1) space.</details>"
        ),
        "test_cases": [
            {"input": "4\n1 2 3 1\n", "expected_output": "4", "comparator_type": "exact"},
            {"input": "5\n2 7 9 3 1\n", "expected_output": "12", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Coin Change",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    coins = [int(x) for x in input_data[1:n+1]]
    amount = int(input_data[n+1])

    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)

    print(dp[amount] if dp[amount] != float('inf') else -1)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[] coins = new int[n];
        for (int i = 0; i < n; i++) coins[i] = sc.nextInt();
        int amount = sc.nextInt();

        int[] dp = new int[amount + 1];
        Arrays.fill(dp, amount + 1);
        dp[0] = 0;

        for (int coin : coins) {
            for (int x = coin; x <= amount; x++) {
                dp[x] = Math.min(dp[x], dp[x - coin] + 1);
            }
        }
        System.out.println(dp[amount] > amount ? -1 : dp[amount]);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const coins = input.slice(1, n + 1);
    const amount = input[n + 1];

    const dp = new Array(amount + 1).fill(Infinity);
    dp[0] = 0;
    for (const coin of coins) {
        for (let x = coin; x <= amount; x++) {
            dp[x] = Math.min(dp[x], dp[x - coin] + 1);
        }
    }
    console.log(dp[amount] === Infinity ? -1 : dp[amount]);
}

main();""",
            """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> coins(n);
    for (int i = 0; i < n; i++) cin >> coins[i];
    int amount;
    cin >> amount;

    vector<int> dp(amount + 1, amount + 1);
    dp[0] = 0;
    for (int coin : coins) {
        for (int x = coin; x <= amount; x++) {
            dp[x] = min(dp[x], dp[x - coin] + 1);
        }
    }
    cout << (dp[amount] > amount ? -1 : dp[amount]) << endl;
    return 0;
}"""
        ),
        "generator_key": "climbing_stairs",
        "description": (
            "You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money.\n\n"
            "Return the **fewest number of coins** that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return `-1`.\n\n"
            "You may assume that you have an infinite number of each kind of coin.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 3`, `coins = [1, 2, 5]`, `amount = 11`\n"
            "- **Output:** `3`\n"
            "- **Explanation:** 11 = 5 + 5 + 1.\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 1`, `coins = [2]`, `amount = 3`\n"
            "- **Output:** `-1`\n\n"
            "### Constraints:\n"
            "- `1 <= coins.length <= 12`\n"
            "- `1 <= coins[i] <= 2^31 - 1`\n"
            "- `0 <= amount <= 10^4`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n` (number of coin types)\n"
            "- **Line 2:** `n` space-separated coin denominations\n"
            "- **Line 3:** Integer `amount`\n"
            "- **Output:** Minimum number of coins or `-1`\n\n"
            "<details><summary>💡 Hint 1</summary>Build a DP array where `dp[i]` represents minimum coins needed for amount `i`.</details>\n"
            "<details><summary>💡 Hint 2</summary>For each coin, update `dp[x] = min(dp[x], dp[x - coin] + 1)`.</details>"
        ),
        "test_cases": [
            {"input": "3\n1 2 5\n11\n", "expected_output": "3", "comparator_type": "exact"},
            {"input": "1\n2\n3\n", "expected_output": "-1", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Number of Islands",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    lines = sys.stdin.read().strip().split('\\n')
    if not lines or not lines[0].strip():
        return
    first = lines[0].split()
    r, c = int(first[0]), int(first[1])
    grid = [list(lines[i+1].strip().replace(" ", "")) for i in range(r)]

    count = 0
    def dfs(i, j):
        if i < 0 or i >= r or j < 0 or j >= c or grid[i][j] != '1':
            return
        grid[i][j] = '0'
        dfs(i + 1, j)
        dfs(i - 1, j)
        dfs(i, j + 1)
        dfs(i, j - 1)

    for i in range(r):
        for j in range(c):
            if grid[i][j] == '1':
                dfs(i, j)
                count += 1

    print(count)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    private static void dfs(char[][] grid, int i, int j) {
        if (i < 0 || i >= grid.length || j < 0 || j >= grid[0].length || grid[i][j] != '1') return;
        grid[i][j] = '0';
        dfs(grid, i + 1, j);
        dfs(grid, i - 1, j);
        dfs(grid, i, j + 1);
        dfs(grid, i, j - 1);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int r = sc.nextInt(), c = sc.nextInt();
        char[][] grid = new char[r][c];
        for (int i = 0; i < r; i++) {
            String row = sc.next();
            grid[i] = row.toCharArray();
        }
        int count = 0;
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                if (grid[i][j] == '1') {
                    dfs(grid, i, j);
                    count++;
                }
            }
        }
        System.out.println(count);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/);
    if (!input || input.length < 2) return;
    const r = parseInt(input[0], 10), c = parseInt(input[1], 10);
    const grid = [];
    for (let i = 0; i < r; i++) {
        grid.push(input[2 + i].split(''));
    }

    function dfs(i, j) {
        if (i < 0 || i >= r || j < 0 || j >= c || grid[i][j] !== '1') return;
        grid[i][j] = '0';
        dfs(i + 1, j);
        dfs(i - 1, j);
        dfs(i, j + 1);
        dfs(i, j - 1);
    }

    let count = 0;
    for (let i = 0; i < r; i++) {
        for (let j = 0; j < c; j++) {
            if (grid[i][j] === '1') {
                dfs(i, j);
                count++;
            }
        }
    }
    console.log(count);
}

main();""",
            """#include <iostream>
#include <vector>
#include <string>
using namespace std;

void dfs(vector<string>& grid, int i, int j, int r, int c) {
    if (i < 0 || i >= r || j < 0 || j >= c || grid[i][j] != '1') return;
    grid[i][j] = '0';
    dfs(grid, i + 1, j, r, c);
    dfs(grid, i - 1, j, r, c);
    dfs(grid, i, j + 1, r, c);
    dfs(grid, i, j - 1, r, c);
}

int main() {
    int r, c;
    if (!(cin >> r >> c)) return 0;
    vector<string> grid(r);
    for (int i = 0; i < r; i++) cin >> grid[i];

    int count = 0;
    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            if (grid[i][j] == '1') {
                dfs(grid, i, j, r, c);
                count++;
            }
        }
    }
    cout << count << endl;
    return 0;
}"""
        ),
        "generator_key": "two_sum",
        "description": (
            "Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water), return the **number of islands**.\n\n"
            "An **island** is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.\n\n"
            "### Example 1:\n"
            "- **Input:**\n"
            "  `4 5`\n"
            "  `11110`\n"
            "  `11010`\n"
            "  `11000`\n"
            "  `00000`\n"
            "- **Output:** `1`\n\n"
            "### Example 2:\n"
            "- **Input:**\n"
            "  `4 5`\n"
            "  `11000`\n"
            "  `11000`\n"
            "  `00100`\n"
            "  `00011`\n"
            "- **Output:** `3`\n\n"
            "### Constraints:\n"
            "- `m == grid.length`, `n == grid[i].length`\n"
            "- `1 <= m, n <= 300`\n"
            "- `grid[i][j]` is `'0'` or `'1'`.\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Two integers `m` and `n`\n"
            "- **Next `m` lines:** String of `n` binary characters per line\n"
            "- **Output:** Integer number of islands\n\n"
            "<details><summary>💡 Hint 1</summary>Traverse the grid. When encountering `'1'`, launch a BFS or DFS to sink all connected land cells by marking them `'0'`.</details>"
        ),
        "test_cases": [
            {"input": "4 5\n11110\n11010\n11000\n00000\n", "expected_output": "1", "comparator_type": "exact"},
            {"input": "4 5\n11000\n11000\n00100\n00011\n", "expected_output": "3", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Trapping Rain Water",
        "difficulty": "hard",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "optimal_solution": opt_sol(
            """import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    n = int(input_data[0])
    height = [int(x) for x in input_data[1:n+1]]

    if not height:
        print(0)
        return

    left, right = 0, n - 1
    left_max, right_max = 0, 0
    ans = 0

    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                ans += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                ans += right_max - height[right]
            right -= 1

    print(ans)

if __name__ == '__main__':
    main()""",
            """import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;
        int n = sc.nextInt();
        int[] height = new int[n];
        for (int i = 0; i < n; i++) height[i] = sc.nextInt();

        int left = 0, right = n - 1;
        int leftMax = 0, rightMax = 0;
        int ans = 0;

        while (left < right) {
            if (height[left] < height[right]) {
                if (height[left] >= leftMax) leftMax = height[left];
                else ans += leftMax - height[left];
                left++;
            } else {
                if (height[right] >= rightMax) rightMax = height[right];
                else ans += rightMax - height[right];
                right--;
            }
        }
        System.out.println(ans);
    }
}""",
            """const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/).map(Number);
    if (!input || input.length === 0 || isNaN(input[0])) return;
    const n = input[0];
    const height = input.slice(1, n + 1);

    let left = 0, right = n - 1;
    let leftMax = 0, rightMax = 0;
    let ans = 0;

    while (left < right) {
        if (height[left] < height[right]) {
            if (height[left] >= leftMax) leftMax = height[left];
            else ans += leftMax - height[left];
            left++;
        } else {
            if (height[right] >= rightMax) rightMax = height[right];
            else ans += rightMax - height[right];
            right--;
        }
    }
    console.log(ans);
}

main();""",
            """#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> height(n);
    for (int i = 0; i < n; i++) cin >> height[i];

    int left = 0, right = n - 1;
    int leftMax = 0, rightMax = 0;
    int ans = 0;

    while (left < right) {
        if (height[left] < height[right]) {
            if (height[left] >= leftMax) leftMax = height[left];
            else ans += leftMax - height[left];
            left++;
        } else {
            if (height[right] >= rightMax) rightMax = height[right];
            else ans += rightMax - height[right];
            right--;
        }
    }
    cout << ans << endl;
    return 0;
}"""
        ),
        "generator_key": "container_with_most_water",
        "description": (
            "Given `n` non-negative integers representing an elevation map where the width of each bar is `1`, compute how much water it can trap after raining.\n\n"
            "### Example 1:\n"
            "- **Input:** `n = 12`, `height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]`\n"
            "- **Output:** `6`\n"
            "- **Explanation:** The above elevation map can trap 6 units of rain water.\n\n"
            "### Example 2:\n"
            "- **Input:** `n = 6`, `height = [4, 2, 0, 3, 2, 5]`\n"
            "- **Output:** `9`\n\n"
            "### Constraints:\n"
            "- `n == height.length`\n"
            "- `1 <= n <= 2 * 10^4`\n"
            "- `0 <= height[i] <= 10^5`\n\n"
            "### Input / Output Format:\n"
            "- **Line 1:** Integer `n` (elevation map size)\n"
            "- **Line 2:** `n` space-separated integers representing heights\n"
            "- **Output:** Total trapped water volume\n\n"
            "<details><summary>💡 Hint 1</summary>The water trapped above index `i` is determined by `min(max_left_height, max_right_height) - height[i]`.</details>\n"
            "<details><summary>💡 Hint 2</summary>You can compute this in O(n) time and O(1) space using two pointers moving towards each other.</details>"
        ),
        "test_cases": [
            {"input": "12\n0 1 0 2 1 0 1 3 2 1 2 1\n", "expected_output": "6", "comparator_type": "exact"},
            {"input": "6\n4 2 0 3 2 5\n", "expected_output": "9", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
]


from app.problems_data.registry import REGISTRY
from app.services.complexity import COMPLEXITY_ORDER
from app.services.hints import DETECTORS

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
ALLOWED_COMPARATORS = {"exact", "numeric_tolerance", "sorted", "custom", "sql_table", "sql", "table"}


def validate_problem_data(prob: dict) -> None:
    """Sanity-check problem data at seed time and fail loudly if malformed."""
    title = prob.get("title", "")
    if not isinstance(title, str) or not (1 <= len(title.strip()) <= 200):
        raise ValueError(f"Invalid problem title: {title!r}")

    desc = prob.get("description", "")
    if not isinstance(desc, str) or not desc.strip():
        raise ValueError(f"Problem '{title}' missing description")

    diff = prob.get("difficulty")
    if diff not in ALLOWED_DIFFICULTIES:
        raise ValueError(f"Problem '{title}' invalid difficulty: {diff!r}")

    opt_time = prob.get("optimal_time_complexity")
    if opt_time not in COMPLEXITY_ORDER:
        raise ValueError(f"Problem '{title}' invalid optimal_time_complexity: {opt_time!r}")

    opt_space = prob.get("optimal_space_complexity")
    if opt_space not in COMPLEXITY_ORDER:
        raise ValueError(f"Problem '{title}' invalid optimal_space_complexity: {opt_space!r}")

    gen_key = prob.get("generator_key")
    if gen_key not in REGISTRY:
        raise ValueError(f"Problem '{title}' unregistered generator_key: {gen_key!r}")

    for tc in prob.get("test_cases", []):
        comp = tc.get("comparator_type")
        if comp not in ALLOWED_COMPARATORS:
            raise ValueError(f"Problem '{title}' invalid comparator_type: {comp!r}")
        if not tc.get("input") or not str(tc.get("input")).strip():
            raise ValueError(f"Problem '{title}' has empty test case input")
        if not tc.get("expected_output") or not str(tc.get("expected_output")).strip():
            raise ValueError(f"Problem '{title}' has empty test case expected_output")

    for sig in prob.get("signatures", []):
        pat = sig.get("pattern_type")
        if pat not in DETECTORS:
            raise ValueError(f"Problem '{title}' unregistered pattern_type: {pat!r}")


from app.models.forum import ForumThread, ForumReply
from app.models.user import User
from app.auth.security import hash_password


def seed_forum(db) -> None:
    """Populate initial forum threads and replies if no threads exist."""
    if db.query(ForumThread).first():
        logger.info("Forum threads already seeded — skipping forum seed.")
        return

    # Ensure a seed author exists
    author = db.query(User).filter(User.email == "soham@example.com").first()
    if not author:
        author = User(
            name="soham_limhan",
            email="soham@example.com",
            password_hash=hash_password("Password123!"),
        )
        db.add(author)
        db.flush()

    threads_data = [
        {
            "title": "How to optimize DP space complexity from O(N^2) to O(N)?",
            "category": "Algorithms",
            "content": "I'm working on a grid path-finding problem (similar to Unique Paths II) and realized we only ever need the previous row's values to compute the current row. Has anyone written a clean template or gotcha list for this type of dimensional reduction?",
            "replies": [
                "Yes! You can use two arrays (prev and curr), or even a single array if you iterate backwards depending on the transition equation.\\n\\nFor grid paths: since grid[i][j] = grid[i-1][j] + grid[i][j-1], you can actually do it in-place using a single 1D array of size Width.",
                "Make sure you watch out for base cases! Often when you compress to 1D, your boundary initialization (like row 0 or col 0) needs to be handled carefully in each loop iteration.",
            ],
        },
        {
            "title": "Tips for debugging Time Limit Exceeded (TLE) in Python",
            "category": "General",
            "content": "Python is great for prototyping and readable syntax, but interpreter overhead can easily trigger TLE in tight loop constraints (e.g., N = 10^5). Here are my top rules:\\n\\n1. Avoid list appends in hot loops — use pre-allocated lists or list comprehensions.\\n2. Prefer collections.deque over lists for FIFO queue operations (list pop(0) is O(N)).\\n3. Use bitwise operations where applicable.\\n4. Avoid global variable lookups; load them into local scope variables inside functions.\\n\\nWhat other python-specific optimization secrets do you guys use?",
            "replies": [],
        },
        {
            "title": "Are segment trees overkill for static range sum queries?",
            "category": "Questions",
            "content": "For a static array (no updates at all) and many range sum queries, isn't a simple Prefix Sum array optimal? It gives O(1) query time and O(N) preprocessing space/time.\\n\\nUnder what circumstances would someone still build a Segment Tree or Fenwick Tree (BIT) for a static problem?",
            "replies": [
                "You are absolutely correct. For static range sums, Prefix Sum is optimal. A Segment Tree is definitely overkill and slower (O(log N) vs O(1)).\\n\\nHowever, if the operator is not invertible (like Range Minimum Query - RMQ), a prefix array won't work directly, though Sparse Tables can still do O(1) query.",
            ],
        },
    ]

    for td in threads_data:
        thread = ForumThread(
            title=td["title"],
            category=td["category"],
            content=td["content"],
            user_id=author.id,
        )
        db.add(thread)
        db.flush()

        for reply_text in td["replies"]:
            reply = ForumReply(
                thread_id=thread.id,
                user_id=author.id,
                content=reply_text,
            )
            db.add(reply)

    logger.info("Forum successfully seeded with default topics and replies.")


def seed() -> None:
    """Populate the problem bank and forum bank. Idempotent."""
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import inspect, text
    with engine.connect() as conn:
        inspector = inspect(engine)
        if "problems" in inspector.get_table_names():
            prob_cols = [c["name"] for c in inspector.get_columns("problems")]
            if "optimal_solution" not in prob_cols:
                try:
                    conn.execute(text("ALTER TABLE problems ADD COLUMN optimal_solution TEXT"))
                    conn.commit()
                except Exception:
                    pass

    db = SessionLocal()
    try:
        all_problems_list = PROBLEMS + DATABASE_PROBLEMS
        # Clean up any duplicate problem titles in the database
        all_titles = {p["title"] for p in all_problems_list}
        for title in all_titles:
            duplicates = db.query(Problem).filter(Problem.title == title).all()
            if len(duplicates) > 1:
                # Keep the first one, delete the rest
                for dup in duplicates[1:]:
                    db.query(TestCase).filter(TestCase.problem_id == dup.id).delete()
                    db.query(InefficiencySignature).filter(InefficiencySignature.problem_id == dup.id).delete()
                    db.delete(dup)
                db.flush()

        seeded = 0
        updated = 0
        for prob_data in all_problems_list:
            validate_problem_data(prob_data)
            existing = db.query(Problem).filter(Problem.title == prob_data["title"]).first()
            if existing:
                existing.description = prob_data["description"]
                existing.difficulty = prob_data["difficulty"]
                existing.optimal_time_complexity = prob_data["optimal_time_complexity"]
                existing.optimal_space_complexity = prob_data["optimal_space_complexity"]
                existing.generator_key = prob_data["generator_key"]
                if prob_data.get("optimal_solution"):
                    existing.optimal_solution = prob_data["optimal_solution"]
                
                # Update test cases
                db.query(TestCase).filter(TestCase.problem_id == existing.id).delete()
                for tc in prob_data["test_cases"]:
                    db.add(TestCase(
                        problem_id=existing.id,
                        input=tc["input"],
                        expected_output=tc["expected_output"],
                        comparator_type=tc["comparator_type"],
                    ))

                # Update signatures
                db.query(InefficiencySignature).filter(InefficiencySignature.problem_id == existing.id).delete()
                for sig in prob_data.get("signatures", []):
                    db.add(InefficiencySignature(
                        problem_id=existing.id,
                        pattern_type=sig["pattern_type"],
                        hint_text=sig["hint_text"],
                    ))

                updated += 1
                logger.info("UPDATED %s (existing problem refreshed with full description & hints)", prob_data["title"])
                continue

            problem = Problem(
                title=prob_data["title"],
                description=prob_data["description"],
                difficulty=prob_data["difficulty"],
                optimal_time_complexity=prob_data["optimal_time_complexity"],
                optimal_space_complexity=prob_data["optimal_space_complexity"],
                optimal_solution=prob_data.get("optimal_solution"),
                generator_key=prob_data["generator_key"],
            )
            db.add(problem)
            db.flush()  # get problem.id

            for tc in prob_data["test_cases"]:
                db.add(TestCase(
                    problem_id=problem.id,
                    input=tc["input"],
                    expected_output=tc["expected_output"],
                    comparator_type=tc["comparator_type"],
                ))

            for sig in prob_data.get("signatures", []):
                db.add(InefficiencySignature(
                    problem_id=problem.id,
                    pattern_type=sig["pattern_type"],
                    hint_text=sig["hint_text"],
                ))

            seeded += 1
            logger.info("SEEDED %s", prob_data["title"])

        seed_forum(db)

        db.commit()
        logger.info("Seed complete — %d problems seeded, %d updated.", seeded, updated)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    sys.exit(0)
