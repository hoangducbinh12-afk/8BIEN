import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. CONFIG GIAO DIỆN ---
st.set_page_config(page_title="50/50 RHYTHM PRO V1.3", layout="centered")

st.markdown("""
    <style>
    .dan-box { 
        background-color: #ffffff; border-radius: 10px; padding: 15px; 
        border: 2px solid #fbbf24; margin-bottom: 10px; 
        font-family: 'JetBrains Mono', monospace; font-weight: 700; 
        color: #1e293b; font-size: 1rem; text-align: center; 
    }
    .stTable td { font-size: 0.75rem !important; text-align: center !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]

def encode_8bit(n):
    try:
        n = int(n)
        d, u = n // 10, n % 10
        return [
            1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
            1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
            1 if n in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0
        ]
    except: return [0]*8

def calculate_hamming(bits1, bits2):
    return sum(b1 != b2 for b1, b2 in zip(bits1, bits2))

def get_rank_for_number(target_num, last_num):
    last_bits = encode_8bit(last_num)
    all_scores = []
    for i in range(100):
        c_bits = encode_8bit(i)
        d = calculate_hamming(last_bits, c_bits)
        score = abs(d - 4) 
        if d == 0 and i != int(last_num): score += 10
        if d in [7, 8]: score += 20
        all_scores.append((f"{i:02d}", score))
    df_rank = pd.DataFrame(all_scores, columns=['SO', 'SCORE']).sort_values(['SCORE', 'SO'])
    df_rank['RANK'] = range(1, 101)
    match = df_rank[df_rank['SO'] == f"{int(target_num):02d}"]['RANK'].values
    return int(match[0]) if len(match) > 0 else 100

# --- 3. GIAO DIỆN ---
if 'db_5050' not in st.session_state:
    st.session_state.db_5050 = {"history": [], "last_n": -1}

db = st.session_state.db_5050
st.title("🧬 50/50 RHYTHM PRO V1.3")

c1, c2, c3 = st.columns([2, 1, 1])
with c1: gdb_in = st.text_input("GĐB mới nhất:", placeholder="Ví dụ: 76669")
with c2: day_in = st.text_input("Ngày:", datetime.now().strftime("%d/%m"))
with c3: ky_in = st.number_input("Kỳ:", step=1, value=len(db["history"])+1)

if st.button("🚀 CẬP NHẬT NHỊP ĐIỆU", type="primary", use_container_width=True):
    if len(gdb_in) >= 2:
        num = int(gdb_in[-2:])
        rank_val = get_rank_for_number(num, db["last_n"]) if db["last_n"] != -1 else 0
        db["history"].insert(0, {"Ngày": day_in, "Kỳ": ky_in, "Số": f"{num:02d}", "Rank": rank_val})
        db["last_n"] = num
        st.rerun()

st.divider()

if db["last_n"] != -1 or len(db["history"]) > 0:
    if db["last_n"] == -1: db["last_n"] = int(db["history"][0]["Số"])
    t1, t2 = st.tabs(["🎯 LẤY DÀN", "📊 NHẬT KÝ"])
    
    with t1:
        col_a, col_b = st.columns([2, 1])
        with col_a: st.write(f"🔢 Nhịp từ số: **{db['last_n']:02d}**")
        with col_b: n_quân = st.number_input("Số lượng quân:", 1, 100, 50)
        
        last_bits = encode_8bit(db["last_n"])
        results = []
        for i in range(100):
            d = calculate_hamming(last_bits, encode_8bit(i))
            w = abs(d - 4)
            if d == 0 and i != db["last_n"]: w += 10
            if d in [7, 8]: w += 20
            results.append({"SO": f"{i:02d}", "W": w})
        
        df_final = pd.DataFrame(results).sort_values(["W", "SO"])
        st.markdown(f"<div class='dan-box'>{' '.join(df_final.head(n_quân)['SO'].tolist())}</div>", unsafe_allow_html=True)

    with t2:
        if db["history"]:
            hist_df = []
            for h in db["history"][:30]:
                b = encode_8bit(h["Số"])
                # FIX LỖI KEYERROR TẠI ĐÂY: Dùng h.get() để tránh sập app
                hist_df.append({
                    "Ngày": h.get("Ngày", "HT"), 
                    "Kỳ": h.get("Kỳ", 0), 
                    "Số": h["Số"],
                    "Rank": h.get("Rank", "-"),
                    "Đầu": "Lẻ" if b[0] else "Chẵn", "Đuôi": "Lẻ" if b[1] else "Chẵn",
                    "Tổng": "Lẻ" if b[2] else "Chẵn", "Đ_TB": "To" if b[3] else "Bé",
                    "U_TB": "To" if b[4] else "Bé", "T_TB": "To" if b[5] else "Bé"
                })
            st.table(pd.DataFrame(hist_df))

with st.sidebar:
    st.header("⚙️ DATA")
    if st.button("🔴 RESET"):
        st.session_state.db_5050 = {"history": [], "last_n": -1}
        st.rerun()
    st.download_button("💾 BACKUP", json.dumps(db), "rhythm_v1.3.json")
    up = st.file_uploader("NẠP FILE:", type="json")
    if up:
        st.session_state.db_5050 = json.load(up)
        st.rerun()
