import streamlit as st
import math

# --- Coefficients de votre Modèle de Cox (Vos données sont conservées !) ---
COEFFICIENTS = {
    'crises_convulsives': 1.1846,
    'fav_confectionnee': -1.0225,
    'albumine_num': -0.0457,
    'age_num': 0.0236,
    'du_residuelle': -0.5294,
    'couverture_medicale_1': -0.1119, # RAMED
    'couverture_medicale_2': -0.8109, # AMO
    'couverture_medicale_3': -1.3382 # CNOPS/FAR/CNSS
}

# ESTIMATION DU SCORE LINÉAIRE MOYEN (LP_moyen) de votre cohorte.
LP_MOYEN = -1.35

# --- Fonction de calcul (Celle-ci reste la même !) ---
def calcul_score_cox(patient):
    # 1. Calcul du Score Linéaire (LP)
    lp = (
        COEFFICIENTS['crises_convulsives'] * patient['crises_convulsives'] +
        COEFFICIENTS['fav_confectionnee'] * patient['fav_confectionnee'] +
        COEFFICIENTS['albumine_num'] * patient['albumine'] +
        COEFFICIENTS['age_num'] * patient['age'] +
        COEFFICIENTS['du_residuelle'] * patient['du_residuelle'] +
        COEFFICIENTS['couverture_medicale_1'] * patient['couv_med_1'] +
        COEFFICIENTS['couverture_medicale_2'] * patient['couv_med_2'] +
        COEFFICIENTS['couverture_medicale_3'] * patient['couv_med_3']
    )

    # 2. Calcul du Risque Relatif (HR) par rapport au patient moyen
    hr_vs_moyen = math.exp(lp - LP_MOYEN)

    # 3. Classification basée sur le HR
    if hr_vs_moyen < 0.6:
        risque = 'Faible (HR < 0.6)'
        couleur = 'green'
    elif hr_vs_moyen < 1.5:
        risque = 'Moyen (0.6 ≤ HR < 1.5)'
        couleur = 'orange'
    else:
        risque = 'Élevé (HR ≥ 1.5)'
        couleur = 'red'

    return hr_vs_moyen, risque, couleur

# ------------------ Interface Utilisateur Streamlit ------------------

st.title("Score de Risque de Décès (Modèle de Cox)")
st.subheader("Comparaison du Risque Relatif (HR) vs Patient Moyen")

# --- Inputs numériques ---
age = st.number_input("Âge (années)", min_value=18.0, max_value=120.0, value=60.0, step=1.0)
albumine = st.number_input("Albumine sérique (g/L)", min_value=10.0, max_value=60.0, value=35.0, step=0.1)

# --- Inputs binaires (Checkboxes) ---
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    crises_convulsives = st.checkbox("Crises Convulsives", value=False)
with col2:
    fav_confectionnee = st.checkbox("FAV Confectionnée", value=False)
with col3:
    du_residuelle = st.checkbox("Diurèse Résiduelle", value=False)

# --- Input Catégoriel (Radio buttons) ---
st.markdown("---")
couv_med_val = st.radio(
    "Couverture Médicale",
    ('Sans Couverture', 'RAMED', 'AMO', 'CNOPS/FAR/CNSS'),
    index=0 # 'Sans Couverture' est la référence par défaut
)

# --- Préparation des données pour la fonction de calcul ---
patient_input = {
    'age': age,
    'albumine': albumine,
    'crises_convulsives': 1 if crises_convulsives else 0,
    'fav_confectionnee': 1 if fav_confectionnee else 0,
    'du_residuelle': 1 if du_residuelle else 0,
    'couv_med_1': 1 if couv_med_val == 'RAMED' else 0,
    'couv_med_2': 1 if couv_med_val == 'AMO' else 0,
    'couv_med_3': 1 if couv_med_val == 'CNOPS/FAR/CNSS' else 0
}

# --- Affichage du résultat ---
if st.button("Calculer le Score de Risque"):
    hr_score, risque, couleur = calcul_score_cox(patient_input)

    st.markdown("---")
    st.subheader("Résultats du Risque")

    # Utilisation des colonnes pour un affichage plus clair
    col_hr, col_risk = st.columns(2)

    with col_hr:
        st.metric(label="Risque Relatif (HR)", value=f"{hr_score:.2f}x")
        st.caption("Par rapport au patient moyen de la cohorte.")

    with col_risk:
        st.info(f"Niveau de Risque : **{risque}**")

    # Jauge simplifiée (avec markdown)
    if couleur == 'green':
        st.success(f"Faible risque par rapport au patient moyen.")
    elif couleur == 'orange':
        st.warning(f"Risque modéré par rapport au patient moyen.")
    elif couleur == 'red':
        st.error(f"Risque élevé par rapport au patient moyen. HR = {hr_score:.2f}x.")