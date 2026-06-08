import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    df = pd.read_csv("results.csv")
    os.makedirs("plots", exist_ok=True)
    sns.set_theme(style="whitegrid")

    # 1. Risk vs. Path Length (Scatter Plot)
    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=df, x="Path_Length", y="Path_Risk_Score", hue="Algorithm", alpha=0.7)
    plt.title("Risk vs. Path Length")
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "Risk_vs_PathLength.pdf"), format="pdf")
    plt.close()

    # 2. Runtime Scalability (Box Plot)
    plt.figure(figsize=(12, 6))
    ax = sns.boxplot(data=df, x="Algorithm", y="Time_ms")
    ax.set_yscale("log")
    plt.title("Runtime Scalability (Time in ms - Log Scale)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "Runtime_Scalability.pdf"), format="pdf")
    plt.close()

    # 3. Search Efficiency (Bar Chart)
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x="Algorithm", y="Visited", errorbar=('ci', 95), capsize=.1)
    plt.title("Search Efficiency (Nodes Visited)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "Search_Efficiency.pdf"), format="pdf")
    plt.close()
    
    print("Custom PDF plots generated successfully.")

if __name__ == "__main__":
    main()
