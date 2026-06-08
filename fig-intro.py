import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def draw_box(ax, x, y, width, height, text, fontsize=9, facecolor='white'):
    rect = plt.Rectangle((x, y), width, height, linewidth=1.5, edgecolor='black', facecolor=facecolor, zorder=1)
    ax.add_patch(rect)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center', fontsize=fontsize, zorder=2)

def draw_arrow(ax, start, end):
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.5, color='black'))

def main():
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')

    bw, bh = 8.0, 0.8
    x_center = (10 - bw) / 2

    # Row 1: Records identified
    y1 = 10.5
    draw_box(ax, x_center, y1, bw, bh, "Records identified from databases (n = 1847)\nScopus, Web of Science, IEEE Xplore, ACM, Springer, ScienceDirect", fontsize=9)

    draw_arrow(ax, (5, y1), (5, y1 - 0.5))

    # Row 2: Duplicates removed
    y2 = 9.2
    draw_box(ax, x_center, y2, bw, bh, "Duplicates removed (n = 312)", facecolor='lightgray')

    draw_arrow(ax, (5, y2), (5, y2 - 0.5))

    # Row 3: Records screened
    y3 = 7.9
    draw_box(ax, x_center, y3, bw, bh, "Records screened (title/abstract) (n = 838)", facecolor='lightgray')

    draw_arrow(ax, (x_center, y3 + bh/2), (x_center - 1.5, y3 + bh/2))
    draw_box(ax, x_center - 3.5, y3 - 0.2, 2.5, bh, "Records excluded (n = 484)\nNot relevant to RQs", fontsize=8)

    draw_arrow(ax, (5, y3), (5, y3 - 0.5))

    # Row 4: Full-text assessed
    y4 = 6.6
    draw_box(ax, x_center, y4, bw, bh, "Full-text articles assessed for eligibility (n = 697)", facecolor='lightgray')

    draw_arrow(ax, (x_center, y4 + bh/2), (x_center - 1.5, y4 + bh/2))
    draw_box(ax, x_center - 3.5, y4 - 0.2, 2.5, bh, "Full-text excluded (n = 456)\nNo novel algorithm,\nno grid benchmark,\nnot peer-reviewed", fontsize=8)

    draw_arrow(ax, (5, y4), (5, y4 - 0.5))

    # Row 5: Studies included
    y5 = 5.3
    draw_box(ax, x_center, y5, bw, bh, "Studies included in review (n = 241)", facecolor='lightgreen', fontsize=10)

    # Backward snowballing
    y6 = 3.8
    draw_arrow(ax, (5, y5), (5, y5 - 0.5))
    draw_box(ax, x_center, y6, bw, bh, "Additional records from backward\nsnowballing on key papers (n = 31)", fontsize=9)
    draw_arrow(ax, (5, y6), (5, y6 - 0.5))
    draw_box(ax, x_center, y6 - 1.0, bw, bh, "Total unique studies included (n = 272)\n(241 from database + 31 from snowballing)", facecolor='lightblue', fontsize=10)

    ax.text(5, 11.8, "PRISMA 2020 Flow Diagram", ha='center', va='center', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig('prisma-flow.pdf', dpi=300, bbox_inches='tight')
    plt.show()
    print("PRISMA flow diagram saved as prisma-flow.pdf")

if __name__ == "__main__":
    main()