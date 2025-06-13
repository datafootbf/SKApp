import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random
import re
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(layout="wide")

def shorten_season(s):
    s = str(s)
    if re.match(r'^\d{4}/\d{4}$', s):
        y1, y2 = s.split('/')
        return f"{y1[-2:]}/{y2[-2:]}"
    return s

@st.cache_data
def load_xphysical():
    df = pd.read_csv('SK_All.csv', sep=",")
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_xtechnical():
    df_tech = pd.read_parquet('SB_All.parquet')
    df_tech.columns = df_tech.columns.str.strip()
    df_tech["season_short"] = df_tech["Season Name"].apply(shorten_season)
    df_tech["Display Name"] = df_tech.apply(
        lambda row: f"{row['Player Known Name']} ({row['Player Name']})"
        if pd.notna(row.get("Player Known Name")) and row["Player Known Name"] != row["Player Name"]
        else row["Player Name"],
        axis=1
    )
    return df_tech

df = load_xphysical()
df_tech = load_xtechnical()

# Ensuite seulement, tes listes et tes widgets/filtres
season_list = sorted(df["Season"].dropna().unique().tolist())
position_list = sorted(df["Position Group"].dropna().unique().tolist())
competition_list = sorted(df["Competition"].dropna().unique().tolist())
player_list = sorted(df["Short Name"].dropna().unique().tolist())

classic_gk_metric_map = {
    "Gsaa Ratio": ("xTech GK GSAA %", [0, 5, 7, 12, 15]),
    "Save Ratio": ("xTech GK Save %", [0, 1, 2, 3, 4]),
    "Da Aggressive Distance": ("xTech GK Aggressive Distance", [0, 1, 2, 3, 4]),
    "Long Ball Ratio": ("xTech GK Long Ball %", [0, 1, 2, 3, 4]),
    "Op Xgbuildup P90": ("xTech GK OPxGBuildup", [0, 1, 2, 3, 4]),
    "Pressured Passing Ratio": ("xTech GK Passing u. Pressure %", [0, 1, 2, 3, 4]),
    "Passing Ratio": ("xTech GK Passing %", [0, 1, 2, 3, 4]),
    "Pass Into Danger Ratio": ("xTech GK Pass Into Danger %", [7, 5, 3, 1, 0])
}

classic_cb_metric_map = {
    "Obv Dribble Carry P90": ("xTech CB OBV D&C", [0, 1, 2, 3, 4]),
    "Long Ball Ratio": ("xTech CB Long Ball %", [0, 1, 2, 3, 4]),
    "Pressured Passing Ratio": ("xTech CB Passing u. Pressure %", [0, 1, 2, 3, 5]),
    "Obv Pass P90": ("xTech CB OBV Pass", [0, 1, 3, 5, 7]),
    "Passing Ratio": ("xTech CB Passing %", [0, 1, 2, 3, 5]),
    "Deep Progressions P90": ("xTech CB Deep Prog", [0, 1, 2, 3, 5]),
    "Blocks Per Shot": ("xTech CB Blocks/Shot", [0, 1, 3, 5, 7]),
    "Challenge Ratio": ("xTech CB Challenge %", [0, 1, 3, 5, 7]),
    "Average X Pressure": ("xTech CB Avg X Pressure", [0, 1, 2, 3, 5]),
    "Padj Tackles P90": ("xTech CB Padj Tackles", [0, 1, 2, 3, 4]),
    "Hops": ("xTech CB HOPS", [0, 5, 7, 10, 12]),
}

classic_fb_metric_map = {
    "Np Shots P90": ("xTech FB Np Shots", [0, 1, 2, 3, 5]),
    "Op Xa P90": ("xTech FB OPxA", [0, 1, 3, 5, 7]),
    "Crossing Ratio": ("xTech FB Crossing %", [0, 1, 2, 3, 4]),
    "Crosses P90": ("xTech FB Crosses", [0, 1, 2, 3, 5]),
    "Op Passes Into And Touches Inside Box P90": ("xTech FB OP Box Touch", [0, 1, 3, 5, 7]),
    "Perte Balle/Passe Ratio": ("xTech FB Ball Loss %", [0, 1, 2, 3, 4]),
    "Scoring Contribution": ("xTech FB G+A", [0, 1, 2, 3, 4]),
    "Op Xgbuildup Per Possession": ("xTech FB OPxGBuildup", [0, 1, 2, 3, 4]),
    "Padj Pressures P90": ("xTech FB Padj Pressures", [0, 1, 3, 5, 7]),
    "Fhalf Pressures P90": ("xTech FB FHalf Pressures", [0, 1, 2, 3, 4]),
    "Fhalf Counterpressures P90": ("xTech FB FHalf Counterpressures", [0, 1, 2, 3, 4]),
    "Padj Tackles And Interceptions P90": ("xTech FB Padj T&I", [0, 1, 2, 3, 5]),
    "Challenge Ratio": ("xTech FB Challenge %", [0, 1, 2, 3, 5]),
    "Hops": ("xTech FB HOPS", [0, 1, 2, 3, 5])
}

classic_mid_metric_map = {
    "Np Shots P90": ("xTech MID Np Shots", [0, 1, 2, 3, 4]),
    "Npxgxa P90": ("xTech MID Npxgxa", [0, 1, 2, 3, 4]),
    "Obv Pass P90": ("xTech MID Obv Pass", [0, 1, 3, 5, 7]),
    "Obv Dribble Carry P90": ("xTech MID Obv Carry", [0, 1, 3, 5, 7]),
    "Op Passes Into And Touches Inside Box P90": ("xTech MID Box Pass+Touch", [0, 1, 2, 3, 5]),
    "Perte Balle/Passe Ratio": ("xTech MID Ball Loss %", [0, 1, 2, 3, 4]),
    "Scoring Contribution": ("xTech MID G+A", [0, 1, 2, 3, 5]),
    "Op Xgbuildup Per Possession": ("xTech MID OPxGBuildup", [0, 1, 2, 3, 4]),
    "Passing Ratio": ("xTech MID Passing %", [0, 1, 3, 5, 7]),
    "Pressured Passing Ratio": ("xTech MID Pressured Passing %", [0, 1, 3, 5, 7]),
    "Fhalf Ball Recoveries P90": ("xTech MID Opp. Ball Recov.", [0, 1, 2, 3, 5]),
    "Pressure Regains P90": ("xTech MID Pressure Regains", [0, 1, 3, 5, 7]),
    "Counterpressure Regains P90": ("xTech MID CPR", [0, 1, 2, 3, 5]),
    "Padj Tackles And Interceptions P90": ("xTech MID T&I", [0, 3, 5, 7, 10]),
    "Challenge Ratio": ("xTech MID Challenge %", [0, 1, 2, 3, 5]),
    "Hops": ("xTech MID HOPS", [0, 1, 2, 3, 5])
}

classic_am_metric_map = {
    "Passes Into Box P90": ("xTech AM Passes Into Box", [0, 1, 3, 4, 5]),
    "Touches Inside Box P90": ("xTech AM Touches In Box", [0, 1, 2, 3, 4]),
    "Dribbles P90": ("xTech AM Dribbles", [0, 1, 3, 4, 5]),
    "Op Xa P90": ("xTech AM xA", [0, 3, 5, 7, 10]),
    "Np Shots P90": ("xTech AM Shots", [0, 3, 5, 7, 10]),
    "Obv Pass P90": ("xTech AM OBV Pass", [0, 3, 5, 7, 10]),
    "Obv Dribble Carry P90": ("xTech AM OBV Carry", [0, 1, 3, 5, 7]),
    "Perte Balle/Passe Ratio": ("xTech AM Ball Loss %", [0, 1, 2, 3, 4]),
    "Scoring Contribution": ("xTech AM G+A", [0, 1, 3, 4, 5]),
    "Through Balls P90": ("xTech AM Through Balls", [0, 1, 2, 3, 4]),
    "Fhalf Pressures P90": ("xTech AM FH Pressures", [0, 3, 5, 7, 10]),
    "Counterpressures P90": ("xTech AM Counterpressures", [0, 3, 5, 7, 10])
}

classic_wing_metric_map = {
    "Touches Inside Box P90": ("xTech WING Touches In Box", [0, 1, 3, 4, 5]),
    "Dribble Ratio": ("xTech WING Dribble Ratio", [0, 1, 2, 3, 4]),
    "Dribbles P90": ("xTech WING Dribbles", [0, 3, 5, 7, 10]),
    "Op Xa P90": ("xTech WING OPxA", [0, 3, 5, 7, 10]),
    "Np Shots P90": ("xTech WING Np Shots", [0, 3, 5, 7, 10]),
    "Obv Dribble Carry P90": ("xTech WING OBV Carry", [0, 5, 7, 10, 12]),
    "Scoring Contribution": ("xTech WING G+A", [0, 1, 3, 4, 5]),
    "Crosses P90": ("xTech WING Crosses", [0, 1, 2, 3, 4]),
    "Shot On Target Ratio": ("xTech WING SOT Ratio", [0, 1, 2, 3, 4]),
    "Fouls Won P90": ("xTech WING Fouls Won", [0, 1, 3, 4, 5]),
    "Fhalf Pressures P90": ("xTech WING FHalf Pressures", [0, 3, 5, 7, 10]),
    "Counterpressures P90": ("xTech WING Counterpressures", [0, 3, 5, 7, 10])
}

classic_st_metric_map = {
    "Np Xg P90": ("xTech ST Np Xg", [0, 5, 7, 10, 12]),
    "Np Shots P90": ("xTech ST Np Shots", [0, 1, 3, 5, 7]),
    "Touches Inside Box P90": ("xTech ST Touches In Box", [0, 3, 5, 7, 10]),
    "Op Xa P90": ("xTech ST Op Xa", [0, 1, 2, 3, 4]),
    "Perte Balle/Passe Ratio": ("xTech ST Ball Loss %", [0, 1, 3, 4, 5]),
    "Np Xg Per Shot": ("xTech ST Xg Per Shot", [0, 1, 3, 4, 5]),
    "Scoring Contribution": ("xTech ST G+A", [0, 1, 3, 5, 7]),
    "PSxG - xG": ("xTech ST PSxG Diff", [0, 1, 2, 3, 4]),
    "Shot On Target Ratio": ("xTech ST SoT %", [0, 1, 2, 3, 4]),
    "Fhalf Pressures P90": ("xTech ST Fhalf Pressures", [0, 3, 5, 7, 10]),
    "Counterpressures P90": ("xTech ST Counterpressures", [0, 3, 5, 7, 10])
}

xtech_columns_map = {
    'Goalkeeper': 'xTechnical GK (/100)',
    'Central Defender': 'xTechnical CB (/100)',
    'Full Back': 'xTechnical FB (/100)',
    'Midfielder': 'xTechnical MID (/100)',
    'Attacking Midfielder': 'xTechnical AM (/100)',
    'Winger': 'xTechnical WING (/100)',
    'Striker': 'xTechnical ST (/100)'
}

xtech_prefix_map = {
    'Goalkeeper': 'GK',
    'Central Defender': 'CB',
    'Full Back': 'FB',
    'Midfielder': 'MID',
    'Attacking Midfielder': 'AM',
    'Winger': 'WING',
    'Striker': 'ST'
}

xtech_tech_columns_map = {
    'Goalkeeper': 'xTech GK Usage (/100)',
    'Central Defender': 'xTech CB TECH (/100)',
    'Full Back': 'xTech FB TECH (/100)',
    'Midfielder': 'xTech MID TECH (/100)',
    'Attacking Midfielder': 'xTech AM TECH (/100)',
    'Winger': 'xTech WING TECH (/100)',
    'Striker': 'xTech ST TECH (/100)'
}

xtech_def_columns_map = {
    'Goalkeeper': 'xTech GK Save (/100)',
    'Central Defender': 'xTech CB DEF (/100)',
    'Full Back': 'xTech FB DEF (/100)',
    'Midfielder': 'xTech MID DEF (/100)',
    'Attacking Midfielder': 'xTech AM DEF (/100)',
    'Winger': 'xTech WING DEF (/100)',
    'Striker': 'xTech ST DEF (/100)'
}

xtech_post_config = {
    "Midfielder": {
        "metric_map": classic_mid_metric_map,
        "def": [
            "Fhalf Ball Recoveries P90",
            "Pressure Regains P90",
            "Counterpressure Regains P90",
            "Padj Tackles And Interceptions P90",
            "Challenge Ratio",
            "Hops"
        ],
        "tech": [
            "Np Shots P90",
            "Npxgxa P90",
            "Obv Pass P90",
            "Obv Dribble Carry P90",
            "Op Passes Into And Touches Inside Box P90",
            "Perte Balle/Passe Ratio",
            "Scoring Contribution",
            "Op Xgbuildup Per Possession",
            "Passing Ratio",
            "Pressured Passing Ratio"
        ],
        "labels": {
            "Fhalf Ball Recoveries P90": "Opp. Half Recoveries",
            "Pressure Regains P90": "Pressure Regains",
            "Counterpressure Regains P90": "Counterpressure Regains",
            "Padj Tackles And Interceptions P90": "PAdj Tackles & Interceptions",
            "Counterpressures P90": "Counterpressures",
            "Challenge Ratio": "Tack./Dribbled Past %",
            "Hops": "HOPS (Aerial Score)",
            "Np Shots P90": "Shots",
            "Npxgxa P90": "NPxG + xA",
            "Obv Pass P90": "OBV Pass",
            "Obv Dribble Carry P90": "OBV Dribble & Carry",
            "Op Passes Into And Touches Inside Box P90": "OP Passes + Touches Into Box",
            "Perte Balle/Passe Ratio": "Ball Loss %",
            "Scoring Contribution": "Scoring Contribution (G+A)",
            "Op Xgbuildup Per Possession": "xGBuildup (/possession)",
            "Passing Ratio": "Passing %",
            "Pressured Passing Ratio": "Passing u. Pressure %"
        }
    },

    "Striker": {
        "metric_map": classic_st_metric_map,
        "def": [
            "Fhalf Pressures P90", "Counterpressures P90"
        ],
        "tech": [
            "Np Xg P90", "Np Shots P90", "Touches Inside Box P90", "Op Xa P90",
            "Perte Balle/Passe Ratio", "Np Xg Per Shot", "Scoring Contribution",
            "PSxG - xG", "Shot On Target Ratio"
        ],
        "labels": {
            "Fhalf Pressures P90": "Opp. Half Pressures",
            "Counterpressures P90": "Counterpressures",       
            "Np Xg P90": "NPxG",
            "Np Shots P90": "Shots",
            "Op Xa P90": "OP xA",
            "Perte Balle/Passe Ratio": "Ball Loss %",
            "Np Xg Per Shot": "xG/Shot",
            "Scoring Contribution": "Scoring Contribution (G+A)",
            "PSxG - xG": "PSxG - xG",
            "Shot On Target Ratio": "Shooting %"
        }
    },

    "Attacking Midfielder": {
        "metric_map": classic_am_metric_map,
        "def": [
            "Fhalf Pressures P90", "Counterpressures P90"
        ],
        "tech": [
            "Passes Into Box P90", "Touches Inside Box P90", "Dribbles P90", "Op Xa P90",
            "Np Shots P90", "Obv Pass P90", "Obv Dribble Carry P90", "Perte Balle/Passe Ratio",
            "Scoring Contribution", "Through Balls P90"
        ],
        "labels": {
            "Fhalf Pressures P90": "Opp. Half Pressures",
            "Counterpressures P90": "Counterpressures",
            "Passes Into Box P90": "Passes Into Box",
            "Touches Inside Box P90": "Touches Inside Box",
            "Dribbles P90": "Succ. Dribbles",
            "Op Xa P90": "OP xA",
            "Np Shots P90": "Shots",
            "Obv Pass P90": "OBV Pass",
            "Obv Dribble Carry P90": "OBV Dribble & Carry",
            "Perte Balle/Passe Ratio": "Ball Loss %",
            "Scoring Contribution": "Scoring Contribution (G+A)",
            "Deep Progressions P90": "Deep Progressions",
            "Through Balls P90": "Throughballs"
        }
    },

    "Winger": {
        "metric_map": classic_wing_metric_map,
        "def": [
            "Fhalf Pressures P90", "Counterpressures P90"
        ],
        "tech": [
            "Touches Inside Box P90", "Dribble Ratio", "Dribbles P90", "Op Xa P90", "Np Shots P90",
            "Obv Dribble Carry P90", "Scoring Contribution", "Crosses P90", "Shot On Target Ratio", "Fouls Won P90"
        ],
        "labels": {
            "Fhalf Pressures P90": "Opp. Half Pressures",
            "Counterpressures P90": "Counterpressures",
            "Touches Inside Box P90": "Touches Inside Box",
            "Dribble Ratio": "Dribble Success %",
            "Dribbles P90": "Succ. Dribbles",
            "Op Xa P90": "OP xA",
            "Np Shots P90": "Shots",
            "Obv Dribble Carry P90": "OBV Dribble & Carry",
            "Scoring Contribution": "Scoring Contribution (G+A)",
            "Crosses P90": "Succ. Crosses",
            "Shot On Target Ratio": "Shooting %",
            "Fouls Won P90": "Fouls Won"
        }
    },

    "Full Back": {
        "metric_map": classic_fb_metric_map,
        "def": [
            "Padj Pressures P90",
            "Fhalf Pressures P90",
            "Fhalf Counterpressures P90",
            "Padj Tackles And Interceptions P90",
            "Challenge Ratio",
            "Hops"
        ],
        "tech": [
            "Np Shots P90",
            "Op Xa P90",
            "Crossing Ratio",
            "Crosses P90",
            "Op Passes Into And Touches Inside Box P90",
            "Perte Balle/Passe Ratio",
            "Scoring Contribution",
            "Op Xgbuildup Per Possession"
        ],
        "labels": {
            "Padj Pressures P90": "PAdj Pressures",
            "Fhalf Pressures P90": "Opp. Half Pressures",
            "Fhalf Counterpressures P90": "Opp. Half Counterpressures",
            "Padj Tackles And Interceptions P90": "PAdj Tackles & Interceptions",
            "Challenge Ratio": "Tack./Dribbled Past %",
            "Hops": "HOPS",   
            "Np Shots P90": "Shots",
            "Op Xa P90": "OP xA",
            "Crossing Ratio": "Crossing %",
            "Crosses P90": "Crosses",
            "Op Passes Into And Touches Inside Box P90": "OP Passes + Touches Into Box",
            "Perte Balle/Passe Ratio": "Ball Loss %",
            "Scoring Contribution": "Scoring Contribution (G+A)",
            "Op Xgbuildup Per Possession": "xGBuildup (/possession)"
        }
    },

    "Central Defender": {
        "metric_map": classic_cb_metric_map,
        "def": [
            "Blocks Per Shot", "Challenge Ratio", "Average X Pressure",
            "Padj Tackles P90", "Hops"
        ],
        "tech": [
            "Obv Dribble Carry P90", "Long Ball Ratio", "Pressured Passing Ratio", "Obv Pass P90",
            "Passing Ratio", "Deep Progressions P90"
        ],
        "labels": {
            "Blocks Per Shot": "Blocks/Shot",
            "Challenge Ratio": "Tack./Dribbled Past %",
            "Average X Pressure": "Av. Pressure Dist.",
            "Padj Tackles P90": "PAdj Tackles",
            "Hops": "HOPS",           
            "Obv Dribble Carry P90": "OBV Dribble & Carry",
            "Long Ball Ratio": "Long Ball %",
            "Pressured Passing Ratio": "Passing u. Pressure %",
            "Obv Pass P90": "OBV Pass",
            "Passing Ratio": "Passing %",
            "Deep Progressions P90": "Deep Progressions"
        }
    },

    "Goalkeeper": {
        "metric_map": classic_gk_metric_map,
        "save": [
            "Gsaa Ratio",
            "Save Ratio",
            "Da Aggressive Distance"
        ],
        "usage": [
            "Long Ball Ratio",
            "Op Xgbuildup P90",
            "Pressured Passing Ratio",
            "Passing Ratio",
            "Pass Into Danger Ratio"
        ],
        "labels": {
            "Gsaa Ratio": "GSAA %",
            "Save Ratio": "Save %",
            "Da Aggressive Distance": "GK Aggressive Dist.",
            "Long Ball Ratio": "Long Ball %",
            "Op Xgbuildup P90": "OP xGBuildup",           
            "Pressured Passing Ratio": "Passing u. Pressure %",
            "Passing Ratio": "Passing %",
            "Pass Into Danger Ratio": "Pass into Danger %",
        }
    }
}

# Mapping affiché → Player Name
display_to_playername = df_tech.set_index("Display Name")["Player Name"].to_dict()

# Nettoyage éventuel des colonnes cibles xTechnical
df_tech["Prefered Foot"] = df_tech["Prefered Foot"].str.strip()
df_tech["Player Name"] = df_tech["Player Name"].str.strip()
df_tech["Position Group"] = df_tech["Position Group"].str.strip()
df_tech["Competition Name"] = df_tech["Competition Name"].str.strip()

# Création des listes de filtres xTechnical
season_list_tech = sorted(df_tech["Season Name"].dropna().unique().tolist())
position_list_tech = sorted(df_tech["Position Group"].dropna().unique().tolist())
competition_list_tech = sorted(df_tech["Competition Name"].dropna().unique().tolist())
player_list_tech = sorted(df_tech["Player Name"].dropna().unique().tolist())
foot_list_tech = sorted(df_tech["Prefered Foot"].dropna().unique().tolist())

# Création des templates Radar xTechnical
metric_templates_tech = {
    "Goalkeeper": [
        "Passing Ratio", "Op Passes P90", "Long Ball Ratio", "Pressured Change In Pass Length",
        "Clcaa", "Da Aggressive Distance", "Gsaa P90", "Save Ratio", "Ot Shots Faced P90",
        "Pass Into Danger Ratio", "Pressured Passing Ratio"
    ],
    "Central Defender": [
        "Passing Ratio", "Op Passes P90", "Long Ball Ratio", "Long Balls P90", "Xgbuildup P90",
        "Aerial Ratio", "Aerial Wins P90", "Padj Tackles And Interceptions P90", "Pressure Regains P90",
        "Defensive Action Regains P90", "Obv Pass P90", "Obv Dribble Carry P90"
    ],
    "CB-DEF": [
        "Fouls P90", "Fhalf Ball Recoveries P90", "Average X Pressure", "Padj Pressures P90",
        "Pressure Regains P90", "Aerial Ratio", "Aerial Wins P90", "Challenge Ratio", "Padj Interceptions P90",
        "Padj Clearances P90", "Blocks Per Shot", "Errors P90"
    ],
    "CB-OFF": [
        "Passing Ratio", "Op Passes P90", "Long Ball Ratio", "Long Balls P90", "Dispossessions P90",
        "Turnovers P90", "Np Shots P90", "Obv Pass P90", "Obv Dribble Carry P90", "Carries P90",
        "Deep Progressions P90", "Pressured Passing Ratio"
    ],
    "Full Back": [
        "Passing Ratio", "Op Passes P90", "Deep Progressions P90", "Crosses P90", "Crossing Ratio",
        "Aerial Ratio", "Average X Defensive Action", "Padj Tackles And Interceptions P90", "Padj Pressures P90",
        "Fhalf Counterpressures P90", "Np Shots P90", "Op Passes Into And Touches Inside Box P90", "Op Xa P90"
    ],
    "FB-DEF": [
        "Fouls P90", "Fhalf Ball Recoveries P90", "Average X Defensive Action", "Padj Pressures P90",
        "Fhalf Pressures P90", "Fhalf Counterpressures P90", "Aerial Ratio", "Aerial Wins P90",
        "Padj Tackles P90", "Challenge Ratio", "Padj Interceptions P90"
    ],
    "FB-OFF": [
        "Passing Ratio", "Op Passes P90", "Deep Progressions P90", "Crosses P90", "Crossing Ratio",
        "Dribbles P90", "Dispossessions P90", "Turnovers P90", "Op Xa P90", "Touches Inside Box P90",
        "Passes Inside Box P90", "Pressured Passing Ratio"
    ],
    "Midfielder (CDM)": [
        "Passing Ratio", "Op Passes P90", "Long Ball Ratio", "Turnovers P90", "Deep Progressions P90",
        "Aerial Ratio", "Padj Tackles P90", "Padj Interceptions P90", "Fhalf Ball Recoveries P90",
        "Padj Pressures P90", "Fhalf Counterpressures P90", "Shots Key Passes P90", "Pressured Passing Ratio"
    ],
    "Midfielder (CM)": [
        "Passing Ratio", "Op Passes P90", "Turnovers P90", "Deep Progressions P90", "Aerial Ratio",
        "Padj Tackles And Interceptions P90", "Padj Pressures P90", "Fhalf Counterpressures P90",
        "Npxgxa P90", "Op Passes Into And Touches Inside Box P90", "Np Shots P90",
        "Scoring Contribution", "Pressured Passing Ratio"
    ],
    "MID-DEF": [
        "Fouls P90", "Aerial Ratio", "Aerial Wins P90", "Padj Tackles P90", "Padj Interceptions P90",
        "Pressure Regains P90", "Fhalf Pressures P90", "Counterpressures P90", "Fhalf Counterpressures P90",
        "Padj Clearances P90", "Fhalf Ball Recoveries P90"
    ],
    "MID-OFF": [
        "Passing Ratio", "Op Passes P90", "Turnovers P90", "Dispossessions P90", "Deep Progressions P90",
        "Through Balls P90", "Op Xa P90", "Op Passes Into And Touches Inside Box P90", "Np Xg P90",
        "Np Shots P90", "Obv Pass P90", "Obv Dribble Carry P90", "Pressured Passing Ratio"
    ],
    "Attacking Midfielder": [
        "Passing Ratio", "Op Passes P90", "Turnovers P90", "Dribbles P90", "Deep Progressions P90",
        "Padj Pressures P90", "Fhalf Counterpressures P90", "Through Balls P90", "Op Xa P90",
        "Op Passes Into And Touches Inside Box P90", "Np Xg P90", "Scoring Contribution", "Pressured Passing Ratio"
    ],
    "Winger": [
        "Passing Ratio", "Padj Pressures P90", "Counterpressures P90", "Op Key Passes P90", "Op Xa P90",
        "Obv Pass P90", "Dribbles P90", "Obv Dribble Carry P90", "Fouls Won P90", "Np Shots P90",
        "Scoring Contribution", "Op Passes Into And Touches Inside Box P90", "Turnovers P90"
    ],
    "Striker": [
        "Passing Ratio", "Turnovers P90", "Dribbles P90", "Aerial Wins P90", "Padj Pressures P90",
        "Counterpressures P90", "Op Xa P90", "Touches Inside Box P90", "Np Xg P90", "Npg P90",
        "Np Shots P90", "Np Xg Per Shot", "Shot On Target Ratio"
    ]
}

metric_labels_tech = {
    "Goalkeeper": ["Passing%", "OP Passes", "Long Ball%", "Being Press. Change in Pass Length",
                   "Claims - CCAA%", "GK Aggressive Distance", "Goals Saved Above Average", "Save%",
                   "On Target Shots Faced", "Pass into Danger%", "Pressured Pass%"],
    "Central Defender": ["Passing%", "OP Passes", "Long Ball%", "Long Balls", "xGBuildup",
                         "Aerial Win%", "Aerial Wins", "PAdj Tackles & Interceptions", "Pressure Regains",
                         "Defensive Action Regains", "Pass OBV", "Dribble & Carry OBV"],
    "CB-DEF": ["Fouls", "Opp. Half Ball Recoveries", "Average Pressure Distance", "PAdj Pressures",
               "Pressure Regains", "Aerial Win%", "Aerial Wins", "Tack/Dribbled Past%", "PAdj Interceptions",
               "PAdj Clearances", "Blocks/Shot", "Errors"],
    "CB-OFF": ["Passing%", "OP Passes", "Long Ball%", "Long Balls", "Dispossessed", "Turnovers",
               "Shots", "Pass OBV", "Dribble & Carry OBV", "Carries", "Deep Progressions", "Pressured Pass%"],
    "Full Back": ["Passing%", "OP Passes", "Deep Progressions", "Successful Crosses", "Crossing %",
                  "Aerial Win%", "Average Def. Action Distance", "Padj Tackles And Interceptions", "PAdj Pressures",
                  "Counterpressures in Opp. Half", "Shots", "OP Passes + Touches In Box", "OP xGAssisted"],
    "FB-DEF": ["Fouls", "Opp. Half Ball Recoveries", "Average Def. Action Distance", "PAdj Pressures",
               "Pressures in Opp. Half", "Counterpressures in Opp. Half", "Aerial Win%", "Aerial Wins",
               "PAdj Tackles", "Tack/Dribbled Past%", "PAdj Interceptions"],
    "FB-OFF": ["Passing%", "OP Passes", "Deep Progressions", "Successful Crosses", "Crossing %",
               "Successful Dribbles", "Dispossessed", "Turnovers", "OP xGAssisted", "Touches In Box",
               "Passes Inside Box", "Pressured Pass%"],
    "Midfielder (CDM)": ["Passing%", "OP Passes", "Long Ball%", "Turnovers", "Deep Progressions",
                  "Aerial Win%", "PAdj Tackles", "PAdj Interceptions", "Opp. Half Ball Recoveries",
                  "PAdj Pressures", "Pressures in Opp. Half", "Shots & Key Passes", "Pressured Pass%"],
    "Midfielder (CM)": ["Passing%", "OP Passes", "Turnovers", "Deep Progressions", "Aerial Win%",
                 "PAdj Tackles And Interceptions", "PAdj Pressures", "Counterpressures in Opp. Half",
                 "xG & xG Assisted", "OP Passes + Touches In Box", "Shots", "Scoring Contribution", "Pressured Pass%"],
    "MID-DEF": ["Fouls", "Aerial Win%", "Aerial Wins", "PAdj Tackles", "PAdj Interceptions",
                "Pressure Regains", "Pressures in Opp. Half", "Counterpressures",
                "Counterpressures in Opp. Half", "PAdj Clearances", "Opp. Half Ball Recoveries"],
    "MID-OFF": ["Passing%", "OP Passes", "Turnovers", "Dispossessed", "Deep Progressions",
                "Throughballs", "OP xGAssisted", "OP Passes + Touches In Box", "xG", "Shots",
                "Pass OBV", "Dribble & Carry OBV", "Pressured Pass%"],
    "Attacking Midfielder": ["Passing%", "OP Passes", "Turnovers", "Successful Dribbles", "Deep Progressions",
                             "PAdj Pressures", "Counterpressures in Opp. Half", "Throughballs", "OP xGAssisted",
                             "OP Passes + Touches In Box", "xG", "Scoring Contribution", "Pressured Pass%"],
    "Winger": ["Passing%", "PAdj Pressures", "Counterpressures", "Key Passes", "OP xGAssisted",
               "Pass OBV", "Successful Dribbles", "Dribble & Carry OBV", "Fouls Won", "Shots",
               "Scoring Contribution", "OP Passes + Touches In Box", "Turnovers"],
    "Striker": ["Passing%", "Turnovers", "Successful Dribbles", "Aerial Wins", "PAdj Pressures",
                "Counterpressures", "OP xGAssisted", "Touches Inside Box", "xG", "NP Goals",
                "Shots", "xG/Shot", "Shooting%"]
}

# In[8]:

# On définit les colonnes pour le graphe
graph_columns = [
    "PSV-99", "TOP 5 PSV-99", "Total Distance P90", "M/min P90", "Running Distance P90",
    "HSR Distance P90", "HSR Count P90", "Sprinting Distance P90", "Sprint Count P90",
    "HI Distance P90", "HI Count P90", "Medium Acceleration Count P90",
    "High Acceleration Count P90", "Medium Deceleration Count P90", "High Deceleration Count P90",
    "Explosive Acceleration to HSR Count P90", "Explosive Acceleration to Sprint Count P90", "xPhysical"
]

# Charge le logo (met le chemin exact si besoin)
logo_path = "AS Roma.png"
logo = Image.open(logo_path)
st.sidebar.image(logo, use_container_width=True)

# === Sélecteur de page dans la sidebar ===
page = st.sidebar.radio(
    "Choose tab",
    ["xPhysical", "xTech/xDef"]
)

if page == "xPhysical":
    
    # Création des sous-onglets
    tab1, tab2, tab3, tab4 = st.tabs(["Scatter Plot", "Radar", "Index", "Top 50"])
    
    # --- Onglet Scatter Plot ---
    with tab1:
        
        with st.expander("📘 About the xPhysical Section", expanded=False):
            st.markdown("""
        This section allows you to visualize and compare players' physical performance data across multiple metrics, competitions, seasons, and positions.

        #### ⚠️ Data Reliability & Scope
        Only players who have played at least **5 matches** with a minimum of **60 minutes per match** are included in this section. This threshold ensures a higher level of reliability and consistency in the dataset.  
        **Please note:** All metrics are provided for comparative analysis only and should not be interpreted as exact measurements.

        #### 🗂️ What you can do in each tab:
        - **Scatter Plot:**  
          Visualize relationships between any two physical metrics for the filtered players. Highlight specific players or teams and view average reference lines.

        - **Radar:**  
          Generate percentile-based radar plots for a selected player (or compare two players) based on the main physical metrics, benchmarked against peers at the same position.

        - **Index:**  
          See a detailed breakdown of the physical score calculation for an individual player.

        - **Top 50:**  
          Display the top 50 players by xPhysical index for a selected competition, season, and position, with sorting and filtering options.

        **All metrics are normalized per 90 minutes (P90), except where otherwise indicated.**
        """)
            
        st.markdown("<div style='height: 2em;'></div>", unsafe_allow_html=True)
                
        # Ligne 1 : saisons, compétitions, postes
        col1, col2, col3 = st.columns([1.2, 1.2, 1.2])
        with col1:
            selected_seasons = st.multiselect(
                "Season(s)",
                options=season_list,
                default=[],
            )
        with col2:
            selected_competitions = st.multiselect(
                "Competition(s)",
                options=competition_list,
                default=[],
            )
        with col3:
            selected_positions = st.multiselect(
                "Position(s)",
                options=position_list,
                default=[],
            )

        # Ligne 2 : âge, joueurs ajoutés (plus étroites car moins d’options)
        col4, col5 = st.columns([1, 1.2])
        with col4:
            age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
            selected_age = st.slider(
                "Age",
                min_value=age_min,
                max_value=age_max,
                value=(age_min, age_max),
                step=1
            )
        with col5:
            selected_extra_players = st.multiselect(
                "Add player(s)",
                options=player_list,
                default=[],
                help="Add players outside filters"
            )
        
        # -- Application des filtres (inchangé)
        filtered_df = df.copy()
        if selected_seasons:
            filtered_df = filtered_df[filtered_df["Season"].isin(selected_seasons)]
        if selected_positions:
            filtered_df = filtered_df[filtered_df["Position Group"].isin(selected_positions)]
        if selected_competitions:
            filtered_df = filtered_df[filtered_df["Competition"].isin(selected_competitions)]
        filtered_df = filtered_df[
            (filtered_df["Age"] >= selected_age[0]) &
            (filtered_df["Age"] <= selected_age[1])
        ]
        if selected_extra_players:
            extra_df = df[df["Short Name"].isin(selected_extra_players)]
            filtered_df = pd.concat([filtered_df, extra_df]).drop_duplicates()

        # Bouton d'export CSV de la sélection actuelle
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download selection as CSV",
            data=csv,
            file_name="selection_physical_data.csv",
            mime="text/csv",
            key="download_scatter_csv"
        )    
            
        st.markdown("---")
               
        # Sélection de l'axe X, Y
        colx, coly = st.columns(2)
        with colx:
            selected_xaxis = st.selectbox(
                "X Axis",
                options=graph_columns,
                index=0
            )
        with coly:
            selected_yaxis = st.selectbox(
                "Y Axis",
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
                "Highlight Player(s)",
                options=filtered_players,
                default=[]
            )
        
        with col2:
            highlight_teams = st.multiselect(
                "Highlight Team(s)",
                options=team_list,
                default=[]
            ) 
        
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
                
        # Section explicative des métriques
        with st.expander("📘 Metrics Explanation (xPhysical)", expanded=False):
            st.markdown("""
- **PSV-99**: Peak sprint velocity at the 99th percentile. This metric reflects the maximum speed reached by a player, as well as their ability to reach it repeatedly or sustain it for a sufficient duration.
- **TOP 5 PSV-99**: Average of a player’s top 5 PSV-99 performances.
- **Total Distance P90**: Total distance covered, normalized per 90 minutes.
- **M/min P90**: Total distance covered divided by the number of minutes played. For TIP (respectively OTIP), divided by the number of TIP (resp. OTIP) minutes.
- **Running Distance P90**: Distance covered between 15 and 20 km/h.
- **HSR Distance P90**: Distance covered between 20 and 25 km/h.
- **HSR Count P90**: Number of actions above 20 km/h (1-second moving average), up to 25 km/h.
- **Sprinting Distance P90**: Distance covered above 25 km/h.
- **Sprint Count P90**: Number of actions above 25 km/h (1-second moving average).
- **HI Distance P90**: Distance covered above 20 km/h.
- **HI Count**: Sum of HSR Count and Sprint Count.
- **Medium Acceleration Count P90**: Number of accelerations between 1.5 and 3 m/s², lasting at least 0.7 seconds.
- **High Acceleration Count P90**: Accelerations above 3 m/s², lasting at least 0.7 seconds.
- **Medium Deceleration Count P90**: Decelerations between -1.5 and -3 m/s², lasting at least 0.7 seconds.
- **High Deceleration Count P90**: Decelerations below -3 m/s², lasting at least 0.7 seconds.
- **Explosive Acceleration to HSR Count P90**: Number of accelerations (as defined above) starting below 9 km/h and reaching at least 20 km/h.
- **Explosive Acceleration to Sprint Count P90**: Number of accelerations starting below 9 km/h and reaching at least 25 km/h.
""")

    
    with tab2:
        # 1) Choix des métriques  
        default_metrics = [
            "TOP 5 PSV-99",
            "HI Distance P90",
            "Total Distance P90",
            "HSR Distance P90",
            "Sprinting Distance P90",
            "Sprint Count P90",
            "High Acceleration Count P90"
        ]
        extra_metrics = [
            "Explosive Acceleration to HSR Count P90",
            "Explosive Acceleration to Sprint Count P90",
            "Note xPhy TOP 5 PSV-99",
            "Note xPhy HI Distance P90",
            "Note xPhy Total Distance P90",
            "Note xPhy HSR Distance P90",
            "Note xPhy Sprinting Distance P90",
            "Note xPhy Sprint Count P90",
            "Note xPhy High Acceleration Count P90",
            "xPhysical"
        ]
        metrics = st.multiselect(
            "Select metrics",
            options=default_metrics + extra_metrics,
            default=default_metrics
        )
        if not metrics:
            st.warning("At least one metric is necessary.")
            st.stop()

        # Ajout colonne Display Name
        df["Display Name"] = df["Short Name"] + " (" + df["Player"] + ")"
        
        # Dictionnaire pour retrouver le Short Name
        display_to_shortname = dict(zip(df["Display Name"], df["Short Name"]))
        
        # === MAPPINGS JOUEURS POUR AFFICHAGE ===
        # Optimisation : mapping unique Player -> Display Name
        df_display = df[["Player", "Display Name"]].dropna().drop_duplicates()
        player_to_display = dict(zip(df_display["Player"], df_display["Display Name"]))
        display_to_player = {v: k for k, v in player_to_display.items()}
        display_options = sorted(player_to_display.values())

        # === JOUEUR 1 ===
        col1, col2 = st.columns(2)

        with col1:
            # Affichage joueur (Display Name), clé réelle = Player
            default_display = next((name for name in display_options if "Artem Dovbyk" in name), display_options[0])
            p1_display = st.selectbox("Player 1", display_options, index=display_options.index(default_display), key="radar_p1")
            p1 = display_to_player[p1_display]

        with col2:
            # Liste des saisons disponibles
            seasons1 = sorted(df[df["Player"] == p1]["Season"].dropna().unique().tolist())
            default_season = "2024/2025" if "2024/2025" in seasons1 else seasons1[-1]
            s1 = st.selectbox("Season 1", seasons1, index=seasons1.index(default_season), key="radar_s1")

        df1 = df[(df["Player"] == p1) & (df["Season"] == s1)]

        # Club
        teams1 = df1["Team"].dropna().unique().tolist()
        if len(teams1) > 1:
            team1 = st.selectbox("Select a team", teams1, key="radar_team1")
            df1 = df1[df1["Team"] == team1]
        else:
            team1 = teams1[0]

        # Poste
        poss1 = df1["Position Group"].dropna().unique().tolist()
        pos1 = st.selectbox("Position 1", poss1, key="radar_pos1") if len(poss1) > 1 else poss1[0]
        df1 = df1[df1["Position Group"] == pos1]

        # Compétition
        comps1 = df1["Competition"].dropna().unique().tolist()
        comp1 = st.selectbox("Compétition 1", comps1, key="radar_c1") if len(comps1) > 1 else comps1[0]
        df1 = df1[df1["Competition"] == comp1]

        # Ligne finale joueur 1
        row1 = df1.iloc[0]

        # === COMPARAISON JOUEUR 2 ===
        compare = st.checkbox("Compare to a 2nd player")
        if compare:
            col3, col4 = st.columns(2)
            with col3:
                p2_display = st.selectbox("Player 2", display_options, key="radar_p2")
                p2 = display_to_player[p2_display]
            with col4:
                seasons2 = sorted(df[df["Player"] == p2]["Season"].unique().tolist())
                s2 = st.selectbox("Season 2", seasons2, key="radar_s2")

            df2 = df[(df["Player"] == p2) & (df["Season"] == s2)]

            # Club
            teams2 = df2["Team"].dropna().unique().tolist()
            if len(teams2) > 1:
                team2 = st.selectbox("Select a team (Player 2)", teams2, key="radar_team2")
                df2 = df2[df2["Team"] == team2]
            else:
                team2 = teams2[0]

            # Poste
            poss2 = df2["Position Group"].dropna().unique().tolist()
            pos2 = st.selectbox("Position 2", poss2, key="radar_pos2") if len(poss2) > 1 else poss2[0]
            df2 = df2[df2["Position Group"] == pos2]

            # Compétition
            comps2 = df2["Competition"].dropna().unique().tolist()
            comp2 = st.selectbox("Competition 2", comps2, key="radar_c2") if len(comps2) > 1 else comps2[0]
            df2 = df2[df2["Competition"] == comp2]

            # Ligne finale joueur 2
            row2 = df2.iloc[0]
        
        # 4) Préparer les peers (cinq ligues), avec fallback pour libellés “AAAA/AAAA”
        champions = [
            "ENG - Premier League","FRA - Ligue 1",
            "ESP - LaLiga","ITA - Serie A","GER - Bundesliga"
        ]
    
        # 4.1) Peers sur même saison & grands championnats
        peers = df[
            (df["Position Group"] == pos1) &
            (df["Season"] == s1) &
            (df["Competition"].isin(champions))
        ]
    
        # 4.2) Si aucun peer et si la saison est du type AAAA/AAAA, on essaye AAAA-1/AAAA
        if peers.empty:
            parts = s1.split("/")
            if len(parts) == 2 and parts[0] == parts[1]:
                year = int(parts[0])
                alt_season = f"{year-1}/{year}"
                peers = df[
                    (df["Position Group"] == pos1) &
                    (df["Season"] == alt_season) &
                    (df["Competition"].isin(champions))
                ]
    
        # 4.3) Si toujours aucun peer, on élargit à toutes compétitions pour la même saison
        if peers.empty:
            peers = df[
                (df["Position Group"] == pos1) &
                (df["Season"] == s1)
            ]
        
        # 5) Fonction fiable de percentile rank
        def pct_rank(series, value):
            """Retourne le percentile de value dans la série series (0–100)."""
            arr = series.dropna().values
            if len(arr) == 0:
                return 0.0
            # nombre de valeurs STRICTEMENT inférieures + moitié des égalités
            lower = (arr < value).sum()
            equal = (arr == value).sum()
            rank = (lower + 0.5 * equal) / len(arr) * 100
            return float(rank)
        
        # 6) Calcul des percentiles pour chaque métrique
        r1 = [pct_rank(peers[m], row1[m]) for m in metrics]
        if compare:
            r2 = [pct_rank(peers[m], row2[m]) for m in metrics]
        else:
            mean_vals = peers[metrics].mean()
            r2 = [pct_rank(peers[m], mean_vals[m]) for m in metrics]
        
        # 7) Fermer les boucles
        metrics_closed = metrics + [metrics[0]]
        r1_closed     = r1 + [r1[0]]
        r2_closed     = r2 + [r2[0]]
        # raw values pour le hover (tableau Nx1 pour Plotly)
        raw1      = [row1[m] for m in metrics]
        raw1_closed = raw1 + [raw1[0]]
        cd1 = [[v] for v in raw1_closed]
        if compare:
            raw2 = [row2[m] for m in metrics]
        else:
            mean_vals = peers[metrics].mean()
            raw2 = [mean_vals[m] for m in metrics]
        raw2_closed = raw2 + [raw2[0]]
        cd2 = [[v] for v in raw2_closed]
        
        # 8) Construction du radar Plotly
        fig = go.Figure()
        
        # Construire les strings de hover
        hover1 = [
            f"<b>{theta}</b><br>"
            f"Value: {raw:.2f}<br>"
            f"Percentile: {r:.1f}%"
            for theta, raw, r in zip(metrics_closed, raw1_closed, r1_closed)
        ]
        hover2 = [
            f"<b>{theta}</b><br>"
            f"Value: {raw:.2f}<br>"
            f"Percentile: {r:.1f}%"
            for theta, raw, r in zip(metrics_closed, raw2_closed, r2_closed)
        ]

        # Trace Joueur 1 avec text + hovertemplate
        # 1) Calque principal “fill” (sans markers ni hover)
        fig.add_trace(go.Scatterpolar(
            r=r1_closed,
            theta=metrics_closed,
            mode='lines',
            hoverinfo='skip',
            fill='toself',
            fillcolor='rgba(255,215,0,0.3)',
            line=dict(color='gold', width=2),
            name=p1
        ))
        # 2) Calque invisible de markers pour le hover
        fig.add_trace(go.Scatterpolar(
            r=r1_closed,
            theta=metrics_closed,
            mode='markers',
            hoverinfo='text',
            hovertext=[
                f"<b>{theta}</b><br>Value: {raw:.2f}<br>Percentile: {r:.1f}%"
                for theta, raw, r in zip(metrics_closed, raw1_closed, r1_closed)
            ],
            marker=dict(size=12, color='rgba(255,215,0,0)'),  # invisible
            showlegend=False
        ))
                
        # 1) Calque principal “fill”
        fig.add_trace(go.Scatterpolar(
            r=r2_closed,
            theta=metrics_closed,
            mode='lines',
            hoverinfo='skip',
            fill='toself',
            fillcolor='rgba(144,238,144,0.3)',
           line=dict(color=(compare and 'cyan') or 'lightgreen', width=2),
            name=(compare and p2) or 'Top5 Average'
        ))
        # 2) Calque markers pour hover
        fig.add_trace(go.Scatterpolar(
            r=r2_closed,
            theta=metrics_closed,
            mode='markers',
            hoverinfo='text',
            hovertext=[
                f"<b>{theta}</b><br>Value: {raw:.2f}<br>Percentile: {r:.1f}%"
                for theta, raw, r in zip(metrics_closed, raw2_closed, r2_closed)
            ],
            marker=dict(size=12, color='rgba(144,238,144,0)'),  # invisible
            showlegend=False
        ))
        
        # 9) Mise en forme finale
        # On récupère aussi les noms d’équipes
        team1 = row1["Team"]
        #Titre de base pour joueur 1
        age1_str = f"{int(row1['Age'])}" if pd.notna(row1['Age']) else "?"
        title_text = f"{p1} ({pos1}) – {s1} – {team1} ({row1['Competition']}) – {age1_str} y/o"

        if compare:
            age2_str = f"{int(row2['Age'])}" if pd.notna(row2['Age']) else "?"
            title_text += f" vs {p2} ({pos2}) – {s2} – {row2['Team']} ({row2['Competition']}) – {age2_str} y/o"
        
        fig.update_layout(
            hovermode='closest',
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(
                    range=[0, 100],
                    tickvals=[0, 25, 50, 75, 100],
                    ticks='outside',
                    showticklabels=True,
                    ticksuffix='%',
                    tickfont=dict(color='white'),
                    gridcolor='gray'
                )
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            showlegend=True,
            title={
                'text': title_text,
                'x': 0.5,
                'xanchor': 'center'
            },
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Section explicative des métriques
        with st.expander("📘 Metrics Explanation (xPhysical)", expanded=False):
            st.markdown("""
- **PSV-99**: Peak sprint velocity at the 99th percentile. This metric reflects the maximum speed reached by a player, as well as their ability to reach it repeatedly or sustain it for a sufficient duration.
- **TOP 5 PSV-99**: Average of a player’s top 5 PSV-99 performances.
- **Total Distance P90**: Total distance covered, normalized per 90 minutes.
- **M/min P90**: Total distance covered divided by the number of minutes played. For TIP (respectively OTIP), divided by the number of TIP (resp. OTIP) minutes.
- **Running Distance P90**: Distance covered between 15 and 20 km/h.
- **HSR Distance P90**: Distance covered between 20 and 25 km/h.
- **HSR Count P90**: Number of actions above 20 km/h (1-second moving average), up to 25 km/h.
- **Sprinting Distance P90**: Distance covered above 25 km/h.
- **Sprint Count P90**: Number of actions above 25 km/h (1-second moving average).
- **HI Distance P90**: Distance covered above 20 km/h.
- **HI Count**: Sum of HSR Count and Sprint Count.
- **Medium Acceleration Count P90**: Number of accelerations between 1.5 and 3 m/s², lasting at least 0.7 seconds.
- **High Acceleration Count P90**: Accelerations above 3 m/s², lasting at least 0.7 seconds.
- **Medium Deceleration Count P90**: Decelerations between -1.5 and -3 m/s², lasting at least 0.7 seconds.
- **High Deceleration Count P90**: Decelerations below -3 m/s², lasting at least 0.7 seconds.
- **Explosive Acceleration to HSR Count P90**: Number of accelerations (as defined above) starting below 9 km/h and reaching at least 20 km/h.
- **Explosive Acceleration to Sprint Count P90**: Number of accelerations starting below 9 km/h and reaching at least 25 km/h.
""")

    
    # --- Onglet Index ---
    with tab3:
        # === MAPPINGS JOUEURS (optimisé une seule fois plus haut)
        # player_to_display = dict(zip(df["Player"], df["Display Name"]))
        # display_to_player = {v: k for k, v in player_to_display.items()}
        # display_options = sorted(player_to_display.values())

        # 1) Sélection Joueur & Saison
        col1, col2 = st.columns(2)

        with col1:
            default_display = next((name for name in display_options if "Artem Dovbyk" in name), display_options[0])
            player_display = st.selectbox("Select a player", display_options, index=display_options.index(default_display), key="idx_p1")
            player = display_to_player[player_display]

        with col2:
            seasons = sorted(df[df["Player"] == player]["Season"].dropna().unique())
            default_season = "2024/2025" if "2024/2025" in seasons else seasons[-1]
            season = st.selectbox("Select a season", seasons, index=seasons.index(default_season), key="idx_s1")

        # 2) Filtrer par Joueur + Saison
        df_fs = df[(df["Player"] == player) & (df["Season"] == season)]
        if df_fs.empty:
            st.warning("No data for this player/season.")
            st.stop()

        # 3) Filtre Club si plusieurs
        teams = df_fs["Team"].dropna().unique().tolist()
        if len(teams) > 1:
            team = st.selectbox("Select a team", teams, key="idx_team")
            df_fs = df_fs[df_fs["Team"] == team]
        else:
            team = teams[0]

        # 4) Filtre Poste si plusieurs
        positions = df_fs["Position Group"].dropna().unique().tolist()
        if len(positions) > 1:
            position = st.selectbox("Select a position", positions, key="idx_position")
        else:
            position = positions[0]
        df_fs = df_fs[df_fs["Position Group"] == position]

        # 5) Filtre Compétition si plusieurs
        competitions = df_fs["Competition"].dropna().unique().tolist()
        if len(competitions) > 1:
            competition = st.selectbox("Select a competition", competitions, key="idx_comp")
            df_fs = df_fs[df_fs["Competition"] == competition]
        else:
            competition = competitions[0]

        # 6) On continue avec df_p
        df_p = df_fs.copy()
        row = df_p.iloc[0]
        position = row["Position Group"]

        # — Affichage des infos du joueur
        age_str = f"{int(row['Age'])}" if pd.notna(row['Age']) else "?"
        info = (
            f"<div style='text-align:center; font-size:16px; margin:10px 0;'>"
            f"<b>{row['Short Name']}</b> – {row['Season']} – {row['Team']} "
            f"(<i>{row['Competition']}</i>) – {age_str} y/o"
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
            st.error(f"No defined scale for this position « {position} »")
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

        # — Construction du tableau de détail
        rows = []
        for metric_key, col_val in metric_map.items():
            raw_val = row.get(col_val, np.nan)
            pts     = row.get(note_map[metric_key], 0)
            max_pts = get_max_pts(metric_key)

            rows.append({
                "Metrics":      col_val,
                "Player Value": f"{raw_val:.2f}" if pd.notna(raw_val) else "NA",
                "Points":        f"{pts} / {max_pts}"
            })

        # — Total et index
        total_pts  = row.get("Note xPhysical", 0)
        total_max  = row.get("Note xPhy_max",  0)
        index_xphy = row.get("xPhysical",      0)
        rows.append({
            "Metrics":      "**Total**",
            "Player Value": "",
            "Points":        f"**{total_pts} / {total_max}**"
        })
        rows.append({
            "Metrics":      "Index xPhysical",
            "Player Value": "",
            "Points":        f"**{index_xphy}**"
        })

        detail_df = pd.DataFrame(rows)

        # — Jauge xPhysical
        df_peers = df[
            (df["Position Group"] == position) &
            (df["Season"] == season) &
            (df["Competition"] == row["Competition"])
        ].sort_values("xPhysical", ascending=False)
        mean_peer  = df_peers["xPhysical"].mean()
        rank       = int(df_peers.reset_index().index[df_peers["Player"] == player][0] + 1)
        total_peers= len(df_peers)
        hue        = 120 * (index_xphy / 100)
        bar_color  = f"hsl({hue:.0f}, 75%, 50%)"

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=index_xphy,
            number={'font': {'size': 48}},  # score en grand
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': bar_color, 'thickness': 0.25},
                'bgcolor': "rgba(255,255,255,0)",
                'borderwidth': 0,
                'shape': "angular",
                'steps': [{'range': [0, 100], 'color': 'rgba(100,100,100,0.3)'}],
                'threshold': {'line': {'color': "white", 'width': 4},
                              'thickness': 0.75,
                              'value': mean_peer}
            },
            domain={'x': [0,1], 'y': [0,1]},
            title={'text': f"<b>{rank}ᵉ/{total_peers}</b>", 'font': {'size': 20}}
        ))
        fig_gauge.update_layout(
            margin={'t':40,'b':0,'l':0,'r':0},
            paper_bgcolor="rgba(0,0,0,0)",
            height=300
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Label xPhy juste sous le score
        st.markdown(
            "<div style='text-align:center; font-size:18px; margin-top:-22px; margin-bottom:2px;'><b>xPhy</b></div>",
            unsafe_allow_html=True
        )
    
        # Phrase moyenne (si tu veux la garder)
        st.markdown(
            f"<div style='text-align:center; font-size:14px; margin-top:-8px; color:grey'>"
            f"xPhysical Average ({position} in {row['Competition']}): {mean_peer:.1f}"
            "</div>",
            unsafe_allow_html=True
        )

        # — Affichage du tableau
        st.markdown("### xPhysical Details")
        display_df = detail_df.set_index("Metrics")\
                              .style.set_properties(**{"text-align":"center"})
        st.dataframe(display_df)  
    
    # --- Onglet Top 50 xPhysical ---
    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            selected_competition = st.selectbox(
                "Competition",
                competition_list,
                index=competition_list.index("ITA - Serie A") if "ITA - Serie A" in competition_list else 0,
                key="top50_xphy_comp"
            )

        with col2:
            available_seasons = df[df["Competition"] == selected_competition]["Season"].dropna().unique().tolist()
            available_seasons = sorted(available_seasons)
            default_season = "2024/2025" if "2024/2025" in available_seasons else available_seasons[-1]
            selected_season = st.selectbox(
                "Season",
                available_seasons,
                index=available_seasons.index(default_season),
                key="top50_xphy_season"
            )

        selected_position = st.selectbox(
            "Position",
            position_list,
            index=position_list.index("Striker") if "Striker" in position_list else 0,
            key="top50_xphy_pos"
        )

        # Filtrage
        filtered_top = df[
            (df["Competition"] == selected_competition) &
            (df["Season"] == selected_season) &
            (df["Position Group"] == selected_position)
        ].copy()

        top_50 = filtered_top.sort_values(by="xPhysical", ascending=False).head(50).reset_index(drop=True)

        # Construction manuelle des rows
        rows = []
        for i, row in top_50.iterrows():
            age = int(row["Age"]) if pd.notna(row["Age"]) else "—"
            rows.append({
                "Rank":      i + 1,
                "Player":    row["Short Name"],
                "Team":    row["Team"],
                "Age":       age,
                "xPhysical": int(round(row["xPhysical"]))
            })

        display_df = pd.DataFrame(rows).set_index("Rank")

        # Mise en forme : Rank centré (en tant qu’index), le reste aligné selon logique demandée
        styled_df = display_df.style\
            .set_properties(subset=["Player", "Team", "Age", "xPhysical"], **{"text-align": "left"})\
            .set_table_styles([
                {"selector": "th", "props": [("text-align", "center")]},              # en-têtes colonnes
                {"selector": ".row_heading", "props": [("text-align", "center")]},   # valeurs d'index (Rank)
                {"selector": ".blank", "props": [("display", "none")]}               # coin vide
            ])

        st.dataframe(styled_df, use_container_width=True)
    
# ============================================= VOLET xTechnical ========================================================
elif page == "xTech/xDef":
    
    # Création des sous-onglets pour xTechnical
    tab1, tab2, tab3, tab4 = st.tabs(["Scatter Plot", "Radar", "Index", "Top 50"])

    # === Onglet Scatter Plot ===
    with tab1:
       
        with st.expander("📘 About the xTech/xDef Section", expanded=False):
            st.markdown("""
        This section provides access to event data, which quantifies what happens on the pitch in direct relation to individual player actions (passes, dribbles, duels, etc.).

        #### ⚠️ Data Coverage & Reliability
        All players who have appeared in available competitions are included, but only those with **at least 500 minutes played** provide a sufficiently robust sample for meaningful analysis.  

        #### 🗂️ What you can do in each tab:
        - **Scatter Plot:**  
          Explore the relationships between any two technical or defensive metrics, filter by competition, season, position, foot, age, or minutes, and highlight specific players or teams.

        - **Radar:**  
          Generate percentile-based radar charts for a selected player (or compare two players), visualizing their technical and/or defensive skillset compared to their positional peers.

        - **Index:**  
          View a detailed breakdown of a player's technical and defensive indexes.

        - **Top 50:**  
          Display the top 50 players by xTECH, xDEF, or the relevant goalkeeper indexes, with full filtering by competition, season, position, and minimum minutes.

        **All metrics are normalized per 90 minutes (P90), except where otherwise noted.**
        """)

        st.markdown("<div style='height: 2em;'></div>", unsafe_allow_html=True)

       # Ligne 1 : Saisons, Compétitions, Postes
        col1, col2, col3 = st.columns([1.2, 1.2, 1.2])
        with col1:
            selected_seasons_tech = st.multiselect(
                "Season(s)",
                options=season_list_tech,
                default=[]
            )
        with col2:
            selected_competitions_tech = st.multiselect(
                "Competition(s)",
                options=competition_list_tech,
                default=[]
            )
        with col3:
            selected_positions_tech = st.multiselect(
                "Position(s)",
                options=position_list_tech,
                default=[]
            )

        # Ligne 2 : Âge et Minutes Played côte à côte
        col4, col5 = st.columns([1, 1.2])
        with col4:
            age_min_tech, age_max_tech = int(df_tech["Age"].min()), int(df_tech["Age"].max())
            selected_age_tech = st.slider(
                "Age",
                min_value=age_min_tech,
                max_value=age_max_tech,
                value=(age_min_tech, age_max_tech),
                step=1
            )
        with col5:
            minutes_min, minutes_max = int(df_tech["Minutes"].min()), int(df_tech["Minutes"].max())
            selected_minutes_tech = st.slider(
                "Minutes Played",
                min_value=minutes_min,
                max_value=minutes_max,
                value=(300, minutes_max),
                step=50
            )

        # Ligne 3 : Preferred Foot et Add Player(s) côte à côte
        col6, col7 = st.columns([1, 1.5])
        with col6:
            selected_foot_tech = st.multiselect(
                "Preferred Foot",
                options=foot_list_tech,
                default=[]
            )
        with col7:
            filtered_players_tech = sorted(df_tech["Player Name"].dropna().unique())
            selected_extra_players_tech = st.multiselect(
                "Add Player(s)",
                options=filtered_players_tech,
                default=[],
                help="Add players outside filters"
            )
            
        # Application des filtres
        filtered_df_tech = df_tech.copy()

        if selected_seasons_tech:
            filtered_df_tech = filtered_df_tech[filtered_df_tech["Season Name"].isin(selected_seasons_tech)]
        if selected_positions_tech:
            filtered_df_tech = filtered_df_tech[filtered_df_tech["Position Group"].isin(selected_positions_tech)]
        if selected_competitions_tech:
            filtered_df_tech = filtered_df_tech[filtered_df_tech["Competition Name"].isin(selected_competitions_tech)]
        if selected_foot_tech:
            filtered_df_tech = filtered_df_tech[filtered_df_tech["Prefered Foot"].isin(selected_foot_tech)]

        # Filtrage sur l'âge
        filtered_df_tech = filtered_df_tech[
            (filtered_df_tech["Age"] >= selected_age_tech[0]) &
            (filtered_df_tech["Age"] <= selected_age_tech[1])
        ]

        # Filtrage sur les minutes
        filtered_df_tech = filtered_df_tech[
            (filtered_df_tech["Minutes"] >= selected_minutes_tech[0]) &
            (filtered_df_tech["Minutes"] <= selected_minutes_tech[1])
        ]

        # Recalcul des joueurs filtrés pour exclure ceux déjà présents
        filtered_players_tech = sorted(filtered_df_tech["Player Name"].dropna().unique())
        available_extra_players_tech = sorted(
            [p for p in player_list_tech if p not in filtered_players_tech]
        )

        # Ajout des joueurs hors filtre sélectionnés
        if selected_extra_players_tech:
            extra_df_tech = df_tech[df_tech["Player Name"].isin(selected_extra_players_tech)]
            filtered_df_tech = pd.concat([filtered_df_tech, extra_df_tech]).drop_duplicates()
        
        # Bouton d'export CSV de la sélection actuelle
        csv = filtered_df_tech.to_csv(index=False)
        st.download_button(
            label="Download selection as CSV",
            data=csv,
            file_name="selection_event_data.csv",
            mime="text/csv",
            key="download_scatter_csv"
        )
        
        st.markdown("---")        
                
        # Mapping noms internes → noms affichés
        metric_display_map = {
            # === Index ===
            "xTECH": "xTECH",
            "xDEF": "xDEF",
            
            # === Scoring ===
            "Npg P90": "NP Goals",
            "Op Assists P90": "OP Assists",
            "Conversion Ratio": "Conversion %",
            "Scoring Contribution": "Contribution G+A",

            # === Shooting ===
            "Shots P90": "Shots",
            "Np Shots P90": "Shots",
            "Shot On Target Ratio": "Shooting %",
            "Np Xg P90": "NP xG",
            "Np Xg Per Shot": "xG/Shot",

            # === Passing / Creativity ===
            "Npxgxa P90": "NPxG + xA",
            "Op Xa P90": "OP xA",
            "Op Key Passes P90": "OP Key Passes",
            "Shots Key Passes P90": "Shots + Key Passes",
            "Op Passes Into And Touches Inside Box P90": "OP Passes + Touches Into Box",
            "Through Balls P90": "Throughballs",
            "Crosses P90": "Crosses",
            "Crossing Ratio": "Crossing %",
            "Deep Progressions P90": "Deep Progressions",
            "Deep Completions P90": "Deep Completions",
            "Op Xgbuildup P90": "OP xG Buildup",
            "Sp Key Passes P90": "Set Pieces Key Passes",
            "Sp Xa P90": "Set Pieces xA",
            
            # === OBV ===
            "Obv P90": "OBV", 
            "Obv Pass P90": "OBV Pass", 
            "Obv Shot P90": "OBV Shot", 
            "Obv Defensive Action P90": "OBV Def. Act.", 
            "Obv Dribble Carry P90": "OBV Dribble & Carry",

            # === Possession / Ball use ===
            "Op Passes P90": "OP Passes",
            "Passing Ratio": "Passing %",
            "Pressured Passing Ratio" : "Pressured Passing %",
            "Pressured Passing Ratio": "Pressured Passing %",
            "Long Balls P90": "Long Ball",
            "Long Ball Ratio": "Long Ball %",
            "Dribbles P90": "Dribbles Succ.",
            "Dribble Ratio": "Dribble %",
            "Carries P90": "Carries",
            "Turnovers P90": "Turnovers",
            "Dispossessions P90": "Dispossessions",

            # === Defensive ===
            "Padj Pressures P90": "PAdj Pressures",
            "Counterpressures P90": "Counterpressures",
            "Fhalf Pressures P90": "Pressures in Opp. Half",
            "Pressure Regains P90": "Pressure Regains",
            "Average X Pressure" : "Average Pressure Distance",
            "Ball Recoveries P90": "Ball Recoveries",
            "Fhalf Ball Recoveries P90": "Ball Recoveries in Opp. Half",
            "Padj Interceptions P90": "PAdj Interceptions",
            "Padj Tackles P90": "PAdj Tackles",
            "Padj Tackles And Interceptions P90": "PAdj Tackles And Interceptions",
            "Tackles And Interceptions P90": "Tackles And Interceptions",
            "Challenge Ratio": "Tack./Dribbled Past %",

            # === Aerial / Blocks ===
            "Hops": "HOPS",
            "Aerial Wins P90": "Aerial Wins",
            "Aerial Ratio": "Aerial Win %",
            "Blocks Per Shot": "Blocks/Shot",
            "Padj Clearances P90" : "PAdj Clearances",

            # === Autres ===
            "Errors P90": "Errors",
            "Penalty Wins P90": "Penalty Won",
            
            # === GK ===
            "xTech GK Save (/100)": "xSave GK", 
            "xTech GK Usage (/100)": "xUsage GK",
            "Save Ratio": "Save % (GK)", 
            "Xs Ratio": "Expected Save % (GK)", 
            "Gsaa P90": "Goals Saved Above Average (GK)", 
            "Clcaa": "Claims % (GK)", 
            "Pass Into Danger Ratio": "Pass Into Danger % (GK)",
            "Obv Gk P90": "OBV GK"
        }

        # Liste ordonnée des métriques à afficher dans les menus X/Y
        metric_keys = list(metric_display_map.keys())

        # Ligne 1 : Axe X / Axe Y côte à côte
        colx, coly = st.columns(2)
        with colx:
            selected_xaxis_tech = st.selectbox(
                "X Axis",
                options=metric_keys,
                format_func=lambda x: metric_display_map.get(x, x),
                index=0
            )
        with coly:
            selected_yaxis_tech = st.selectbox(
                "Y Axis",
                options=metric_keys,
                format_func=lambda x: metric_display_map.get(x, x),
                index=1
            )

        # Ligne 2 : surligner joueurs / équipes côte à côte
        players_filtered = sorted(filtered_df_tech["Player Last Name"].dropna().unique())
        teams_filtered = sorted(filtered_df_tech["Team Name"].dropna().unique())

        col1, col2 = st.columns(2)
        with col1:
            highlight_players_tech = st.multiselect(
                "Highlight Player(s)",
                options=players_filtered,
                default=[]
            )
        with col2:
            highlight_teams_tech = st.multiselect(
                "Highlight Team(s)",
                options=teams_filtered,
                default=[]
            )
        
        # Ajout label + typage
        plot_df_tech = filtered_df_tech.copy()
        plot_df_tech["Player_Label"] = plot_df_tech["Player Last Name"] + " " + plot_df_tech["season_short"]

        # Typage
        plot_df_tech[selected_xaxis_tech] = pd.to_numeric(plot_df_tech[selected_xaxis_tech], errors='coerce')
        plot_df_tech[selected_yaxis_tech] = pd.to_numeric(plot_df_tech[selected_yaxis_tech], errors='coerce')
        plot_df_tech = plot_df_tech.dropna(subset=[selected_xaxis_tech, selected_yaxis_tech])

        # Sélection des labels (si > 300, on sample)
        nb_points = len(plot_df_tech)
        label_df_tech = plot_df_tech if nb_points <= 300 else plot_df_tech.sample(n=300, random_state=42)

        # Marquage couleurs
        plot_df_tech["color_marker"] = "blue"
        label_df_tech["color_marker"] = "blue"

        if highlight_players_tech:
            mask_p = plot_df_tech["Player Last Name"].isin(highlight_players_tech)
            plot_df_tech.loc[mask_p, "color_marker"] = "yellow"
            label_df_tech.loc[mask_p, "color_marker"] = "yellow"

        if highlight_teams_tech:
            mask_t = plot_df_tech["Team Name"].isin(highlight_teams_tech)
            plot_df_tech.loc[mask_t, "color_marker"] = "red"
            label_df_tech.loc[mask_t, "color_marker"] = "red"

        # Plot de base
        fig = px.scatter(
            plot_df_tech,
            x=selected_xaxis_tech,
            y=selected_yaxis_tech,
            hover_name="Player Name",
            hover_data=["Team Name", "Age", "Position Group"],
            color="color_marker",
            color_discrete_map={"blue":"blue", "yellow":"yellow", "red":"red"},
        )
        fig.update_layout(showlegend=False)
        fig.update_traces(marker=dict(size=10 if nb_points < 300 else 5))

        # Ajout des étiquettes
        fig_labels = px.scatter(
            label_df_tech,
            x=selected_xaxis_tech,
            y=selected_yaxis_tech,
            text="Player_Label",
            hover_name="Player_Label",
            hover_data=["Team Name", "Age", "Position Group"],
            color="color_marker",
            color_discrete_map={"blue":"blue", "yellow":"yellow", "red":"red"},
        )
        fig_labels.update_traces(hoverinfo='skip', hovertemplate=None)

        import random
        positions = [
            "top left", "top center", "top right",
            "middle left", "middle right",
            "bottom left", "bottom center", "bottom right"
        ]
        text_positions = [random.choice(positions) for _ in range(len(label_df_tech))]

        fig_labels.update_traces(
            textposition=text_positions,
            textfont=dict(size=9, color="black"),
            marker=dict(size=6),
            cliponaxis=False
        )

        # Ajout des traces de texte
        for trace in fig_labels.data:
            fig.add_trace(trace)

        # Moyennes croisées
        fig.add_vline(x=plot_df_tech[selected_xaxis_tech].mean(), line_dash="dash", line_color="gray")
        fig.add_hline(y=plot_df_tech[selected_yaxis_tech].mean(), line_dash="dash", line_color="gray")

        fig.update_layout(
            width=1200,
            height=700,
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="gainsboro", zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="gainsboro", zeroline=False)
        )

        st.plotly_chart(fig, use_container_width=False)
        
        with st.expander("📘 Metric Definitions (xTechnical)", expanded=False):
            st.markdown("""
            ### 🔹 Index
            - **xTECH**: Contribution to build-up, passing, creativity, and attack.
            - **xDEF**: Contribution to defensive activity, pressure, recoveries.

            ### 🎯 Scoring
            - **NP Goals**: Goals scored (not including penalties).
            - **OP Assists**: Number of assists from open play.
            - **Conversion %**: Percentage of non-penalty shots a player takes that are converted into goals.
            - **Contribution G+A**: Non-penalty goals and assists. A combined measure of the direct goal contribution of a player via goalscoring or goal assisting.

            ### 🔫 Shooting
            - **Shots**: Number of non-penalty shots a player takes.
            - **Shooting %**: The percentage of total shots by a player that are on target (includes goals, saved, and cleared off line).
            - **NP xG**: Cumulative expected goal value of all non-penalty shots.
            - **xG/Shot**: Non-penalty expected goals per shot.

            ### 🧠 Passing & Creativity
            - **NPxG + xA**: Combined non-penalty xG and xA.
            - **OP xA**: xG assisted from open play.
            - **OP Key Passes**: Passes that create shots for teammates, just from open play.
            - **Shots + Key Passes**: Non-penalty shots and key passes. A combined measure of a player's contribution to shots via shots themselves or the key pass prior to the shot.
            - **OP Passes + Touches Into Box**: Successful passes into the box from outside the box (open play) + touches inside the box.
            - **Throughballs**: A completed pass splitting the defence for a teammate to run onto.
            - **Crosses / Crossing %**: Volume and success rate of crosses.
            - **Deep Progressions**: Passes and dribbles/carries into the opposition final third.
            - **Deep Completions**: Successful passes within 20 metres of the opposition goal.
            - **OP xG Buildup**: A model that attributes the xG value of the final shot to all players involved in the entire possession. The buildup version omits xG and xG Assisted to focus on possession work prior to the end of the chain.
            - **Set Pieces Key Passes / xA**: Key passes and xA generated from set pieces.

            ### 📈 OBV Metrics
            - **OBV**: On Ball Value Added (net) total (all event types).
            - **OBV Pass**: On Ball Value Added (net) from Passes. 
            - **OBV Shot**: On Ball Value Added (net) from Shots.
            - **OBV Dribble & Carry**: On Ball Value Added (net) from Dribbles and Carries.
            - **OBV Def. Act.**: On Ball Value Added (net) from Defensive Actions.

            ### 🏃 Possession & Ball Use
            - **OP Passes**: Number of attempted passes in open play.
            - **Passing %**: Passing completion rate.
            - **Pressured Passing %**: Proportion of pressured passes that were completed.
            - **Long Balls / Long Ball %**: Long passes volume and success rate.
            - **Dribbles Succ.**: How often a player successfully dribbles past an opponent.
            - **Dribble %**: Percentage of dribbles that were successful.
            - **Carries**: Number of ball carries (A player controls the ball at their feet while moving or standing still).
            - **Turnovers / Dispossessions**: Ball losses by poor control or opponent tackle.

            ### 🛡 Defensive Actions
            - **PAdj Pressures**: Possession adjusted pressures.
            - **Counterpressures**: Pressures exerted within 5 seconds of a turnover.
            - **Pressures in Opp. Half**: How many pressures are exerted in the opposition (final) half of the pitch.
            - **Pressure Regains**: Ball is regained within 5 seconds of a player pressuring an opponent.
            - **Average Pressure Distance**: The average distance from the goal line that the player presses opponents with the ball. The scale here is the x-axis of the pitch, measured from 0-100.
            - **Ball Recoveries / in Opp. Half**: How many ball recoveries the player made + made in the opposition (final) half of the pitch.
            - **PAdj Interceptions**: Number of interceptions adjusted proportionally to the possession volume of a team.
            - **PAdj Tackles**: Number of tackles adjusted proportionally to the possession volume of a team.
            - **Tackles And Interceptions**: Combination of tackles and interceptions.
            - **Tack./Dribbled Past %**: Percentage of time a player makes a tackle when going into a duel vs getting dribbled past.

            ### 🧱 Aerial / Blocking
            - **HOPS**: HOPS is a model that measures a player's ability to win aerial duels. HOPS take into account the aerial ability of the opposing duellist in order to credit the winner of the duel appropriately.
            - **Aerial Wins / Aerial Win %**: Success and volume of aerial duels.
            - **Blocks/Shot**: Blocks per shot faced.
            - **PAdj Clearances**: Number of clearances adjusted proportionally to the possession volume of a team.

            ### ⚠️ Miscellaneous
            - **Errors**: How many errors the player makes per 90. An error is an on the ball mistake that led to a shot.
            - **Penalty Won**: Penalties won by the player.

            ### 🧤 Goalkeeping (GK)
            - **Save %**: Percentage of on-target shots that were saved by the goalkeeper.
            - **Expected Save %**: Given the post-shot xG (modelled from on frame location) of shots faced by the goalkeeper what % would we expect them to save?.
            - **Goals Saved Above Average**: How many goals did the keeper save/concede versus expectation (post-shot xG faced)? This is representative of how many goals the goalkeeper's saves prevented wthin a season.
            - **Claims % (CLCAA)**: Claims or CCAA% (Claimable Collection Attempts over Average), is a measure of how likely the goalkeeper is to attempt to claim a "claimable" pass, versus the average goalkeeper attempted claim rate.
            - **Pass Into Danger %**: Percentage of passes made where the recipient was deemed to be under pressure or was next engaged with a defensive action.
            - **OBV GK**: On Ball Value Added (net) Goalkeeper.

            _All values are per 90 minutes unless otherwise specified._
            """)
        
    # === Onglet Radar ===
    with tab2:
        # Sélection Joueur 1 + Saison
        col1, col2 = st.columns(2)
        with col1:
            display_options = sorted(df_tech["Display Name"].dropna().unique())
            default_display_name = next(
                (name for name in display_options if "Artem Dovbyk" in name),
                display_options[0]
            )
            p1_display = st.selectbox(
                "Player 1",
                options=display_options,
                index=display_options.index(default_display_name),
                key="tech_radar_p1"
            )
            p1 = display_to_playername[p1_display]
        with col2:
            seasons1 = sorted(df_tech[df_tech["Player Name"] == p1]["Season Name"].dropna().unique().tolist())
            s1 = st.selectbox("Season 1", seasons1, key="tech_radar_s1")

        df1 = df_tech[(df_tech["Player Name"] == p1) & (df_tech["Season Name"] == s1)]
        if df1.empty:
            st.warning("Aucune donnée trouvée pour ce joueur et cette saison.")
            st.stop()

        # Calcul de la compétition principale (où le joueur a le plus joué sur cette saison)
        df_allplayer1 = df_tech[(df_tech["Player Name"] == p1) & (df_tech["Season Name"] == s1)]
        comp_minutes1 = df_allplayer1.groupby("Competition Name")["Minutes"].sum().sort_values(ascending=False)
        main_competition1 = comp_minutes1.index[0] if not comp_minutes1.empty else None

        competitions1 = df1["Competition Name"].dropna().unique().tolist()
        # --------------------------
        # *** ZONE DES 2 FILTRES CÔTE À CÔTE ***
        # --------------------------
        colA, colB = st.columns(2)
        with colA:
            if len(competitions1) > 1:
                index_main1 = competitions1.index(main_competition1) if main_competition1 in competitions1 else 0
                comp1 = st.selectbox(
                    "Competition 1",
                    sorted(competitions1),
                    key="tech_radar_comp1",
                    index=index_main1
                )
                df1 = df1[df1["Competition Name"] == comp1]
            else:
                comp1 = competitions1[0]

        # Extraction du poste pour choix du template
        if "Position Group" in df1.columns and df1["Position Group"].notna().any():
            pos1 = df1["Position Group"].dropna().unique()[0]
        else:
            pos1 = "Striker"  # fallback
        position_group_to_template = {
            "Goalkeeper": "Goalkeeper",
            "Central Defender": "Central Defender",
            "Full Back": "Full Back",
            "Midfielder": "Midfielder (CDM)",
            "Attacking Midfielder": "Attacking Midfielder",
            "Winger": "Winger",
            "Striker": "Striker"
        }
        default_template = position_group_to_template.get(pos1, "Striker")
        with colB:
            selected_template = st.selectbox(
                "Choose a template",
                options=list(metric_templates_tech.keys()),
                index=list(metric_templates_tech.keys()).index(default_template)
            )
        # --------------------------
        # Suite du code inchangée :
        teams1 = df1["Team Name"].dropna().unique().tolist()
        if len(teams1) > 1:
            team1 = st.selectbox("Team 1", teams1, key="tech_radar_team1")
            df1 = df1[df1["Team Name"] == team1]
        else:
            team1 = teams1[0]
        comp1 = df1["Competition Name"].dropna().unique()[0]
        row1 = df1.iloc[0]

        metrics = metric_templates_tech[selected_template]
        labels = metric_labels_tech[selected_template]

        # Comparaison
        # 1. Liste des joueurs AS Roma
        roma_players = df_tech[df_tech["Team Name"] == "AS Roma"]["Player Name"].dropna().unique().tolist()

        # 2. Tous les autres joueurs sauf ceux de la Roma déjà inclus
        all_players = df_tech["Player Name"].dropna().unique().tolist()
        other_players = [p for p in all_players if p not in roma_players]

        # 3. Liste ordonnée pour le selectbox
        player2_options = roma_players + other_players
        
        compare = st.checkbox("Compare to a 2nd player")
        if compare:
            col3, col4 = st.columns(2)
            with col3:
                p2_display = st.selectbox("Player 2", display_options, key="tech_radar_p2")
                p2 = display_to_playername[p2_display]
            with col4:
                seasons2 = sorted(df_tech[df_tech["Player Name"] == p2]["Season Name"].dropna().unique().tolist())
                s2 = st.selectbox("Season 2", seasons2, key="tech_radar_s2")
            df2 = df_tech[(df_tech["Player Name"] == p2) & (df_tech["Season Name"] == s2)]
            if df2.empty:
                st.warning("Aucune donnée trouvée pour le joueur 2.")
                st.stop()
        
            # === Sélection compétition pour Joueur 2 ===
            df_allplayer2 = df_tech[(df_tech["Player Name"] == p2) & (df_tech["Season Name"] == s2)]
            comp_minutes2 = df_allplayer2.groupby("Competition Name")["Minutes"].sum().sort_values(ascending=False)
            main_competition2 = comp_minutes2.index[0] if not comp_minutes2.empty else None
        
            competitions2 = df2["Competition Name"].dropna().unique().tolist()
            if len(competitions2) > 1:
                index_main2 = competitions2.index(main_competition2) if main_competition2 in competitions2 else 0
                comp2 = st.selectbox("Competition 2", sorted(competitions2), key="tech_radar_comp2", index=index_main2)
                df2 = df2[df2["Competition Name"] == comp2]
            else:
                comp2 = competitions2[0]
        
            teams2 = df2["Team Name"].dropna().unique().tolist()
            if len(teams2) > 1:
                team2 = st.selectbox("Team 2", teams2, key="tech_radar_team2")
                df2 = df2[df2["Team Name"] == team2]
            else:
                team2 = teams2[0]
        
            row2 = df2.iloc[0]
            pos2 = row2["Position Group"] if "Position Group" in row2 else ""

        # Peers
        top5_leagues = ["Premier League", "Ligue 1", "La Liga", "Serie A", "1. Bundesliga"]
        peers = df_tech[
            (df_tech["Position Group"] == pos1) &
            (df_tech["Season Name"] == s1) &
            (df_tech["Competition Name"].isin(top5_leagues)) &
            (df_tech["Minutes"] >= 600)
        ]
        if peers.empty:
            peers = df_tech[
                (df_tech["Position Group"] == pos1) &
                (df_tech["Season Name"] == s1) &
                (df_tech["Minutes"] >= 600)
            ]

        # Percentiles
        def pct_rank(series, value):
            arr = series.dropna().values
            if len(arr) == 0:
                return 0.0
            lower = (arr < value).sum()
            equal = (arr == value).sum()
            return (lower + 0.5 * equal) / len(arr) * 100

        # Liste des métriques à inverser
        inverse_metrics = ["Turnovers P90", "Dispossessions P90"]

        # Calcul des percentiles en tenant compte de l’inversion
        r1 = [
            100 - pct_rank(peers[m], row1[m]) if m in inverse_metrics else pct_rank(peers[m], row1[m])
            for m in metrics
        ]

        if compare:
            r2 = [
                100 - pct_rank(peers[m], row2[m]) if m in inverse_metrics else pct_rank(peers[m], row2[m])
                for m in metrics
            ]
        else:
            r2 = [
                100 - pct_rank(peers[m], peers[m].mean()) if m in inverse_metrics else pct_rank(peers[m], peers[m].mean())
                for m in metrics
            ]


        r1_closed = r1 + [r1[0]]
        r2_closed = r2 + [r2[0]]
        metrics_closed = labels + [labels[0]]

        raw1 = [row1[m] for m in metrics]
        raw1_closed = raw1 + [raw1[0]]
        raw2 = [row2[m] for m in metrics] if compare else [peers[m].mean() for m in metrics]
        raw2_closed = raw2 + [raw2[0]]

        # Radar plot
        # 8) Construction du radar Plotly
        fig = go.Figure()

        # 1) Joueur 1 – Calque “fill”
        fig.add_trace(go.Scatterpolar(
            r=r1_closed,
            theta=metrics_closed,
            mode='lines',
            hoverinfo='skip',
            fill='toself',
            fillcolor='rgba(255,215,0,0.3)',
            line=dict(color='gold', width=2),
            name=p1
        ))
        # Calque invisible pour hover
        fig.add_trace(go.Scatterpolar(
            r=r1_closed,
            theta=metrics_closed,
            mode='markers',
            hoverinfo='text',
            hovertext=[
                f"<b>{theta}</b><br>Value: {raw:.2f}<br>Percentile: {r:.1f}%"
                for theta, raw, r in zip(metrics_closed, raw1_closed, r1_closed)
            ],
            marker=dict(size=12, color='rgba(255,215,0,0)'),  # invisible
            showlegend=False
        ))

        # 2) Joueur 2 ou moyenne – Calque “fill”
        fig.add_trace(go.Scatterpolar(
            r=r2_closed,
            theta=metrics_closed,
            mode='lines',
            hoverinfo='skip',
            fill='toself',
            fillcolor='rgba(144,238,144,0.3)',
            line=dict(color=(compare and 'cyan') or 'lightgreen', width=2),
            name=(compare and p2) or 'Top5 Average'
        ))
        # Calque invisible pour hover
        fig.add_trace(go.Scatterpolar(
            r=r2_closed,
            theta=metrics_closed,
            mode='markers',
            hoverinfo='text',
            hovertext=[
                f"<b>{theta}</b><br>Value: {raw:.2f}<br>Percentile: {r:.1f}%"
                for theta, raw, r in zip(metrics_closed, raw2_closed, r2_closed)
            ],
            marker=dict(size=12, color='rgba(144,238,144,0)'),  # invisible
            showlegend=False
        ))

        # Titre dynamique
        team1 = row1["Team Name"] if "Team Name" in row1 else ""
        minutes1 = int(row1["Minutes"]) if "Minutes" in row1 else "NA"
        title_text = f"{p1} ({pos1}) – {s1} – {team1} - {minutes1} min"
        if compare:
            team2 = row2["Team Name"] if "Team Name" in row2 else ""
            minutes2 = int(row2["Minutes"]) if "Minutes" in row2 else "NA"
            pos2 = row2["Position Group"] if "Position Group" in row2 else ""
            title_text += f" vs {p2} ({pos2}) – {s2} – {team2} - {minutes2} min"

        # 9) Mise en forme finale
        fig.update_layout(
            hovermode='closest',
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(
                    range=[0, 100],
                    tickvals=[0, 25, 50, 75, 100],
                    ticks='outside',
                    showticklabels=True,
                    ticksuffix='%',
                    tickfont=dict(color='white'),
                    gridcolor='gray'
                ),
                angularaxis=dict(
                rotation=90,  # <<< Pour commencer en haut
                direction="clockwise"  # (optionnel) explicite le sens de rotation
                )
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            showlegend=True,
            title={
                'text': title_text,
                'x': 0.5,
                'xanchor': 'center'
            },
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # 📘 Metric Definitions: integrated into Radar tab
        definitions_rich = {
            "Passing%": "Passing completion rate.",
            "OP Passes": "Number of attempted passes in open play.",
            "Long Ball%": "Accuracy of long balls attempted.",
            "Long Balls": "Number of completed long balls",
            "Being Press. Change in Pass Length": "Change in average pass length when under pressure.",
            "Claims - CCAA%": "Claims or CCAA% (Claimable Collection Attempts over Average), is a measure of how likely the goalkeeper is to attempt to claim a \"claimable\" pass, versus the average goalkeeper attempted claim rate.",
            "GK Aggressive Distance": "Average distance from goal when goalkeeper performs defensive actions outside the box.",
            "Goals Saved Above Average": "How many goals the keeper saved/conceded versus expectation (post-shot xG faced).",
            "Save%": "Percentage of on-target shots saved by the goalkeeper.",
            "On Target Shots Faced": "Number of on-target shots faced by the goalkeeper.",
            "Pass into Danger%": "Percentage of passes made where the recipient was deemed under pressure or was next engaged with a defensive action.",
            "Pressured Pass%": "Proportion of pressured passes that were completed.",
            "Aerial Win%": "Percentage of aerial duels won.",
            "Aerial Wins": "Number of aerial duels won.",
            "PAdj Tackles And Interceptions": "Number of tackles and interceptions adjusted proportionally to the possession volume of a team.",
            "Pressure Regains": "Ball is regained within 5 seconds of a player pressuring an opponent.",
            "Defensive Action Regains": "Times a player’s team won the ball back within 5 seconds of the player making a defensive action against an opponent.",
            "Pass OBV": "On Ball Value Added (net) from Passes.",
            "Dribble & Carry OBV": "On Ball Value Added (net) from Dribbles and Carries.",
            "Fouls": "Number of fouls committed per 90 minutes.",
            "Opp. Half Ball Recoveries": "How many ball recoveries the player made in the opposition (final) half of the pitch.",
            "Average Pressure Distance": "The average distance from the goal line that the player presses opponents with the ball. The scale here is the x-axis of the pitch, measured from 0-100.",
            "Tack/Dribbled Past %": "Success rate in duels (tackles vs times dribbled past).",
            "PAdj Pressures": "Possession adjusted pressures.",
            "PAdj Interceptions": "Interceptions adjusted for possession volume.",
            "PAdj Clearances": "Clearances adjusted for possession volume.",
            "Blocks/Shot": "Blocks made per shot faced.",
            "Errors": "On-the-ball mistakes that lead to a shot.",
            "Dispossessed": "Times dispossessed by opponent intervention.",
            "Turnovers": "Number of possessions lost through miscontrol or errant passing.",
            "Shots": "Number of non-penalty shots a player takes.",
            "Carries": "Number of ball carries (player controls the ball at feet while moving or standing still).",
            "Deep Progressions": "Passes and dribbles/carries into the opposition final third.",
            "Successful Crosses": "Number of crosses completed to a teammate.",
            "Crossing %": "Success rate of crosses completed.",
            "Counterpressures in Opp. Half": "Counterpressures applied in the opponent’s half.",
            "Pressures in Opp. Half": "Pressures exerted in the opposition half of the pitch.",
            "PAdj Tackles": "Tackles adjusted for possession volume.",
            "Successful Dribbles": "Dribbles that successfully beat an opponent.",
            "Touches In Box": "Number of touches inside the opposition box.",
            "Passes Inside Box": "Number of passes played into the opposition box.",
            "Shots & Key Passes": "Total of shots taken and key passes made.",
            "xG & xG Assisted": "Combined value of xG and xA from all actions.",
            "Counterpressures": "Immediate pressure applied after possession loss.",
            "Throughballs": "A completed pass splitting the defence for a teammate to run onto.",
            "xG": "Cumulative expected goal value of all shots taken.",
            "Key Passes": "Passes that create shots for teammates.",
            "Fouls Won": "Number of fouls drawn per 90 minutes.",
            "xG/Shot": "Average xG per shot.",
            "Shooting%": "The percentage of total shots that are on target.",
            "NP Goals": "Goals scored (not including penalties).",
            "Average Def. Action Distance": "The average distance from the goal line that the player successfully makes a defensive action. The scale is the x-axis of the pitch, measured from 0-100.",
            "PAdj Tackles & Interceptions": "Tackles + Interceptions per 90 (possession adjusted).",
            "Padj Tackles And Interceptions": "Tackles + Interceptions per 90 (possession adjusted).",
            "OP Passes + Touches In Box": "Successful passes into the box from outside the box (open play) + touches inside the box.",
            "OP xGAssisted": "xG assisted from open play.",
            "xGBuildup": "xG buildup value of a player’s involvement in possession sequences, excluding their own xG and xA.",
            "Scoring Contribution": "Non-penalty goals and assists. A combined measure of the direct goal contribution of a player via goalscoring or goal assisting.",
            "Touches Inside Box": "Number of touches inside the opposition box.",
            "Open Play xG Assisted": "Expected assists from open play passes.",
            "Tack/Dribbled Past%": "Percentage of time a player makes a tackle when going into a duel vs getting dribbled past."
        }

        # 📘 Dynamic display below radar
        with st.expander("📘 Metric Definitions (shown on this radar only)", expanded=False):
            st.markdown("Only the metrics shown on the selected radar are explained below.\n")
            for label in metric_labels_tech[selected_template]:
                explanation = definitions_rich.get(label, "❓ Definition not available.")
                st.markdown(f"- **{label}**: {explanation}")


        
    # === Onglet Index ===
    with tab3:
        # Sélection Joueur + Saison
        col1, col2 = st.columns(2)
        with col1:
            display_options = sorted(df_tech["Display Name"].dropna().unique())
            default_display_name = next((name for name in display_options if "Artem Dovbyk" in name), display_options[0])
            p1_display = st.selectbox("Player", display_options, index=display_options.index(default_display_name), key="tech_index_p1")
            p1 = display_to_playername[p1_display]
        with col2:
            seasons = sorted(df_tech[df_tech["Player Name"] == p1]["Season Name"].dropna().unique())
            s1 = st.selectbox("Season", seasons, index=len(seasons) - 1, key="tech_index_s1")

        # Filtrage Joueur + Saison
        df1 = df_tech[(df_tech["Player Name"] == p1) & (df_tech["Season Name"] == s1)]
        if df1.empty:
            st.warning("No data found.")
            st.stop()
        
        # Sélection compétition principale (où le joueur a le plus joué)
        df_allplayer = df_tech[(df_tech["Player Name"] == p1) & (df_tech["Season Name"] == s1)]
        comp_minutes = df_allplayer.groupby("Competition Name")["Minutes"].sum().sort_values(ascending=False)
        main_competition = comp_minutes.index[0] if not comp_minutes.empty else None
        
        competitions = df1["Competition Name"].dropna().unique().tolist()
        if len(competitions) > 1:
            # Préselection sur la compétition principale
            index_main = competitions.index(main_competition) if main_competition in competitions else 0
            comp = st.selectbox("Competition", sorted(competitions), key="tech_index_comp", index=index_main)
            df1 = df1[df1["Competition Name"] == comp]
        else:
            comp = competitions[0]
        
        # Ensuite seulement : sélection club si plusieurs
        teams = df1["Team Name"].dropna().unique().tolist()
        if len(teams) > 1:
            team1 = st.selectbox("Team", teams, key="tech_index_team1")
            df1 = df1[df1["Team Name"] == team1]
        else:
            team1 = teams[0]
        
        row = df1.iloc[0]
        is_gk = row["Position Group"] == "Goalkeeper"
        pos = row["Position Group"]
        comp = row["Competition Name"]
        age = int(row["Age"])
        minutes = int(row["Minutes"])

        # Mapping colonnes selon poste
        if pos == "Goalkeeper":
            tech_col = "xTech GK Usage (/100)"
            def_col = "xTech GK Save (/100)"
            tech_label = "Usage"
            def_label = "Save"
        else:
            tech_col = "xTECH"
            def_col = "xDEF"
            tech_label = "xTECH"
            def_label = "xDEF"

        tech_score = row.get(tech_col, np.nan)
        def_score = row.get(def_col, np.nan)

        # Filtrage pairs pour chaque jauge
        peers = df_tech[
            (df_tech["Position Group"] == pos) &
            (df_tech["Season Name"] == s1) &
            (df_tech["Competition Name"] == comp) &
            (df_tech["Minutes"] >= 600)
        ]
        mean_tech = peers[tech_col].mean()
        mean_def = peers[def_col].mean()
        
        sorted_peers_tech = peers.sort_values(tech_col, ascending=False).reset_index(drop=True)
        if row["Player Name"] in sorted_peers_tech["Player Name"].values:
            rank_tech = sorted_peers_tech[sorted_peers_tech["Player Name"] == row["Player Name"]].index[0] + 1
        else:
            rank_tech = "—"
            
        sorted_peers_def = peers.sort_values(def_col, ascending=False).reset_index(drop=True)
        if row["Player Name"] in sorted_peers_def["Player Name"].values:
            rank_def = sorted_peers_def[sorted_peers_def["Player Name"] == row["Player Name"]].index[0] + 1
        else:
            rank_def = "—"
        
        total_peers = len(sorted_peers_tech)  # ou sorted_peers_def, c’est la même longueur
            
        # Affichage infos joueur
        info = (
            f"<div style='text-align:center; font-size:16px; margin:10px 0;'>"
            f"<b>{p1} ({pos})</b> – {s1} – {team1} "
            f"(<i>{comp}</i>) – {age} y/o – {minutes} min"
            "</div>"
        )
        st.markdown(info, unsafe_allow_html=True)

        # --- Deux colonnes côte à côte
        col1, col2 = st.columns(2)
        hue_def  = 120 * (def_score / 100)
        bar_color_def  = f"hsl({hue_def:.0f}, 75%, 50%)"
        with col1:
            if is_gk:
                # ========== DEF GK ========== 
                gk_def_metrics = [
                    ("xTech GK GSAA %", "GSAA %"),
                    ("xTech GK Save %", "Save %"),
                    ("xTech GK Aggressive Distance", "Aggressive Distance"),
                    ("xTech GK Long Ball %", "Long Ball %"),
                    ("xTech GK OPxGBuildup", "OPxGBuildup"),
                ]
                metric_rows = []
                for col, label in gk_def_metrics:
                    val = row.get(col, None)
                    metric_rows.append({
                        "Mectrics": label,
                        "Player Figures": f"{val:.2f}" if pd.notna(val) else "NA",
                        "Points": ""  # Pas de barème pour GK, adapter si besoin
                    })
                # Index Save (/100)
                save_score = row.get("xTech GK Save (/100)", np.nan)
                if pd.notna(save_score):
                    metric_rows.append({
                        "Metrics": "**GK Save Index**",
                        "Player Figures": "",
                        "Points": f"**{save_score:.0f} / 100**"
                    })
                detail_df = pd.DataFrame(metric_rows)
                detail_df = detail_df.drop_duplicates(subset=["Metrics"], keep="first")
            
                # Affichage jauge Save (en premier)
                hue_save = 120 * (save_score / 100) if pd.notna(save_score) else 0
                bar_color_save = f"hsl({hue_save:.0f}, 75%, 50%)"
                fig_save = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=round(save_score) if pd.notna(save_score) else 0,
                    number={'font': {'size': 40}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': bar_color_save, 'thickness': 0.25},
                        'bgcolor': "rgba(255,255,255,0)",
                        'borderwidth': 0,
                        'steps': [{'range': [0, 100], 'color': 'rgba(100,100,100,0.2)'}],
                        'threshold': {'line': {'color': "white", 'width': 4},
                                      'thickness': 0.75,
                                      'value': mean_def}
                    },
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"<b>{rank_def}ᵉ / {total_peers}</b>", 'font': {'size': 18}}
                ))
                fig_save.update_layout(margin={'t': 40, 'b': 0, 'l': 0, 'r': 0}, paper_bgcolor="rgba(0,0,0,0)", height=250)
                st.plotly_chart(fig_save, use_container_width=True)
            
                # Label sous la jauge
                st.markdown(
                    f"<div style='text-align:center; font-size:18px; margin-top:-22px; margin-bottom:2px;'><b>Save</b></div>",
                    unsafe_allow_html=True
                )
            
                # Moyenne Save index
                df_filtre = df_tech[
                    (df_tech["Position Group"] == "Goalkeeper") &
                    (df_tech["Competition Name"] == comp) &
                    (df_tech["Minutes"] >= 500)
                ]
                if not df_filtre.empty:
                    mean_save = df_filtre["xTech GK Save (/100)"].mean()
                    if pd.notnull(mean_save):
                        st.markdown(
                            f"<div style='text-align:center; color:grey; margin-top:-8px; margin-bottom:12px;'>"
                            f"Average xSave (GK in {comp}) : {round(mean_save)}</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        "<div style='text-align:center; color:#b0b0b0; font-size:13px; margin-top:-8px; margin-bottom:12px;'>"
                        "The 500min threshold is not reached in the competition, no average can be calculated.</div>",
                        unsafe_allow_html=True
                    )
            
                # Titre avant le tableau
                st.markdown("##### xSave Details")

                # === Tableau xSave (GK) ===
                config = xtech_post_config.get("Goalkeeper")
                if not config:
                    st.error("Aucun mapping défini pour le poste Goalkeeper")
                    st.stop()

                metric_map = config["metric_map"]
                labels = config["labels"]
                metric_rows = []

                # --- Métriques SAVE uniquement ---
                for raw_col in config["save"]:
                    note_col, scores = metric_map.get(raw_col, (None, None))
                    if not note_col or raw_col not in df1.columns:
                        continue
                    raw_val = row.get(raw_col, None)  # valeur brute
                    note_val = row.get(note_col, None)  # valeur barémée
                    max_pts = max(scores)
                    label = labels.get(raw_col, raw_col)
                    metric_rows.append({
                        "Metrics": label,
                        "Player Figures": f"{raw_val:.2f}" if pd.notna(raw_val) else "NA",
                        "Points": f"{note_val} / {max_pts}" if pd.notna(note_val) else f"0 / {max_pts}"
                    })

                # --- Total xSave ---
                total_points = 0
                total_max = 0
                for row_ in metric_rows:
                    label = row_["Metrics"]
                    if row_["Points"] and "/" in row_["Points"] and not any(x in label for x in ["Sub-index", "Total", "Index"]):
                        try:
                            pts, max_pts = row_["Points"].split("/")
                            total_points += int(pts.strip(" *"))
                            total_max += int(max_pts.strip(" *"))
                        except:
                            continue

                metric_rows.append({
                    "Metrics": "**Total**",
                    "Player Figures": "",
                    "Points": f"**{total_points} / {total_max}**"
                })

                # --- Sous-index Save ---
                sub_val = row.get("xTech GK Save (/100)", None)
                if pd.notna(sub_val):
                    metric_rows.append({
                        "Metrics": "**GK Save Index**",
                        "Player Figures": "",
                        "Points": f"**{sub_val:.0f} / 100**"
                    })

                # === Affichage final du tableau
                detail_df = pd.DataFrame(metric_rows)
                detail_df = detail_df.drop_duplicates(subset=["Metrics"], keep="first")
                st.dataframe(detail_df.set_index("Metrics"), use_container_width=True)

            else:
                fig_def = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=round(def_score),
                    number={'font': {'size': 40}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': bar_color_def, 'thickness': 0.25},
                        'bgcolor': "rgba(255,255,255,0)",
                        'borderwidth': 0,
                        'steps': [{'range': [0, 100], 'color': 'rgba(100,100,100,0.2)'}],
                        'threshold': {'line': {'color': "white", 'width': 4},
                                      'thickness': 0.75,
                                      'value': mean_def}
                    },
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"<b>{rank_def}ᵉ / {total_peers}</b>", 'font': {'size': 18}}
                ))
                fig_def.update_layout(margin={'t': 40, 'b': 0, 'l': 0, 'r': 0}, paper_bgcolor="rgba(0,0,0,0)", height=250)
                st.plotly_chart(fig_def, use_container_width=True)
    
                st.markdown(
                    f"<div style='text-align:center; font-size:18px; margin-top:-22px; margin-bottom:2px;'><b>{def_label}</b></div>",
                    unsafe_allow_html=True
                )
    
                # Moyenne, placée juste sous le label
                # Filtrage des joueurs pour la moyenne
                df_filtre = df_tech[
                    (df_tech["Position Group"] == pos) &
                    (df_tech["Competition Name"] == comp) &
                    (df_tech["Minutes"] >= 500)
                ]
                
                if not df_filtre.empty:
                    mean_def = df_filtre[def_col].mean()
                    if pd.notnull(mean_def):
                        mean_def_affiche = round(mean_def)
                        st.markdown(
                            f"<div style='text-align:center; color:grey; margin-top:-8px; margin-bottom:12px;'>"
                            f"Average {def_label} ({pos} in {comp}) : {mean_def_affiche}</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        "<div style='text-align:center; color:#b0b0b0; font-size:13px; margin-top:-8px; margin-bottom:12px;'>"
                        "The 500min threshold is not reached in the competition, no average can be calculated.</div>",
                        unsafe_allow_html=True
                    )
                
                st.markdown("##### xDef Details")

            # Tableau DEF
            if pos == "Goalkeeper":
                metrics = [
                    ("xTech GK GSAA %", "GSAA %"),
                    ("xTech GK Save %", "Save %"),
                    ("xTech GK Aggressive Distance", "Aggressive Distance"),
                    ("xTech GK Long Ball %", "Long Ball %"),
                    ("xTech GK OPxGBuildup", "OPxGBuildup"),
                ]
            else:
                # === Tableau xDEF ===
                config = xtech_post_config.get(pos)
                if not config:
                    st.error(f"Aucun mapping défini pour le poste : {pos}")
                    st.stop()
                prefix = config.get("prefix", pos.split()[0].upper())
                metric_map = config["metric_map"]
                labels = config["labels"]

                metric_rows = []

                # --- Métriques DEF uniquement ---
                for raw_col in config["def"]:
                    note_col, scores = metric_map.get(raw_col, (None, None))
                    if not note_col or note_col not in df1.columns:
                        continue
                    raw_val = row.get(raw_col, None)
                    note_val = row.get(note_col, None)
                    max_pts = max(scores)
                    label = labels.get(raw_col, raw_col)
                    metric_rows.append({
                        "Metrics": label,
                        "Player Figures": f"{raw_val:.2f}" if pd.notna(raw_val) else "NA",
                        "Points": f"{note_val} / {max_pts}" if pd.notna(note_val) else f"0 / {max_pts}"
                    })

                # --- Total DEF ---
                total_points = 0
                total_max = 0
                for row_ in metric_rows:
                    label = row_["Metrics"]
                    if row_["Points"] and "/" in row_["Points"] and not any(x in label for x in ["Sub-index", "Total", "Index"]):
                        try:
                            pts, max_pts = row_["Points"].split("/")
                            total_points += int(pts.strip(" *"))
                            total_max += int(max_pts.strip(" *"))
                        except:
                            continue

                metric_rows.append({
                    "Metrics": "**Total**",
                    "Player Figures": "",
                    "Points": f"**{total_points} / {total_max}**"
                })
                
                # --- Sous-index DEF ---
                sub_val = row.get("xDEF", None)
                if pd.notna(sub_val):
                    metric_rows.append({
                        "Metrics": "**Index xDEF**",
                        "Player Figures": "",
                        "Points": f"**{sub_val:.0f} / 100**"
                    })

                # === Affichage final du tableau (propre, sans index auto)
                detail_df = pd.DataFrame(metric_rows)
                detail_df = detail_df.drop_duplicates(subset=["Metrics"], keep="first")
                st.dataframe(detail_df.set_index("Metrics"), use_container_width=True)
        
                hue_tech = 120 * (tech_score / 100)
                bar_color_tech = f"hsl({hue_tech:.0f}, 75%, 50%)"
        with col2:
            if is_gk:
                # ========== TECH GK ==========
                gk_tech_metrics = [
                    ("xTech GK Passing %", "Passing %"),
                    ("xTech GK Passing u. Pressure %", "Passing under Pressure %"),
                    ("xTech GK Pass Into Danger %", "Pass into Danger %"),
                    ("xTech GK Long Ball %", "Long Ball %"),
                    ("xTech GK OPxGBuildup", "OPxGBuildup"),
                ]
                metric_rows = []
                for col, label in gk_tech_metrics:
                    val = row.get(col, None)
                    metric_rows.append({
                        "Metrics": label,
                        "Player Figures": f"{val:.2f}" if pd.notna(val) else "NA",
                        "Points": ""  # Pas de barème pour GK, adapter si besoin
                    })
                # Index Usage (/100)
                usage_score = row.get("xTech GK Usage (/100)", np.nan)
                if pd.notna(usage_score):
                    metric_rows.append({
                        "Metrics": "**GK Usage Index**",
                        "Player Figures": "",
                        "Points": f"**{usage_score:.0f} / 100**"
                    })
                detail_df = pd.DataFrame(metric_rows)
                detail_df = detail_df.drop_duplicates(subset=["Metrics"], keep="first")
            
                # Affichage jauge Usage (en premier)
                hue_usage = 120 * (usage_score / 100) if pd.notna(usage_score) else 0
                bar_color_usage = f"hsl({hue_usage:.0f}, 75%, 50%)"
                fig_usage = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=round(usage_score) if pd.notna(usage_score) else 0,
                    number={'font': {'size': 40}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': bar_color_usage, 'thickness': 0.25},
                        'bgcolor': "rgba(255,255,255,0)",
                        'borderwidth': 0,
                        'steps': [{'range': [0, 100], 'color': 'rgba(100,100,100,0.2)'}],
                        'threshold': {'line': {'color': "white", 'width': 4},
                                      'thickness': 0.75,
                                      'value': mean_tech}
                    },
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"<b>{rank_tech}ᵉ / {total_peers}</b>", 'font': {'size': 18}}
                ))
                fig_usage.update_layout(margin={'t': 40, 'b': 0, 'l': 0, 'r': 0}, paper_bgcolor="rgba(0,0,0,0)", height=250)
                st.plotly_chart(fig_usage, use_container_width=True)
            
                # Label sous la jauge
                st.markdown(
                    f"<div style='text-align:center; font-size:18px; margin-top:-22px; margin-bottom:2px;'><b>Usage</b></div>",
                    unsafe_allow_html=True
                )
            
                # Moyenne Usage index
                df_filtre_tech = df_tech[
                    (df_tech["Position Group"] == "Goalkeeper") &
                    (df_tech["Competition Name"] == comp) &
                    (df_tech["Minutes"] >= 500)
                ]
                if not df_filtre_tech.empty:
                    mean_usage = df_filtre_tech["xTech GK Usage (/100)"].mean()
                    if pd.notnull(mean_usage):
                        st.markdown(
                            f"<div style='text-align:center; color:grey; margin-top:-8px; margin-bottom:12px;'>"
                            f"Average xUsage (GK in {comp}) : {round(mean_usage)}</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        "<div style='text-align:center; color:#b0b0b0; font-size:13px; margin-top:-8px; margin-bottom:12px;'>"
                        "The 500min threshold is not reached in the competition, no average can be calculated.</div>",
                        unsafe_allow_html=True
                    )
            
                # Titre avant le tableau
                # Titre avant le tableau
                st.markdown("##### xUsage Details")

                # === Tableau xUsage (GK) avec barèmes ===
                metric_rows = []

                # --- Métriques USAGE uniquement ---
                for raw_col in config["usage"]:
                    note_col, scores = metric_map.get(raw_col, (None, None))
                    if not note_col or raw_col not in df1.columns:
                        continue
                    raw_val = row.get(raw_col, None)  # valeur brute
                    note_val = row.get(note_col, None)  # valeur barémée
                    max_pts = max(scores)
                    label = labels.get(raw_col, raw_col)
                    metric_rows.append({
                        "Metrics": label,
                        "Player Figures": f"{raw_val:.2f}" if pd.notna(raw_val) else "NA",
                        "Points": f"{note_val} / {max_pts}" if pd.notna(note_val) else f"0 / {max_pts}"
                    })

                # --- Total xUsage ---
                total_points = 0
                total_max = 0
                for row_ in metric_rows:
                    label = row_["Metrics"]
                    if row_["Points"] and "/" in row_["Points"] and not any(x in label for x in ["Sub-index", "Total", "Index"]):
                        try:
                            pts, max_pts = row_["Points"].split("/")
                            total_points += int(pts.strip(" *"))
                            total_max += int(max_pts.strip(" *"))
                        except:
                            continue

                metric_rows.append({
                    "Metrics": "**Total**",
                    "Player Figures": "",
                    "Points": f"**{total_points} / {total_max}**"
                })

                # --- Sous-index Usage ---
                sub_val = row.get("xTech GK Usage (/100)", None)
                if pd.notna(sub_val):
                    metric_rows.append({
                        "Metrics": "**GK Usage Index**",
                        "Player Figures": "",
                        "Points": f"**{sub_val:.0f} / 100**"
                    })

                # === Affichage final du tableau
                detail_df = pd.DataFrame(metric_rows)
                detail_df = detail_df.drop_duplicates(subset=["Metrics"], keep="first")
                st.dataframe(detail_df.set_index("Metrics"), use_container_width=True)
            else:
                fig_tech = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=round(tech_score),
                    number={'font': {'size': 40}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': bar_color_tech, 'thickness': 0.25},
                        'bgcolor': "rgba(255,255,255,0)",
                        'borderwidth': 0,
                        'steps': [{'range': [0, 100], 'color': 'rgba(100,100,100,0.2)'}],
                        'threshold': {'line': {'color': "white", 'width': 4},
                                      'thickness': 0.75,
                                      'value': mean_tech}
                    },
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"<b>{rank_tech}ᵉ / {total_peers}</b>", 'font': {'size': 18}}
                ))
                fig_tech.update_layout(margin={'t': 40, 'b': 0, 'l': 0, 'r': 0}, paper_bgcolor="rgba(0,0,0,0)", height=250)
                st.plotly_chart(fig_tech, use_container_width=True)
                # Ajoute le label juste sous la jauge, avant la moyenne
                st.markdown(
                    f"<div style='text-align:center; font-size:18px; margin-top:-22px; margin-bottom:2px;'><b>{tech_label}</b></div>",
                    unsafe_allow_html=True
                )
                # Filtrage des joueurs pour la moyenne TECH
                df_filtre_tech = df_tech[
                    (df_tech["Position Group"] == pos) &
                    (df_tech["Competition Name"] == comp) &
                    (df_tech["Minutes"] >= 500)
                ]
                
                if not df_filtre_tech.empty:
                    mean_tech = df_filtre_tech[tech_col].mean()
                    if pd.notnull(mean_tech):
                        mean_tech_affiche = round(mean_tech)
                        st.markdown(
                            f"<div style='text-align:center; color:grey; margin-top:-8px; margin-bottom:12px;'>"
                            f"Average {tech_label} ({pos} in {comp}) : {mean_tech_affiche}</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        "<div style='text-align:center; color:#b0b0b0; font-size:13px; margin-top:-8px; margin-bottom:12px;'>"
                        "The 500min threshold is not reached in the competition, no average can be calculated.</div>",
                        unsafe_allow_html=True
                    )
                
                st.markdown("##### xTech Details")

            # Tableau TECH
            if pos == "Goalkeeper":
                metrics = [
                    ("xTech GK Passing %", "Passing %"),
                    ("xTech GK Passing u. Pressure %", "Passing under Pressure %"),
                    ("xTech GK Pass Into Danger %", "Pass into Danger %"),
                    ("xTech GK Long Ball %", "Long Ball %"),
                    ("xTech GK OPxGBuildup", "OPxGBuildup"),
                ]
            else:
                # === Tableau xTECH ===
                config = xtech_post_config.get(pos)
                if not config:
                    st.error(f"Aucun mapping défini pour le poste : {pos}")
                    st.stop()
                prefix = config.get("prefix", pos.split()[0].upper())
                metric_map = config["metric_map"]
                labels = config["labels"]

                metric_rows = []

                # --- Métriques TECH uniquement ---
                for raw_col in config["tech"]:
                    note_col, scores = metric_map.get(raw_col, (None, None))
                    if not note_col or note_col not in df1.columns:
                        continue
                    raw_val = row.get(raw_col, None)
                    note_val = row.get(note_col, None)
                    max_pts = max(scores)
                    label = labels.get(raw_col, raw_col)
                    metric_rows.append({
                        "Metrics": label,
                        "Player Figures": f"{raw_val:.2f}" if pd.notna(raw_val) else "NA",
                        "Points": f"{note_val} / {max_pts}" if pd.notna(note_val) else f"0 / {max_pts}"
                    })

                # --- Total TECH (ligne avant-dernière) ---
                total_points = 0
                total_max = 0
                for row_ in metric_rows:
                    label = row_["Metrics"]
                    if row_["Points"] and "/" in row_["Points"] and not any(x in label for x in ["Sub-index", "Total", "Index"]):
                        try:
                            pts, max_pts = row_["Points"].split("/")
                            total_points += int(pts.strip(" *"))
                            total_max += int(max_pts.strip(" *"))
                        except:
                            continue

                metric_rows.append({
                    "Metrics": "**Total**",
                    "Player Figures": "",
                    "Points": f"**{total_points} / {total_max}**"
                })

                # --- Sous-index TECH (à la toute fin) ---
                sub_val = row.get("xTECH", None)
                if pd.notna(sub_val):
                    metric_rows.append({
                        "Metrics": "**Index xTECH**",
                        "Player Figures": "",
                        "Points": f"**{sub_val:.0f} / 100**"
                    })
                
                # === Affichage final du tableau (propre, sans index auto)
                detail_df = pd.DataFrame(metric_rows)
                detail_df = detail_df.drop_duplicates(subset=["Metrics"], keep="first")
                st.dataframe(detail_df.set_index("Metrics"), use_container_width=True)
    
################### --- Onglet Top 50 xTechnical --- ###################
    with tab4:
        # 1. Sélection Compétition et Saison (déjà côte à côte)
        col1, col2 = st.columns(2)
        with col1:
            selected_comp = st.selectbox(
                "Competition",
                competition_list_tech,
                index=competition_list_tech.index("Serie A") if "Serie A" in competition_list_tech else 0,
                key="top50_xtech_comp"
            )
        with col2:
            available_seasons = df_tech[df_tech["Competition Name"] == selected_comp]["Season Name"].dropna().unique().tolist()
            available_seasons = sorted(available_seasons)
            default_season = "2024/2025" if "2024/2025" in available_seasons else available_seasons[-1]
            selected_season = st.selectbox(
                "Season",
                available_seasons,
                index=available_seasons.index(default_season),
                key="top50_xtech_season"
            )

        # 2. Sélection POSTE et INDEX côte à côte
        col3, col4 = st.columns(2)
        with col3:
            ordered_positions = [
                "Goalkeeper", "Central Defender", "Full Back", "Midfielder", "Attacking Midfielder", "Winger", "Striker"
            ]
            positions_available = [p for p in ordered_positions if p in df_tech["Position Group"].unique()]
            selected_pos = st.selectbox(
                "Position",
                positions_available,
                index=positions_available.index("Striker") if "Striker" in positions_available else 0,
                key="top50_xtech_pos"
            )
        with col4:
            if selected_pos == "Goalkeeper":
                index_options = {
                    "xSave": "xTech GK Save (/100)",
                    "xUsage": "xTech GK Usage (/100)"
                }
                default_index = "xSave"
            else:
                index_options = {
                    "xDEF": "xDEF",
                    "xTECH": "xTECH"
                }
                default_index = "xTECH"
            selected_index_label = st.selectbox(
                "Index to display",
                list(index_options.keys()),
                key="top50_xtech_index"
            )
            selected_index = index_options[selected_index_label]

        # 3. Slider Minutes
        min_minutes = st.slider(
            "Minimum minutes played",
            0,
            int(df_tech["Minutes"].max()),
            600,
            50,
            key="top50_xtech_min"
        )

        # 5. FILTRAGE
        filtered_top = df_tech[
            (df_tech["Competition Name"] == selected_comp) &
            (df_tech["Season Name"] == selected_season) &
            (df_tech["Position Group"] == selected_pos) &
            (df_tech["Minutes"] >= min_minutes)
        ].copy()

        filtered_top = filtered_top[filtered_top[selected_index].notna()]
        top_50 = filtered_top.sort_values(by=selected_index, ascending=False).head(50).reset_index(drop=True)

        # 6. CONSTRUCTION TABLEAU
        rows = []
        for i, row in top_50.iterrows():
            index_value = row[selected_index]
            rows.append({
                "Rank":      i + 1,
                "Player":    row["Player Name"],
                "Team":    row["Team Name"],
                "Minutes":   int(round(row["Minutes"])),
                "Age":       int(row["Age"]),
                selected_index_label: int(round(index_value)) if pd.notna(index_value) else "—"
            })

        display_df = pd.DataFrame(rows).set_index("Rank")
        styled_df = display_df.style.set_properties(**{
            "text-align": "center"
        }).set_table_styles([
            {"selector": "th", "props": [("text-align", "center")]},
            {"selector": ".row_heading", "props": [("text-align", "center")]},
            {"selector": ".blank", "props": [("display", "none")]}
        ])

        st.dataframe(styled_df, use_container_width=True)
