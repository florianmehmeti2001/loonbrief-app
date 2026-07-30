import streamlit as st
import pandas as pd
from datetime import time

st.set_page_config(page_title="Wagon Plastron - Looncalculator", layout="wide")

# 1. Standaard waarden dictionary (kledij standaard op 1)
standaard_waarden = {
    'statuut': 'Student',
    'uurloon': 0.0,
    'hotel': 'NEE',
    'kledij_aantal': 1,
    'declaraties': 0.0,
    'aantal_shiften': 1,
}

for i in [1, 2, 3]:
    standaard_waarden.update({
        f'h{i}_shift': 'H.L.P.', f'h{i}_f1': 'Steward', f'h{i}_f2': 'Geen',
        f'h{i}_start_u': 0, f'h{i}_start_m': 0,
        f'h{i}_einde_u': 0, f'h{i}_einde_m': 0,
        f'h{i}_zondag': False, f'h{i}_feestdag': False,
        
        f't{i}_shift': 'H.L.P.', f't{i}_f1': 'Steward', f't{i}_f2': 'Geen',
        f't{i}_start_u': 0, f't{i}_start_m': 0,
        f't{i}_einde_u': 0, f't{i}_einde_m': 0,
        f't{i}_zondag': False, f't{i}_feestdag': False,
    })

for key, val in standaard_waarden.items():
    if key not in st.session_state:
        st.session_state[key] = val

def reset_alle_velden():
    for key in standaard_waarden.keys():
        if key in st.session_state:
            del st.session_state[key]

# Sidebar met instellingen
with st.sidebar:
    st.header("⚙️ Instellingen")
    st.selectbox("Kies je statuut", ["Student", "Flexi", "Extra (Horeca)"], key='statuut')
    st.number_input("Basis Uurloon (€)", value=0.0, step=0.10, key='uurloon')
    st.selectbox("Aantal reizen/shiften deze week", [1, 2, 3], key='aantal_shiften')
    st.radio("Hotelovernachting?", ["JA", "NEE"], key='hotel')
    st.number_input("Aantal dagen kledijvergoeding", min_value=0, max_value=10, key='kledij_aantal')
    st.number_input("Declaraties (€)", min_value=0.0, step=1.0, key='declaraties')
    
    st.markdown("---")
    if st.button("🧹 Reset alle cellen"):
        reset_alle_velden()
        st.rerun()

st.title("🚆 Wagon Plastron — Looncalculator")

# Grappig introductietekstje
st.markdown("""
**Genoeg gehad van al die 'mysterieuze' fouten in je loonbrief?** 🚂💶  
Maak plaats voor de **ECHTE** loonbrief! Bereken hier snel, eerlijk en feilloos wat je bankrekening *echt* mag verwachten voor al dat harde werk op de sporen.
""")

hours_list = list(range(24))
minutes_list = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

# Functie om netto tijd en pauze per rit te berekenen
def bereken_netto_tijd(shift, start, einde):
    if shift == "H.L.P.":
        return 0.0, 0.0
        
    s_uur = start.hour + start.minute / 60.0
    e_uur = einde.hour + einde.minute / 60.0
    
    if shift == "PRS":
        totaal_duur = e_uur - s_uur
        if totaal_duur < 0: totaal_duur += 24
        pauze = 0.0
        netto_tijd = max(0.0, totaal_duur - pauze)
    else:
        totaal_duur = (24.0 - s_uur + e_uur) % 24
        if totaal_duur == 0: totaal_duur = 24.0
        pauze = 5.0 if totaal_duur > 5 else 0.0
        netto_tijd = max(0.0, totaal_duur - pauze)
        
    return netto_tijd, pauze

# Loop door het aantal geselecteerde shiften en tel alles correct op
totaal_werken = 0.0
totaal_pauze = 0.0
totaal_150 = 0.0
totaal_200 = 0.0

atm_count = 0
tm_count = 0
bru_count = 0
prs_count = 0
zondag_premie_aantal = 0
feestdag_premie_aantal = 0

for i in range(1, st.session_state.aantal_shiften + 1):
    h_start = time(st.session_state[f'h{i}_start_u'], st.session_state[f'h{i}_start_m'])
    h_einde = time(st.session_state[f'h{i}_einde_u'], st.session_state[f'h{i}_einde_m'])
    t_start = time(st.session_state[f't{i}_start_u'], st.session_state[f't{i}_start_m'])
    t_einde = time(st.session_state[f't{i}_einde_u'], st.session_state[f't{i}_einde_m'])
    
    h_shift = st.session_state[f'h{i}_shift']
    t_shift = st.session_state[f't{i}_shift']
    h_f1 = st.session_state[f'h{i}_f1']
    t_f1 = st.session_state[f't{i}_f1']
    h_f2 = st.session_state[f'h{i}_f2']
    t_f2 = st.session_state[f't{i}_f2']
    
    h_zondag = st.session_state[f'h{i}_zondag']
    t_zondag = st.session_state[f't{i}_zondag']
    h_feestdag = st.session_state[f'h{i}_feestdag']
    t_feestdag = st.session_state[f't{i}_feestdag']

    h_netto, h_pauze = bereken_netto_tijd(h_shift, h_start, h_einde)
    t_netto, t_pauze = bereken_netto_tijd(t_shift, t_start, t_einde)
    
    totaal_pauze += (h_pauze + t_pauze)
    
    # Als beide ritten in deze shift PRS zijn, tellen we de uren van die dag samen
    if h_shift == "PRS" and t_shift == "PRS":
        dag_netto = h_netto + t_netto
        w_shift = min(11.0, dag_netto)
        o_shift = max(0.0, dag_netto - 11.0)
        
        totaal_werken += w_shift
        
        if h_zondag or t_zondag or h_feestdag or t_feestdag:
            totaal_200 += o_shift
        else:
            totaal_150 += o_shift
    else:
        # Losse ritten / andere bestemmingen apart behandelen
        h_w = min(11.0, h_netto) if h_shift != "H.L.P." else 0.0
        h_o = max(0.0, h_netto - 11.0) if h_shift != "H.L.P." else 0.0
        t_w = min(11.0, t_netto) if t_shift != "H.L.P." else 0.0
        t_o = max(0.0, t_netto - 11.0) if t_shift != "H.L.P." else 0.0
        
        totaal_werken += (h_w + t_w)
        
        if h_zondag or h_feestdag:
            totaal_200 += h_o
        else:
            totaal_150 += h_o
            
        if t_zondag or t_feestdag:
            totaal_200 += t_o
        else:
            totaal_150 += t_o
        
    # Premies per rit optellen
    if h_shift != "H.L.P.":
        if h_f1 == "ATM": atm_count += 1
        if h_f1 == "TM": tm_count += 1
        if h_f2 == "Conducteur":
            if h_shift in ["DD", "PRG"]: bru_count += 1
            elif h_shift in ["PRS", "BLN"]: prs_count += 1
        if h_zondag: zondag_premie_aantal += 1
        if h_feestdag: feestdag_premie_aantal += 1
        
    if t_shift != "H.L.P.":
        if t_f1 == "ATM": atm_count += 1
        if t_f1 == "TM": tm_count += 1
        if t_f2 == "Conducteur":
            if t_shift in ["DD", "PRG"]: bru_count += 1
            elif t_shift in ["PRS", "BLN"]: prs_count += 1
        if t_zondag: zondag_premie_aantal += 1
        if t_feestdag: feestdag_premie_aantal += 1

u = st.session_state.uurloon

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
dagvergoeding = (st.session_state.aantal_shiften * 25.0) + (25.0 if st.session_state.hotel == "JA" else 0.0)

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
    totaal_vakantiegeld = 0.0

totaal_loon_met_vakantie = netto_loon + totaal_vakantiegeld

# --- Grote Totaal Weergave Bovenaan ---
st.markdown("---")
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("💵 Totaal Loon (Netto + Vak)", f"€ {totaal_loon_met_vakantie:.2f}")
col_m2.metric("💰 Netto Loon", f"€ {netto_loon:.2f}")
col_m3.metric("🏖️ Vakantiegeld", f"€ {totaal_vakantiegeld:.2f}")
st.markdown("---")

# Render invoerblokken dynamisch op basis van gekozen aantal shiften
for i in range(1, st.session_state.aantal_shiften + 1):
    if st.session_state.aantal_shiften > 1:
        st.markdown(f"### 🔁 Shift / Reis {i}")
        
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚆 Heenrit")
        st.selectbox("Bestemming", ["H.L.P.", "PRG", "PRS", "BLN", "DD"], key=f'h{i}_shift')
        st.selectbox("Functie 1", ["Steward", "ATM", "TM"], key=f'h{i}_f1')
        st.selectbox("Functie 2", ["Conducteur", "Geen"], key=f'h{i}_f2')
        
        st.text("Start shift")
        hs1, hs2 = st.columns(2)
        hs1.selectbox("Uur", hours_list, key=f'h{i}_start_u', format_func=lambda x: f"{x:02d}u")
        hs2.selectbox("Min", minutes_list, key=f'h{i}_start_m', format_func=lambda x: f"{x:02d}m")
        
        st.text("Einde shift")
        he1, he2 = st.columns(2)
        he1.selectbox("Uur", hours_list, key=f'h{i}_einde_u', format_func=lambda x: f"{x:02d}u")
        he2.selectbox("Min", minutes_list, key=f'h{i}_einde_m', format_func=lambda x: f"{x:02d}m")
        
        st.checkbox("Feestdag?", key=f'h{i}_feestdag')
        st.checkbox("Zondag?", key=f'h{i}_zondag')

    with col2:
        st.subheader("🚆 Terugrit")
        st.selectbox("Bestemming", ["H.L.P.", "PRG", "PRS", "BLN", "DD"], key=f't{i}_shift')
        st.selectbox("Functie 1", ["Steward", "ATM", "TM"], key=f't{i}_f1')
        st.selectbox("Functie 2", ["Conducteur", "Geen"], key=f't{i}_f2')
        
        st.text("Start shift")
        ts1, ts2 = st.columns(2)
        ts1.selectbox("Uur", hours_list, key=f't{i}_start_u', format_func=lambda x: f"{x:02d}u")
        ts2.selectbox("Min", minutes_list, key=f't{i}_start_m', format_func=lambda x: f"{x:02d}m")
        
        st.text("Einde shift")
        te1, te2 = st.columns(2)
        te1.selectbox("Uur", hours_list, key=f't{i}_einde_u', format_func=lambda x: f"{x:02d}u")
        te2.selectbox("Min", minutes_list, key=f't{i}_einde_m', format_func=lambda x: f"{x:02d}m")
        
        st.checkbox("Feestdag?", key=f't{i}_feestdag')
        st.checkbox("Zondag?", key=f't{i}_zondag')

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
        ["Conducteur premie (DD/PRG €100)", f"{bru_count}", "€ 100.00", f"€ {bruprg_geld:.2f}"],
        ["Conducteur premie (PRS/BLN €50)", f"{prs_count}", "€ 50.00", f"€ {prsbln_geld:.2f}"],
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
        ["Dagvergoeding", f"€ {dagvergoeding:.2f}"],
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

# --- Credits Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 14px;'>Gemaakt door Florian 🚂 — Om je bankrekening veilig te houden</p>",
    unsafe_allow_html=True
)
