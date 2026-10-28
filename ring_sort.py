"""
Ring-sort puzzle solver.

Rules (as agreed):
  * n colours, `height` rings of each colour.
  * n + 1 rods, each holding at most `height` rings (so exactly one rod's
    worth of free space in total, spread anywhere).
  * A move takes the TOP ring of any rod and puts it on any rod with space.
  * Goal: every non-empty rod is full of a single colour.

Algorithm (constructive, always succeeds):
  Repeat for each colour until everything is sorted:
    1. Consolidate the free space so one rod E is empty and the rest are full.
    2. Pick the colour c that is cheapest to extract.
    3. For every full rod A holding c, "partition" it so all its c-rings sit
       on top, using E and another full rod B as scratch space
       (<= 2*height + 2*a moves, B is restored exactly, E ends empty).
    4. Pour the c-rings off every rod's top into E. Exactly `height` of them
       exist, so E becomes a finished rod. Retire it and recurse on n-1 colours.

Complexity:
  Moves  <= (4k + 2) * height in the phase with k colours left,
            so O(n^2 * height) moves overall.
  Time   O(n^2 * height): every phase is linear in the rings it touches,
            so running time is linear in the size of the answer.
  This is a fast valid solution, not a minimum-move one: finding the fewest
  moves for this family of puzzles is NP-hard.

Rods are lists from BOTTOM to TOP. Colours can be any hashable values.
Moves are (from_rod, to_rod) pairs, 0-indexed.
"""

from collections import Counter


def solve(rods, height):
    rods = [list(r) for r in rods]
    _validate(rods, height)
    moves = []

    def mv(src, dst, times=1):
        for _ in range(times):
            rods[dst].append(rods[src].pop())
            moves.append((src, dst))

    def is_done(i):
        r = rods[i]
        return len(r) == height and r.count(r[0]) == height

    active = list(range(len(rods)))

    while True:
        # Retire rods that are already full and single-coloured (free).
        active = [i for i in active if not is_done(i)]
        if all(not rods[i] for i in active):
            return moves

        # 1. Consolidate: empty the emptiest rod into the gaps elsewhere.
        e = min(active, key=lambda i: len(rods[i]))
        others = [i for i in active if i != e]
        j = 0
        while rods[e]:
            while len(rods[others[j]]) == height:
                j += 1
            mv(e, others[j])
        full = others  # every one of these is now full

        # 2. Choose the colour with the cheapest partition cost.
        per_rod = {i: Counter(rods[i]) for i in full}
        cost = Counter()
        for i in full:
            r = rods[i]
            top, run = r[-1], 1
            while run < height and r[-1 - run] == top:
                run += 1
            for colour, a in per_rod[i].items():
                already_on_top = colour == top and a == run
                cost[colour] += 0 if already_on_top else 2 * height + 2 * a
        c = min(cost, key=cost.get)

        # 3. Partition every rod holding c so its c-rings are on top.
        for a_rod in full:
            a = per_rod[a_rod][c]
            r = rods[a_rod]
            if a == 0 or all(x == c for x in r[height - a:]):
                continue
            b_rod = next(i for i in full if i != a_rod)
            mv(b_rod, e, a)                     # make room on B for a c-rings
            for _ in range(height):             # split A: c -> B, other -> E
                mv(a_rod, b_rod if rods[a_rod][-1] == c else e)
            mv(e, a_rod, height - a)            # non-c back to A (bottom)
            mv(b_rod, a_rod, a)                 # c-rings onto A (top)
            mv(e, b_rod, a)                     # restore B, E is empty again

        # 4. Pour all c-rings into E; it becomes a finished rod.
        for i in full:
            while rods[i] and rods[i][-1] == c:
                mv(i, e)


def _validate(rods, height):
    counts = Counter(x for r in rods for x in r)
    n = len(counts)
    if len(rods) != n + 1:
        raise ValueError(f"{n} colours need {n + 1} rods, got {len(rods)}")
    if any(len(r) > height for r in rods):
        raise ValueError("a rod holds more than `height` rings")
    bad = {c: k for c, k in counts.items() if k != height}
    if bad:
        raise ValueError(f"each colour needs exactly {height} rings: {bad}")


def apply_moves(rods, moves, height):
    """Replay moves under the rules and return the final state (for checking)."""
    rods = [list(r) for r in rods]
    for src, dst in moves:
        if not rods[src]:
            raise ValueError(f"move {src}->{dst}: source rod is empty")
        if len(rods[dst]) >= height:
            raise ValueError(f"move {src}->{dst}: destination rod is full")
        rods[dst].append(rods[src].pop())
    return rods


def is_solved(rods, height):
    return all(not r or (len(r) == height and len(set(r)) == 1) for r in rods)


if __name__ == "__main__":
    # Example roughly in the spirit of the video: 6 colours, height 8.
    import random

    colours = ["blue", "green", "orange", "lime", "sky", "red"]
    h = 8
    rings = [c for c in colours for _ in range(h)]
    random.seed(1)
    random.shuffle(rings)
    start = [rings[i * h:(i + 1) * h] for i in range(len(colours))] + [[]]

    moves = solve(start, h)
    end = apply_moves(start, moves, h)
    print(f"Solved in {len(moves)} moves: {is_solved(end, h)}")
    for i, r in enumerate(end):
        print(i, r)
