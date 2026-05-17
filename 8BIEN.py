import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. CONFIG GIAO DIỆN ---
st.set_page_config(page_title="50/50 RHYTHM MASTER", layout="centered")

st.markdown("""
    <style>
    .bit-box { 
        background-color: #1e293b; color: #38bdf8; border-radius: 5px; padding: 5px; 
        font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; text-align: center;
    }
    .dan-box { 
        background-color: #f8fafc; border-radius: 10px; padding: 15px; 
        border: 2px solid #3b82f6; margin-bottom: 10px; 
        font-family: 'JetBrains Mono', monospace; font-weight: 700; 
        color: #1e293b; font-size: 1rem; text-align: center; 
    }
    .stTable td { font-size: 0.75rem !important; text-align: center !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]

def encode_8bit(n):
    n = int(n)
    d, u = n // 10, n % 10
    return [
        1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
        1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
        1 if n in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0
    ]

def calculate_hamming(bits1, bits2):
    return sum(b1 != b2 for b1, b2 in zip(bits1, bits2))

# --- 3. DỰ BÁO NHỊP ---
def predict_rhythm(history):
    if len(history) < 2: return [4]
    diffs = []
    for i in range(len(history)-1):
        b_curr = encode_8bit(history[i]["Số"])
        b_prev = encode_8bit(history[i+1]["Số"])
        diffs.append(calculate_hamming(b_curr, b_prev))
    if not diffs: return [4]
    counts = np.bincount(diffs, minlength=9)
    return np.argsort(-counts)[:2].tolist()

# --- 4. GIAO DIỆN & XỬ LÝ ---
if 'db_5050' not in st.session_state:
    st.session_state.db_5050 = {"history": [], "last_n": -1}

db = st.session_state.db_5050

st.title("🧬 50/50 RHYTHM MASTER")

c1, c2 = st.columns([3, 1])
with c1: gdb_input = st.text_input("GĐB vừa ra:", placeholder="Ví dụ: 76669")
with c2: ky_input = st.number_input("Kỳ:", step=1, value=1)

if st.button("🚀 GIẢI MÃ NHỊ PHÂN", type="primary", use_container_width=True):
    if len(gdb_input) >= 2:
        num = int(gdb_input[-2:])
        db["history"].insert(0, {"Kỳ": ky_input, "Số": f"{num:02d}"})
        db["last_n"] = num
        st.rerun()

st.divider()

if db["last_n"] != -1 or (len(db["history"]) > 0):
    # Nếu nạp file mà last_n chưa có, lấy con số mới nhất trong history
    if db["last_n"] == -1 and len(db["history"]) > 0:
        db["last_n"] = int(db["history"][0]["Số"])

    tab1, tab2 = st.tabs(["🎯 DÀN NHỊP ĐIỆU", "📊 LỊCH SỬ BIT"])
    last_bits = encode_8bit(db["last_n"])
    
    with tab1:
        st.write(f"🔢 Số kỳ trước: **{db['last_n']:02d}**")
        recommended_diffs = predict_rhythm(db["history"])
        st.info(f"💡 AI gợi ý đánh theo nhịp lệch: **{', '.join(map(str, recommended_diffs))} bit**")
        
        dan_tinh_anh = []
        for i in range(100):
            curr_bits = encode_8bit(i)
            diff = calculate_hamming(last_bits, curr_bits)
            # Bộ lọc xét yếu
            if diff == 0 and i != db["last_n"]: continue
            if diff in [7, 8]: continue
            if diff in recommended_diffs:
                dan_tinh_anh.append(f"{i:02d}")
        
        st.markdown(f"### 💎 Dàn Tinh Anh (Nhịp {recommended_diffs} bit)")
        st.markdown(f"<div class='dan-box'>{' '.join(dan_tinh_anh)}</div>", unsafe_allow_html=True)
        st.caption(f"Tổng cộng: {len(dan_tinh_anh)} số")

    with tab2:
        if db["history"]:
            hist_display = []
            for h in db["history"][:20]:
                # FIX LỖI TẠI ĐÂY: Tự encode nếu thiếu trường Bits
                b = h.get("Bits") if h.get("Bits") else encode_8bit(h["Số"])
                hist_display.append({
                    "Kỳ": h["Kỳ"], "Số": h["Số"],
                    "Đầu": "Lẻ" if b[0] else "Chẵn", "Đuôi": "Lẻ" if b[1] else "Chẵn",
                    "Tổng": "Lẻ" if b[2] else "Chẵn", "Đ_TB": "To" if b[3] else "Bé",
                    "U_TB": "To" if b[4] else "Bé", "T_TB": "To" if b[5] else "Bé",
                    "Hệ": "Thường" if b[6] else "Kép", "H_TB": "To" if b[7] else "Bé"
                })
            st.table(pd.DataFrame(hist_display))

st.sidebar.header("⚖️ DATA CENTER")
if st.sidebar.button("🔴 RESET ALL"):
    st.session_state.db_5050 = {"history": [], "last_n": -1}
    st.rerun()

st.sidebar.download_button("💾 Backup", json.dumps(db), "rhythm_data.json")
up = st.sidebar.file_uploader("Nạp file dữ liệu (Restore):", type="json")
if up:
    st.session_state.db_5050 = json.load(up)
    st.rerun()
