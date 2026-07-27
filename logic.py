import os
import glob
import json
import pandas as pd
import matplotlib.pyplot as plt

try:
    from report_gen import generate_full_report
except ImportError:
    def generate_full_report(x): pass

# 1. Function to load logs from a specific directory 
def load_logs(log_dir):
    data = []
    # Search for log files in the input directory
    files = glob.glob(os.path.join(log_dir, "*.log"))
    print(f"[*] Analyzing logs in: {log_dir}")

    for file_path in files:
        if "analysis.log" in file_path: continue

        filename = os.path.basename(file_path)
        # Extract experiment name from filename
        experiment_name = filename.replace("attempts_", "").replace(".log", "")

        with open(file_path, "r", encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    # Add experiment name if missing in the log entry
                    if "experiment" not in entry:
                        entry["experiment"] = experiment_name
                    data.append(entry)
                except json.JSONDecodeError:
                    continue

    if not data:
        print("[!] No data found in logs.")
        return pd.DataFrame()

    print(f"[+] Loaded {len(data)} total log entries.")
    return pd.DataFrame(data)

# 2.  Function to generate graphs in the output directory 
def generate_graphs(df, output_dir):
    if df.empty:
        return

    # Ensure graphs subfolder exists inside the output folder
    graphs_dir = os.path.join(output_dir, "graphs")
    os.makedirs(graphs_dir, exist_ok=True)
    print(f"[*] Saving graphs to: {graphs_dir}")

    # Graph 1: Total Attempts per Experiment
    if "experiment" in df.columns:
        plt.figure(figsize=(12, 6))
        df["experiment"].value_counts().plot(kind="bar", color="skyblue", edgecolor="black")
        plt.title("Total Attempts per Experiment")
        plt.xlabel("Experiment")
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(graphs_dir, "1_attempts_per_experiment.png"))
        plt.close()

    # Graph 2: Success Rate 
    if "experiment" in df.columns and "result" in df.columns:
        # Calculate success rate for all experiments 
        success_rates = df.groupby("experiment")["result"].apply(
            lambda x: (x == "success").mean() * 100
        )

        if not success_rates.empty:
            plt.figure(figsize=(10, 6))
            success_rates.plot(kind="bar", color="#66b3ff", edgecolor="black")
            plt.title("Success Rate per Experiment (%)")
            plt.ylabel("Success Rate %")
            plt.xlabel("Experiment")
            plt.ylim(0, 105)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(os.path.join(graphs_dir, "2_success_rate.png"))
            plt.close()
            print("[+] Generated graph: 2_success_rate.png")

    # Graph 3: Hashing Speed Comparison
    if "latency_ms" in df.columns and "hash_mode" in df.columns:
        avg_latency = df.groupby("hash_mode")["latency_ms"].mean()
        if not avg_latency.empty:
            plt.figure(figsize=(8, 5))
            avg_latency.plot(kind="bar", color="purple", logy=True)
            plt.title("Hashing Speed Comparison (Logarithmic Scale)")
            plt.ylabel("Avg Latency (ms) - Log Scale")
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(graphs_dir, "3_hashing_speed.png"))
            plt.close()

    # Graph 4: Failure Reasons
    if "reason" in df.columns:
        failures = df[df["result"] == "fail"]
        if not failures.empty:
            reason_counts = failures["reason"].value_counts()
            plt.figure(figsize=(10, 6))
            def smart_autopct(pct):
                return f'{pct:.1f}%' if pct > 5 else ''
            
            wedges, texts, autotexts = plt.pie(
                reason_counts,
                autopct=smart_autopct,
                startangle=140,
                colors=plt.get_cmap('Pastel1').colors
            )
            plt.setp(autotexts, size=9, weight="bold")
            total = sum(reason_counts)
            legend_labels = [f'{name} - {(count/total*100):.1f}%'
                             for name, count in zip(reason_counts.index, reason_counts)]

            plt.legend(wedges, legend_labels, title="Failure Reasons", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            plt.title("Failure Reasons Analysis")
            plt.tight_layout()
            plt.savefig(os.path.join(graphs_dir, "4_failure_reasons.png"), bbox_inches='tight')
            plt.close()

    # Graph 5: Attack Progression
    if "timestamp" in df.columns and "experiment" in df.columns:
        plt.figure(figsize=(14, 8))
        experiments = df["experiment"].unique()
        has_data = False
        for exp in experiments:
            subset = df[df["experiment"] == exp].sort_values("timestamp")
            if not subset.empty and len(subset) > 1:
                start_time = subset["timestamp"].iloc[0]
                subset["relative_time"] = subset["timestamp"] - start_time
                plt.plot(subset["relative_time"], range(1, len(subset) + 1), label=exp, linewidth=2)
                has_data = True

        if has_data:
            plt.title("Attack Progression Over Time (All Experiments)")
            plt.xlabel("Time (Seconds)")
            plt.ylabel("Cumulative Attempts")
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.savefig(os.path.join(graphs_dir, "5_attack_progression.png"), bbox_inches="tight")
            plt.close()

#  Summary Graphs for Conclusions 
def generate_summary_graphs(df, output_folder):
    """
    Generates specific graphs to visualize the research conclusions:
    1. Latency Cost (SHA256 vs Argon2 vs Bcrypt)
    2. Defense Effectiveness (Success/Fail/Locked distribution)
    """
    graphs_dir = os.path.join(output_folder, "graphs")
    os.makedirs(graphs_dir, exist_ok=True)

    #  Graph 6: Latency Comparison (Bar Chart)
    if "latency_ms" in df.columns and "hash_mode" in df.columns:
        plt.figure(figsize=(10, 6))
        # Calculate mean latency per algorithm
        latency_data = df.groupby("hash_mode")["latency_ms"].mean().sort_values()
        
        if not latency_data.empty:
            latency_data.plot(kind="bar", color=['#ff9999', '#66b3ff', '#99ff99'], edgecolor='black')
            
            plt.title("Average Latency by Hashing Algorithm (Security Cost)", fontsize=14)
            plt.xlabel("Algorithm", fontsize=12)
            plt.ylabel("Time (ms)", fontsize=12)
            plt.grid(axis='y', linestyle='--', alpha=0.5)
            plt.xticks(rotation=0)

            # Add labels
            for i, v in enumerate(latency_data):
                plt.text(i, v + 0.1, f"{v:.1f}ms", ha='center', fontweight='bold')

            plt.tight_layout()
            plt.savefig(os.path.join(graphs_dir, "6_latency_comparison.png"))
            plt.close()
            print("[+] Generated graph: 6_latency_comparison.png")

    # Graph 7: Defense Effectiveness (Stacked Bar)
    if "experiment" in df.columns and "result" in df.columns:
        plt.figure(figsize=(14, 8))
        valid = ["success", "fail", "account_locked", "captcha_required", "totp_wrong"]
        df_filtered = df[df["result"].isin(valid)].copy()
        if not df_filtered.empty:
            outcome = df_filtered.groupby(["experiment", "result"]).size().unstack(fill_value=0)
            outcome.plot(kind="bar", stacked=True, figsize=(14, 7), edgecolor='black')
            plt.title("Attack Outcomes per Experiment")
            plt.tight_layout()
            plt.savefig(os.path.join(graphs_dir, "7_defense_effectiveness.png"))
            plt.close()

#  3. Main Logic Entry Point 
def run_analysis(input_folder, output_folder):
    """
    Main function to orchestrate the analysis process.
    """
    print(f"--- Starting Analysis on {input_folder} ---")
    
    # 1. Load data
    df = load_logs(input_folder)
    if df.empty:
        print("[!] No data found. Skipping analysis.")
        return

    # 2. Generate and save graphs
    generate_graphs(df, output_folder)
    print("Generating summary graphs for conclusions...")
    generate_summary_graphs(df, output_folder)

    # 3. Generate final report
    print("Generating full report...")
    generate_full_report(output_folder)

    print("--- Analysis Logic Complete ---")