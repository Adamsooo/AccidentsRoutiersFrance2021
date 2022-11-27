from dash import Dash, html, dcc 
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#Instancier le dash 
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

#Incorporer le dataset
##Scrapping des jeux de données
adresse_web_carateristiques = "https://www.data.gouv.fr/fr/datasets/r/85cfdc0c-23e4-4674-9bcd-79a970d7269b"
adresse_web_lieux = "https://www.data.gouv.fr/fr/datasets/r/8a4935aa-38cd-43af-bf10-0209d6d17434"
adresse_web_usagers = "https://www.data.gouv.fr/fr/datasets/r/ba5a1956-7e82-41b7-a602-89d7dd484d7a"
adresse_web_vehicules = "https://www.data.gouv.fr/fr/datasets/r/0bb5953a-25d8-46f8-8c25-b5c2f5ba905e"

##Fichier Carasteristiques
carasteristiquesCSV=pd.read_csv(adresse_web_carateristiques, sep=";")
carasteristiquesCSV= carasteristiquesCSV.drop(['jour', 'mois', 'an', 'hrmn','dep', 'com', 'agg',
       'int', 'atm', 'col'], axis=1)
##Fichier Usagers
usagersCSV=pd.read_csv(adresse_web_usagers, sep=';')
usagersCSV=usagersCSV.drop(['place',
        'trajet', 'secu1', 'secu2', 'secu3', 'locp', 'actp',      
        'etatp'], axis = 1)
usagersCSV=usagersCSV.dropna(axis=0)
usagersCSV=usagersCSV[usagersCSV['sexe']>0]

##Production du dataset Carasteristiques X Usagers['grav']
carasteristiquesCSV['adr'] = usagersCSV['grav']
carasteristiquesCSV.columns = ['Num_Acc', 'luminosite', 'gravite', 'lat', 'long']

#Transformer les coordonnées en float
liste_latitude = list(carasteristiquesCSV['lat'])
liste_longitude = list(carasteristiquesCSV['long'])

for pos_latitudes in range (len(liste_latitude)):
    liste_latitude[pos_latitudes] = str(liste_latitude[pos_latitudes]).replace(",",".")
    liste_latitude[pos_latitudes] = float(liste_latitude[pos_latitudes])
for pos_longitudes in range (len(liste_longitude)):
    liste_longitude[pos_longitudes] = str(liste_longitude[pos_longitudes]).replace(",",".")
    liste_longitude[pos_longitudes] = float(liste_longitude[pos_longitudes])

liste_latitude = pd.Series(liste_latitude)
liste_longitude = pd.Series(liste_longitude)
carasteristiquesCSV['lat'] = liste_latitude
carasteristiquesCSV['long'] = liste_longitude



#Construction du scatter
scat_fig = px.scatter_mapbox(
    carasteristiquesCSV,
    mapbox_style="open-street-map",
    lat=carasteristiquesCSV['lat'],
    lon=carasteristiquesCSV['long'],
    center={
        'lat':float('46.539758'),
        'lon':float('2.430331')},
    color='gravite',
    color_continuous_scale='peach',
    zoom=4
)

#Construction des histogrammes 
histo_fig1 = px.bar(
    x=list(carasteristiquesCSV['luminosite'].value_counts().keys()),
    y=carasteristiquesCSV['luminosite'].value_counts().values,
    title="Nombre d'accidents en fonction de la luminosite du lieux"
)
histo_fig2 = px.bar(
    x=list(usagersCSV['sexe'].value_counts().keys()),
    y=usagersCSV['sexe'].value_counts().values,
    title="Nombres d'accidents selon les hommes et les femmes"
)

#Le Dash à afficher
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Projet DSIA-4201A", style={"textAlign": 'left'}),
        ], width=8)
    ]),
    dbc.Row([
        dbc.Col([
            html.H2("Géographie des accidents routiers - France 2021", style={"textAlign": 'left'}),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='scatFig',
                figure=scat_fig
            )
        ], width=8),
        dbc.Col([
            dcc.Graph(
                id='histoFig',
                figure=histo_fig2
            )
        ], width=4)
    ])
])

#Run le dash
if __name__ == '__main__':
    app.run_server(debug=True)
