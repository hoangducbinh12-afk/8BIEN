import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. CONFIG MOBILE & CSS ÉP BẢNG 8 CỘT ---
st.set_page_config(page_title="8-BIT MASTER V1.8", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.75rem !important; }
    .dan-box { 
        background-color: #ffffff; border: 1px solid #fbbf24; border-radius: 8px; 
        padding: 5px; margin-bottom: 5px; font-family: monospace; 
        font-weight: bold; color: #1e293b; text-align: center; font-size: 0.8rem;
    }
    /* Ép bảng nhỏ lại để vừa 8 cột trên mobile */
    .stTable td, .stTable th { 
        padding: 1px 2px !important; 
        font-size: 0.65rem !important; 
        text-align: center !important;
        min-width: 25px !important;
    }
    .stButton button { width: 100%; border-radius: 8px; height: 32px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]

def encode_8bit(n):
    try:
        n = int(n); d, u = n // 10, n % 10
        return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
                1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
                1 if n in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]
    except: return [0]*8

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

# --- 3. KHỞI TẠO & LƯU TRỮ BỀN VỮNG ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_n' not in st.session_state:
    st.session_state.last_n = -1

# --- 4. GIAO DIỆN ---
st.title("🧬 8-BIT MASTER V1.8")

with st.expander("➕ CẬP NHẬT KỲ MỚI", expanded=True):
    # Tính kỳ tự động
    curr_max_ky = 0
    if st.session_state.history:
        curr_max_ky = max([int(h.get("Kỳ", 0)) for h in st.session_state.history])
    
    c1, c2, c3 = st.columns([1.5, 1, 1.2])
    with c1: gdb_in = st.text_input("Số cuối:", key="num_in")
    with c2: ky_in = st.number_input("Kỳ:", value=curr_max_ky + 1, step=1)
    with c3: day_in = st.text_input("Ngày:", datetime.now().strftime("%d/%m"))
    
    if st.button("🚀 LƯU NHẬT KÝ", type="primary"):
        if len(gdb_in) >= 2:
            num = int(gdb_in[-2:])
            rank_val = get_rank(num, st.session_state.last_n)
            
            # Lưu vào bộ nhớ Session
            new_item = {
                "Ngày": str(day_in), 
                "Kỳ": int(ky_in), 
                "Số": f"{num:02d}", 
                "Rank": int(rank_val)
            }
            st.session_state.history.append(new_item)
            st.session_state.last_n = num
            
            # Sắp xếp ngay lập tức
            st.session_state.history = sorted(st.session_state.history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
            st.rerun()

st.divider()

if st.session_state.last_n != -1 or st.session_state.history:
    # Đồng bộ mốc tính sau khi load file
    if st.session_state.last_n == -1 and st.session_state.history:
        st.session_state.last_n = int(st.session_state.history[0]["Số"])

    t1, t2 = st.tabs(["🎯 LẤY DÀN", "📊 NHẬT KÝ 8 CỘT"])
    
    with t1:
        st.write(f"🔢 Nhịp từ: **{st.session_state.last_n:02d}**")
        
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

        ca, cb = st.columns(2)
        with ca:
            n1 = st.number_input("Dàn A:", 1, 100, 50, key="n1")
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n1, st.session_state.last_n))}</div>", unsafe_allow_html=True)
        with cb:
            n2 = st.number_input("Dàn B:", 1, 100, 36, key="n2")
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n2, st.session_state.last_n))}</div>", unsafe_allow_html=True)

    with t2:
        if st.session_state.history:
            disp = []
            for h in st.session_state.history[:30]:
                b = encode_8bit(h["Số"])
                disp.append({
                    "Kỳ": int(h.get("Kỳ", 0)),
                    "Số": h["Số"],
                    "R": int(h.get("Rank", 0)),
                    "ĐL": "L" if b[0] else "C",
                    "ĐuL": "L" if b[1] else "C",
                    "TL": "L" if b[2] else "C",
                    "ĐT": "T" if b[3] else "B",
                    "UT": "T" if b[4] else "B",
                    "TT": "T" if b[5] else "B",
                    "Hệ": "Th" if b[6] else "Kp",
                    "HiT": "T" if b[7] else "B"
                })
            # Hiển thị bảng nguyên bản 8 cột
            st.table(pd.DataFrame(disp))

with st.sidebar:
    st.header("⚙️ DỮ LIỆU")
    if st.button("🔴 XOÁ HẾT"):
        st.session_state.history = []
        st.session_state.last_n = -1
        st.rerun()
    up = st.file_uploader("Nạp file JSON:", type="json")
    if up:
        data = json.load(up)
        # Ép nạp vào Session State
        st.session_state.history = data.get("history", [])
        st.session_state.last_n = data.get("last_n", -1)
        st.rerun()
    st.download_button("💾 Backup", json.dumps({"history": st.session_state.history, "last_n": st.session_state.last_n}), "8bit_v1.8.json")
