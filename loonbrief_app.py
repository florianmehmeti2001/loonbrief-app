import streamlit as st
import pandas as pd
from datetime import time

st.set_page_config(page_title="Wagon Plastron - Looncalculator", layout="wide")

# 1. Standaard waarden dictionary (leeg / op nul bij opstarten)
standaard_waarden = {
    'statuut': 'Student',
    'uurloon': 0.0,
    'hotel': 'NEE',
    'kledij_aantal': 0,
    'declaraties': 0.0,
    # Heenrit
    'h_shift': 'H.L.P.', 'h_f1': 'Steward', 'h_f2': 'Geen',
    'h_start': time(0, 0), 'h_einde': time(0, 0),
    'h_zondag': False, 'h_feestdag': 'NEE',
    'h_prsbln': 0, 'h_bruprg': 0,
    # Terugrit
    't_shift': 'H.L.P.', 't_f1': 'Steward', 't_f2': 'Geen',
    't_start': time(0, 0), 't_einde': time(0, 0),
    't_zondag': False, 't_feestdag': 'NEE',
    't_prsbln': 0, 't_bruprg': 0,
}

for key, val in standaard_waarden.items():
    if key not in st.session_state:
        st.session_state[key] = val

def reset_alle_velden():
    for key in standaard_waarden.keys():
        if key in st.session_state:
            del st.session_state[key]

# Sidebar met instellingen (Statuten in volgorde: Student, Flexi, Extra)
with st.sidebar:
    st.header("⚙️ Instellingen")
    st.selectbox("Kies je statuut", ["Student", "Flexi", "Extra (Horeca)"], key='statuut')
    st.number_input("Basis Uurloon (€)", value=0.0, step=0.10, key='uurloon')
    st.radio("Hotelovernachting?", ["JA", "NEE"], key='hotel')
    st.number_input("Aantal dagen kledijvergoeding", min_value=0, max_value=10, key='kledij_aantal')
    st.number_input("Declaraties (€)", min_value=0.0, step=1.0, key='declaraties')
    
    st.markdown("---")
    if st.button("🧹 Reset alle cellen"):
        reset_alle_velden()
        st.rerun()

st.title("🚆 Wagon Plastron — Looncalculator")

# 2. Urenberekening functie per rit met H.L.P., Zondag en Feestdag check
def bereken_rit_uren(shift, start, einde, is_zondag, feestdag):
    if shift == "H.L.P.":
        return 0.0, 0.0, 0.0, 0.0
        
    s_uur = start.hour + start.minute / 60.0
    e_uur = einde.hour + einde.minute / 60.0
    is_weekend_of_feestdag = is_zondag or (feestdag == "JA")
    
    if shift == "PRS":
        totaal_duur = e_uur - s_uur
        if totaal_duur < 0: totaal_duur += 24
        pauze = 0.0
        werken = max(0.0, totaal_duur - pauze)
        over_tijd = max(0.0, werken - 11.0)
    else:
        totaal_duur = (24.0 - s_uur + e_uur) % 24
        if totaal_duur == 0: totaal_duur = 24.0
        pauze = 5.0 if totaal_duur > 5 else 0.0
        netto_tijd = max(0.0, totaal_duur - pauze)
        werken = min(11.0, netto_tijd)
        over_tijd = max(0.0, netto_tijd - 11.0)
        
    if is_weekend_of_feestdag:
        over_150 = 0.0
        over_200 = over_tijd
    else:
        over_150 = over_tijd
        over_200 = 0.0
        
    return werken, pauze, over_150, over_200

h_w, h_p, h_150, h_200 = bereken_rit_uren(st.session_state.h_shift, st.session_state.h_start, st.session_state.h_einde, st.session_state.h_zondag, st.session_state.h_feestdag)
t_w, t_p, t_150, t_200 = bereken_rit_uren(st.session_state.t_shift, st.session_state.t_start, st.session_state.t_einde, st.session_state.t_zondag, st.session_state.t_feestdag)

totaal_werken = h_w + t_w
totaal_pauze = h_p + t_p
totaal_150 = h_150 + t_150
totaal_200 = h_200 + t_200

u = st.session_state.uurloon

# Premies en tellingen
atm_count = (1 if st.session_state.h_f1 == "ATM" and st.session_state.h_shift != "H.L.P." else 0) + (1 if st.session_state.t_f1 == "ATM" and st.session_state.t_shift != "H.L.P." else 0)
tm_count = (1 if st.session_state.h_f1 == "TM" and st.session_state.h_shift != "H.L.P." else 0) + (1 if st.session_state.t_f1 == "TM" and st.session_state.t_shift != "H.L.P." else 0)

bru_count = (st.session_state.h_bruprg if st.session_state.h_shift != "H.L.P." else 0) + (st.session_state.t_bruprg if st.session_state.t_shift != "H.L.P." else 0)
prs_count = (st.session_state.h_prsbln if st.session_state.h_shift != "H.L.P." else 0) + (st.session_state.t_prsbln if st.session_state.t_shift != "H.L.P." else 0)

zondag_premie_aantal = (1 if st.session_state.h_zondag and st.session_state.h_shift != "H.L.P." else 0) + (1 if st.session_state.t_zondag and st.session_state.t_shift != "H.L.P." else 0)
feestdag_premie_aantal = (1 if st.session_state.h_feestdag == "JA" and st.session_state.h_shift != "H.L.P." else 0) + (1 if st.session_state.t_feestdag == "JA" and st.session_state.t_shift != "H.L.P." else 0)

atm_geld = atm_count * 30.0
tm_geld = tm_count * 50.0
bruprg_geld = bru_count * 100.0
prsbln_geld = prs_count * 50.0
zondag_geld = zondag_premie_aantal * (6 * 2.0)
feestdag_geld = feestdag_premie_aantal * (6 * 2.0)

bruto = (totaal_werken * u) + (totaal_pauze * u) + (totaal_150 * u * 1.5) + (totaal_200 * u * 2.0) + atm_geld + tm_geld + bruprg_geld + prsbln_geld + zondag_geld + feestdag_geld

stat = st.session_state.statuut
rsz = 0.0
bv = 0.0

if stat == "Student":
    rsz = -bruto * 0.0271
elif stat == "Extra (Horeca)":
    bv = -bruto * 0.3331

belastbaar = bruto + rsz + bv

kledij = st.session_state.kledij_aantal * 2.20
declaraties = st.session_state.declaraties
dagvergoeding = 50.0 if st.session_state.hotel == "JA" else 25.0

netto_loon = belastbaar + kledij + declaraties + dagvergoeding

# Vakantiegeld berekening per statuut
vak_dubbel = 0.0
vak_rsz = 0.0
vak_enkel = 0.0
vak_aanvullend = 0.0
totaal_vakantiegeld = 0.0

if stat == "Extra (Horeca)":
    vak_dubbel = bruto * 0.0680
    vak_rsz = -vak_dubbel * 0.1307
    vak_enkel = bruto * 0.0767
    vak_aanvullend = bruto * 0.0087
    totaal_vakantiegeld = vak_dubbel + vak_rsz + vak_enkel + vak_aanvullend
elif stat == "Flexi":
    totaal_vakantiegeld = bruto * 0.0767
elif stat == "Student":
    totaal_vakantiegeld = 0.0 # Studenten bouwen doorgaans geen vakantiegeld op

totaal_loon_met_vakantie = netto_loon + totaal_vakantiegeld

# Grote totaal weergave bovenaan (inclusief Vakantiegeld)
st.markdown("---")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("💵 Totaal Loon (Netto + Vak)", f"€ {totaal_loon_met_vakantie:.2f}")
col_m2.metric("💰 Netto Loon", f"€ {netto_loon:.2f}")
col_m3.metric("🏖️ Vakantiegeld", f"€ {totaal_vakantiegeld:.2f}")
col_m4.metric("📈 Bruto Totaal", f"€ {bruto:.2f}")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚆 Heenrit")
    st.selectbox("Bestemming", ["H.L.P.", "PRG", "PRS", "BLN", "DD", "BRU"], key='h_shift')
    st.selectbox("Functie 1", ["Steward", "ATM", "TM"], key='h_f1')
    st.selectbox("Functie 2", ["Conducteur", "Geen"], key='h_f2')
    st.time_input("Start shift", key='h_start')
    st.time_input("Einde shift", key='h_einde')
    st.radio("Feestdag? (Heen)", ["JA", "NEE"], key='h_feestdag', horizontal=True)
    st.checkbox("Zondag? (Heen)", key='h_zondag')
    st.selectbox("Conducteur Premie BRU/PRG", [0, 1], key='h_bruprg')
    st.selectbox("Conducteur Premie PRS/BLN", [0, 1], key='h_prsbln')

with col2:
    st.subheader("🚆 Terugrit")
    st.selectbox("Bestemming (Terug)", ["H.L.P.", "PRG", "PRS", "BLN", "DD", "BRU"], key='t_shift')
    st.selectbox("Functie 1 (Terug)", ["Steward", "ATM", "TM"], key='t_f1')
    st.selectbox("Functie 2 (Terug)", ["Conducteur", "Geen"], key='t_f2')
    st.time_input("Start shift (Terug)", key='t_start')
    st.time_input("Einde shift (Terug)", key='t_einde')
    st.radio("Feestdag? (Terug)", ["JA", "NEE"], key='t_feestdag', horizontal=True)
    st.checkbox("Zondag? (Terug)", key='t_zondag')
    st.selectbox("Conducteur Premie BRU/PRG (Terug)", [0, 1], key='t_bruprg')
    st.selectbox("Conducteur Premie PRS/BLN (Terug)", [0, 1], key='t_prsbln')

st.markdown("---")

st.subheader(f"📋 Gedetailleerde Uitsplitsing — Statuut: {stat}")

tab1, tab2, tab3, tab4 = st.tabs(["1. Bruto Opbouw", "2. Inhoudingen & Belastbaar", "3. Netto & Vergoedingen", "4. Vakantiegeld"])

with tab1:
    df_bruto = pd.DataFrame([
        ["Totaal Werken", f"{totaal_werken:.1f} u", f"€ {u:.2f}", f"€ {totaal_werken * u:.2f}"],
        ["Totaal Pauze", f"{totaal_pauze:.1f} u", f"€ {u:.2f}", f"€ {totaal_pauze * u:.2f}"],
        ["Overuren 150%", f"{totaal_150:.1f} u", f"€ {u*1.5:.2f}", f"€ {totaal_150 * u * 1.5:.2f}"],
        ["Overuren 200%", f"{totaal_200:.1f} u", f"€ {u*2.0:.2f}", f"€ {totaal_200 * u * 2.0:.2f}"],
        ["Feestdagpremie", f"{feestdag_premie_aantal}", "€ 12.00", f"€ {feestdag_geld:.2f}"],
        ["Zondagpremie", f"{zondag_premie_aantal}", "€ 12.00", f"€ {zondag_geld:.2f}"],
        ["ATM premie", f"{atm_count}", "€ 30.00", f"€ {atm_geld:.2f}"],
        ["TM premie", f"{tm_count}", "€ 50.00", f"€ {tm_geld:.2f}"],
        ["Conducteur BRUPRG", f"{bru_count}", "€ 100.00", f"€ {bruprg_geld:.2f}"],
        ["Conducteur PRSBLN", f"{prs_count}", "€ 50.00", f"€ {prsbln_geld:.2f}"],
    ], columns=["Onderdeel", "Aantal / Uren", "Basis", "Totaal (€)"])
    st.table(df_bruto)

with tab2:
    df_inh = pd.DataFrame([
        ["Bruto Totaal", f"€ {bruto:.2f}"],
        ["RSZ Bijdrage", f"€ {rsz:.2f}"],
        ["Bedrijfsvoorheffing", f"€ {bv:.2f}"],
        ["Belastbaar Totaal", f"€ {belastbaar:.2f}"],
    ], columns=["Onderdeel", "Bedrag (€)"])
    st.table(df_inh)

with tab3:
    df_netto = pd.DataFrame([
        ["Belastbaar", f"€ {belastbaar:.2f}"],
        ["Kledijvergoeding", f"€ {kledij:.2f} ({st.session_state.kledij_aantal} d)"],
        ["Declaraties", f"€ {declaraties:.2f}"],
        ["Dagvergoeding (Hotel: " + st.session_state.hotel + ")", f"€ {dagvergoeding:.2f}"],
        ["Netto Loon", f"€ {netto_loon:.2f}"],
    ], columns=["Onderdeel", "Bedrag (€)"])
    st.table(df_netto)

with tab4:
    if stat == "Extra (Horeca)":
        df_vak = pd.DataFrame([
            ["Vakantiegeld dubbel (6.8%)", f"€ {vak_dubbel:.2f}"],
            ["RSZ op dubbel vakantiegeld (-13.07%)", f"€ {vak_rsz:.2f}"],
            ["Vakantiegeld enkel (7.67%)", f"€ {vak_enkel:.2f}"],
            ["Aanvullend vakantiegeld (0.87%)", f"€ {vak_aanvullend:.2f}"],
            ["Totaal Vakantiegeld", f"€ {totaal_vakantiegeld:.2f}"],
        ], columns=["Onderdeel", "Bedrag (€)"])
        st.table(df_vak)
    elif stat == "Flexi":
        df_vak = pd.DataFrame([
            ["Flexi Vakantiegeld (7.67%)", f"€ {totaal_vakantiegeld:.2f}"],
        ], columns=["Onderdeel", "Bedrag (€)"])
        st.table(df_vak)
    else:
        df_vak = pd.DataFrame([
            ["Vakantiegeld", f"€ {totaal_vakantiegeld:.2f}"],
        ], columns=["Onderdeel", "Bedrag (€)"])
        st.table(df_vak)
