import polars as pl
import matplotlib

from ai_engineer.applications.data_analytics_agent.application.processing_data import load_and_prepare_data
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def draw_pie_chart(
    df: pl.DataFrame,
    date_column: str = None,
    pie_chart_elements: dict = None,
    pie_chart_title: str = None,
    set_legend: bool = False,
):
    if not pie_chart_elements:
        return None, ""

    column_names = list(pie_chart_elements.keys())
    labels = list(pie_chart_elements.values())

    element_lists = {}
    for col in column_names:
        element_lists[col] = df[col].to_list()

    date_list = []
    if date_column:
        date_list = df[date_column].to_list()

    n_dates = max(1, len(date_list)) if date_list else 1

    data_preview = []

    legend_rows = 1 if set_legend else 0
    fig, axes = plt.subplots(1, n_dates, figsize=(10 * n_dates, 6+ legend_rows *0.1)) #Update here to change background size
    if n_dates == 1:
        axes = [axes]

    n_elements = len(column_names)
    cmap = plt.get_cmap("tab10")
    colors = [cmap(i % 10) for i in range(n_elements)]

    def _autopct(pct, allvals):
        absolute = int(round(pct / 100.0 * sum(allvals)))
        if absolute >= 1_000_000_000:
            val_str = f'{absolute/1_000_000_000:.1f}B'
        elif absolute >= 1_000_000:
            val_str = f'{absolute/1_000_000:.1f}M'
        elif absolute >= 1_000:
            val_str = f'{absolute/1_000:.1f}K'
        else:
            val_str = f'{absolute}'
        return f'{pct:.1f}%\n({val_str})'

    wedges_ref = None
    for i in range(n_dates):
        sizes = [element_lists[col][i] for col in column_names]

        wedges, texts, autotexts = axes[i].pie(
            sizes,
            labels=None,
            startangle=90,
            colors=colors,
            wedgeprops={'edgecolor': 'white'},
            radius=1.05,
            autopct=lambda pct: _autopct(pct, sizes),
            pctdistance=0.75,
            textprops={'fontsize': 9},
        )
        for autotext in autotexts:
            autotext.set_fontweight('bold')
            autotext.set_color('white')

        if i == 0:
            wedges_ref = wedges

        if date_list and pie_chart_title:
            axes[i].set_title(
                f'{pie_chart_title} {date_list[i]}', fontsize=18, fontweight='bold', pad=15
            )
        elif date_list:
            axes[i].set_title(
                f'Ngày {date_list[i]}', fontsize=14, pad=15
            )
        elif pie_chart_title:
            axes[i].set_title(
                pie_chart_title, fontsize=14, pad=15
            )

    if set_legend and wedges_ref:
        ncols_legend = min(n_elements, 3)
        fig.legend(
            wedges_ref,
            labels,
            title='Chú thích',
            loc='lower center',
            bbox_to_anchor=(0.5, 0.12),
            ncol=ncols_legend,
            fontsize=10,
            title_fontsize=11,
            frameon=False,
            borderaxespad=0.2,
        )
        bottom_pad = 0.14
    else:
        bottom_pad = 0.05

    plt.subplots_adjust(left=0.03, right=0.97, top=0.9, bottom=bottom_pad, wspace=0.1)

    text_output = "\n".join(data_preview)
    return fig, text_output
            
bctc_url = "/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/data_analytics_agent/resources/vnm/bcdkt.json"
columns = ["ngay", "tai_san_ngan_han", "tai_san_dai_han"]

df = load_and_prepare_data(bctc_url, columns)

fig, text = draw_pie_chart(
    df=df,
    date_column="ngay",
    pie_chart_elements={
        "tai_san_ngan_han": "Tài sản ngắn hạn",
        "tai_san_dai_han": "Tài sản dài hạn",
    },
    pie_chart_title="Cơ cấu tài sản ngày",
)
