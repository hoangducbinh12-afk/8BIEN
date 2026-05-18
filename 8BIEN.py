import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. THIẾT LẬP GIAO DIỆN ---
st.set_page_config(page_title="8-BIT QUANTUM V4.7", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.75rem !important; }
    .dan-box { background-color: #ffffff; border: 2px solid #1e3a8a; border-radius: 8px; padding: 10px; font-family: monospace; font-weight: 700; color: #1e3a8a; text-align: center; font-size: 1rem; }
    .stButton button { width: 100%; border-radius: 5px; height: 45px; font-weight: 700; background-color: #1e3a8a !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIC 8-BIT DNA ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]
BIT_LABELS = ["Đ.CL", "Đu.CL", "T.CL", "Đ.TB", "Đu.TB", "T.TB", "Hệ", "Hi.TB"]

@st.cache_data
def get_8bit(n):
    try:
        val = int(n); d, u = val // 10, val % 10
        return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
                1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
                1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]
    except: return [0]*8

# --- 3. LÕI PHÂN TÍCH SIÊU TỐC (OPTIMIZED ENGINE) ---
def fast_quantum_engine(history, last_n):
    if not history or last_n == -1: return [0.5]*8
    
    # Chuyển lịch sử thành mảng Numpy để tính cho nhanh
    all_bits = np.array([get_8bit(h["Số"]) for h in history])
    current_bits = np.array(get_8bit(last_n))
    
    # Đảo ngược để index 0 là cũ nhất, -1 là mới nhất (số vừa nổ)
    all_bits = all_bits[::-1] 
    
    final_probs = np.zeros(8)
    
    # TẦNG 1: 1-BIT (10 KỲ)
    seg10 = all_bits[-11:] # Lấy 11 để có 10 cặp
    if len(seg10) > 1:
        for i in range(8):
            matches = [seg10[k+1] for k in range(len(seg10)-1) if seg10[k][i] == current_bits[i]]
            if matches: final_probs += np.mean(matches, axis=0) * 0.4
    
    # TẦNG 2: 2-BIT (22 KỲ)
    seg22 = all_bits[-23:]
    if len(seg22) > 1:
        match_count = 0
        for i in range(8):
            for j in range(i+1, 8):
                matches = [seg22[k+1] for k in range(len(seg22)-1) if seg22[k][i] == current_bits[i] and seg22[k][j] == current_bits[j]]
                if matches:
                    final_probs += np.mean(matches, axis=0) * 0.6
                    match_count += 1
        if match_count > 0: final_probs /= (match_count + 1)
    
    return np.clip(final_probs, 0.1, 0.9).tolist()

# --- 4. GIAO DIỆN VÀ ĐIỀU KHIỂN ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

st.title("🧬 8-BIT QUANTUM V4.7 (HIGH SPEED)")

# Sidebar
with st.sidebar:
    st.header("📁 QUẢN LÝ DỮ LIỆU")
    up_file = st.file_uploader("Nạp file Master .json", type="json")
    if up_file:
        data = json.load(up_file)
        hist = data.get("history", [])
        st.session_state.history = sorted(hist, key=lambda x: int(x["Kỳ"]), reverse=True)
        st.session_state.last_n = int(st.session_state.history[0]["Số"])
        st.success(f"Nạp thành công {len(st.session_state.history)} kỳ")
    if st.button("🔴 RESET"): 
        st.session_state.history = []; st.session_state.last_n = -1; st.rerun()

# Form nhập liệu
with st.container():
    c1, c2, c3 = st.columns(3)
    num_val = c1.text_input("Số vừa nổ (2 số cuối):")
    ky_val = c2.number_input("Kỳ tiếp theo:", value=len(st.session_state.history)+1)
    
    if st.button("🚀 PHÂN TÍCH NGAY"):
        if num_val:
            val = int(num_val[-2:])
            # Thêm vào đầu danh sách
            st.session_state.history.insert(0, {"Ngày": datetime.now().strftime("%d/%m"), "Kỳ": int(ky_val)-1, "Số": f"{val:02d}"})
            st.session_state.last_n = val
            st.success("Đã cập nhật số mới!")
            st.rerun()

# Hiển thị kết quả
if st.session_state.history:
    probs = fast_quantum_engine(st.session_state.history, st.session_state.last_n)
    
    # Tính Rank
    scores = []
    for i in range(100):
        b = get_8bit(i)
        m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        scores.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(scores).sort_values("M", ascending=False)

    t1, t2 = st.tabs(["🎯 DÀN TINH ANH", "📊 NHẬT KÝ"])
    
    with t1:
        st.write(f"🔢 Nhịp từ số: **{st.session_state.last_n:02d}**")
        ms = st.columns(8)
        for i, (label, p) in enumerate(zip(BIT_LABELS, probs)):
            ms[i].metric(label, f"{int(p*100)}%")
        
        st.divider()
        da, db = st.columns(2)
        da.subheader("🔥 Dàn A (50 số)")
        da.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(50)['S'].tolist())}</div>", unsafe_allow_html=True)
        db.subheader("💎 Dàn B (36 số)")
        db.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(36)['S'].tolist())}</div>", unsafe_allow_html=True)

    with t2:
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
