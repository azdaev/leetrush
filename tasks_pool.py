from config import TASK_START_NUMBER

_raw = [
    # #12 — уже активна, оставляем как якорь
    ("Reverse String", "https://leetcode.com/problems/reverse-string/description/", "Два указателя", "easy"),

    # Новый пул — Два указателя (#13–#21)
    ("Reverse Vowels of a String", "https://leetcode.com/problems/reverse-vowels-of-a-string/description/", "Два указателя", "easy"),
    ("Valid Palindrome", "https://leetcode.com/problems/valid-palindrome/description/", "Два указателя", "easy"),
    ("Find First Palindromic String in the Array", "https://leetcode.com/problems/find-first-palindromic-string-in-the-array/description/", "Два указателя", "easy"),
    ("Move Zeroes", "https://leetcode.com/problems/move-zeroes/description/", "Два указателя", "easy"),
    ("Remove Duplicates from Sorted Array", "https://leetcode.com/problems/remove-duplicates-from-sorted-array/description/", "Два указателя", "easy"),
    ("Squares of a Sorted Array", "https://leetcode.com/problems/squares-of-a-sorted-array/description/", "Два указателя", "easy"),
    ("Two Sum II - Input Array Is Sorted", "https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/description/", "Два указателя", "medium"),
    ("Reverse String II", "https://leetcode.com/problems/reverse-string-ii/description/", "Два указателя", "easy"),
    ("Longest Palindromic Substring", "https://leetcode.com/problems/longest-palindromic-substring/description/", "Два указателя", "medium"),
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
