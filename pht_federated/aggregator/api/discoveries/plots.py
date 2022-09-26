import plotly.express as px
import plotly.io
from plotly.graph_objects import Figure
import pandas as pd
import plotly.graph_objects as go


def plot_figure_json(fig_data: dict):
    plotly.io.show(fig_data)


def create_dot_plot(json_data: dict) -> Figure:
    """
    Creates dot plot from numerical data aggregated during discovery summary
    :param json_data: dict containing the numerical discovery summary data
    :return: plotly Figure object
    """
    feature_name = [json_data['title']]
    mean = [json_data['mean']]
    std_plus = [json_data['mean'] + json_data['std']]
    std_minus = [json_data['mean'] - json_data['std']]
    min_value = [json_data['min']]
    max_value = [json_data['max']]

    trace_mean = go.Scatter(
        x=feature_name,
        y=mean,
        marker=dict(color="blue", size=12),
        mode='markers',
        name="Mean"
    )
    trace_std_plus = go.Scatter(
        x=feature_name,
        y=std_plus,
        marker=dict(color="red", size=12),
        mode='markers',
        name="Standard Deivation"
    )
    trace_std_minus = go.Scatter(
        x=feature_name,
        y=std_minus,
        marker=dict(color="red", size=12),
        mode='markers',
        name="Standard Deviation -",
        showlegend=False
    )
    trace_min = go.Scatter(
        x=feature_name,
        y=min_value,
        marker=dict(color="green", size=12),
        mode='markers',
        name="Min-Value"
    )
    trace_max = go.Scatter(
        x=feature_name,
        y=max_value,
        marker=dict(color="green", size=12),
        mode='markers',
        name="Max-Value"
    )

    data = [trace_mean, trace_std_plus, trace_std_minus, trace_min, trace_max]
    layout = go.Layout(
        title=f'Dot-Plot over Discovery Results of Numerical Feature : "{feature_name[0]}"',
        xaxis_title="Feature Name",
        yaxis_title="Value"
    )
    fig = go.Figure(data=data, layout=layout)

    return fig


def create_barplot(json_data: dict) -> Figure:
    """
    Creates bar plot from categorical data aggregated during discovery summary
    :param json_data: dict containing the categorical discovery summary data
    :return: plotly Figure object
    """
    value_counts = json_data['value_counts']
    feature_title = json_data['title']
    names_col = ["Value", "Count"]
    dat = value_counts.items()
    plot_df = pd.DataFrame(data=dat, columns=names_col)

    bar = px.bar(plot_df, x='Count', y='Value', title=f'Value Counts of Categorical Feature : "{feature_title}"',
                 color=dat)

    return bar
