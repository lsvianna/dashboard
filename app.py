import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import preprocessamento

# Ler o arquivo de pluviometria e ajustar o dataframe
pluvio = pd.read_csv('pluvio_out.csv',
                     parse_dates=[0],
                     date_format='%d/%m/%Y-%H:%M:%S')
pluvio_dia = pluvio.resample('1D', on='Data').sum()
pluvio_blumenau = pluvio_dia.iloc[:, -1:]
pluvio_estacoes = pluvio_dia.iloc[:, :-1]

# Ler o arquivo com tweets e ajustar o dataframe
tweets = pd.read_csv('tweets_out.csv',
                     parse_dates=[1],
                     date_format='%Y-%m-%d %H:%M:%S')
tweets.drop_duplicates(subset=['id'], inplace=True, keep='last')
tweets.reset_index(inplace=True, drop=True)
tweets['data'] = tweets['data'].dt.date
tweets['texto'] = tweets['texto'].apply(preprocessamento.text_cleaning)
tags = preprocessamento.tags
tweets_dia = tweets.groupby('data')['texto'].apply(preprocessamento.conta_palavras, tags=tags)

# Ler o arquivo com as probabilidades
prob_dia = pd.read_csv('probabilidade.csv', index_col=0)
prob = f'{round(prob_dia.iloc[-1, -1] * 100, 2)}%'

# Construção dos gráficos
figura1 = px.line(pluvio_blumenau)
figura1.update_layout(title='Índice Pluviométrico Médio de Blumenau',
                      yaxis_title='',
                      xaxis_title='',
                      template='plotly_dark',
                      showlegend=False)

figura3 = px.line(pluvio_blumenau)
figura3.add_bar(x=tweets_dia.index,
                y=tweets_dia.values,
                name='Tweets por dia')
figura3.update_layout(title='Incidência de tags nos tweets por dia',
                      yaxis_title='',
                      xaxis_title='',
                      template='plotly_dark')
figura3.update_legends(title='')

graf1 = go.Bar(x=prob_dia.index,
               y=prob_dia.values.flatten(),
               name='Probabilidade dos Tweets',
               yaxis='y1',
               opacity=0.5)
graf2 = go.Scatter(x=pluvio_blumenau.index,
                   y=pluvio_blumenau.values.flatten(),
                   name='Índice Pluviométrico',
                   yaxis='y2')
layout = go.Layout(title='Probabilidade de Tweets sobre Enchente',
                   yaxis1=dict(title='Probabilidade', side='left'),
                   yaxis2=dict(title='Índice Pluviométrico', side='right', overlaying='y', showgrid=False),
                   template='plotly_dark')
figura4 = go.Figure(data=[graf1, graf2], layout=layout)

#Inicialização da aplicação

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.CYBORG])

#Layout do dashboard

app.layout = dbc.Container([

    dbc.Row([

        dbc.Col([

            html.H2('Monitoramento de Enchente em Blumenau',
                    className='text-center text-primary'),
            html.H3('Previsão através de monitoramento de tweets',
                    className='text-center text-primary'),
            html.Br()

        ])

    ]),

    dbc.Row([

        dbc.Col([
            
            dcc.Graph(figure=figura1)

        ])

    ]),

    dbc.Row([

        dbc.Col([

            dcc.Dropdown(id='menu', value=pluvio_estacoes.columns,
                         options={x:x for x in pluvio_estacoes.columns},
                         multi=True,
                         style={'background-color': '#111111'}),
            dcc.Graph(id='grafico')

        ], width=6),

        dbc.Col([

            dcc.Graph(figure=figura3)

        ], width=6)

    ], class_name='g-0'),

    dbc.Row([

        dbc.Col([

            dcc.Graph(figure=figura4)

        ])

    ])

])

# Callbacks
@app.callback(
    Output('grafico', 'figure'),
    Input('menu', 'value')
)
def funcao(estacoes):
    data_fig = pluvio_estacoes[estacoes]
    fig = px.line(data_fig)
    fig.update_layout(title='Índice Pluviométrico por Estação',
                      yaxis_title='',
                      xaxis_title='',
                      template='plotly_dark',
                      showlegend=False)
    return fig

# Execução da aplicação
if __name__ == '__main__':
    app.run_server(debug=True)