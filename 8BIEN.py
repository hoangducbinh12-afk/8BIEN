import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. CONFIG GIAO DIỆN MOBILE & FONT NHỎ ---
st.set_page_config(page_title="8-BIT RHYTHM V1.4", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.85rem !important; }
    .dan-box { 
        background-color: #f8fafc; border: 1px solid #3b82f6; border-radius: 8px; 
        padding: 10px; margin-bottom: 10px; font-family: monospace; 
        font-weight: bold; color: #1e293b; text-align: center; font-size: 0.9rem;
    }
    .stTable td { padding: 2px !important; font-size: 0.75rem !important; }
    .stButton button { width: 100%; border-radius: 20px; }
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

# --- 3. XỬ LÝ DỮ LIỆU ---
if 'db' not in st.session_state:
    st.session_state.db = {"history": [], "last_n": -1}

db = st.session_state.db

# --- 4. GIAO DIỆN NHẬP LIỆU ---
st.title("🧬 8-BIT RHYTHM V1.4")

with st.expander("➕ NHẬP KẾT QUẢ MỚI", expanded=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: gdb_in = st.text_input("GĐB:", placeholder="76669")
    with c2: day_in = st.text_input("Ngày:", datetime.now().strftime("%d/%m"), label_visibility="collapsed")
    with c3: ky_in = st.number_input("Kỳ:", value=len(db["history"])+1, label_visibility="collapsed")
    
    if st.button("🚀 CẬP NHẬT NHẬT KÝ"):
        if len(gdb_in) >= 2:
            num = int(gdb_in[-2:])
            rank_val = get_rank(num, db["last_n"]) if db["last_n"] != -1 else 0
            # Thêm vào đầu và lọc trùng Kỳ
            new_entry = {"Ngày": day_in, "Kỳ": ky_in, "Số": f"{num:02d}", "Rank": rank_val}
            db["history"].insert(0, new_entry)
            db["last_n"] = num
            # Sắp xếp lại nhật ký theo Kỳ giảm dần
            db["history"] = sorted(db["history"], key=lambda x: x.get("Kỳ", 0), reverse=True)
            st.rerun()

st.divider()

if db["last_n"] != -1 or len(db["history"]) > 0:
    if db["last_n"] == -1: db["last_n"] = int(db["history"][0]["Số"])
    
    tab1, tab2 = st.tabs(["🎯 LẤY DÀN", "📊 NHẬT KÝ"])
    
    with tab1:
        st.caption(f"Đang xét nhịp từ số: {db['last_n']:02d}")
        
        # Hàm lấy dàn dùng chung
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

        # Ô DÀN 1
        st.markdown("---")
        c1, c2 = st.columns([1, 2])
        with c1: n1 = st.number_input("Số lượng 1:", 1, 100, 50, key="n1")
        with c2: st.markdown(f"**DÀN A ({n1}s)**")
        st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n1, db['last_n']))}</div>", unsafe_allow_html=True)

        # Ô DÀN 2
        st.markdown("---")
        c3, c4 = st.columns([1, 2])
        with c3: n2 = st.number_input("Số lượng 2:", 1, 100, 36, key="n2")
        with c4: st.markdown(f"**DÀN B ({n2}s)**")
        st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n2, db['last_n']))}</div>", unsafe_allow_html=True)

    with tab2:
        if db["history"]:
            disp = []
            for h in db["history"][:25]:
                b = encode_8bit(h["Số"])
                disp.append({
                    "Kỳ": h.get("Kỳ", 0), "Số": h["Số"], "Rank": h.get("Rank", "-"),
                    "Đầu": "L" if b[0] else "C", "Đuôi": "L" if b[1] else "C",
                    "Tổng": "L" if b[2] else "C", "Đ_TB": "T" if b[3] else "B",
                    "U_TB": "T" if b[4] else "B", "Hệ": "Th" if b[6] else "Kp"
                })
            st.table(pd.DataFrame(disp))

# Sidebar tối giản
with st.sidebar:
    st.header("⚙️ CÀI ĐẶT")
    if st.button("🔴 RESET"):
        st.session_state.db = {"history": [], "last_n": -1}
        st.rerun()
    up = st.file_uploader("Nạp file:", type="json")
    if up:
        st.session_state.db = json.load(up)
        st.rerun()
    st.download_button("💾 Backup", json.dumps(db), "data_v1.4.json")
