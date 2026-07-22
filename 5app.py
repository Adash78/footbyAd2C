import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard 5 Grands Championnats", layout="wide")

# ----------------------------------------------------------
# Chargement des données
# ----------------------------------------------------------
@st.cache_data
def charger_donnees():
    par_saison = pd.read_csv("classement_par_saison.csv")
    cumul = pd.read_csv("cumul_5_championnats.csv")
    return par_saison, cumul

par_saison, cumul = charger_donnees()

# Nombre de saisons disponibles par championnat (pour le filtre "non relégué")
nb_saisons_total_par_champ = par_saison.groupby('championnat')['saison'].nunique()

liste_championnats = sorted(cumul['championnat'].unique())
liste_championnats_avec_tous = ["Tous les championnats"] + liste_championnats

# ----------------------------------------------------------
# Navigation
# ----------------------------------------------------------
st.sidebar.title("⚽ Dashboard Football")
page = st.sidebar.radio(
    "Choisir une page",
    ["🏠 Accueil", "🏆 Classement général", "⚔️ Meilleures attaques", "🛡️ Meilleures défenses"]
)

# ----------------------------------------------------------
# PAGE ACCUEIL
# ----------------------------------------------------------
if page == "🏠 Accueil":
    st.title("Analyse des 5 grands championnats européens")
    st.write(
        "Bienvenue sur ce tableau de bord d'analyse des performances des équipes "
        "des 5 grands championnats européens, depuis la saison 2020-2021."
    )
    st.markdown("""
    - **🏆 Classement général** — points, victoires, nuls, défaites, titres
    - **⚔️ Meilleures attaques** — buts marqués, total / domicile / extérieur
    - **🛡️ Meilleures défenses** — buts encaissés, total / domicile / extérieur, avec option "équipes non reléguées"
    """)
    st.info(f"Championnats couverts : {', '.join(liste_championnats)}")
    st.info(f"Saisons couvertes : de {par_saison['saison'].min()} à {par_saison['saison'].max()}")

# ----------------------------------------------------------
# PAGE CLASSEMENT GÉNÉRAL
# ----------------------------------------------------------
elif page == "🏆 Classement général":
    st.title("🏆 Classement général cumulé")

    champ_choisi = st.selectbox("Choisir un championnat :", liste_championnats_avec_tous)

    if champ_choisi == "Tous les championnats":
        data = cumul.copy()
        colonnes = ['equipe', 'championnat', 'points_total', 'victoires_total', 'nuls_total', 'defaites_total', 'titres']
        noms = {
            'equipe': 'Équipe', 'championnat': 'Championnat', 'points_total': 'Points',
            'victoires_total': 'Victoires', 'nuls_total': 'Nuls',
            'defaites_total': 'Défaites', 'titres': 'Titres'
        }
    else:
        data = cumul[cumul['championnat'] == champ_choisi]
        colonnes = ['equipe', 'points_total', 'victoires_total', 'nuls_total', 'defaites_total', 'titres']
        noms = {
            'equipe': 'Équipe', 'points_total': 'Points',
            'victoires_total': 'Victoires', 'nuls_total': 'Nuls',
            'defaites_total': 'Défaites', 'titres': 'Titres'
        }

    tableau = data[colonnes].rename(columns=noms).sort_values('Points', ascending=False).reset_index(drop=True)

    tableau.index = range(1, len(tableau) + 1)
    tableau.index.name = 'Rang'
    st.dataframe(tableau, use_container_width=True)

# ----------------------------------------------------------
# PAGE MEILLEURES ATTAQUES
# ----------------------------------------------------------
elif page == "⚔️ Meilleures attaques":
    st.title("⚔️ Meilleures attaques")

    champ_choisi = st.selectbox("Choisir un championnat :", liste_championnats_avec_tous)
    vue = st.radio("Afficher :", ["Total", "Domicile", "Extérieur"], horizontal=True)

    if vue == "Total":
        col = 'buts_marques_total'
        titre_col = 'Buts marqués (total)'
    elif vue == "Domicile":
        col = 'buts_marques_dom_total'
        titre_col = 'Buts marqués (domicile)'
    else:
        col = 'buts_marques_ext_total'
        titre_col = 'Buts marqués (extérieur)'

    if champ_choisi == "Tous les championnats":
        data = cumul.copy()
        tableau = data[['equipe', 'championnat', col]].rename(
            columns={'equipe': 'Équipe', 'championnat': 'Championnat', col: titre_col}
        ).sort_values(titre_col, ascending=False).reset_index(drop=True)
    else:
        data = cumul[cumul['championnat'] == champ_choisi]
        tableau = data[['equipe', col]].rename(
            columns={'equipe': 'Équipe', col: titre_col}
        ).sort_values(titre_col, ascending=False).reset_index(drop=True)

    tableau.index = range(1, len(tableau) + 1)
    tableau.index.name = 'Rang'
    st.dataframe(tableau, use_container_width=True)
    st.bar_chart(tableau.set_index('Équipe')[titre_col])

# ----------------------------------------------------------
# PAGE MEILLEURES DÉFENSES
# ----------------------------------------------------------
elif page == "🛡️ Meilleures défenses":
    st.title("🛡️ Meilleures défenses")

    champ_choisi = st.selectbox("Choisir un championnat :", liste_championnats_avec_tous)
    vue = st.radio("Afficher :", ["Total", "Domicile", "Extérieur"], horizontal=True)
    non_relegues_seulement = st.checkbox("Afficher uniquement les équipes présentes sur toutes les saisons (non reléguées)")

    if vue == "Total":
        col = 'buts_encaisses_total'
        titre_col = 'Buts encaissés (total)'
    elif vue == "Domicile":
        col = 'buts_encaisses_dom_total'
        titre_col = 'Buts encaissés (domicile)'
    else:
        col = 'buts_encaisses_ext_total'
        titre_col = 'Buts encaissés (extérieur)'

    if champ_choisi == "Tous les championnats":
        data = cumul.copy()
        if non_relegues_seulement:
            data['nb_saisons_total_champ'] = data['championnat'].map(nb_saisons_total_par_champ)
            data = data[data['nb_saisons'] == data['nb_saisons_total_champ']]
        tableau = data[['equipe', 'championnat', col, 'nb_saisons']].rename(
            columns={'equipe': 'Équipe', 'championnat': 'Championnat', col: titre_col, 'nb_saisons': 'Saisons jouées'}
        ).sort_values(titre_col, ascending=True).reset_index(drop=True)
    else:
        data = cumul[cumul['championnat'] == champ_choisi]
        if non_relegues_seulement:
            total_saisons = nb_saisons_total_par_champ[champ_choisi]
            data = data[data['nb_saisons'] == total_saisons]
        tableau = data[['equipe', col, 'nb_saisons']].rename(
            columns={'equipe': 'Équipe', col: titre_col, 'nb_saisons': 'Saisons jouées'}
        ).sort_values(titre_col, ascending=True).reset_index(drop=True)

    tableau.index = range(1, len(tableau) + 1)
    tableau.index.name = 'Rang'
    st.dataframe(tableau, use_container_width=True)
    st.bar_chart(tableau.set_index('Équipe')[titre_col])
