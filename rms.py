from dataclasses import dataclass
from math import gcd
from functools import reduce


@dataclass
class Task:
    name: str
    execution_time: int 
    period: int        
    remaining: int = 0
    next_release: int = 0


def lcm(a, b):
    return a * b // gcd(a, b)


def utilization_test(tasks):
    n = len(tasks)
    u = sum(t.execution_time / t.period for t in tasks)
    bound = n * (2 ** (1 / n) - 1)
    print(f"CPU Utilization (U) : {u:.4f}")
    print(f"Liu-Layland Bound   : {bound:.4f}")
    if u <= bound:
        print("Result: Schedulable (guaranteed by the bound)\n")
    elif u <= 1:
        print("Result: Not guaranteed by the bound, simulation needed\n")
    else:
        print("Result: NOT schedulable (U > 1)\n")
    return u


def rate_monotonic(tasks):
    """Preemptive Rate Monotonic simulation over one hyperperiod"""
    hyperperiod = reduce(lcm, (t.period for t in tasks))
    tasks = sorted(tasks, key=lambda t: t.period)

    timeline = []       
    missed = []         

    for t in tasks:
        t.remaining = 0
        t.next_release = 0

    for time in range(hyperperiod):
        for t in tasks:
            if time % t.period == 0:
                if t.remaining > 0:
                    missed.append((t.name, time))
                t.remaining = t.execution_time

        running = next((t for t in tasks if t.remaining > 0), None)

        if running:
            running.remaining -= 1
            timeline.append(running.name)
        else:
            timeline.append("Idle")

    for t in tasks:
        if t.remaining > 0:
            missed.append((t.name, hyperperiod))

    return timeline, missed, hyperperiod


def print_timeline(timeline):
    print("--- Gantt Chart (each cell = 1 time unit) ---")
    segments = []
    start = 0
    for i in range(1, len(timeline) + 1):
        if i == len(timeline) or timeline[i] != timeline[start]:
            segments.append((timeline[start], start, i))
            start = i
    print("".join(f"| {name} " for name, _, _ in segments) + "|")
    print("  ".join([str(segments[0][1])] + [str(e) for _, _, e in segments]))


if __name__ == "__main__":
    tasks = [
        Task("T1", execution_time=1, period=4),
        Task("T2", execution_time=2, period=6),
        Task("T3", execution_time=3, period=12),
    ]

    print("=== Rate Monotonic Scheduling ===\n")
    utilization_test(tasks)
    timeline, missed, hp = rate_monotonic(tasks)

    print(f"Hyperperiod: {hp}\n")
    print_timeline(timeline)

    print("\n--- Deadline Check ---")
    if missed:
        for name, t in missed:
            print(f"Deadline missed: {name} at time {t}")
    else:
        print("All deadlines met.")
