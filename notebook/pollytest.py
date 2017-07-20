#%%
import uuid
import benchbuild.settings as settings
import benchbuild.utils.schema as schema
import pandas as pd
import sqlalchemy as sa
import plotly
import plotly.graph_objs as go

settings.CFG.load(".benchbuild.yml")
session = schema.Session()
QUERY_EVAL = \
    sa.sql.select([
        sa.column('project'),
        sa.column('variable'),
        sa.column('metric'),
        sa.column('value')
    ]).\
    select_from(
        sa.func.pollytest_eval_melted(
            sa.sql.bindparam('exp_ids'),
            sa.sql.bindparam('components')))
qry = QUERY_EVAL.unique_params(exp_ids=[uuid.UUID("6c9d1f23-d9ee-4744-88ea-243dcaa50cd4")],
                               components=["polly-scops"])
#%%
df = pd.read_sql_query(qry, session.bind)
print(df.head())

#%%
configs = df['variable'].unique()
print(configs)
metrics = df['metric'].unique()
print(metrics)

#%%
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

cfg_rename = {
    '-O3 -polly': 'P',
    '-O3 -polly -polly-position=before-vectorizer': 'PV',
    '-O3 -polly -polly-position=before-vectorizer -polly-process-unprofitable': 'PVU',
    '-O3 -polly -polly-process-unprofitable': 'PU',
}

def get_metric_data(metric, all_data):
    return all_data.loc[all_data.metric == metric]

def generate_traces(data, configs):
    traces = []
    for config in configs:
        cfg_data = data.loc[data.variable == config]
        traces.append(
                go.Bar(
                    x = cfg_data["project"],
                    y = cfg_data["value"],
                    name = cfg_rename[config]
                ))
    return traces

def generate_group_plot(title, traces):
    layout = go.Layout(
        barmode='grouped',
        height=800,
        width=800,
        xaxis=dict(
            autorange=True,
            showgrid=False,
            zeroline=False,
            showline=False,
            autotick=True,
            showticklabels=True
        ),
        yaxis=dict(
            zeroline=True,
            showline=True,
            autorange=True
        ),
        title=title,
        legend=dict(x=-.1, y=1.2)
    )
    fig = go.Figure(data=traces, layout=layout)
    plot(fig, filename="gp-{}".format(title).replace(' ', '_'))

init_notebook_mode()
for metric in metrics:
    m_data = get_metric_data(metric, df)
    traces = generate_traces(m_data, configs)
    generate_group_plot(metric, traces)
    print("Writing %s" % metric + ".png")
