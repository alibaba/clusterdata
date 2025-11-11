#!/usr/bin/env python3
import csv
import os
import sys
import subprocess
from pathlib import Path
from collections import defaultdict


def create_filtered_traces(original_trace, target_user=None, num_jobs=2000):
    """Create single-user and multi-user traces for comparison."""

    print(f"Reading original trace: {original_trace}")

    jobs = []
    user_counts = defaultdict(int)

    with open(original_trace, "r") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            jobs.append(row)
            user_counts[row["user"]] += 1

    print(f"Found {len(jobs)} jobs from {len(user_counts)} users")

    # Select target user (most active if not specified)
    if target_user is None:
        target_user = max(user_counts.items(), key=lambda x: x[1])[0]

    print(f"Target user: {target_user} ({user_counts[target_user]} jobs available)")

    # Create single-user trace
    user_jobs = [job for job in jobs if job["user"] == target_user]
    if len(user_jobs) > num_jobs:
        user_jobs = user_jobs[:num_jobs]

    # Sort by original submit time and reset to start from 0
    user_jobs.sort(key=lambda x: int(x.get("submit_time", 0)))
    for i, job in enumerate(user_jobs):
        job["submit_time"] = str(i * 60)  # One job per minute
    # NOTE: why one job per minute?

    single_trace = Path("simulator/traces/pai/single_user_temp.csv")
    with open(single_trace, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(user_jobs)

    print(f"Created single-user trace: {len(user_jobs)} jobs")

    # Create multi-user trace with same number of jobs
    # NOTE: why are you grabbing jobs from the complete job trace?
    # NOTE: this means that the user_jobs may not even be included in this list.
    multi_jobs = jobs[: len(user_jobs)]
    multi_jobs.sort(key=lambda x: int(x.get("submit_time", 0)))
    for i, job in enumerate(multi_jobs):
        job["submit_time"] = str(i * 60)

    multi_trace = Path("simulator/traces/pai/multi_user_temp.csv")
    with open(multi_trace, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(multi_jobs)

    unique_users = len(set(job["user"] for job in multi_jobs))
    print(f"Created multi-user trace: {len(multi_jobs)} jobs from {unique_users} users")

    return single_trace.name, multi_trace.name, target_user, len(user_jobs)


def run_simulation(trace_filename, scenario_name, num_jobs, num_gpus=6500):
    """Run simulation using the existing simulator."""

    print(f"\n=== Running {scenario_name} simulation ===")

    original_dir = os.getcwd()
    os.chdir("simulator")

    cmd = [
        "python3",
        "run_simulator.py",
        "--num_jobs",
        str(num_jobs),
        "--num_gpus",
        str(num_gpus),
        "--repeat",
        "1",
    ]

    with open("run_simulator.py", "r") as f:
        content = f.read()

    modified_content = content.replace(
        "CSV_FILE = 'pai_job_duration_estimate_100K.csv'",
        f"CSV_FILE = '{trace_filename}'",
    ).replace(
        "for alloc_policy in [0, 1, 2, 4, 8]:",  # Only test FIFO and SJF for now
        "for alloc_policy in [8, 0]:",
    )

    with open("run_simulator_temp.py", "w") as f:
        f.write(modified_content)

    result = subprocess.run(
        ["python3", "run_simulator_temp.py"] + cmd[2:],
        capture_output=True,
        text=True,
        timeout=300,
    )

    os.remove("run_simulator_temp.py")

    results = {}
    lines = result.stdout.split("\n")

    for line in lines:
        if "FIFO" in line and "," in line:
            parts = line.split(",")
            if len(parts) >= 4:
                policy = "FIFO"
                avg_jct = float(parts[2])
                wait_time = float(parts[3])
                results[policy] = {"avg_jct": avg_jct, "wait_time": wait_time}
        elif "SJF" in line and "," in line:
            parts = line.split(",")
            if len(parts) >= 4:
                policy = "SJF"
                avg_jct = float(parts[2])
                wait_time = float(parts[3])
                results[policy] = {"avg_jct": avg_jct, "wait_time": wait_time}

    os.chdir(original_dir)

    return results


def main():
    num_jobs = 20000
    num_gpus = 6500
    target_user = None

    original_trace = Path("simulator/traces/pai/pai_job_duration_estimate_100K.csv")

    single_trace, multi_trace, selected_user, actual_jobs = create_filtered_traces(
        original_trace, target_user, num_jobs
    )

    # Run simulations
    print(f"\nRunning simulations with {num_gpus} GPUs...")

    # NOTE: shouldn't the single_results be running on a fraction of num_gpus inv. proportional to number of jobs?
    single_results = run_simulation(single_trace, "Single-User", actual_jobs, num_gpus)
    multi_results = run_simulation(multi_trace, "Multi-User", actual_jobs, num_gpus)

    # Display results
    print(f"\n{'='*60}")
    print(f"COMPARISON RESULTS")
    print(f"User: {selected_user}, Jobs: {actual_jobs}, GPUs: {num_gpus}")
    print(f"{'='*60}")

    for policy in ["FIFO", "SJF"]:
        if policy in single_results and policy in multi_results:
            single = single_results[policy]
            multi = multi_results[policy]

            print(f"\n{policy} Policy:")
            print(
                f"  Single-user: JCT={single['avg_jct']:.1f}s, Wait={single['wait_time']:.1f}s"
            )
            print(
                f"  Multi-user:  JCT={multi['avg_jct']:.1f}s, Wait={multi['wait_time']:.1f}s"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
