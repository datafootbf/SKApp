#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random
import re
import plotly.graph_objects as go

# In[2]:

# Helper pour raccourcir uniquement les saisons "YYYY/YYYY" -> "YY/YY"
def shorten_season(s):
    s = str(s)
    # ne traite que le format 4 chiffres / 4 chiffres
    if re.match(r'^\d{4}/\d{4}$', s):
        y1, y2 = s.split('/')
        return f"{y1[-2:]}/{y2[-2:]}"
    # tout autre format reste identique
    return s


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
    "TOP 3 Time to HSR", "TOP 3 Time to Sprint", "Player ID"
]
df = df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors="ignore")


# In[6]:


# Conversion birthdate → âge
df["Birthdate"] = pd.to_datetime(df["Birthdate"], errors="coerce").dt.strftime("%Y-%m-%d")
current_year = pd.Timestamp.now().year
df["Age"] = df["Birthdate"].apply(lambda x: current_year - int(x[:4]) if isinstance(x, str) else None)


# In[7]:


# Listes pour les filtres
season_list = sorted(df["Season"].dropna().unique().tolist())
position_list = sorted(df["Position Group"].dropna().unique().tolist())
competition_list = sorted(df["Competition"].dropna().unique().tolist())
player_list = sorted(df["Short Name"].dropna().unique().tolist())

# In[8]:


# On définit les colonnes pour le graphe
graph_columns = [
    "PSV-99", "TOP 5 PSV-99", "Total Distance P90", "M/min P90", "Running Distance P90",
    "HSR Distance P90", "HSR Count P90", "Sprinting Distance P90", "Sprint Count P90",
    "HI Distance P90", "HI Count P90", "Medium Acceleration Count P90",
    "High Acceleration Count P90", "Medium Deceleration Count P90", "High Deceleration Count P90",
    "Explosive Acceleration to HSR Count P90", "Explosive Acceleration to Sprint Count P90", "xPhysical"
]


# === Sélecteur de page dans la sidebar ===
page = st.sidebar.radio(
    "Choisir le volet",
    ["Visualisation", "xPhysical"]
)

if page == "Visualisation":
    st.title("SkillCorner Viz - Streamlit")
    with st.sidebar:
        st.header("Filtres")
        selected_seasons = st.multiselect(
            "Saisons",
            options=season_list,
            default=[],
            help="Sélectionne une ou plusieurs saisons"
        )
        
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
    if selected_seasons:
        filtered_df = filtered_df[filtered_df["Season"].isin(selected_seasons)]
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
    
    # Supprime la colonne index importée en trop, si elle existe
    display_df = filtered_df.drop(columns=["Unnamed: 0"], errors="ignore")
    st.dataframe(display_df)
    
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
    
    # Récupérer les joueurs filtrés
    filtered_players = sorted(filtered_df["Short Name"].dropna().unique())
    team_list = sorted(filtered_df["Team"].dropna().unique())
    
    # On positionne les deux filtres sur la même ligne
    col1, col2 = st.columns(2)
    
    with col1:
        highlight_players = st.multiselect(
            "Surligner Joueurs",
            options=filtered_players,
            default=[]
        )
    
    with col2:
        highlight_teams = st.multiselect(
            "Surligner Équipe",
            options=team_list,
            default=[]
        )
    
    st.write("---")
    
    ############################
    # 4. Création du Scatter Plot
    ############################
    st.subheader("Graphique XY")
    
    # Copy/Convert
    plot_df = filtered_df.copy()
    # Ajout de la saison courte et du label complet
    plot_df["season_short"] = plot_df["Season"].apply(shorten_season)
    plot_df["Player_Label"] = plot_df["Short Name"] + " " + plot_df["season_short"]
    
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
    label_df["color_marker"] = "blue"  # initialise aussi pour les labels
    
    # 1) Surlignage joueurs en jaune
    if highlight_players:
        mask_p = plot_df["Short Name"].isin(highlight_players)
        plot_df.loc[mask_p, "color_marker"] = "yellow"
        label_df.loc[mask_p, "color_marker"] = "yellow"
    
    # 2) Surlignage équipes en rouge
    if highlight_teams:
        mask_t = plot_df["Team"].isin(highlight_teams)
        plot_df.loc[mask_t, "color_marker"] = "red"
        label_df.loc[mask_t, "color_marker"] = "red"
    
    # Scatter principal (points) avec Player_Label
    fig = px.scatter(
        plot_df,
        x=selected_xaxis,
        y=selected_yaxis,
        hover_name="Player_Label",
        hover_data=["Team", "Age", "Position Group"],
        color="color_marker",  # Utilise la colonne color_marker
        color_discrete_map={"blue":"blue", "yellow":"yellow", "red":"red"},
    )
    # Supprime la légende
    fig.update_layout(showlegend=False)
    # Force la taille
    fig.update_traces(marker=dict(size=point_size))
    
    # -- On gère maintenant l'échantillon qui aura les étiquettes
    label_df = label_df.copy()
    
    # On reprend directement la couleur déjà calculée dans plot_df
    label_df["color_marker"] = plot_df.loc[label_df.index, "color_marker"]
    
    #Trace des labels (texte = Player_Label)
    fig_labels = px.scatter(
        label_df,
        x=selected_xaxis,
        y=selected_yaxis,
        text="Player_Label",
        hover_name="Player_Label",
        hover_data=["Team", "Age", "Position Group"],
        color="color_marker",
        color_discrete_map={"blue":"blue", "yellow":"yellow", "red":"red"},
    )
    fig_labels.update_traces(hoverinfo='skip', hovertemplate=None)
    
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
    
    st.write("---")
    
    # Section explicative des métriques
    st.markdown("### Explication des métriques")
    st.markdown("""
    **PSV-99** : Peak sprint velocity 99th percentile. Cette métrique reflète la vitesse maximale atteinte par un joueur, et sa capacité à l’atteindre plusieurs fois ou à la maintenir suffisamment longtemps.  
    **TOP 5 PSV-99** : Moyenne des meilleures performances PSV-99 d’un joueur (les 5 meilleures).  
    **Total Distance P90** : Distance totale parcourue, ramenée à 90 minutes.  
    **M/min P90** : Distance totale parcourue divisée par le nombre de minutes. Pour TIP (resp. OTIP), divisé par le nombre de minutes TIP (resp. OTIP).  
    **Running Distance P90** : Distance parcourue entre 15 et 20 km/h.  
    **HSR Distance P90** : Distance parcourue entre 20 et 25 km/h.  
    **HSR Count P90** : Nombre d’actions au-dessus de 20 km/h (moyenne glissante sur 1 seconde), jusqu’à 25 km/h.  
    **Sprinting Distance P90** : Distance parcourue au-dessus de 25 km/h.  
    **Sprint Count P90** : Nombre d’actions au-dessus de 25 km/h (moyenne glissante sur 1 seconde).  
    **HI Distance P90** : Distance parcourue au-dessus de 20 km/h.  
    **HI Count** : Somme de HSR Count et Sprint Count.  
    **Medium Acceleration Count P90** : Nombre d’accélérations comprises entre 1.5 et 3 m/s², durant au moins 0.7 seconde.  
    **High Acceleration Count P90** : Accélérations supérieures à 3 m/s², durant au moins 0.7 seconde.  
    **Medium Deceleration Count P90** : Décélérations entre -1.5 et -3 m/s², durant au moins 0.7 seconde.  
    **High Deceleration Count P90** : Décélérations inférieures à -3 m/s², durant au moins 0.7 seconde.  
    **Explosive Acceleration to HSR Count P90** : Nombre d’accélérations (cf. définition ci-dessus) démarrant sous 9 km/h et atteignant au moins 20 km/h.  
    **Explosive Acceleration to Sprint Count P90** : Nombre d’accélérations démarrant sous 9 km/h et atteignant au moins 25 km/h.
    """)

# === VOLET NOUVEAU VOLET ===
elif page == "xPhysical":
    st.title("Détail xPhysical")

    # 1) Liste des saisons et calcul de l'index par défaut
    seasons = sorted(df["Season"].dropna().unique().tolist())
    default_idx = seasons.index("2024/2025") if "2024/2025" in seasons else len(seasons) - 1

    # 2) Sélecteurs côte à côte
    col1, col2 = st.columns(2)

    with col1:
        player = st.selectbox(
            "Sélectionner un joueur",
            options=sorted(df["Short Name"].dropna().unique())
        )

    with col2:
        season = st.selectbox(
            "Sélectionner une saison",
            options=seasons,
            index=default_idx
        )

    df_p = df[(df["Short Name"] == player) & (df["Season"] == season)]
    if df_p.empty:
        st.warning("Pas de données pour ce joueur / cette saison.")
        st.stop()
    positions = df_p["Position Group"].dropna().unique().tolist()
    if len(positions) > 1:
        chosen_position = st.selectbox(
            "Choisir le poste pour xPhysical",
            options=positions
        )
        df_p = df_p[df_p["Position Group"] == chosen_position]
    else:
        chosen_position = positions[0]
    row = df_p.iloc[0]
    # On travaille ensuite sur 'position' pour tout le calcul
    position = chosen_position

    # Affichage centré des infos du joueur
    info = (
        f"<div style='text-align:center; font-size:16px; margin:10px 0;'>"
        f"<b>{row['Short Name']}</b> – {row['Season']} – {row['Team']} "
        f"(<i>{row['Competition']}</i>) – {int(row['Age'])} ans"
        "</div>"
    )
    st.markdown(info, unsafe_allow_html=True)

    # 2) Barème complet
    threshold_dict = {
    'psv99_top5': {
        'Central Defender': [
            {'min': 31.48, 'max': None, 'score': 12},
            {'min': 30.84, 'max': 31.48, 'score': 9},
            {'min': 30.28, 'max': 30.84, 'score': 6},
            {'min': 29.64, 'max': 30.28, 'score': 3},
            {'min': None,  'max': 29.64, 'score': 0},
        ],
        'Full Back': [
            {'min': 32.0,  'max': None, 'score': 14},
            {'min': 31.46, 'max': 32.0,  'score': 10},
            {'min': 30.94, 'max': 31.46, 'score': 6},
            {'min': 30.08, 'max': 30.94, 'score': 4},
            {'min': None,  'max': 30.08, 'score': 0},
        ],
        'Midfield': [
            {'min': 29.76, 'max': None, 'score': 10},
            {'min': 29.07, 'max': 29.76, 'score': 7},
            {'min': 28.38,  'max': 29.07, 'score': 5},
            {'min': 27.62, 'max': 28.38,  'score': 3},
            {'min': None,  'max': 27.62, 'score': 0},
        ],
        'Wide Attacker': [
            {'min': 32.56, 'max': None, 'score': 14},
            {'min': 31.82, 'max': 32.56, 'score': 10},
            {'min': 31.22, 'max': 31.82, 'score': 6},
            {'min': 30.24, 'max': 31.22, 'score': 4},
            {'min': None,  'max': 30.24, 'score': 0},
        ],
        'Center Forward': [
            {'min': 32.2,  'max': None, 'score': 14},
            {'min': 31.28, 'max': 32.2,  'score': 10},
            {'min': 30.7,  'max': 31.28, 'score': 6},
            {'min': 29.96, 'max': 30.7,  'score': 4},
            {'min': None,  'max': 29.96, 'score': 0},
        ],
    },
    'hi_distance_full_all_p90': {
        'Central Defender': [
            {'min': 551.56, 'max': None, 'score': 4},
            {'min': 492.06, 'max': 551.56, 'score': 3},
            {'min': 441.2,  'max': 492.06, 'score': 2},
            {'min': 390.76, 'max': 441.2,  'score': 1},
            {'min': None,   'max': 390.76, 'score': 0},
        ],
        'Full Back': [
            {'min': 946.93, 'max': None, 'score': 4},
            {'min': 860.03, 'max': 946.93, 'score': 3},
            {'min': 786.18, 'max': 860.03, 'score': 2},
            {'min': 703.91, 'max': 786.18, 'score': 1},
            {'min': None,   'max': 703.91, 'score': 0},
        ],
        'Midfield': [
            {'min': 854.02, 'max': None, 'score': 4},
            {'min': 746.49, 'max': 854.02, 'score': 3},
            {'min': 665.42, 'max': 746.49, 'score': 2},
            {'min': 560.44, 'max': 665.42, 'score': 1},
            {'min': None,   'max': 560.44, 'score': 0},
        ],
        'Wide Attacker': [
            {'min': 1035.79,'max': None, 'score': 4},
            {'min': 940.79, 'max': 1035.79,'score': 3},
            {'min': 863.0,  'max': 940.79, 'score': 2},
            {'min': 777.13, 'max': 863.0,  'score': 1},
            {'min': None,   'max': 777.13, 'score': 0},
        ],
        'Center Forward': [
            {'min': 924.18, 'max': None, 'score': 4},
            {'min': 837.87, 'max': 924.18, 'score': 3},
            {'min': 754.05, 'max': 837.87, 'score': 2},
            {'min': 659.55, 'max': 754.05, 'score': 1},
            {'min': None,   'max': 659.55, 'score': 0},
        ],
    },
    'total_distance_full_all_p90': {
        'Central Defender': [
            {'min': 9688.63, 'max': None, 'score': 7},
            {'min': 9446.1,  'max': 9688.63, 'score': 5},
            {'min': 9231.08, 'max': 9446.1,  'score': 3},
            {'min': 8913.02, 'max': 9231.08, 'score': 1},
            {'min': None,    'max': 8913.02, 'score': 0},
        ],
        'Full Back': [
            {'min': 10330.71,'max': None, 'score': 7},
            {'min': 10103.2, 'max': 10330.71,'score': 5},
            {'min': 9802.22, 'max': 10103.2, 'score': 3},
            {'min': 9525.6,  'max': 9802.22, 'score': 1},
            {'min': None,    'max': 9525.6,  'score': 0},
        ],
        'Midfield': [
            {'min': 11193.90,  'max': None, 'score': 10},
            {'min': 10926.04,  'max': 11193.90,  'score': 7},
            {'min': 10627.19,  'max': 10926.04,  'score': 5},
            {'min': 10271.79,   'max': 10627.19,  'score': 3},
            {'min': None,    'max': 10271.79,   'score': 0},
        ],
        'Wide Attacker': [
            {'min': 10597.7,  'max': None, 'score': 7},
            {'min': 10253.05,  'max': 10597.7, 'score': 5},
            {'min': 9922.66,   'max': 10253.05, 'score': 3},
            {'min': 9576.8,    'max': 9922.66,  'score': 1},
            {'min': None,    'max': 9576.8,   'score': 0},
        ],
        'Center Forward': [
            {'min': 10337.14,  'max': None, 'score': 7},
            {'min': 9986.61,  'max': 10337.14, 'score': 5},
            {'min': 9725.31,   'max': 9986.61, 'score': 3},
            {'min': 9370.5,  'max': 9725.31,  'score': 1},
            {'min': None,    'max': 9370.5, 'score': 0},
        ],
    },
    'hsr_distance_full_all_p90': {
        'Central Defender': [
            {'min': 418.68,  'max': None,    'score': 7},
            {'min': 386.56,  'max': 418.68,  'score': 5},
            {'min': 359.06,  'max': 386.56,  'score': 3},
            {'min': 319.99,  'max': 359.06,  'score': 1},
            {'min': None,    'max': 319.99,  'score': 0},
        ],
        'Full Back': [
            {'min': 683.49,  'max': None,    'score': 7},
            {'min': 626.45,  'max': 683.49,  'score': 5},
            {'min': 574.46,  'max': 626.45,  'score': 3},
            {'min': 515.74,  'max': 574.46,  'score': 1},
            {'min': None,    'max': 515.74,  'score': 0},
        ],
        'Midfield': [
            {'min': 671.14,  'max': None,    'score': 7},
            {'min': 603.56,  'max': 671.14,  'score': 5},
            {'min': 547.54,  'max': 603.56,  'score': 3},
            {'min': 465.70,  'max': 547.54,  'score': 1},
            {'min': None,    'max': 465.70,  'score': 0},
        ],
        'Wide Attacker': [
            {'min': 719.96,  'max': None,    'score': 7},
            {'min': 671.78,  'max': 719.96,  'score': 5},
            {'min': 622.00,  'max': 671.78,  'score': 3},
            {'min': 560.85,  'max': 622.00,  'score': 1},
            {'min': None,    'max': 560.85,  'score': 0},
        ],
        'Center Forward': [
            {'min': 649.93,  'max': None,    'score': 7},
            {'min': 595.20,  'max': 649.93,  'score': 5},
            {'min': 551.35,  'max': 595.20,  'score': 3},
            {'min': 484.71,  'max': 551.35,  'score': 1},
            {'min': None,    'max': 484.71,  'score': 0},
        ],
    },
    'sprint_distance_full_all_p90': {
        'Central Defender': [
            {'min': 139.22, 'max': None,    'score': 7},
            {'min': 119.31, 'max': 139.22,  'score': 5},
            {'min': 102.34,  'max': 119.31,  'score': 3},
            {'min': 82.93,  'max': 102.34,   'score': 1},
            {'min': None,   'max': 82.93,   'score': 0},
        ],
        'Full Back': [
            {'min': 272.36, 'max': None,    'score': 7},
            {'min': 240.01, 'max': 272.36,  'score': 5},
            {'min': 204.02, 'max': 240.01,  'score': 3},
            {'min': 172.29,  'max': 204.02,  'score': 1},
            {'min': None,   'max': 172.29,   'score': 0},
        ],
        'Midfield': [
            {'min': 180.98, 'max': None,    'score': 4},
            {'min': 139.11, 'max': 180.98,  'score': 3},
            {'min': 109.68, 'max': 139.11,  'score': 2},
            {'min': 80.78,  'max': 109.68,  'score': 1},
            {'min': None,   'max': 80.78,   'score': 0},
        ],
        'Wide Attacker': [
            {'min': 305.22, 'max': None,    'score': 7},
            {'min': 258.86, 'max': 305.22,  'score': 5},
            {'min': 224.24, 'max': 258.86,  'score': 3},
            {'min': 179.44, 'max': 224.24,  'score': 1},
            {'min': None,   'max': 179.44,  'score': 0},
        ],
        'Center Forward': [
            {'min': 253.71, 'max': None,    'score': 7},
            {'min': 219.69, 'max': 253.71,  'score': 5},
            {'min': 180.40, 'max': 219.69,  'score': 3},
            {'min': 136.27, 'max': 180.40,  'score': 1},
            {'min': None,   'max': 136.27,  'score': 0},
        ],
    },
    'sprint_count_full_all_p90': {
        'Central Defender': [
            {'min': 7.79, 'max': None,   'score': 7},
            {'min': 6.74,  'max': 7.79,  'score': 5},
            {'min': 5.87,  'max': 6.74,   'score': 3},
            {'min': 4.9,  'max': 5.87,   'score': 1},
            {'min': None,  'max': 4.9,   'score': 0},
        ],
        'Full Back': [
            {'min': 14.47, 'max': None,   'score': 7},
            {'min': 12.89, 'max': 14.47,  'score': 5},
            {'min': 11.44, 'max': 12.89,  'score': 3},
            {'min': 9.69,  'max': 11.44,  'score': 1},
            {'min': None,  'max': 9.69,   'score': 0},
        ],
        'Midfield': [
            {'min': 10.10, 'max': None,   'score': 4},
            {'min': 7.85,  'max': 10.10,  'score': 3},
            {'min': 6.26,  'max': 7.85,   'score': 2},
            {'min': 4.83,  'max': 6.26,   'score': 1},
            {'min': None,  'max': 4.83,   'score': 0},
        ],
        'Wide Attacker': [
            {'min': 16.27, 'max': None,   'score': 7},
            {'min': 14.26, 'max': 16.27,  'score': 5},
            {'min': 12.32, 'max': 14.26,  'score': 3},
            {'min': 10.2,  'max': 12.32,  'score': 1},
            {'min': None,  'max': 10.2,   'score': 0},
        ],
        'Center Forward': [
            {'min': 14.28, 'max': None,   'score': 7},
            {'min': 12.44, 'max': 14.28,  'score': 5},
            {'min': 10.54,  'max': 12.44,  'score': 3},
            {'min': 7.99,  'max': 10.54,   'score': 1},
            {'min': None,  'max': 7.99,   'score': 0},
        ],
    },
    'highaccel_count_full_all_p90': {
        'Central Defender': [
            {'min': 5.84, 'max': None, 'score': 7},
            {'min': 5.14, 'max': 5.84, 'score': 5},
            {'min': 4.62, 'max': 5.14, 'score': 3},
            {'min': 4.09, 'max': 4.62, 'score': 1},
            {'min': None,'max': 4.09,  'score': 0},
        ],
        'Full Back': [
            {'min': 8.93, 'max': None, 'score': 7},
            {'min': 8.07, 'max': 8.93, 'score': 5},
            {'min': 7.22, 'max': 8.07, 'score': 3},
            {'min': 6.24, 'max': 7.22, 'score': 1},
            {'min': None,'max': 6.24,  'score': 0},
        ],
        'Midfield': [
            {'min': 5.18,'max': None,'score': 7},
            {'min': 4.37,'max': 5.18,'score': 5},
            {'min': 3.77,'max': 4.37,'score': 3},
            {'min': 3.15,'max': 3.77,'score': 1},
            {'min': None,'max': 3.15,'score': 0},
        ],
        'Wide Attacker': [
            {'min': 9.96,'max': None,'score': 10},
            {'min': 8.88,'max': 9.96,'score': 7},
            {'min': 7.63,'max': 8.88,'score': 5},
            {'min': 6.30,'max': 7.63,'score': 3},
            {'min': None,'max': 6.30,'score': 0},
        ],
        'Center Forward': [
            {'min': 9.52,'max': None,'score': 4},
            {'min': 8.35,'max': 9.52,'score': 3},
            {'min': 7.12,'max': 8.35,'score': 2},
            {'min': 6.20,'max': 7.12,'score': 1},
            {'min': None,'max': 6.20,'score': 0},
            ],
        },
    }

    position = row["Position Group"]
    if position not in next(iter(threshold_dict.values())):
        st.error(f"Pas de barème défini pour le poste « {position} »")
        st.stop()

    # 3) Mappings colonne brute <-> metric_key, et metric_key <-> colonne points
    metric_map = {
        "psv99_top5":                "TOP 5 PSV-99",
        "hi_distance_full_all_p90":  "HI Distance P90",
        "total_distance_full_all_p90":"Total Distance P90",
        "hsr_distance_full_all_p90": "HSR Distance P90",
        "sprint_distance_full_all_p90":"Sprinting Distance P90",
        "sprint_count_full_all_p90": "Sprint Count P90",
        "highaccel_count_full_all_p90":"High Acceleration Count P90",
    }
    note_map = {
        "psv99_top5":                "Note xPhy TOP 5 PSV-99",
        "hi_distance_full_all_p90":  "Note xPhy HI Distance P90",
        "total_distance_full_all_p90":"Note xPhy Total Distance P90",
        "hsr_distance_full_all_p90": "Note xPhy HSR Distance P90",
        "sprint_distance_full_all_p90":"Note xPhy Sprinting Distance P90",
        "sprint_count_full_all_p90": "Note xPhy Sprint Count P90",
        "highaccel_count_full_all_p90":"Note xPhy High Acceleration Count P90",
    }

    # 4) Fonction pour extraire le max de points par metric pour ce poste
    def get_max_pts(metric_key):
        rules = threshold_dict[metric_key][position]
        return max(r["score"] for r in rules)

    # 5) Construction de la table de détail
    rows = []
    for metric_key, col_val in metric_map.items():
        col_note = note_map[metric_key]
        raw_val = row.get(col_val, np.nan)
        pts     = row.get(col_note,    0)
        max_pts = get_max_pts(metric_key)

        rows.append({
            "Métrique":      col_val,
            "Valeur Joueur": f"{raw_val:.2f}" if pd.notna(raw_val) else "NA",
            "Points":        f"{pts} / {max_pts}"
        })

    # 6) Total et index depuis le DF
    total_pts   = row.get("Note xPhysical", 0)
    total_max   = row.get("Note xPhy_max",  0)
    index_xphy  = row.get("xPhysical",      0)

    rows.append({
        "Métrique":      "**Total**",
        "Valeur Joueur": "",
        "Points":        f"**{total_pts} / {total_max}**"
    })
    rows.append({
        "Métrique":      "Index xPhysical",
        "Valeur Joueur": "",
        "Points":        f"**{index_xphy}**"
    })
    
    # --- 2.1) Calcul du rang du joueur dans son Position Group / Season / Competition
    df_peers = df[
        (df["Position Group"] == position) &
        (df["Season"] == season) &
        (df["Competition"] == row["Competition"])
    ]
    # Trier par xPhysical décroissant et ranker
    df_peers = df_peers.sort_values("xPhysical", ascending=False)

    mean_peer = df_peers["xPhysical"].mean()

    # Rang (1 = meilleur)
    rank = int(df_peers.reset_index().index[df_peers["Short Name"] == player][0] + 1)
    total_peers = len(df_peers)

    # --- 2.2) Couleur de la jauge en fonction de l’index (0=rouge,100=vert)
    # On passe l'index sur 0–120° de hue
    hue = 120 * (index_xphy / 100)
    bar_color = f"hsl({hue:.0f}, 75%, 50%)"

    # --- 2.3) Construction du gauge
    fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=index_xphy,
    number={'font': {'size': 48}},
    gauge={
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
        'bar': {'color': bar_color, 'thickness': 0.25},
        'bgcolor': "rgba(255,255,255,0)",
        'borderwidth': 0,
        'shape': "angular",
        'steps': [
            {'range': [0, 100], 'color': 'rgba(100,100,100,0.3)'}
        ],
        'threshold': {
            'line': {'color': "white", 'width': 4},
            'thickness': 0.75,
            'value': mean_peer   # <-- ta moyenne ici
        }
    },
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': f"<b>{rank}ᵉ/{total_peers}</b>", 'font': {'size': 20}}
    ))
    
    fig_gauge.update_layout(
        margin={'t':40,'b':0,'l':0,'r':0},
        paper_bgcolor="rgba(0,0,0,0)",
        height=300
    )

    # --- 2.4) Affichage
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown(f"<div style='text-align:center; font-size:14px; margin-top:-20px; color:grey'>"
                f"Moyenne xPhysical ({position} en {row['Competition']}): {mean_peer:.1f}"
                "</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; font-size:18px; margin-top:-10px'><b>xPhy</b></div>",
                unsafe_allow_html=True)

    detail_df = pd.DataFrame(rows)

    # 7) Affichage sans colonne d’index numérique
    st.markdown("### Détail de l’index xPhysical")
    display_df = detail_df.set_index("Métrique").style.set_properties(**{"text-align": "center"})
    st.dataframe(display_df)
