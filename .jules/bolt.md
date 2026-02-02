## 2024-05-23 - [Regex Pre-compilation in Loops]
**Learning:** Pre-compiling regular expressions (`re.compile`) at the module level provides a significant performance boost (measured ~1.8x speedup) when the regex is used inside a tight loop or a pandas `apply` function, compared to compiling it repeatedly or implicitly inside the loop. Vectorized string operations in Pandas are usually faster, but in complex logic cases (multiple prioritized regex groups + fallback logic), a simple pre-compiled regex with `apply` can sometimes be cleaner and sufficiently fast, or even faster if the vectorized approach requires multiple passes or expensive intermediate structures.
**Action:** Always check for regex usage in loops or `apply` calls. If found, refactor to use module-level pre-compiled patterns. When considering vectorization, benchmark against the optimized loop version, as the overhead of complex vectorization might outweigh the benefits for moderate dataset sizes.

## 2025-02-20 - [Pandas Series Iteration]
**Learning:** Iterating directly over a pandas Series in a list comprehension is significantly slower (approx 2.7x) than converting it to a list first using `.tolist()`. This is due to the overhead of pandas indexing and boxing during iteration.
**Action:** Always prefer `[f(x) for x in series.tolist()]` over `[f(x) for x in series]` when creating a list from a series.
