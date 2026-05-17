import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. CONFIG MOBILE & FONT SIÊU NHỎ ---
st.set_page_config(page_title="8-BIT MASTER V1.7", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.75rem !important; }
    .dan-box { 
        background-color: #ffffff; border: 1px solid #fbbf24; border-radius: 8px; 
        padding: 5px; margin-bottom: 5px; font-family: monospace; 
        font-weight: bold; color: #1e293b; text-align: center; font-size: 0.8rem;
    }
    .stTable td { padding: 1px !important; font-size: 0.65rem !important; font-weight: bold !important; text-align: center !important;}
    .stButton button { width: 100%; border-radius: 8px; height: 32px; font-weight: bold; }
    .bit-string { font-family: monospace; color: #0369a1; font-weight: bold; font-size: 0.7rem; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC 8 BIẾN ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]

def encode_8bit(n):
    try:
        n = int(n); d, u = n // 10, n % 10
        bits = [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
                1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
                1 if n in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]
        return bits
    except: return [0]*8

def get_bit_string(b):
    # Tạo chuỗi hiển thị nhanh: L/C, T/B, Th/Kp
    labels = ["L","L","L","T","T","T","Th","T"]
    anti_labels = ["C","C","C","B","B","B","Kp","B"]
    res = ""
    for i in range(8):
        res += labels[i] if b[i] else anti_labels[i]
    return res

def calculate_hamming(bits1, bits2):
    return sum(b1 != b2 for b1, b2 in zip(bits1, bits2))

def get_rank(target, last):
    if last == -1: return 0
    last_b = encode_8bit(last)
    scores = []
    for i in range(100):
        d = calculate_hamming(last_b, encode_8bit(i))
        w = abs(d - 4)
        if d == 0 and i != int(last): w += 10
        if d in [7, 8]: w += 20
        scores.append({"S": f"{i:02d}", "W": w})
    df = pd.DataFrame(scores).sort_values(["W", "S"])
    df['R'] = range(1, 101)
    res = df[df['S'] == f"{int(target):02d}"]['R'].values
    return int(res[0]) if len(res) > 0 else 100

# --- 3. QUẢN LÝ DỮ LIỆU (BỀN VỮNG) ---
if 'db' not in st.session_state:
    st.session_state.db = {"history": [], "last_n": -1}

# Rút trích db ra để dùng cho gọn
history = st.session_state.db["history"]

# Tính kỳ tiếp theo
next_ky_val = 1
if history:
    next_ky_val = max([int(h.get("Kỳ", 0)) for h in history]) + 1

# --- 4. GIAO DIỆN ---
st.title("🧬 8-BIT MASTER V1.7")

with st.expander("➕ CẬP NHẬT KỲ MỚI", expanded=True):
    c1, c2, c3 = st.columns([1.5, 1, 1.2])
    with c1: gdb_in = st.text_input("Số cuối:", key="input_num")
    with c2: ky_in = st.number_input("Kỳ:", value=next_ky_val, step=1)
    with c3: day_in = st.text_input("Ngày:", datetime.now().strftime("%d/%m"))
    
    if st.button("🚀 LƯU NHẬT KÝ", type="primary"):
        if len(gdb_in) >= 2:
            num = int(gdb_in[-2:])
            rank_val = get_rank(num, st.session_state.db["last_n"])
            
            # Thêm mới và sắp xếp ngay
            new_item = {"Ngày": str(day_in), "Kỳ": int(ky_in), "Số": f"{num:02d}", "Rank": int(rank_val)}
            st.session_state.db["history"].append(new_item)
            st.session_state.db["last_n"] = num
            st.session_state.db["history"] = sorted(st.session_state.db["history"], key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
            st.rerun()

st.divider()

if st.session_state.db["last_n"] != -1 or history:
    if st.session_state.db["last_n"] == -1 and history:
        st.session_state.db["last_n"] = int(history[0]["Số"])

    t1, t2 = st.tabs(["🎯 LẤY DÀN", "📊 NHẬT KÝ"])
    
    with t1:
        st.write(f"🔢 Nhịp từ: **{st.session_state.db['last_n']:02d}**")
        
        def generate_dan(n_size, last_n):
            last_b = encode_8bit(last_n)
            res = []
            for i in range(100):
                d = calculate_hamming(last_b, encode_8bit(i))
                w = abs(d - 4)
                if d == 0 and i != last_n: w += 10
                if d in [7, 8]: w += 20
                res.append({"S": f"{i:02d}", "W": w})
            df = pd.DataFrame(res).sort_values(["W", "S"])
            return df.head(n_size)["S"].tolist()

        c_a, c_b = st.columns(2)
        with c_a:
            n1 = st.number_input("Dàn A:", 1, 100, 50, key="n1")
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n1, st.session_state.db['last_n']))}</div>", unsafe_allow_html=True)
        with c_b:
            n2 = st.number_input("Dàn B:", 1, 100, 36, key="n2")
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n2, st.session_state.db['last_n']))}</div>", unsafe_allow_html=True)

    with t2:
        if history:
            disp = []
            for h in history[:30]:
                bits = encode_8bit(h["Số"])
                bit_str = get_bit_string(bits)
                disp.append({
                    "Kỳ": int(h.get("Kỳ", 0)),
                    "Số": h["Số"],
                    "Rank": int(h.get("Rank", 0)),
                    "8 Biến (Nhịp)": bit_str
                })
            st.table(pd.DataFrame(disp))

with st.sidebar:
    st.header("⚙️ DATA")
    if st.button("🔴 RESET"):
        st.session_state.db = {"history": [], "last_n": -1}
        st.rerun()
    up = st.file_uploader("Nạp file:", type="json")
    if up:
        st.session_state.db = json.load(up)
        st.rerun()
    st.download_button("💾 Backup", json.dumps(st.session_state.db), "data_rhythm.json")
