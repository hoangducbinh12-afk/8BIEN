import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. CONFIG MOBILE & FONT ---
st.set_page_config(page_title="8-BIT RHYTHM V1.5", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.8rem !important; }
    .dan-box { 
        background-color: #ffffff; border: 1px solid #fbbf24; border-radius: 8px; 
        padding: 8px; margin-bottom: 5px; font-family: monospace; 
        font-weight: bold; color: #1e293b; text-align: center; font-size: 0.85rem;
    }
    .stTable td { padding: 1px !important; font-size: 0.7rem !important; font-weight: bold !important; }
    .stButton button { width: 100%; border-radius: 10px; height: 35px; }
    input { font-size: 0.9rem !important; }
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

# --- 3. KHỞI TẠO BIẾN HỆ THỐNG ---
if 'db' not in st.session_state:
    st.session_state.db = {"history": [], "last_n": -1}

# Dùng để tự nhảy số kỳ
if 'next_ky' not in st.session_state:
    st.session_state.next_ky = 1

db = st.session_state.db

# Cập nhật số kỳ dựa trên lịch sử hiện tại
if db["history"]:
    st.session_state.next_ky = max([int(h.get("Kỳ", 0)) for h in db["history"]]) + 1

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🧬 RHYTHM ULTIMATE V1.5")

with st.expander("➕ NHẬP KẾT QUẢ", expanded=True):
    c1, c2, c3 = st.columns([2, 1, 1.2])
    with c1: gdb_in = st.text_input("GĐB:", placeholder="Số đuôi...")
    with c2: ky_in = st.number_input("Kỳ:", value=st.session_state.next_ky, step=1)
    with c3: day_in = st.text_input("Ngày:", datetime.now().strftime("%d/%m"))
    
    if st.button("🚀 CẬP NHẬT NGAY", type="primary"):
        if len(gdb_in) >= 2:
            num = int(gdb_in[-2:])
            rank_val = get_rank(num, db["last_n"])
            
            # Thêm dữ liệu mới
            new_entry = {"Ngày": day_in, "Kỳ": ky_in, "Số": f"{num:02d}", "Rank": rank_val}
            db["history"].append(new_entry) # Dùng append để lưu vĩnh viễn
            db["last_n"] = num
            
            # Sắp xếp lại kỳ mới nhất lên đầu
            db["history"] = sorted(db["history"], key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
            
            # Tự động tăng kỳ cho lần sau
            st.session_state.next_ky = int(ky_in) + 1
            st.rerun()

st.divider()

if db["last_n"] != -1 or db["history"]:
    if db["last_n"] == -1 and db["history"]: 
        db["last_n"] = int(db["history"][0]["Số"])
    
    t1, t2 = st.tabs(["🎯 LẤY DÀN", "📊 NHẬT KÝ"])
    
    with t1:
        st.write(f"🔢 Gốc: **{db['last_n']:02d}** (Kỳ {st.session_state.next_ky - 1})")
        
        def generate_dan(n_size, last_n):
            last_b = encode_8bit(last_n)
            res = []
            for i in range(100):
                d = calculate_hamming(last_b, encode_8bit(i))
                w = abs(d - 4); 
                if d == 0 and i != last_n: w += 10
                if d in [7, 8]: w += 20
                res.append({"S": f"{i:02d}", "W": w})
            df = pd.DataFrame(res).sort_values(["W", "S"])
            return df.head(n_size)["S"].tolist()

        c_a, c_b = st.columns(2)
        with c_a: 
            n1 = st.number_input("Số lượng A:", 1, 100, 50)
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n1, db['last_n']))}</div>", unsafe_allow_html=True)
        with c_b: 
            n2 = st.number_input("Số lượng B:", 1, 100, 36)
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n2, db['last_n']))}</div>", unsafe_allow_html=True)

    with t2:
        if db["history"]:
            disp = []
            for h in db["history"][:25]:
                b = encode_8bit(h["Số"])
                disp.append({
                    "Kỳ": h.get("Kỳ"), "Số": h["Số"], "Rank": h.get("Rank"),
                    "Đầu": "L" if b[0] else "C", "Đuôi": "L" if b[1] else "C",
                    "Tổng": "L" if b[2] else "C", "T/B": "T" if b[5] else "B",
                    "Hệ": "Th" if b[6] else "Kp"
                })
            st.table(pd.DataFrame(disp))

# Sidebar 
with st.sidebar:
    st.header("⚙️ QUẢN LÝ")
    if st.button("🔴 XOÁ SẠCH"):
        st.session_state.db = {"history": [], "last_n": -1}
        st.session_state.next_ky = 1
        st.rerun()
    up = st.file_uploader("Nạp file dữ liệu:", type="json")
    if up:
        st.session_state.db = json.load(up)
        st.rerun()
    st.download_button("💾 Xuất Backup", json.dumps(db), "data_rhythm.json")
