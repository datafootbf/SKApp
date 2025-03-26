#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random


# In[2]:


# Chargement du fichier
file_path = "SK_All.csv"

df = pd.read_csv(file_path, sep=",")


# In[3]:


# Nettoyage colonnes
df.columns = df.columns.str.strip()

# Suppression des colonnes non voulues (comme avant, si besoin)
columns_to_remove = [
    "Team ID", "Competition ID", "Season ID",
    "Count Performances (Physical Check passed)", 
    "Count Performances (Physical Check failed)",
    "TOP 3 Time to HSR", "TOP 3 Time to Sprint"
]
df = df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors="ignore")


# In[6]:


# Conversion birthdate → âge
df["Birthdate"] = pd.to_datetime(df["Birthdate"], errors="coerce").dt.strftime("%Y-%m-%d")
current_year = pd.Timestamp.now().year
df["Age"] = df["Birthdate"].apply(lambda x: current_year - int(x[:4]) if isinstance(x, str) else None)


# In[7]:


# Listes pour les filtres
position_list = sorted(df["Position Group"].dropna().unique().tolist())
competition_list = sorted(df["Competition"].dropna().unique().tolist())
player_list = sorted(df["Short Name"].dropna().unique().tolist())


# In[8]:


# On définit les colonnes pour le graphe
graph_columns = [
    "PSV-99", "TOP 5 PSV-99", "Distance P90", "M/min P90", "Running Distance P90",
    "HSR Distance P90", "HSR Count P90", "Sprint Distance P90", "Sprint Count P90",
    "HI Distance P90", "HI Count P90", "Medium Acceleration Count P90",
    "High Acceleration Count P90", "Medium Deceleration Count P90", "High Deceleration Count P90",
    "Explosive Acceleration to HSR Count P90", "Explosive Acceleration to Sprint Count P90"
]


# In[9]:


st.title("SkillCorner Viz - Streamlit")

# -- FILTRES dans la sidebar (ou en haut)
with st.sidebar:
    st.header("Filtres")
    selected_competitions = st.multiselect(
        "Compétitions",
        options=competition_list,
        default=[],
        help="Sélectionne une ou plusieurs compétitions"
    )
    selected_positions = st.multiselect(
        "Postes",
        options=position_list,
        default=[],
        help="Sélectionne un ou plusieurs postes"
    )
    
    age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
    selected_age = st.slider(
        "Âge",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max),
        step=1
    )
    
    # Joueur(s) ajouté(s)
    selected_extra_players = st.multiselect(
        "Joueur(s) ajouté(s)",
        options=player_list,
        default=[],
        help="Permet d'ajouter des joueurs particuliers, hors filtre"
    )

st.write("---")

st.subheader("Tableau filtré")

# -- Application des filtres
filtered_df = df.copy()
if selected_positions:
    filtered_df = filtered_df[filtered_df["Position Group"].isin(selected_positions)]
if selected_competitions:
    filtered_df = filtered_df[filtered_df["Competition"].isin(selected_competitions)]

# Filtrage sur l'âge
filtered_df = filtered_df[
    (filtered_df["Age"] >= selected_age[0]) &
    (filtered_df["Age"] <= selected_age[1])
]

# Ajout de joueurs "hors filtre"
if selected_extra_players:
    extra_df = df[df["Short Name"].isin(selected_extra_players)]
    filtered_df = pd.concat([filtered_df, extra_df]).drop_duplicates()

st.dataframe(filtered_df)

st.write("---")

############################
# 3. Sélection des axes + highlight
############################
st.subheader("Paramètres du Graphe")

# Sélection de l'axe X, Y
selected_xaxis = st.selectbox(
    "Axe X",
    options=graph_columns,
    index=0
)
selected_yaxis = st.selectbox(
    "Axe Y",
    options=graph_columns,
    index=1
)

# Récupérer les joueurs (Short Name) seulement depuis le dataframe filtré
filtered_players = sorted(filtered_df["Short Name"].dropna().unique())

# Choix des joueurs à surligner
highlight_players = st.multiselect(
    "Surligner Joueurs",
    options=filtered_players,  # au lieu de la liste globale
    default=[]
)

# Bouton ou direct ?

st.write("---")

############################
# 4. Création du Scatter Plot
############################
st.subheader("Graphique XY")

# Copy/Convert
plot_df = filtered_df.copy()

# Sécurité: vérifie colonnes
if (selected_xaxis not in plot_df.columns) or (selected_yaxis not in plot_df.columns):
    st.warning("Colonnes invalides pour le graphe.")
    st.stop()

# Convert numeric
plot_df[selected_xaxis] = pd.to_numeric(plot_df[selected_xaxis], errors='coerce')
plot_df[selected_yaxis] = pd.to_numeric(plot_df[selected_yaxis], errors='coerce')
plot_df = plot_df.dropna(subset=[selected_xaxis, selected_yaxis])

if plot_df.empty:
    st.info("Aucune donnée à afficher.")
    st.stop()

# Calcul du nombre total de points
nb_points_total = len(plot_df)
point_size = 10 if nb_points_total < 300 else 5

# -- GESTION DES ETIQUETTES (SAMPLING)
max_labels = 300
if nb_points_total > max_labels:
    label_df = plot_df.sample(n=max_labels, random_state=42)
else:
    label_df = plot_df

# -- On crée un champ "color" pour distinguer les joueurs à highlight
plot_df["color_marker"] = "blue"
if highlight_players:
    plot_df.loc[plot_df["Short Name"].isin(highlight_players), "color_marker"] = "yellow"

# Scatter principal (points)
fig = px.scatter(
    plot_df,
    x=selected_xaxis,
    y=selected_yaxis,
    hover_data=["Short Name", "Team", "Age"],
    color="color_marker",  # Utilise la colonne color_marker
    color_discrete_map={"blue":"blue", "yellow":"yellow"},
)
# Supprime la légende
fig.update_layout(showlegend=False)
# Force la taille
fig.update_traces(marker=dict(size=point_size))

# -- On gère maintenant l'échantillon qui aura les étiquettes
label_df = label_df.copy()
label_df["color_marker"] = plot_df["color_marker"]  # Récupère la couleur pour cohérence
label_df.loc[label_df.index, "color_marker"] = label_df["Short Name"].apply(
    lambda x: "yellow" if x in highlight_players else "blue"
)

fig_labels = px.scatter(
    label_df,
    x=selected_xaxis,
    y=selected_yaxis,
    text="Short Name",
    hover_data=["Short Name", "Team", "Age"],
    color="color_marker",
    color_discrete_map={"blue":"blue", "yellow":"yellow"}
)

# Position variable
possible_positions = [
    "top left", "top center", "top right",
    "middle left", "middle right",
    "bottom left", "bottom center", "bottom right"
]
text_positions = [random.choice(possible_positions) for _ in range(len(label_df))]

fig_labels.update_traces(
    textposition=text_positions,
    textfont=dict(size=9, color="black"),
    marker=dict(size=point_size+1),
    cliponaxis=False
)

# On fusionne la seconde trace dans fig
for trace in fig_labels.data:
    fig.add_trace(trace)

# Ajout lignes de moyennes
mean_x = plot_df[selected_xaxis].mean()
mean_y = plot_df[selected_yaxis].mean()

fig.add_vline(
    x=mean_x,
    line_dash="dash",
    line_color="dimgrey",
    line_width=2
)
fig.add_hline(
    y=mean_y,
    line_dash="dash",
    line_color="dimgrey",
    line_width=2
)

# Layout final
fig.update_layout(
    width=1200,
    height=700,
    plot_bgcolor="white",
    xaxis=dict(showgrid=True, gridcolor="gainsboro", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="gainsboro", zeroline=False)
)

st.plotly_chart(fig, use_container_width=False)

