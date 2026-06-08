import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    combined_df = pd.read_csv("results.csv")
    os.makedirs("plots", exist_ok=True)

    sns.set_theme(style="whitegrid")
    metrics = ["Path_Length", "Visited", "Success", "Hesitations", "Time_ms", "Path_Risk_Score"]
    
    for metric in metrics:
        if metric not in combined_df.columns:
            continue
        plt.figure(figsize=(12, 8))
        
        # Show all individual result points instead of just the mean
        sns.stripplot(data=combined_df, x="Algorithm", y=metric, alpha=0.6, jitter=True, size=4)
        sns.boxplot(data=combined_df, x="Algorithm", y=metric, color="gray", fill=False, showcaps=False, fliersize=0)
        
        plt.title(f"All Results for {metric} by Algorithm")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join("plots", f"{metric}_plot.pdf"), format="pdf")
        plt.close()
        
    print("PDF plots generated and saved in plots/ directory.")

if __name__ == "__main__":
    main()
