import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from itertools import combinations

# --- 1. GIAO DIỆN CHUẨN (V5.2) ---
st.set_page_config(page_title="8-BIT DNA MASTER V5.2", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { color: #000000 !important; background-color: #ffffff !important; font-size: 0.8rem !important; }
    .stButton button { 
        width: 100%; border-radius: 6px; height: 42px; font-weight: 700; 
        background-color: #0047AB !important; color: #ffffff !important; border: none !important;
    }
    .dan-box { 
        background-color: #f1f5f9; border: 2px solid #0047AB; border-radius: 8px; 
        padding: 12px; font-family: monospace; font-weight: 700; color: #0047AB; 
        text-align: center; font-size: 1rem;
    }
    .dna-tag { background-color: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; }
    </style>
""", unsafe_allow_html=True)

# --- 2. TƯ DUY 44 DẠNG BIT (DNA ENGINE) ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]
BIT_LABELS = ["Đ.CL", "Đu.CL", "T.CL", "Đ.TB", "Đu.TB", "T.TB", "Hệ", "Hi.TB"]

@st.cache_data
def get_8bit(n):
    val = int(n); d, u = val // 10, val % 10
    return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
            1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
            1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]

# Tạo bản đồ 44 dạng DNA
@st.cache_resource
def get_dna_map():
    dna_map = {}
    for i in range(100):
        code = tuple(get_8bit(i))
        if code not in dna_map: dna_map[code] = []
        dna_map[code].append(f"{i:02d}")
    return dna_map

DNA_CHART = get_dna_map()

# --- 3. QUANTUM ENGINE V5.2 ---
def quantum_core(history, last_n):
    if len(history) < 2: return [0.5]*8, []
    bits_data = np.array([get_8bit(h["Số"]) for h in history])
    current_bits = np.array(get_8bit(last_n))
    final_probs = np.zeros(8)
    insights = []

    # Quét Đơn (10k) & Quét Cặp (22k)
    seg10 = bits_data[-11:]
    for i in range(8):
        m = [seg10[k+1] for k in range(len(seg10)-1) if seg10[k][i] == current_bits[i]]
        if m: final_probs += np.mean(m, axis=0) * 0.4

    if len(history) >= 22:
        seg22 = bits_data[-23:]
        for i, j in combinations(range(8), 2):
            m = [seg22[k+1] for k in range(len(seg22)-1) if seg22[k][i] == current_bits[i] and seg22[k][j] == current_bits[j]]
            if m:
                r = np.mean(m, axis=0)
                final_probs += r * 0.6
                if np.max(r) >= 0.85: insights.append(f"Cặp {BIT_LABELS[i]}-{BIT_LABELS[j]}: {int(np.max(r)*100)}%")

    return np.clip(final_probs / (1.0 if len(history) < 22 else 1.2), 0.05, 0.95).tolist(), insights

# --- 4. APP MAIN ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

st.title("🛡️ 8-BIT DNA ARCHITECT V5.2")

with st.sidebar:
    st.header("📂 HỆ THỐNG")
    up = st.file_uploader("Nạp Master JSON:", type="json")
    if up:
        data = json.load(up); raw = data.get("history", [])
        st.session_state.history = sorted([{"Ngày": h.get("Ngày", "00/00"), "Kỳ": int(h.get("Kỳ", 0)), "Số": f"{int(h.get('Số', 0)):02d}", "Rank": h.get("Rank", 0)} for h in raw], key=lambda x: x["Kỳ"])
        if st.session_state.history: st.session_state.last_n = int(st.session_state.history[-1]["Số"])
    if st.button("🔴 RESET"): st.session_state.history = []; st.rerun()

# NHẬP LIỆU
with st.container():
    c1, c2, c3 = st.columns(3)
    n_in = c1.text_input("Số vừa nổ:")
    next_ky = st.session_state.history[-1]["Kỳ"] + 1 if st.session_state.history else 1
    k_in = c2.number_input("Kỳ:", value=next_ky)
    if st.button("🚀 PHÂN TÍCH DNA"):
        if n_in:
            val = int(n_in[-2:])
            if st.session_state.history:
                p, _ = quantum_core(st.session_state.history, st.session_state.last_n)
                scr = []
                for i in range(100):
                    b = get_8bit(i); m = sum(b[j]*p[j] + (1-b[j])*(1-p[j]) for j in range(8))
                    scr.append({"S": f"{i:02d}", "M": m})
                df_t = pd.DataFrame(scr).sort_values("M", ascending=False); df_t['R'] = range(1, 101)
                r_v = df_t[df_t['S'] == f"{val:02d}"]['R'].values[0]
            else: r_v = 0
            st.session_state.history.append({"Ngày": datetime.now().strftime("%d/%m"), "Kỳ": int(k_in), "Số": f"{val:02d}", "Rank": int(r_v)})
            st.session_state.last_n = val; st.rerun()

if st.session_state.history:
    probs, insights = quantum_core(st.session_state.history, st.session_state.last_n)
    res = []
    for i in range(100):
        b = get_8bit(i); m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        res.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(res).sort_values("M", ascending=False)

    t1, t2, t3 = st.tabs(["🎯 DÀN TINH ANH", "🔬 GIẢI MÃ DNA (44 DẠNG)", "📊 NHẬT KÝ"])
    
    with t1:
        st.write(f"🔢 Số gốc: **{st.session_state.last_n:02d}** | DNA: **{len(DNA_CHART[tuple(get_8bit(st.session_state.last_n))])} số chung nhóm**")
        ms = st.columns(8)
        for i, (l, p) in enumerate(zip(BIT_LABELS, probs)): ms[i].metric(l, f"{int(p*100)}%")
        st.divider()
        da, db = st.columns(2)
        da.markdown("**🔥 DÀN A (50 SỐ)**"); da.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(50)['S'].tolist())}</div>", unsafe_allow_html=True)
        db.markdown("**💎 DÀN B (36 SỐ)**"); db.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(36)['S'].tolist())}</div>", unsafe_allow_html=True)

    with t2:
        st.subheader("Bản đồ 44 dạng Bit (DNA Cluster)")
        for code, members in DNA_CHART.items():
            if f"{st.session_state.last_n:02d}" in members:
                st.info(f"🧬 Nhóm DNA hiện tại của số {st.session_state.last_n:02d} gồm: {', '.join(members)}")
        if insights: st.success("⚡ Các cặp nhịp bùng nổ: " + " | ".join(insights))

    with t3:
        disp = []
        for h in reversed(st.session_state.history):
            b = get_8bit(h["Số"]); code = tuple(b)
            disp.append({"Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"], "DNA": len(DNA_CHART[code]), "Nhịp": "".join([str(x) for x in b])})
        st.dataframe(pd.DataFrame(disp), use_container_width=True)
