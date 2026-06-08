from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Journal-ready formatting
sns.set_theme(style='whitegrid', font='serif', rc={
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9,
    'figure.titlesize': 15,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

OUTPUT_DIR = Path('plots')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_PATH = Path('results.csv')

if not RESULTS_PATH.exists():
    raise FileNotFoundError('results.csv not found. Please run z_search_algo.py first to generate the benchmark results.')

print(f'Reading benchmark results from {RESULTS_PATH}')
df = pd.read_csv(RESULTS_PATH)

if 'Path_Risk_Score' in df.columns:
    df['Path_Risk'] = df['Path_Risk_Score']
elif 'Path_Risk' not in df.columns:
    df['Path_Risk'] = df['Path_Length'].astype(float)

if 'Success' in df.columns:
    df['Success'] = df['Success'].astype(int)
else:
    df['Success'] = 1

if 'Time_ms' not in df.columns:
    raise ValueError('results.csv must contain Time_ms column.')

# Keep only successful trajectories for aggregated performance metrics

df_valid = df[df['Success'] == 1].copy()

summary = (
    df_valid.groupby('Algorithm')
    .agg(
        Mean_Path=('Path_Length', 'mean'),
        Mean_Visited=('Visited', 'mean'),
        Mean_Time=('Time_ms', 'mean'),
        Mean_Risk=('Path_Risk', 'mean'),
        Success_Rate=('Success', 'mean'),
    )
    .reset_index()
)

algo_order = [
    'A*', 'Dijkstra', 'BFS', 'DFS', 'Greedy', 'Weighted A*',
    'Chance-Constrained A*', 'CVaR A*',
    'Risk-Penalized A*', 'Risk-Penalized Dijkstra', 'Risk-Penalized Greedy', 'ZEN'
]
summary['Algorithm'] = pd.Categorical(summary['Algorithm'], categories=algo_order, ordered=True)
summary = summary.sort_values('Algorithm').reset_index(drop=True)

if 'A*' in summary['Algorithm'].values:
    base = summary[summary['Algorithm'] == 'A*'].iloc[0]
    summary['Path_Ratio_vs_A*'] = summary['Mean_Path'] / base['Mean_Path']
    summary['Risk_Ratio_vs_A*'] = summary['Mean_Risk'] / base['Mean_Risk']
else:
    summary['Path_Ratio_vs_A*'] = 1.0
    summary['Risk_Ratio_vs_A*'] = 1.0

print('Summary metrics:')
print(summary[['Algorithm', 'Mean_Path', 'Mean_Visited', 'Mean_Time', 'Mean_Risk', 'Success_Rate']])


def normalize_lower_is_better(series):
    if series.max() == series.min():
        return pd.Series(1.0, index=series.index)
    return 1.0 - (series - series.min()) / (series.max() - series.min())

summary['Score_Time'] = normalize_lower_is_better(summary['Mean_Time'])
summary['Score_Risk'] = normalize_lower_is_better(summary['Mean_Risk'])
summary['Score_Visited'] = normalize_lower_is_better(summary['Mean_Visited'])
summary['Score_Path'] = normalize_lower_is_better(summary['Mean_Path'])
summary['Score_Success'] = summary['Success_Rate']
summary['Overall_Score'] = summary[
    ['Score_Time', 'Score_Risk', 'Score_Visited', 'Score_Path', 'Score_Success']
].mean(axis=1)
summary['Rank'] = summary['Overall_Score'].rank(ascending=False, method='dense').astype(int)

ranked_summary = summary.sort_values('Overall_Score', ascending=False).reset_index(drop=True)
print('\nOverall ranking:')
print(ranked_summary[['Rank', 'Algorithm', 'Overall_Score']])

ordered_summary = summary.dropna(subset=['Algorithm']).copy()

palette = sns.color_palette('tab10', n_colors=len(ordered_summary))
color_map = dict(zip(ordered_summary['Algorithm'], palette))


def save(fig, name):
    path = OUTPUT_DIR / name
    fig.savefig(path, format='pdf')
    print(f'Saved {path}')


# FIGURE 1: Time vs. Risk tradeoff
fig, ax = plt.subplots(figsize=(10, 8))
for algo in ordered_summary['Algorithm']:
    row = ordered_summary[ordered_summary['Algorithm'] == algo].iloc[0]
    ax.scatter(
        row['Mean_Time'], row['Mean_Risk'],
        s=220, color=color_map[algo], edgecolor='k', linewidth=0.9, alpha=0.92, zorder=5
    )
    ax.annotate(
        algo,
        (row['Mean_Time'], row['Mean_Risk']),
        xytext=(8, 6),
        textcoords='offset points',
        fontsize=10,
        weight='bold',
        bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.75)
    )
ax.set_xlabel('Mean Planning Time (ms)')
ax.set_ylabel('Mean Cumulative Path Risk')
ax.set_title('Risk-Time Tradeoff Across Risk-Aware Planners')
ax.set_xscale('log')
ax.grid(True, alpha=0.35, linestyle='--', which='both')
ax.set_axisbelow(True)
ax.set_xlim(left=max(0.1, ordered_summary['Mean_Time'].min() * 0.8), right=ordered_summary['Mean_Time'].max() * 1.4)
ax.set_ylim(bottom=max(0, ordered_summary['Mean_Risk'].min() * 0.9), top=ordered_summary['Mean_Risk'].max() * 1.08)
save(fig, 'fig_tradeoff_risk_time.pdf')
plt.close(fig)

# FIGURE 1B: Overall composite ranking across all metrics
fig, ax = plt.subplots(figsize=(10, 6))
bar_colors = [color_map[algo] if algo in color_map else '#7f7f7f' for algo in ranked_summary['Algorithm']]
ax.barh(ranked_summary['Algorithm'], ranked_summary['Overall_Score'], color=bar_colors, edgecolor='k')
ax.invert_yaxis()
for idx, row in ranked_summary.head(3).iterrows():
    ax.text(row['Overall_Score'] + 0.01, idx + 1, f"{row['Rank']}. {row['Algorithm']}",
            va='center', fontweight='bold', color='black')
ax.set_xlabel('Composite Score (higher is better)')
ax.set_title('Overall Algorithm Ranking: Time, Risk, Path Optimality, Search Cost, Success')
ax.set_xlim(0, 1.05)
ax.grid(axis='x', alpha=0.2)
save(fig, 'fig_overall_ranking.pdf')
plt.close(fig)

# FIGURE 2: Mean search size and risk profile
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
axes[0].bar(ordered_summary['Algorithm'], ordered_summary['Mean_Visited'], color=list(color_map.values()), edgecolor='k')
axes[0].set_ylabel('Mean Visited Nodes')
axes[0].set_title('Search Space Effort')
axes[0].tick_params(axis='x', rotation=45)

axes[1].bar(ordered_summary['Algorithm'], ordered_summary['Mean_Risk'], color=list(color_map.values()), edgecolor='k')
axes[1].set_ylabel('Mean Risk Score')
axes[1].set_title('Average Path Risk')
axes[1].tick_params(axis='x', rotation=45)

plt.suptitle('Benchmark Comparison: Search Overhead and Safety Risk')
save(fig, 'fig_metrics_bars.pdf')
plt.close(fig)

# FIGURE 3: Success rate and path efficiency
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
axes[0].bar(ordered_summary['Algorithm'], ordered_summary['Success_Rate'], color='#5a9bd5', edgecolor='k')
axes[0].set_ylim(0, 1.05)
axes[0].set_ylabel('Success Rate')
axes[0].set_title('Solution Reliability')
axes[0].tick_params(axis='x', rotation=45)

axes[1].bar(ordered_summary['Algorithm'], ordered_summary['Path_Ratio_vs_A*'], color='#ed7d31', edgecolor='k')
axes[1].set_ylabel('Mean Path Length / A*')
axes[1].set_title('Path Optimality Relative to A*')
axes[1].tick_params(axis='x', rotation=45)
axes[1].axhline(1.0, color='gray', linestyle='--', linewidth=1)

plt.suptitle('Reliability and Optimality Comparisons')
save(fig, 'fig_success_path_efficiency.pdf')
plt.close(fig)

# FIGURE 4: Risk distribution across successful runs
plot_algos = ordered_summary['Algorithm'].tolist()
box_data = df_valid[df_valid['Algorithm'].isin(plot_algos)].copy()
fig, ax = plt.subplots(figsize=(10, 6))

box_samples = [box_data.loc[box_data['Algorithm'] == algo, 'Path_Risk'] for algo in plot_algos]
boxes = ax.boxplot(box_samples, patch_artist=True, widths=0.6, showfliers=False)
for patch, algo in zip(boxes['boxes'], plot_algos):
    patch.set_facecolor(color_map[algo])
    patch.set_edgecolor('k')
    patch.set_alpha(0.75)

ax.set_xticks(range(1, len(plot_algos) + 1))
ax.set_xticklabels(plot_algos, rotation=45, ha='right')
ax.set_xlabel('Algorithm')
ax.set_ylabel('Path Risk Distribution')
ax.set_title('Distribution of Cumulative Risk Across Successful Runs')
save(fig, 'fig_risk_distribution.pdf')
plt.close(fig)

print('\nAll publication-ready figures are stored in the plots/ directory.')
