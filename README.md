# ring-sort

Solver and animated visualiser for the coloured ring sorting puzzle: **n** colours, **h** rings of each, **n + 1** rods of height **h**. A move takes the top ring of any rod and puts it on any rod with space; the goal is one colour per rod.

**Live demo:** https://dasosis.github.io/ring-sort/

## Algorithm

Repeat once per colour:

1. **Consolidate** the free space so one rod `E` is empty and every other rod is full.
2. **Pick** the colour `c` that is cheapest to extract.
3. **Partition** each full rod holding `c` so its `c` rings sit on top, using `E` and one borrowed full rod as scratch. The borrowed rod is restored exactly (≤ 4h moves per rod).
4. **Pour** the `c` rings off every top into `E`, which is now a finished rod. Recurse on n − 1 colours.

| | Bound |
|---|---|
| Moves | ≤ Σ (4k + 2)·h = O(n²·h) |
| Time | O(n²·h), linear in the length of the output |

It always succeeds, but it isn't minimum-move: finding the fewest moves for this family of puzzles is NP-hard.

## Python

```python
from ring_sort import solve, apply_moves, is_solved

h = 4
start = [["r", "g", "b", "r"], ["g", "b", "r", "g"], ["b", "r", "g", "b"], []]
moves = solve(start, h)              # list of (from_rod, to_rod), 0-indexed
assert is_solved(apply_moves(start, moves, h), h)
```

Rods are lists from bottom to top; colours can be any hashable value.

Tested on 3,000 random puzzles (all solved); a 100-colour × 100-height puzzle solves in about 0.4 s.
