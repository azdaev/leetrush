# Пул #12–#21 («Два указателя») полностью пройден.
# Новый пул — две темы по итогам опроса: «Скользящее окно» и «Куча».
# Нумерация продолжается с #22 (закрытые #12–#21 в БД не трогаются).
# Маппинг номер→строка таблицы остаётся через TASK_START_NUMBER (#12 → строка 2).

POOL_START_NUMBER = 22

_raw = [
    # Скользящее окно (#22–#30)
    ("Maximum Average Subarray I", "https://leetcode.com/problems/maximum-average-subarray-i/description/", "Скользящее окно", "easy"),
    ("Contains Duplicate II", "https://leetcode.com/problems/contains-duplicate-ii/description/", "Скользящее окно", "easy"),
    ("Minimum Recolors to Get K Consecutive Black Blocks", "https://leetcode.com/problems/minimum-recolors-to-get-k-consecutive-black-blocks/description/", "Скользящее окно", "easy"),
    ("Max Consecutive Ones III", "https://leetcode.com/problems/max-consecutive-ones-iii/description/", "Скользящее окно", "medium"),
    ("Longest Substring Without Repeating Characters", "https://leetcode.com/problems/longest-substring-without-repeating-characters/description/", "Скользящее окно", "medium"),
    ("Substrings of Size Three with Distinct Characters", "https://leetcode.com/problems/substrings-of-size-three-with-distinct-characters/description/", "Скользящее окно", "easy"),
    ("Minimum Size Subarray Sum", "https://leetcode.com/problems/minimum-size-subarray-sum/description/", "Скользящее окно", "medium"),
    ("Defuse the Bomb", "https://leetcode.com/problems/defuse-the-bomb/description/", "Скользящее окно", "easy"),
    ("Longest Subarray of 1's After Deleting One Element", "https://leetcode.com/problems/longest-subarray-of-1s-after-deleting-one-element/description/", "Скользящее окно", "medium"),

    # Куча (#31–#34)
    ("Last Stone Weight", "https://leetcode.com/problems/last-stone-weight/description/", "Куча", "easy"),
    ("Kth Largest Element in an Array", "https://leetcode.com/problems/kth-largest-element-in-an-array/description/", "Куча", "medium"),
    ("Top K Frequent Words", "https://leetcode.com/problems/top-k-frequent-words/description/", "Куча", "medium"),
    ("K Closest Points to Origin", "https://leetcode.com/problems/k-closest-points-to-origin/description/", "Куча", "medium"),
]

TASKS_POOL = [
    {
        "number": POOL_START_NUMBER + i,
        "title": title,
        "url": url,
        "topic": topic,
        "difficulty": difficulty,
    }
    for i, (title, url, topic, difficulty) in enumerate(_raw)
]
