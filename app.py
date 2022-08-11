%%capture
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
#from jupyter_dash import JupyterDash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')
markdown_text = "This is my text"
rel_gend2 = gss_clean.groupby(['sex'])\
.agg({'income':'mean', 'job_prestige':'mean', 'socioeconomic_index':'mean', 'education':'mean'}).reset_index()
rel_gend2 = round(rel_gend2,2).rename({'income':'Mean Income','job_prestige':'Mean Job Prestige Score',
                           'socioeconomic_index':'Mean Socioeconomic Index',
                          'education':'Mean Years of Education','sex':'Sex'},axis=1)
table = ff.create_table(rel_gend2)
gss_clean.male_breadwinner = gss_clean.male_breadwinner.astype('category')
gss_clean.male_breadwinner = gss_clean.male_breadwinner.cat.\
reorder_categories(["strongly agree","agree","disagree","strongly disagree"])
rel_gend2 = gss_clean.groupby(['male_breadwinner','sex']).size().reset_index()
rel_gend2 = rel_gend2.rename({0:'count'},axis=1)
fig = px.bar(rel_gend2, x='male_breadwinner', y='count', color='sex',
            labels={'male_breadwinner':'Opinion on Males as Breadwinners', 'count':'Count'},
            barmode = 'group')
fig.update_layout(showlegend=True)
fig2 = px.scatter(gss_clean, x='job_prestige', y='income', 
                 color = 'sex', 
                 trendline='ols',
                 height=600, width=600,
                 labels={'job_prestige':'Job Prestige Score', 
                        'income':'Personal Annual Income'},
                 hover_data=['education', 'socioeconomic_index'])
fig3 = px.box(gss_clean, x='income', y = 'sex', color='sex',
                   labels={'income':'Personal Annual Income', 'sex':'Sex'})
fig3.update_layout(showlegend=False)
fig4 = px.box(gss_clean, x='job_prestige', y = 'sex', color='sex',
                   labels={'job_prestige':'Job Prestige Index', 'sex':'Sex'})
fig4.update_layout(showlegend=False)
gss_new = pd.DataFrame(gss_clean[["income","sex","job_prestige"]])
gss_new["cat_job_prestige"] = pd.cut(gss_new.job_prestige, bins=6, labels=["Lowest Job Prestige",
                                                                           "Lower Job Prestige",
                                                                           "Low Job Prestige",
                                                                           "High Job Prestige",
                                                                           "Higher Job Prestige",
                                                                          "Highest Job Prestige"])
gss_new = gss_new.dropna()
gss_new = gss_new.sort_values("cat_job_prestige").reset_index()
fig_bar = px.box(gss_new, x='income', y='sex', color='sex', 
             facet_col='cat_job_prestige', facet_col_wrap=2,
            labels={'income':'Annual Personal Income', 'sex':'Sex'},
            width=1000, height=600,
            color_discrete_map = {'male':'blue', 'female':'red'})
fig_bar.update_layout(showlegend=False)
fig_bar.for_each_annotation(lambda a: a.update(text=a.text.replace("cat_job_prestige=", "")))
#html.H1("Opinion of Males as Breadwinners by Gender")
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1("Gender Disparities in Jobs and Income"),  
        
        dcc.Markdown(children = markdown_text),
        
        html.H2("Distribution of Wealth, Job Prestige, and Education by Gender"),
        
        dcc.Graph(figure=table),
        
        html.H2("Opinion of Males as Breadwinners by Gender"),
        
        dcc.Graph(figure=fig),
        
        html.H2("Personal Annual Income vs Job Prestige Score by Gender"),
        
        dcc.Graph(figure=fig2),
        
        html.H2("Distribution of Personal Annual Income by Sex"),
        
        dcc.Graph(figure=fig3),
        
        html.H2("Distribution of Job Prestige by Sex"),
        
        dcc.Graph(figure=fig4),
        
        html.H2("Distribution of Income by Different Job Prestige Levels and Gender"),
        
        dcc.Graph(figure=fig_bar)
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
