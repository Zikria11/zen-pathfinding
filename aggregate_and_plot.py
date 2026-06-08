import os
import glob
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    # 1. Aggregate CSVs
    csv_files = glob.glob("results_*.map.csv")
    if not csv_files:
        print("No results_*.map.csv files found.")
        return

    df_list = []
    for f in csv_files:
        df_list.append(pd.read_csv(f))
    
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # Save combined results to root
    combined_df.to_csv("results.csv", index=False)
    print("Saved combined results to results.csv")

    # 2. Create directories
    os.makedirs("csv_files", exist_ok=True)
    os.makedirs("plots", exist_ok=True)

    # Move individual CSV files to csv_files folder
    for f in csv_files:
        shutil.move(f, os.path.join("csv_files", f))
    print(f"Moved {len(csv_files)} files to csv_files/ directory")

    # 3. Create Plots
    sns.set_theme(style="whitegrid")
    metrics = ["Path_Length", "Visited", "Success", "Hesitations", "Time_ms", "Path_Risk_Score"]
    
    for metric in metrics:
        if metric not in combined_df.columns:
            continue
        plt.figure(figsize=(10, 6))
        # Use a bar plot to show the mean of each metric per algorithm
        sns.barplot(data=combined_df, x="Algorithm", y=metric, errorbar=('ci', 95), capsize=.1)
        plt.title(f"Average {metric} by Algorithm")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join("plots", f"{metric}_plot.png"))
        plt.close()
        
    print("Plots generated and saved in plots/ directory.")

if __name__ == "__main__":
    main()
