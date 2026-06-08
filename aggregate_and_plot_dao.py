import os
import glob
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    csv_files = glob.glob("results_*.map.csv")
    if not csv_files:
        print("No CSV files found yet. Run this once `run_dao_maps.py` finishes.")
        return

    print(f"Aggregating {len(csv_files)} CSV files...")
    df_list = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            df_list.append(df)
        except pd.errors.EmptyDataError:
            pass

    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df.to_csv("results.csv", index=False)
    print("Saved combined global results to results.csv")

    os.makedirs("csv_files", exist_ok=True)
    os.makedirs("plots", exist_ok=True)

    for f in csv_files:
        shutil.move(f, os.path.join("csv_files", f))
    print(f"Moved {len(csv_files)} individual CSV files to csv_files/ directory")

    sns.set_theme(style="whitegrid")

    # 1. Risk vs. Path Length (Scatter Plot)
    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=combined_df, x="Path_Length", y="Path_Risk_Score", hue="Algorithm", alpha=0.7)
    plt.title("Risk vs. Path Length (DAO Maps)")
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "Risk_vs_PathLength.pdf"), format="pdf")
    plt.close()

    # 2. Runtime Scalability (Box Plot)
    plt.figure(figsize=(12, 6))
    ax = sns.boxplot(data=combined_df, x="Algorithm", y="Time_ms")
    ax.set_yscale("log")
    plt.title("Runtime Scalability (Time in ms - Log Scale) (DAO Maps)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "Runtime_Scalability.pdf"), format="pdf")
    plt.close()

    # 3. Search Efficiency (Bar Chart)
    plt.figure(figsize=(12, 6))
    sns.barplot(data=combined_df, x="Algorithm", y="Visited", errorbar=('ci', 95), capsize=.1)
    plt.title("Search Efficiency (Nodes Visited) (DAO Maps)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "Search_Efficiency.pdf"), format="pdf")
    plt.close()
    
    print("DAO PDF plots generated and saved successfully.")

if __name__ == "__main__":
    main()
