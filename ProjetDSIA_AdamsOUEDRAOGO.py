#Essaie Encore

##Importations
from dash import Dash, html, dcc 
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output

##Token pour la carte géographique
mapbox_access_token = 'pk.eyJ1IjoiYWRhbXNvb28iLCJhIjoiY2xpMXloOG40MGd2YjN2bHB3MmpkcTMxeiJ9.Tj9mGTrzrguRFcHvTLVk4A'

##Création de fonctions utiles 
#Application des palettes couleurs aux points de la carte
def assign_color(gravite):
    if gravite == 1:
        return '#B68100'
    elif gravite == 2:
        return '#6C4516'
    elif gravite == 3:
        return '#FB0D0D'
    elif gravite == 4:
        return '#DA16FF'
    else:
        return None
#Conversion des coordonnées géographiques en nombres réels 
def nettoyer_coordonnees(dataframe, colonne_latitude, colonne_longitude):
    dataframe[colonne_latitude] = dataframe[colonne_latitude].str.replace(",", ".").astype(float)
    dataframe[colonne_longitude] = dataframe[colonne_longitude].str.replace(",", ".").astype(float)

#Création du graphes à points
def creer_graphique_dispersion(dataframe):
    locations = [go.Scattermapbox(
        lon=dataframe['long'],
        lat=dataframe['lat'],
        mode='markers',
        hoverinfo = 'text',
        hovertext = dataframe['gravite'],
        marker=dict(
            color=dataframe['couleur']
            # cmin=1,  
            # cmax=4
        )
    )]
    fig_dispersion = {'data' : locations, 'layout': go.Layout(
        uirevision='uid',
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

#Création histogramme du nombres d'accidents en fonction de la luminosité de l'endroit 
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

#Création histogramme du nombres d'accidents en fonction du sexe du chauffeur
def creer_histogramme_sexe(dataframe):
    fig_sexe = px.bar(
        x=list(dataframe['sexe'].value_counts().keys()),
        y=dataframe['sexe'].value_counts().values,
        title="Nombre d'accidents selon les hommes(1) et les femmes(2)"
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

##Scrapping et traitement des datasets 
adresse_web_carasteristiques = "https://www.data.gouv.fr/fr/datasets/r/85cfdc0c-23e4-4674-9bcd-79a970d7269b"
adresse_web_usagers = "https://www.data.gouv.fr/fr/datasets/r/ba5a1956-7e82-41b7-a602-89d7dd484d7a"

carasteristiques_df = pd.read_csv(adresse_web_carasteristiques, sep=";")
carasteristiques_df = carasteristiques_df.drop(['jour', 'mois', 'an', 'hrmn','dep', 'com', 'agg', 'int', 'atm', 'col'], axis=1)

usagers_df = pd.read_csv(adresse_web_usagers, sep=';')
usagers_df = usagers_df.drop(['place', 'trajet', 'secu1', 'secu2', 'secu3', 'locp', 'actp', 'etatp'], axis=1)
usagers_df = usagers_df.dropna(axis=0)
usagers_df = usagers_df[usagers_df['sexe'] > 0]

carasteristiques_df['adr'] = usagers_df['grav']
carasteristiques_df.columns = ['Num_Acc', 'luminosite', 'gravite', 'lat', 'long']
carasteristiques_df = carasteristiques_df[carasteristiques_df['gravite'] > 0]
carasteristiques_df['gravite'] = carasteristiques_df['gravite'].astype('int64')
carasteristiques_df = carasteristiques_df[carasteristiques_df['gravite'] > 0]
carasteristiques_df['couleur'] = carasteristiques_df['gravite'].map(assign_color)
nettoyer_coordonnees(carasteristiques_df, 'lat', 'long')


figure_dispersion = creer_graphique_dispersion(carasteristiques_df)
fig_luminosite = creer_histogramme_luminosite(carasteristiques_df)
fig_sexe = creer_histogramme_sexe(usagers_df)

#Création du tableau de bord 
app.layout = dbc.Container([
    #Première ligne du dashboard contenant le titre et le sous titre du sujet 
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
    dbc.Row([
        #Deuxième ligne comprenant une checkliste et un carte de dispersion des localisatiosn des accidents 
        dbc.Col([
            #La checkliste
            html.H4("Ordre de gravite des accidents"),
            dcc.Checklist(
                id='checklist_gravite',
                options = [
                    {
                        "label": html.Div(['1-Indemne'], style={'color': '#B68100', 'font-size':20}),
                        "value": 1
                    },
                    {
                        "label": html.Div(['2-Tué'], style={'color': '#6C4516', 'font-size': 20}),
                        "value": 2
                    },
                    {
                        "label": html.Div(['3-Blessé hospitalisé'], style={'color': '#FB0D0D', 'font-size': 20}),
                        "value": 3
                    },
                    {
                        "label": html.Div(['4-Blessé leger'], style={'color': '#DA16FF', 'font-size': 20}),
                        "value": 4
                    }
                ],
                value = [1, 2, 3, 4],
                labelStyle={"display": "flex", "align-items": "center"},
                #options=[{'label': 'Ordre '+str(e), 'value': e} for e in sorted(carasteristiques_df['gravite'].unique())],
                #value=[e for e in sorted(carasteristiques_df['gravite'].unique())],
                #labelStyle={'display': 'block'},
                #style={"display": "flex", "justify-content": "center", "align-items": "center"}
            )
        ],width = 3, align = 'left'),
        #La carte 
        dbc.Col([
            dcc.Graph(
                id='graph_dispersion',
                figure=figure_dispersion,
                config={'displayModeBar': False, 'scrollZoom': True},
                style={'padding-bottom': '0', 'padding-left': '0' }
            ),
            html.H4('Repartition géographique des lieux daccidents', style={"textAlign": 'center'}  )
        ],width =9, align = 'right')
        
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
])

@app.callback(
    Output('graph_dispersion','figure'),
    [Input('checklist_gravite','value')]
)

def update_affichage_graphe(gravite_choisie):
    caracteristiques_df_prime = carasteristiques_df[(carasteristiques_df['gravite'].isin(gravite_choisie))]
    graphique_genere = creer_graphique_dispersion(caracteristiques_df_prime)    
    return graphique_genere

if __name__ == '__main__':
    app.run_server(debug=True)
