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
    st.title("⚽ Analyse des 5 grands championnats européens")
    st.caption(f"Données de {par_saison['saison'].min()} à {par_saison['saison'].max()} — "
               f"{', '.join(liste_championnats)}")

    st.divider()

    # ---- Chiffres clés calculés automatiquement ----
    # Meilleure défense : uniquement parmi les équipes présentes sur toutes les saisons de leur championnat
    cumul_avec_total = cumul.copy()
    cumul_avec_total['nb_saisons_total_champ'] = cumul_avec_total['championnat'].map(nb_saisons_total_par_champ)
    equipes_non_reléguées = cumul_avec_total[cumul_avec_total['nb_saisons'] == cumul_avec_total['nb_saisons_total_champ']]

    meilleure_attaque = cumul.loc[cumul['buts_marques_total'].idxmax()]
    meilleure_defense = equipes_non_reléguées.loc[equipes_non_reléguées['buts_encaisses_total'].idxmin()]
    plus_titree = cumul.loc[cumul['titres'].idxmax()]
    plus_de_points = cumul.loc[cumul['points_total'].idxmax()]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏆 Plus de titres", plus_titree['equipe'], f"{int(plus_titree['titres'])} titre(s)")
    col2.metric("🔥 Meilleure attaque", meilleure_attaque['equipe'], f"{int(meilleure_attaque['buts_marques_total'])} buts")
    col3.metric("🧱 Meilleure défense*", meilleure_defense['equipe'], f"{int(meilleure_defense['buts_encaisses_total'])} encaissés")
    col4.metric("⭐ Plus de points", plus_de_points['equipe'], f"{int(plus_de_points['points_total'])} pts")
    st.caption("*Parmi les équipes présentes sur toutes les saisons de leur championnat")

    st.divider()

    # ---- Présentation / navigation ----
    st.subheader("Explorer les données")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🏆 Classement général")
        st.write("Points, victoires, nuls, défaites et titres — par championnat ou toutes ligues confondues.")
    with c2:
        st.markdown("### ⚔️ Meilleures attaques")
        st.write("Buts marqués, total / domicile / extérieur, avec ratio par match.")
    with c3:
        st.markdown("### 🛡️ Meilleures défenses")
        st.write("Buts encaissés, avec filtre sur les équipes non reléguées.")

    st.info("👈 Utilisez le menu à gauche pour naviguer entre les pages")

# ----------------------------------------------------------
# PAGE CLASSEMENT GÉNÉRAL
# ----------------------------------------------------------
elif page == "🏆 Classement général":
    st.title("🏆 Classement général cumulé")

    champ_choisi = st.selectbox("Choisir un championnat :", liste_championnats_avec_tous)

    if champ_choisi == "Tous les championnats":
        data = cumul.copy()

        # Nombre de matchs joués = victoires + nuls + défaites
        data['nb_matchs'] = data['victoires_total'] + data['nuls_total'] + data['defaites_total']

        # Ratios par match (arrondis à 2 décimales)
        data['pts_par_match'] = (data['points_total'] / data['nb_matchs']).round(2)
        data['buts_par_match'] = (data['buts_marques_total'] / data['nb_matchs']).round(2)
        data['buts_encaisses_par_match'] = (data['buts_encaisses_total'] / data['nb_matchs']).round(2)

        colonnes = [
            'equipe', 'championnat', 'points_total', 'victoires_total', 'nuls_total', 'defaites_total',
            'titres', 'nb_matchs', 'pts_par_match', 'buts_par_match', 'buts_encaisses_par_match'
        ]
        noms = {
            'equipe': 'Équipe', 'championnat': 'Championnat', 'points_total': 'Points',
            'victoires_total': 'Victoires', 'nuls_total': 'Nuls',
            'defaites_total': 'Défaites', 'titres': 'Titres',
            'nb_matchs': 'Matchs joués', 'pts_par_match': 'Points / match',
            'buts_par_match': 'Buts marqués / match', 'buts_encaisses_par_match': 'Buts encaissés / match'
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
        data['nb_matchs'] = data['victoires_total'] + data['nuls_total'] + data['defaites_total']
        data['ratio'] = (data[col] / data['nb_matchs']).round(2)
        tableau = data[['equipe', 'championnat', col, 'nb_matchs', 'ratio']].rename(
            columns={'equipe': 'Équipe', 'championnat': 'Championnat', col: titre_col,
                     'nb_matchs': 'Matchs joués', 'ratio': f'{titre_col} / match'}
        ).sort_values(titre_col, ascending=False).reset_index(drop=True)
    else:
        data = cumul[cumul['championnat'] == champ_choisi]
        data['nb_matchs'] = data['victoires_total'] + data['nuls_total'] + data['defaites_total']
        data['ratio'] = (data[col] / data['nb_matchs']).round(2)
        tableau = data[['equipe', col, 'nb_matchs', 'ratio']].rename(
            columns={'equipe': 'Équipe', col: titre_col,
                     'nb_matchs': 'Matchs joués', 'ratio': f'{titre_col} / match'}
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
        data['nb_matchs'] = data['victoires_total'] + data['nuls_total'] + data['defaites_total']
        data['ratio'] = (data[col] / data['nb_matchs']).round(2)
        tableau = data[['equipe', 'championnat', col, 'nb_matchs', 'ratio', 'nb_saisons']].rename(
            columns={'equipe': 'Équipe', 'championnat': 'Championnat', col: titre_col,
                     'nb_matchs': 'Matchs joués', 'ratio': f'{titre_col} / match', 'nb_saisons': 'Saisons jouées'}
        ).sort_values(titre_col, ascending=True).reset_index(drop=True)
    else:
        data = cumul[cumul['championnat'] == champ_choisi]
        if non_relegues_seulement:
            total_saisons = nb_saisons_total_par_champ[champ_choisi]
            data = data[data['nb_saisons'] == total_saisons]
        data['nb_matchs'] = data['victoires_total'] + data['nuls_total'] + data['defaites_total']
        data['ratio'] = (data[col] / data['nb_matchs']).round(2)
        tableau = data[['equipe', col, 'nb_matchs', 'ratio', 'nb_saisons']].rename(
            columns={'equipe': 'Équipe', col: titre_col,
                     'nb_matchs': 'Matchs joués', 'ratio': f'{titre_col} / match', 'nb_saisons': 'Saisons jouées'}
        ).sort_values(titre_col, ascending=True).reset_index(drop=True)

    tableau.index = range(1, len(tableau) + 1)
    tableau.index.name = 'Rang'
    st.dataframe(tableau, use_container_width=True)
    st.bar_chart(tableau.set_index('Équipe')[titre_col])
