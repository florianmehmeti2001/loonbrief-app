import streamlit as st
import pandas as pd
from datetime import time, date, timedelta

st.set_page_config(page_title="Wagon Plastron - Looncalculator", layout="wide", page_icon="🚆")

# --- Wachtwoordbeveiliging ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("🚆 Wagon Plastron — Beveiligde Toegang")
    st.markdown("Voer het wachtwoord in om de looncalculator te ontgrendelen.")
    
    password = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen"):
        if password == "wagonplastron":  # Je kunt dit wachtwoord hier aanpassen
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Onjuist wachtwoord. Probeer het opnieuw.")
    return False

if not check_password():
    st.stop()

# --- Custom Railway UI & Styling ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
        color: white;
        border-radius: 8px;
        border: 1px solid #e43f5a;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #e43f5a 0%, #1f4068 100%);
        border-color: white;
    }
</style>
""", unsafe_allow_html=True)

# 1. Standaard waarden dictionary
standaard_waarden = {
    'gebruik_voorbeeld': False,
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
        f'h{i}_start_time': time(0, 0), f'h{i}_einde_time': time(0, 0),
        f'h{i}_zondag': False, f'h{i}_feestdag': False,
        f'shift_{i}_date': date.today(),
        
        f't{i}_shift': 'H.L.P.', f't{i}_f1': 'Steward', f't{i}_f2': 'Geen',
        f't{i}_start_time': time(0, 0), f't{i}_einde_time': time(0, 0),
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
    
    st.checkbox("📌 Gebruik voorbeeld van foto's", key='gebruik_voorbeeld')
    st.markdown("---")

    if st.session_state.gebruik_voorbeeld:
        st.session_state.statuut = "Extra (Horeca)"
        st.session_state.uurloon = 15.97
        st.session_state.aantal_shiften = 2
        st.session_state.hotel = "JA"
        st.session_state.kledij_aantal = 3
        st.session_state.declaraties = 18.00
        
        for i in [1, 2]:
            st.session_state[f'shift_{i}_date'] = date.today()
            st.session_state[f'h{i}_shift'] = "PRS"
            st.session_state[f'h{i}_f1'] = "ATM"
            st.session_state[f'h{i}_f2'] = "Conducteur"
            st.session_state[f'h{i}_start_time'] = time(7, 35)
            st.session_state[f'h{i}_einde_time'] = time(12, 30)
            st.session_state[f'h{i}_feestdag'] = False
            st.session_state[f'h{i}_zondag'] = False
            
            st.session_state[f't{i}_shift'] = "PRS"
            st.session_state[f't{i}_f1'] = "ATM"
            st.session_state[f't{i}_f2'] = "Conducteur"
            st.session_state[f't{i}_start_time'] = time(15, 10)
            st.session_state[f't{i}_einde_time'] = time(21, 50)
            st.session_state[f't{i}_feestdag'] = False
            st.session_state[f't{i}_zondag'] = (i == 2)

    is_locked = st.session_state.gebruik_voorbeeld

    st.selectbox("Kies je statuut", ["Student", "Flexi", "Extra (Horeca)"], key='statuut', disabled=is_locked)
    st.number_input("Basis Uurloon (€)", value=15.97, step=0.10, key='uurloon', disabled=is_locked)
    st.selectbox("Aantal reizen/shiften deze week", [1, 2, 3], key='aantal_shiften', disabled=is_locked)
    st.radio("Hotelovernachting?", ["JA", "NEE"], key='hotel', disabled=is_locked, horizontal=True)
    st.number_input("Aantal dagen kledijvergoeding", min_value=0, max_value=10, key='kledij_aantal', disabled=is_locked)
    st.number_input("Declaraties (€)", min_value=0.0, step=1.0, key='declaraties', disabled=is_locked)
    
    st.markdown("---")
    if not is_locked:
        if st.button("🧹 Reset alle cellen"):
            reset_alle_velden()
            st.rerun()

st.title("🚆 Wagon Plastron — Looncalculator")

st.markdown("""
**Genoeg gehad van al die 'mysterieuze' fouten in je loonbrief?** 🚂💶  
Maak plaats voor de **ECHTE** loonbrief! Bereken hier snel, eerlijk en feilloos wat je bankrekening *echt* mag verwachten voor al dat harde werk op de sporen.
""")

def bereken_netto_tijd(shift, start_time, einde_time):
    if shift == "H.L.P.":
        return 0.0, 0.0
        
    s_uur = start_time.hour + start_time.minute / 60.0
    e_uur = einde_time.hour + einde_time.minute / 60.0
    
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

def get_terugrit_date(h_date, h_shift):
    if not isinstance(h_date, date):
        return h_date
    wd = h_date.weekday()
    
    if h_shift == "PRS":
        if wd == 5:
            return h_date + timedelta(days=1)
        return h_date
    elif h_shift == "BLN":
        return h_date + timedelta(days=1)
    elif h_shift in ["DD", "PRG"]:
        if wd == 4:
            return h_date + timedelta(days=2)
        return h_date + timedelta(days=1)
    
    return h_date

hotel_actief_op_shift = 1
if st.session_state.hotel == "JA":
    gevonden = False
    for i in range(1, st.session_state.aantal_shiften + 1):
        if st.session_state[f'h{i}_zondag'] or st.session_state[f't{i}_zondag'] or st.session_state[f'h{i}_feestdag'] or st.session_state[f't{i}_feestdag']:
            hotel_actief_op_shift = i
            gevonden = True
            break
    if not gevonden:
        hotel_actief_op_shift = st.session_state.aantal_shiften

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
    h_start = st.session_state[f'h{i}_start_time']
    h_einde = st.session_state[f'h{i}_einde_time']
    t_start = st.session_state[f't{i}_start_time']
    t_einde = st.session_state[f't{i}_einde_time']
    
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
    
    is_overnachting_shift = (st.session_state.hotel == "JA" and i == hotel_actief_op_shift)
    
    if is_overnachting_shift:
        h_w = min(11.0, h_netto) if h_shift != "H.L.P." else 0.0
        h_o = max(0.0, h_netto - 11.0) if h_shift != "H.L.P." else 0.0
        t_w = min(11.0, t_netto) if t_shift != "H.L.P." else 0.0
        t_o = max(0.0, t_netto - 11.0) if t_shift != "H.L.P." else 0.0
        
        totaal_werken += (h_w + t_w)
        
        if h_zondag or h_feestdag: totaal_200 += h_o
        else: totaal_150 += h_o
        
        if t_zondag or t_feestdag: totaal_200 += t_o
        else: totaal_150 += t_o
    else:
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
            h_w = min(11.0, h_netto) if h_shift != "H.L.P." else 0.0
            h_o = max(0.0, h_netto - 11.0) if h_shift != "H.L.P." else 0.0
            t_w = min(11.0, t_netto) if t_shift != "H.L.P." else 0.0
            t_o = max(0.0, t_netto - 11.0) if t_shift != "H.L.P." else 0.0
            
            totaal_werken += (h_w + t_w)
            
            if h_zondag or h_feestdag: totaal_200 += h_o
            else: totaal_150 += h_o
            
            if t_zondag or t_feestdag: totaal_200 += t_o
            else: totaal_150 += t_o
        
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

# Render invoerblokken in mooie kaarten met datumselectie
for i in range(1, st.session_state.aantal_shiften + 1):
    with st.container(border=True):
        st.markdown(f"### 🔁 Shift / Reis {i}")
        st.date_input(f"Datum van Reis {i} (Heenrit)", key=f'shift_{i}_date', disabled=is_locked)
        
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚆 Heenrit")
            st.selectbox("Bestemming", ["H.L.P.", "PRG", "PRS", "BLN", "DD"], key=f'h{i}_shift', disabled=is_locked)
            st.selectbox("Functie 1", ["Steward", "ATM", "TM"], key=f'h{i}_f1', disabled=is_locked)
            st.selectbox("Functie 2", ["Conducteur", "Geen"], key=f'h{i}_f2', disabled=is_locked)
            
            st.time_input("Start shift (Heen)", key=f'h{i}_start_time', disabled=is_locked)
            st.time_input("Einde shift (Heen)", key=f'h{i}_einde_time', disabled=is_locked)
            
            st.checkbox("Feestdag?", key=f'h{i}_feestdag', disabled=is_locked)
            st.checkbox("Zondag?", key=f'h{i}_zondag', disabled=is_locked)

        with col2:
            st.subheader("🚆 Terugrit")
            st.selectbox("Bestemming", ["H.L.P.", "PRG", "PRS", "BLN", "DD"], key=f't{i}_shift', disabled=is_locked)
            st.selectbox("Functie 1", ["Steward", "ATM", "TM"], key=f't{i}_f1', disabled=is_locked)
            st.selectbox("Functie 2", ["Conducteur", "Geen"], key=f't{i}_f2', disabled=is_locked)
            
            st.time_input("Start shift (Terug)", key=f't{i}_start_time', disabled=is_locked)
            st.time_input("Einde shift (Terug)", key=f't{i}_einde_time', disabled=is_locked)
            
            st.checkbox("Feestdag?", key=f't{i}_feestdag', disabled=is_locked)
            st.checkbox("Zondag?", key=f't{i}_zondag', disabled=is_locked)

st.markdown("---")

# --- Weekagenda Overzicht (Maandag t/m Zondag) met Kleurcodes per Traject ---
st.subheader("📅 Weekagenda (Maandag — Zondag)")
dagnamen = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']
week_cols = st.columns(7)

def get_agenda_styling(text):
    if "PRS" in text:
        return "#1b4f72", "#3498db"
    elif "BLN" in text:
        return "#2471a3", "#5499c7"
    elif "DD" in text:
        return "#7d6608", "#f1c40f"
    elif "PRG" in text:
        return "#b7950b", "#f39c12"
    else:
        return "#2c3e50", "#7f8c8d"

dag_dict = {dag: [] for dag in dagnamen}
for i in range(1, st.session_state.aantal_shiften + 1):
    h_date = st.session_state[f'shift_{i}_date']
    h_shift = st.session_state[f'h{i}_shift']
    t_shift = st.session_state[f't{i}_shift']
    
    if h_shift != "H.L.P.":
        h_wd = h_date.weekday()
        h_dag_naam = dagnamen[h_wd]
        dag_dict[h_dag_naam].append(f"R{i}: BRU ➔ {h_shift}")
        
    if t_shift != "H.L.P.":
        t_date = get_terugrit_date(h_date, h_shift)
        t_wd = t_date.weekday()
        t_dag_naam = dagnamen[t_wd]
        dag_dict[t_dag_naam].append(f"R{i}: {t_shift} ➔ BRU")

for idx, dag in enumerate(dagnamen):
    with week_cols[idx]:
        st.markdown(f"**{dag}**")
        if dag_dict[dag]:
            for item in dag_dict[dag]:
                bg_color, border_color = get_agenda_styling(item)
                st.markdown(f"""
                    <div style="background-color: {bg_color}; border-left: 4px solid {border_color}; padding: 6px 10px; border-radius: 4px; margin-bottom: 5px; font-size: 12px; color: white; font-weight: 500;">
                        {item}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.write("—")

st.markdown("---")

st.subheader(f"📋 Gedetailleerde Uitsplitsing — Statuut: {stat}")

tab1, tab2, tab3, tab4 = st.tabs(["1. Bruto Opbouw", "2. Inhoudingen & Belastbaar", "3. Netto & Vergoedingen", "4. Vakantiegeld"])

with tab1:
    df_bruto = pd.DataFrame([
        ["Totaal Werken", f"{totaal_werken:.2f} u", f"€ {u:.2f}", f"€ {totaal_werken * u:.2f}"],
        ["Totaal Pauze", f"{totaal_pauze:.2f} u", f"€ {u:.2f}", f"€ {totaal_pauze * u:.2f}"],
        ["Overuren 150%", f"{totaal_150:.2f} u", f"€ {u*1.5:.2f}", f"€ {totaal_150 * u * 1.5:.2f}"],
        ["Overuren 200%", f"{totaal_200:.2f} u", f"€ {u*2.0:.2f}", f"€ {totaal_200 * u * 2.0:.2f}"],
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
