from config import TASK_START_NUMBER

_raw = [
    # Два указателя (9 — без Two Sum II, 3Sum, Container with most water)
    ("Reverse String", "https://leetcode.com/problems/reverse-string/description/?envType=problem-list-v2&envId=two-pointers", "Два указателя", "easy"),
    ("Valid Palindrome", "https://leetcode.com/problems/valid-palindrome/description/?envType=problem-list-v2&envId=two-pointers", "Два указателя", "easy"),
    ("Merge Sorted Array", "https://leetcode.com/problems/merge-sorted-array?envType=problem-list-v2&envId=two-pointers", "Два указателя", "easy"),
    ("Intersection of Two Arrays", "https://leetcode.com/problems/intersection-of-two-arrays/description/", "Два указателя", "easy"),
    ("Squares of a Sorted Array", "https://leetcode.com/problems/squares-of-a-sorted-array/description/?envType=problem-list-v2&envId=two-pointers", "Два указателя", "easy"),
    ("Remove Duplicates from Sorted Array", "https://leetcode.com/problems/remove-duplicates-from-sorted-array/description/?envType=problem-list-v2&envId=two-pointers", "Два указателя", "easy"),
    ("Move Zeroes", "https://leetcode.com/problems/move-zeroes/?envType=problem-list-v2&envId=two-pointers", "Два указателя", "easy"),
    ("String Compression", "https://leetcode.com/problems/string-compression/description/?envType=problem-list-v2&envId=two-pointers", "Два указателя", "medium"),
    ("Compare Version Numbers", "https://leetcode.com/problems/compare-version-numbers/description/?envType=problem-list-v2&envId=two-pointers", "Два указателя", "medium"),

    # Матрицы (5)
    ("Matrix Diagonal Sum", "https://leetcode.com/problems/matrix-diagonal-sum/description/", "Матрицы", "easy"),
    ("Transpose Matrix", "https://leetcode.com/problems/transpose-matrix/description/?envType=problem-list-v2&envId=matrix", "Матрицы", "easy"),
    ("Valid Sudoku", "https://leetcode.com/problems/valid-sudoku/?envType=problem-list-v2&envId=matrix", "Матрицы", "medium"),
    ("Rotate Image", "https://leetcode.com/problems/rotate-image/description/?envType=problem-list-v2&envId=matrix", "Матрицы", "medium"),
    ("Spiral Matrix", "https://leetcode.com/problems/spiral-matrix/description/?envType=problem-list-v2&envId=matrix", "Матрицы", "medium"),

    # Хеш-таблицы (5)
    ("Two Sum", "https://leetcode.com/problems/two-sum/?envType=problem-list-v2&envId=hash-table", "Хеш-таблицы", "easy"),
    ("Isomorphic Strings", "https://leetcode.com/problems/isomorphic-strings/description/?envType=problem-list-v2&envId=hash-table", "Хеш-таблицы", "easy"),
    ("Roman to Integer", "https://leetcode.com/problems/roman-to-integer/description/?envType=problem-list-v2&envId=hash-table", "Хеш-таблицы", "easy"),
    ("Valid Anagram", "https://leetcode.com/problems/valid-anagram/?envType=problem-list-v2&envId=hash-table", "Хеш-таблицы", "easy"),
    ("Group Anagrams", "https://leetcode.com/problems/group-anagrams/?envType=problem-list-v2&envId=hash-table", "Хеш-таблицы", "medium"),

    # Префиксная сумма (5)
    ("Range Sum Query - Immutable", "https://leetcode.com/problems/range-sum-query-immutable/description/", "Префиксная сумма", "easy"),
    ("Find the Highest Altitude", "https://leetcode.com/problems/find-the-highest-altitude", "Префиксная сумма", "easy"),
    ("Find Pivot Index", "https://leetcode.com/problems/find-pivot-index/description/", "Префиксная сумма", "easy"),
    ("Range Sum Query 2D - Immutable", "https://leetcode.com/problems/range-sum-query-2d-immutable/description/", "Префиксная сумма", "medium"),
    ("Subarray Sum Equals K", "https://leetcode.com/problems/subarray-sum-equals-k/description/", "Префиксная сумма", "medium"),

    # Битовые манипуляции (5)
    ("Power of Two", "https://leetcode.com/problems/power-of-two/?envType=problem-list-v2&envId=bit-manipulation", "Битовые манипуляции", "easy"),
    ("Single Number", "https://leetcode.com/problems/single-number/description/?envType=problem-list-v2&envId=bit-manipulation", "Битовые манипуляции", "easy"),
    ("Find the Difference", "https://leetcode.com/problems/find-the-difference/description/?envType=problem-list-v2&envId=bit-manipulation", "Битовые манипуляции", "easy"),
    ("Reverse Bits", "https://leetcode.com/problems/reverse-bits/description/?envType=problem-list-v2&envId=bit-manipulation", "Битовые манипуляции", "easy"),
    ("Number of 1 Bits", "https://leetcode.com/problems/number-of-1-bits/description/?envType=problem-list-v2&envId=bit-manipulation", "Битовые манипуляции", "easy"),

    # Бинарный поиск (10)
    ("Binary Search", "https://leetcode.com/problems/binary-search/", "Бинарный поиск", "easy"),
    ("Search Insert Position", "https://leetcode.com/problems/search-insert-position/description/", "Бинарный поиск", "easy"),
    ("First Bad Version", "https://leetcode.com/problems/first-bad-version/description/?envType=problem-list-v2&envId=binary-search", "Бинарный поиск", "easy"),
    ("Sqrt(x)", "https://leetcode.com/problems/sqrtx/description/", "Бинарный поиск", "easy"),
    ("Valid Perfect Square", "https://leetcode.com/problems/valid-perfect-square/description/", "Бинарный поиск", "easy"),
    ("Find First and Last Position of Element in Sorted Array", "https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/description/", "Бинарный поиск", "medium"),
    ("Search a 2D Matrix", "https://leetcode.com/problems/search-a-2d-matrix/?envType=problem-list-v2&envId=binary-search", "Бинарный поиск", "medium"),
    ("Find Peak Element", "https://leetcode.com/problems/find-peak-element/description/?envType=problem-list-v2&envId=binary-search", "Бинарный поиск", "medium"),
    ("Capacity to Ship Packages Within D Days", "https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/description/", "Бинарный поиск", "medium"),
    ("Search in Rotated Sorted Array", "https://leetcode.com/problems/search-in-rotated-sorted-array/description/?envType=problem-list-v2&envId=binary-search", "Бинарный поиск", "medium"),

    # Сортировки (12)
    ("Sort Array By Parity", "https://leetcode.com/problems/sort-array-by-parity/description/?envType=problem-list-v2&envId=two-pointers", "Сортировки", "easy"),
    ("Bubble Sort (Sort an Array)", "https://leetcode.com/problems/sort-an-array/description/", "Сортировки", "medium"),
    ("Insertion Sort (Sort an Array)", "https://leetcode.com/problems/sort-an-array/description/", "Сортировки", "medium"),
    ("Selection Sort (Sort an Array)", "https://leetcode.com/problems/sort-an-array/description/", "Сортировки", "medium"),
    ("Counting Sort (Sort an Array)", "https://leetcode.com/problems/sort-an-array/description/", "Сортировки", "medium"),
    ("Bucket Sort (Sort an Array)", "https://leetcode.com/problems/sort-an-array/description/", "Сортировки", "medium"),
    ("Top K Frequent Elements", "https://leetcode.com/problems/top-k-frequent-elements", "Сортировки", "medium"),
    ("Merge Sort (Sort an Array)", "https://leetcode.com/problems/sort-an-array/description/", "Сортировки", "medium"),
    ("Quick Sort (Sort an Array)", "https://leetcode.com/problems/sort-an-array/description/", "Сортировки", "medium"),
    ("Kth Largest Element in an Array", "https://leetcode.com/problems/kth-largest-element-in-an-array/description/?envType=problem-list-v2&envId=quickselect", "Сортировки", "medium"),
    ("Radix Sort (Sort an Array)", "https://leetcode.com/problems/sort-an-array/description/", "Сортировки", "medium"),
    ("Sort Colors", "https://leetcode.com/problems/sort-colors/description/", "Сортировки", "medium"),

    # Интервалы (3)
    ("Merge Intervals", "https://leetcode.com/problems/merge-intervals/description/", "Интервалы", "medium"),
    ("Insert Interval", "https://leetcode.com/problems/insert-interval/description/", "Интервалы", "medium"),
    ("Non-overlapping Intervals", "https://leetcode.com/problems/non-overlapping-intervals/description/", "Интервалы", "medium"),

    # Связные списки (8)
    ("Middle of the Linked List", "https://leetcode.com/problems/middle-of-the-linked-list?envType=problem-list-v2&envId=linked-list", "Связные списки", "easy"),
    ("Linked List Cycle", "https://leetcode.com/problems/linked-list-cycle?envType=problem-list-v2&envId=linked-list", "Связные списки", "easy"),
    ("Merge Two Sorted Lists", "https://leetcode.com/problems/merge-two-sorted-lists/description/?envType=problem-list-v2&envId=linked-list", "Связные списки", "easy"),
    ("Reverse Linked List", "https://leetcode.com/problems/reverse-linked-list/?envType=problem-list-v2&envId=linked-list", "Связные списки", "easy"),
    ("Palindrome Linked List", "https://leetcode.com/problems/palindrome-linked-list?envType=problem-list-v2&envId=linked-list", "Связные списки", "easy"),
    ("Intersection of Two Linked Lists", "https://leetcode.com/problems/intersection-of-two-linked-lists/description/?envType=problem-list-v2&envId=linked-list", "Связные списки", "easy"),
    ("Delete Node in a Linked List", "https://leetcode.com/problems/delete-node-in-a-linked-list?envType=problem-list-v2&envId=linked-list", "Связные списки", "medium"),
    ("Sort List", "https://leetcode.com/problems/sort-list/description/?envType=problem-list-v2&envId=linked-list", "Связные списки", "medium"),

    # Деревья (10)
    ("Binary Tree Inorder Traversal", "https://leetcode.com/problems/binary-tree-inorder-traversal/description/", "Деревья", "easy"),
    ("Search in a Binary Search Tree", "https://leetcode.com/problems/search-in-a-binary-search-tree/description/", "Деревья", "easy"),
    ("Maximum Depth of Binary Tree", "https://leetcode.com/problems/maximum-depth-of-binary-tree/", "Деревья", "easy"),
    ("Diameter of Binary Tree", "https://leetcode.com/problems/diameter-of-binary-tree/", "Деревья", "easy"),
    ("Range Sum of BST", "https://leetcode.com/problems/range-sum-of-bst/description/", "Деревья", "easy"),
    ("Symmetric Tree", "https://leetcode.com/problems/symmetric-tree/", "Деревья", "easy"),
    ("Insert into a Binary Search Tree", "https://leetcode.com/problems/insert-into-a-binary-search-tree/description/", "Деревья", "medium"),
    ("Delete Node in a BST", "https://leetcode.com/problems/delete-node-in-a-bst/description/", "Деревья", "medium"),
    ("Binary Tree Level Order Traversal", "https://leetcode.com/problems/binary-tree-level-order-traversal/", "Деревья", "medium"),
    ("Validate Binary Search Tree", "https://leetcode.com/problems/validate-binary-search-tree/?envType=problem-list-v2&envId=binary-tree", "Деревья", "medium"),

    # Стеки и очереди (7 — без Valid Parentheses и Min Stack)
    ("Implement Queue using Stacks", "https://leetcode.com/problems/implement-queue-using-stacks?envType=problem-list-v2&envId=stack", "Стеки и очереди", "easy"),
    ("Implement Stack using Queues", "https://leetcode.com/problems/implement-stack-using-queues/description/?envType=problem-list-v2&envId=stack", "Стеки и очереди", "easy"),
    ("Score of Parentheses", "https://leetcode.com/problems/score-of-parentheses/description/", "Стеки и очереди", "medium"),
    ("Minimum Add to Make Parentheses Valid", "https://leetcode.com/problems/minimum-add-to-make-parentheses-valid/description/", "Стеки и очереди", "medium"),
    ("Minimum Remove to Make Valid Parentheses", "https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/description/", "Стеки и очереди", "medium"),
    ("Daily Temperatures", "https://leetcode.com/problems/daily-temperatures/description/", "Стеки и очереди", "medium"),
    ("Decode String", "https://leetcode.com/problems/decode-string/submissions/1329256666/?envType=problem-list-v2&envId=stack", "Стеки и очереди", "medium"),

    # Плавающие окна (5)
    ("Longest Substring Without Repeating Characters", "https://leetcode.com/problems/longest-substring-without-repeating-characters/description/?envType=problem-list-v2&envId=hash-table", "Плавающие окна", "medium"),
    ("Find All Anagrams in a String", "https://leetcode.com/problems/find-all-anagrams-in-a-string/?envType=problem-list-v2&envId=sliding-window", "Плавающие окна", "medium"),
    ("Longest Harmonious Subsequence", "https://leetcode.com/problems/longest-harmonious-subsequence/description/?envType=problem-list-v2&envId=sliding-window", "Плавающие окна", "medium"),
    ("Longest Repeating Character Replacement", "https://leetcode.com/problems/longest-repeating-character-replacement/description/?envType=problem-list-v2&envId=sliding-window", "Плавающие окна", "medium"),
    ("Fruit Into Baskets", "https://leetcode.com/problems/fruit-into-baskets/description/?envType=problem-list-v2&envId=sliding-window", "Плавающие окна", "medium"),

    # Поиск с возвратом (3)
    ("Generate Parentheses", "https://leetcode.com/problems/generate-parentheses", "Поиск с возвратом", "medium"),
    ("Permutations", "https://leetcode.com/problems/permutations", "Поиск с возвратом", "medium"),
    ("Combinations", "https://leetcode.com/problems/combinations", "Поиск с возвратом", "medium"),

    # Графы (5)
    ("Number of Islands", "https://leetcode.com/problems/number-of-islands", "Графы", "medium"),
    ("The Maze", "https://leetcode.com/problems/the-maze", "Графы", "medium"),
    ("Course Schedule", "https://leetcode.com/problems/course-schedule", "Графы", "medium"),
    ("Cheapest Flights Within K Stops", "https://leetcode.com/problems/cheapest-flights-within-k-stops", "Графы", "medium"),
    ("Min Cost to Connect All Points", "https://leetcode.com/problems/min-cost-to-connect-all-points", "Графы", "medium"),

    # Динамическое программирование (4)
    ("Climbing Stairs", "https://leetcode.com/problems/climbing-stairs", "Динамическое программирование", "easy"),
    ("Jump Game", "https://leetcode.com/problems/jump-game", "Динамическое программирование", "medium"),
    ("House Robber", "https://leetcode.com/problems/house-robber", "Динамическое программирование", "medium"),
    ("Coin Change", "https://leetcode.com/problems/coin-change", "Динамическое программирование", "medium"),
]

TASKS_POOL = [
    {
        "number": TASK_START_NUMBER + i,
        "title": title,
        "url": url,
        "topic": topic,
        "difficulty": difficulty,
    }
    for i, (title, url, topic, difficulty) in enumerate(_raw)
]
