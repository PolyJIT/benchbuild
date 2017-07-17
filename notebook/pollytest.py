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
        sa.column('p'),
        sa.column('pv'),
        sa.column('pvu'),
        sa.column('pu')
    ]).\
    select_from(
        sa.func.pollytest_eval(
            sa.sql.bindparam('exp_ids'),
            sa.sql.bindparam('components')))
qry = QUERY_EVAL.unique_params(exp_ids=[uuid.UUID("6c9d1f23-d9ee-4744-88ea-243dcaa50cd4")],
                               components=["polly-scops"])
#%%
df = pd.read_sql_query(qry, session.bind)
print(df.head())

#%%
comps = df['variable'].unique()
print(comps)

layout = go.Layout(
    xaxis=dict(tickangle=-45),
    barmode='group'
)
traces = []
comp = 'Number of valid Scops'

data = df.loc[df.variable == comp]
traces.append(
        go.Bar(
            x = data["project"],
            y = data["p"],
            name="-polly"
        ))
traces.append(
        go.Bar(
            x = data["project"],
            y = data["pv"],
            name="-polly -polly-position=before-vectorizer"
        ))
traces.append(
        go.Bar(
            x = data["project"],
            y = data["pvu"],
            name="-polly -polly-position=before-vectorizer -polly-process-unprofitable"
        ))
traces.append(
        go.Bar(
            x = data["project"],
            y = data["pu"],
            name="-polly -polly-process-unprofitable"
        ))
#%%
layout = go.Layout(
    barmode='grouped',
    height=600,
    width=600,
    xaxis=dict(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=False,
        autotick=True,
        ticks='',
        showticklabels=False
    ),
    title=comp
)

from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

fig = go.Figure(data=traces, layout=layout)
init_notebook_mode()
iplot(fig, filename='grouped-bar.html')
print(__version__)
