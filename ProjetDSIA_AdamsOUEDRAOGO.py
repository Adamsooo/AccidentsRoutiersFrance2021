from dash import Dash, html, dcc 
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output

mapbox_access_token = 'pk.eyJ1IjoiYWRhbXNvb28iLCJhIjoiY2xpMXloOG40MGd2YjN2bHB3MmpkcTMxeiJ9.Tj9mGTrzrguRFcHvTLVk4A'

##Création de fonctions utiles 
def nettoyer_coordonnees(dataframe, colonne_latitude, colonne_longitude):
    dataframe[colonne_latitude] = dataframe[colonne_latitude].str.replace(",", ".").astype(float)
    dataframe[colonne_longitude] = dataframe[colonne_longitude].str.replace(",", ".").astype(float)


def creer_graphique_dispersion(dataframe):
    locations = [go.Scattermapbox(
        lat=dataframe['lat'],
        lon=dataframe['long'],
        mode='markers',
        hoverinfo = 'text',
        hovertext = dataframe['gravite'],
        marker=dict(
            color=dataframe['gravite'],
            colorscale='peach',
            cmin=1,  # Valeur minimale de l'échelle de couleur
            cmax=4  # Valeur maximale de l'échelle de couleur
        )
    )]

    fig_dispersion = {'data' : locations, 'layout': go.Layout(
        title="Géographie des accidents routiers - France 2021",
        #uirevision='uid',
        font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height  = 900,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            center=dict(lat=46.539758, lon=2.430331),
            zoom=5
    ))}
    return fig_dispersion


def creer_histogramme_luminosite(dataframe):
    fig_luminosite = px.bar(
        x=list(dataframe['luminosite'].value_counts().keys()),
        y=dataframe['luminosite'].value_counts().values,
        title="Nombre d'accidents en fonction de la luminosité du lieu"
    )
    fig_luminosite.update_layout(
    xaxis_title="Luminosité",
    yaxis_title="Nombre d'accidents",
    margin=dict(t=50, b=0, l=0, r=0),
    barmode='group',
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)',
    font=dict(color='white'),
    legend=dict(
        x=0.5,  
        y=1.1,
    )
    )
    return fig_luminosite

def creer_histogramme_sexe(dataframe):
    fig_sexe = px.bar(
        x=list(dataframe['sexe'].value_counts().keys()),
        y=dataframe['sexe'].value_counts().values,
        title="Nombre d'accidents selon les hommes et les femmes"
    )
    fig_sexe.update_layout(
    xaxis_title="Sexe",
    yaxis_title="Nombre d'accidents",
    barmode='group',
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)', 
    font=dict(color='white'),
    margin=dict(t=50, b=0, l=0, r=0),
    legend=dict(
        x=0.5,  
        y=1.1,
        )
    )
    return fig_sexe

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

adresse_web_caracteristiques = "https://www.data.gouv.fr/fr/datasets/r/85cfdc0c-23e4-4674-9bcd-79a970d7269b"
adresse_web_usagers = "https://www.data.gouv.fr/fr/datasets/r/ba5a1956-7e82-41b7-a602-89d7dd484d7a"

caracteristiques_df = pd.read_csv(adresse_web_caracteristiques, sep=";")
caracteristiques_df = caracteristiques_df.drop(['jour', 'mois', 'an', 'hrmn','dep', 'com', 'agg', 'int', 'atm', 'col'], axis=1)

usagers_df = pd.read_csv(adresse_web_usagers, sep=';')
usagers_df = usagers_df.drop(['place', 'trajet', 'secu1', 'secu2', 'secu3', 'locp', 'actp', 'etatp'], axis=1)
usagers_df = usagers_df.dropna(axis=0)
usagers_df = usagers_df[usagers_df['sexe'] > 0]

caracteristiques_df['adr'] = usagers_df['grav']
caracteristiques_df.columns = ['Num_Acc', 'luminosite', 'gravite', 'lat', 'long']
caracteristiques_df = caracteristiques_df[caracteristiques_df['gravite'] > 0]

nettoyer_coordonnees(caracteristiques_df, 'lat', 'long')

fig_dispersion = creer_graphique_dispersion(caracteristiques_df)
fig_luminosite = creer_histogramme_luminosite(caracteristiques_df)
fig_sexe = creer_histogramme_sexe(usagers_df)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Projet DSIA-4201A", style={"textAlign": 'left'}),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H2("Géographie des accidents routiers - France 2021", style={"textAlign": 'left'}),
        ])
    ]),
    #Graphique de points 
    dbc.Row([
        #dbc.Col([]),
        dbc.Col([
            html.Div([
                dcc.Graph(
                    id='graph_dispersion',
                    config={'displayModeBar': False, 'scrollZoom': True},
                    style={'padding-bottom': '0', 'padding-left': '0' }
                )
            ], style={'background': 'none'}),
        ])
    ]),
    dbc.Row([
        #Checklist
        dbc.Col([
            html.H4("Filtre par gravité", className="text-left"),
            dcc.Checklist(
                id='checklist_gravite',
                options=[{'label': 'Ordre '+str(int(e)), 'value': e} for e in sorted(caracteristiques_df['gravite'].unique())],
                value=[e for e in sorted(caracteristiques_df['gravite'].unique())],
                labelStyle={'display': 'block'},
                style={"display": "flex", "justify-content": "center", "align-items": "center"}
            )
        ], width = '2'),
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("Quelques graphiques", style={"textAlign": 'left'}),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='graph_luminosite',
                figure=fig_luminosite,
                config={'displayModeBar': False}
            )
        ], width=6),
        dbc.Col([
            dcc.Graph(
                id='graph_sexe',
                figure=fig_sexe,
                config={'displayModeBar': False}
            )
        ], width=6)
    ])
], fluid=True, style={'paddingLeft': '100px', 'paddingRight': '100px'})

@app.callback(
    Output(component_id='graph_dispersion', component_property='figure'),
    Input(component_id='checklist_gravite', component_property='value')
)
def update_affichage_graphe(gravite_choisie):


    if len(gravite_choisie)>0:
        print(len(gravite_choisie))
        caracteristiques_df_prime = caracteristiques_df[caracteristiques_df['gravite'].isin(gravite_choisie)]
        graphique_genere = creer_graphique_dispersion(caracteristiques_df_prime)
        return graphique_genere
    else:

        return fig_dispersion

if __name__ == '__main__':
    app.run_server(debug=True)
