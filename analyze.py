import os
import glob
import json
import sys
import matplotlib.pyplot as plt
from fpdf import FPDF

# Function to load logs from a specific directory
def load_logs(log_dir):
    data = []
    files = glob.glob(os.path.join(log_dir, "*.log"))
    print(f"[*] Analyzing logs in: {log_dir}")

    for file_path in files:
        if "analysis.log" in file_path: continue

        filename = os.path.basename(file_path)
        experiment_name = filename.replace("attempts_", "").replace(".log", "")

        with open(file_path, "r", encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if "experiment" not in entry:
                        entry["experiment"] = experiment_name
                    data.append(entry)
                except json.JSONDecodeError:
                    continue

    if not data:
        return [] #d
    
    
    return data

# Function to generate graphs 
def generate_graphs(data, output_dir):
    if not data:
        return

    graphs_dir = os.path.join(output_dir, "graphs")
    os.makedirs(graphs_dir, exist_ok=True)
    
    # Helper to filter data by experiment
    def get_exp_data(exp_name):
        return [d for d in data if d.get("experiment") == exp_name]

    # Get all experiment names
    experiments = set(d.get("experiment") for d in data if d.get("experiment"))

    # Graph 1: Total Attempts as Simple Bar
    plt.figure(figsize=(12, 6))
    counts = {}
    for exp in experiments:
        counts[exp] = len(get_exp_data(exp))
    
    plt.bar(counts.keys(), counts.values(), color="skyblue", edgecolor="black")
    plt.title("Total Attempts per Experiment")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(graphs_dir, "1_attempts_per_experiment.png"))
    plt.close()

    # Graph 5: Attack Progression --
    target_experiments = ["no_protection", "with_protection", "bcrypt", "argon2id"]
    
    plt.figure(figsize=(14, 8))
    has_data = False
    
    for exp in target_experiments:
        subset = [d for d in data if d.get("experiment") == exp]
        if not subset: continue
        
        # Sort by timestamp
        subset.sort(key=lambda x: x["timestamp"])
        
        start_time = subset[0]["timestamp"]
        relative_times = [x["timestamp"] - start_time for x in subset]
        attempts = range(1, len(subset) + 1)
        
        plt.plot(relative_times, attempts, label=exp, linewidth=3, marker='o', markersize=4)
        has_data = True

    if has_data:
        plt.title("Attack Progression: Protections Comparison (Zoomed In)")
        plt.xlabel("Time (Seconds)")
        plt.ylabel("Cumulative Attempts")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(graphs_dir, "5_attack_progression.png"))
        plt.close()
        print("[+] Fixed Graph 5 generated (filtered view).")

# Dummy functions to keep compatibility with r main.py
def generate_summary_graphs(data, output_folder):
    pass
def generate_full_report(output_folder):
    pass

# Main Logic 
def run_analysis(input_folder, output_folder):
    print(f"--- Starting Analysis on {input_folder} ---")
    data = load_logs(input_folder)
    if not data:
        print("[!] No data found.")
        return

    generate_graphs(data, output_folder)
    print("--- Analysis Logic Complete ---")

if __name__ == "__main__":
    # If run directly
    run_analysis("logs", "output")