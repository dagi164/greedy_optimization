import random
import time
import csv
import os
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# TIME & SPACE COMPLEXITY ANALYSIS
# ============================================================
# 1. Fractional Knapsack (Greedy)
#    - Sorting step:        O(n log n)  — dominant step
#    - Greedy selection:    O(n)        — single pass through items
#    - Overall Time:        O(n log n)
#    - Space Complexity:    O(n)        — for the sorted list and result
#
# 2. 0/1 Knapsack (Dynamic Programming)
#    - DP table fill:       O(n * W)    — n items, W = capacity
#    - Backtracking:        O(n)        — trace back through DP table
#    - Overall Time:        O(n * W)
#    - Space Complexity:    O(n * W)    — 2D DP table of size (n+1) x (W+1)
#
# Comparison:
#    Fractional is faster (O(n log n)) but allows splitting items.
#    0/1 DP is exact for integer items but slower for large W.
# ============================================================


# ── CSV Export Helpers ──────────────────────────────────────

def export_to_csv(dataset, filename="dataset.csv"):
    """Export item dataset to CSV."""
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Weight", "Profit", "Ratio"])
        for item in dataset:
            writer.writerow([item[0], item[1], item[2], round(item[3], 2)])
    print(f"Dataset exported to {filename}")


def export_fractional_solution(contents, filename):
    """Export fractional knapsack solution to CSV."""
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Item ID", "Fraction Taken"])
        for item_id, fraction in contents:
            writer.writerow([item_id, fraction])
    print(f"Fractional solution exported to {filename}")


def export_zero_one_solution(items, selected_ids, filename):
    """Export 0/1 knapsack solution to CSV."""
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Item ID", "Weight", "Profit"])
        for item in items:
            if item[0] in selected_ids:
                writer.writerow([item[0], item[1], item[2]])
    print(f"0/1 solution exported to {filename}")


# ── Algorithms ───────────────────────────────────────────────

def fractional_knapsack(items, capacity):
    """
    Greedy Fractional Knapsack.
    Time:  O(n log n) — sort by profit/weight ratio, then one pass
    Space: O(n)       — result list
    """
    items.sort(key=lambda x: x[3], reverse=True)   # O(n log n)

    total_profit = 0.0
    knapsack_contents = []
    remaining_capacity = capacity

    for item in items:                              # O(n)
        if remaining_capacity <= 0:
            break
        if item[1] <= remaining_capacity:
            remaining_capacity -= item[1]
            total_profit += item[2]
            knapsack_contents.append((item[0], 1.0))
        else:
            fraction = remaining_capacity / item[1]
            total_profit += item[2] * fraction
            knapsack_contents.append((item[0], round(fraction, 2)))
            remaining_capacity = 0

    return total_profit, knapsack_contents


def zero_one_knapsack_dp(items, capacity):
    """
    Dynamic Programming 0/1 Knapsack with backtracking.
    Time:  O(n * W) — fill DP table of n items x W capacity
    Space: O(n * W) — 2D DP table
    """
    n = len(items)
    # Build DP table — O(n * W) time and space
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):                      # O(n * W)
        for w in range(1, capacity + 1):
            if items[i-1][1] <= w:
                dp[i][w] = max(
                    items[i-1][2] + dp[i-1][w - items[i-1][1]],
                    dp[i-1][w]
                )
            else:
                dp[i][w] = dp[i-1][w]

    # Backtrack to find selected items — O(n)
    w = capacity
    selected_items = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected_items.append(items[i-1][0])
            w -= items[i-1][1]

    selected_items.reverse()
    return dp[n][capacity], selected_items


# ── Visualization ────────────────────────────────────────────

def save_visualizations(
    cap_pcts, frac_profits, exec_times,
    small_dataset, small_cap,
    frac_p_small, zero_one_p_small,
    frac_items_small, selected_ids_small
):
    """Generate and save all visualization charts to the images/ folder."""
    os.makedirs("images", exist_ok=True)

    # ── 1. Profit vs Capacity % (bar chart) ──────────────────
    fig, ax = plt.subplots(figsize=(7, 5))
    labels = [f"{int(p*100)}%" for p in cap_pcts]
    bars = ax.bar(labels, frac_profits, color=["#4C72B0", "#55A868", "#C44E52"], width=0.5)
    ax.set_title("Fractional Knapsack — Total Profit vs Capacity", fontsize=13, fontweight='bold')
    ax.set_xlabel("Capacity (% of total weight)")
    ax.set_ylabel("Total Profit")
    for bar, val in zip(bars, frac_profits):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 500,
                f"{val:,.0f}", ha='center', va='bottom', fontsize=10)
    ax.set_ylim(0, max(frac_profits) * 1.12)
    plt.tight_layout()
    plt.savefig("images/profit_vs_capacity.png", dpi=150)
    plt.close()
    print("Saved: images/profit_vs_capacity.png")

    # ── 2. Execution Time vs Capacity % (line chart) ─────────
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(labels, exec_times, marker='o', color="#C44E52", linewidth=2, markersize=8)
    for x, y in zip(labels, exec_times):
        ax.annotate(f"{y:.4f}s", (x, y), textcoords="offset points",
                    xytext=(0, 10), ha='center', fontsize=9)
    ax.set_title("Fractional Knapsack — Execution Time vs Capacity", fontsize=13, fontweight='bold')
    ax.set_xlabel("Capacity (% of total weight)")
    ax.set_ylabel("Execution Time (seconds)")
    y_max = max(exec_times) * 1.5 if max(exec_times) > 0 else 0.01
    ax.set_ylim(0, y_max)
    plt.tight_layout()
    plt.savefig("images/execution_time.png", dpi=150)
    plt.close()
    print("Saved: images/execution_time.png")

    # ── 3. Small dataset — item weights and profits (grouped bar) ──
    ids     = [item[0] for item in small_dataset]
    weights = [item[1] for item in small_dataset]
    profits = [item[2] for item in small_dataset]

    x = range(len(ids))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([i - width/2 for i in x], weights, width, label='Weight', color='#4C72B0')
    ax.bar([i + width/2 for i in x], profits, width, label='Profit', color='#55A868')
    ax.set_title("Small Dataset — Weight vs Profit per Item", fontsize=13, fontweight='bold')
    ax.set_xlabel("Item ID")
    ax.set_ylabel("Value")
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(i) for i in ids])
    ax.legend()
    plt.tight_layout()
    plt.savefig("images/small_dataset_items.png", dpi=150)
    plt.close()
    print("Saved: images/small_dataset_items.png")

    # ── 4. Fractional vs 0/1 profit comparison (small dataset) ──
    fig, ax = plt.subplots(figsize=(6, 5))
    algo_labels = ["Fractional\n(Greedy)", "0/1\n(DP)"]
    profits_cmp = [frac_p_small, zero_one_p_small]
    colors = ["#4C72B0", "#C44E52"]
    bars = ax.bar(algo_labels, profits_cmp, color=colors, width=0.4)
    for bar, val in zip(bars, profits_cmp):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val:.2f}", ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_title(f"Fractional vs 0/1 Knapsack\n(Small Dataset, Cap={small_cap})",
                 fontsize=13, fontweight='bold')
    ax.set_ylabel("Total Profit")
    ax.set_ylim(0, max(profits_cmp) * 1.2)
    plt.tight_layout()
    plt.savefig("images/fractional_vs_zero_one.png", dpi=150)
    plt.close()
    print("Saved: images/fractional_vs_zero_one.png")

    # ── 5. Profit/Weight ratio distribution (histogram) ──────
    fig, ax = plt.subplots(figsize=(8, 5))
    ratios = [item[3] for item in small_dataset]
    ax.bar([str(item[0]) for item in small_dataset], ratios, color='#8172B2')
    ax.set_title("Small Dataset — Profit/Weight Ratio per Item", fontsize=13, fontweight='bold')
    ax.set_xlabel("Item ID")
    ax.set_ylabel("Profit/Weight Ratio")
    plt.tight_layout()
    plt.savefig("images/ratio_distribution.png", dpi=150)
    plt.close()
    print("Saved: images/ratio_distribution.png")

    # ── 6. Complexity comparison (theoretical, illustrative) ─
    n_vals = np.arange(1, 201)
    W = 500  # fixed capacity for illustration
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(n_vals, n_vals * np.log2(n_vals),
            label="Fractional: O(n log n)", color="#4C72B0", linewidth=2)
    ax.plot(n_vals, n_vals * W / 100,
            label=f"0/1 DP: O(n·W), W={W} (scaled /100)", color="#C44E52",
            linewidth=2, linestyle='--')
    ax.set_title("Theoretical Time Complexity Comparison", fontsize=13, fontweight='bold')
    ax.set_xlabel("Number of Items (n)")
    ax.set_ylabel("Operations (relative)")
    ax.legend()
    plt.tight_layout()
    plt.savefig("images/complexity_comparison.png", dpi=150)
    plt.close()
    print("Saved: images/complexity_comparison.png")


# ── Main Experiment ──────────────────────────────────────────

def run_experiment():
    # 1. Generate 1000-item dataset stored as arrays [id, weight, profit, ratio]
    dataset = []
    for i in range(1000):
        weight = random.randint(1, 50)
        profit = random.randint(10, 500)
        ratio = profit / weight
        dataset.append([i, weight, profit, ratio])

    export_to_csv(dataset, "knapsack_dataset.csv")

    total_weight = sum(item[1] for item in dataset)

    # 2. Capacity scenarios: 50%, 75%, 90%
    capacities = [0.5, 0.75, 0.9]
    frac_profits = []
    exec_times   = []

    print(f"\n{'Capacity %':<12} | {'Total Profit':<15} | {'Execution Time'}")
    print("-" * 50)

    for cap_pct in capacities:
        cap = int(total_weight * cap_pct)

        start_time = time.time()
        frac_profit, frac_items = fractional_knapsack(dataset[:], cap)
        end_time = time.time()

        elapsed = end_time - start_time
        frac_profits.append(frac_profit)
        exec_times.append(elapsed)

        export_fractional_solution(frac_items, f"fractional_{int(cap_pct*100)}.csv")
        print(f"{cap_pct*100:>10}% | {frac_profit:>15.2f} | {elapsed:.6f}s")

    # 3. Small dataset (n=10) for verification and visualization
    small_dataset = []
    for i in range(10):
        weight = random.randint(1, 10)
        profit = random.randint(10, 100)
        ratio = profit / weight
        small_dataset.append([i, weight, profit, ratio])

    small_cap = 15
    export_to_csv(small_dataset, "small_dataset.csv")

    frac_p, frac_items_small = fractional_knapsack(small_dataset[:], small_cap)
    export_fractional_solution(frac_items_small, "small_fractional_solution.csv")

    zero_one_p, selected_ids = zero_one_knapsack_dp(small_dataset, small_cap)
    export_zero_one_solution(small_dataset, selected_ids, "small_zero_one_solution.csv")

    print("\n--- Verification (Small Dataset) ---")
    print(f"Small Dataset (n=10, Cap={small_cap})")
    print(f"Fractional (Greedy) Profit : {frac_p:.2f}")
    print(f"0/1 (DP) Profit            : {zero_one_p}")
    print("Note: Fractional >= 0/1 because fractions are allowed.")

    # 4. Generate all visualizations
    print("\n--- Generating Visualizations ---")
    save_visualizations(
        capacities, frac_profits, exec_times,
        small_dataset, small_cap,
        frac_p, zero_one_p,
        frac_items_small, selected_ids
    )
    print("\nAll done. Charts saved in the images/ folder.")


if __name__ == "__main__":
    run_experiment()
