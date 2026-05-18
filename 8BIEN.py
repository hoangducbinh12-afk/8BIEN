import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. THIẾT LẬP GIAO DIỆN (NỀN TRẮNG - NÚT XANH CHỮ TRẮNG) ---
st.set_page_config(page_title="8-BIT MASTER V5.0", layout="wide")
st.markdown("""
    <style>
    /* Tổng thể nền trắng chữ đen */
    html, body, [class*="st-"] { 
        font-size: 0.8rem !important; 
        color: #000000 !important; 
        background-color: #ffffff !important; 
    }
    /* Nút bấm: Nền xanh đậm - Chữ trắng */
    .stButton button { 
        width: 100%; 
        border-radius: 8px; 
        height: 45px; 
        font-weight: 700; 
        background-color: #0047AB !important; 
        color: #ffffff !important;
        border: none !important;
    }
    .stButton button:hover { background-color: #0056D2 !important; }
    /* Ô hiển thị dàn số */
    .dan-box { 
        background-color: #f8f9fa; 
        border: 2px solid #0047AB; 
        border-radius: 10px; 
        padding: 15px; 
        font-family: 'Courier New', monospace; 
        font-weight: 700; 
        color: #0047AB; 
        text-align: center; 
        font-size: 1.1rem;
        margin-bottom: 10px;
    }
    /* Định dạng bảng */
    .stDataFrame { border: 1px solid #dee2e6; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]
BIT_LABELS = ["Đ.CL", "Đu.CL", "T.CL", "Đ.TB", "Đu.TB", "T.TB", "Hệ", "Hi.TB"]

def get_8bit(n):
    try:
        val = int(n); d, u = val // 10, val % 10
        return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
                1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
                1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]
    except: return [0]*8

def quantum_analyze(history_list, last_n):
    if len(history_list) < 2: return [0.5]*8
    bits_data = np.array([get_8bit(h["Số"]) for h in history_list])
    current_bits = np.array(get_8bit(last_n))
    final_probs = np.zeros(8)
    
    # 1-Bit (10k)
    seg10 = bits_data[-11:]
    for i in range(8):
        matches = [seg10[k+1] for k in range(len(seg10)-1) if seg10[k][i] == current_bits[i]]
        if matches: final_probs += np.mean(matches, axis=0) * 0.4
        else: final_probs += 0.5 * 0.4

    # 2-Bit (22k)
    seg22 = bits_data[-23:]
    if len(seg22) > 1:
        p_scores = np.zeros(8); hits = 0
        for i in range(8):
            for j in range(i+1, 8):
                matches = [seg22[k+1] for k in range(len(seg22)-1) if seg22[k][i] == current_bits[i] and seg22[k][j] == current_bits[j]]
                if matches: p_scores += np.mean(matches, axis=0); hits += 1
        if hits > 0: final_probs += (p_scores / hits) * 0.6
        else: final_probs += 0.5 * 0.6
    return np.clip(final_probs, 0.05, 0.95).tolist()

# --- 3. SESSION STATE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

# --- 4. GIAO DIỆN ---
st.title("🚀 8-BIT QUANTUM MASTER V5.0")

with st.sidebar:
    st.header("📂 QUẢN LÝ FILE")
    up = st.file_uploader("Nạp file Master (.json):", type="json")
    if up:
        try:
            data = json.load(up)
            raw = data.get("history", []) if isinstance(data, dict) else data
            st.session_state.history = sorted([
                {"Ngày": h.get("Ngày", "00/00"), "Kỳ": int(h.get("Kỳ", 0)), 
                 "Số": f"{int(h.get('Số', 0)):02d}", "Rank": int(h.get("Rank", 0))} 
                for h in raw
            ], key=lambda x: x["Kỳ"])
            if st.session_state.history:
                st.session_state.last_n = int(st.session_state.history[-1]["Số"])
            st.success(f"Đã nạp {len(st.session_state.history)} kỳ!")
        except: st.error("File lỗi định dạng!")
    
    st.divider()
    if st.button("🔴 RESET DỮ LIỆU"):
        st.session_state.history = []; st.session_state.last_n = -1; st.rerun()

# NHẬP LIỆU
with st.container():
    c1, c2, c3 = st.columns(3)
    n_in = c1.text_input("Số vừa về (2 số):")
    next_ky = st.session_state.history[-1]["Kỳ"] + 1 if st.session_state.history else 1
    k_in = c2.number_input("Kỳ vừa về:", value=next_ky)
    
    if st.button("🔥 PHÂN TÍCH & LƯU"):
        if n_in:
            val = int(n_in[-2:])
            if st.session_state.history:
                probs = quantum_analyze(st.session_state.history, st.session_state.last_n)
                scores = []
                for i in range(100):
                    b = get_8bit(i)
                    m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
                    scores.append({"S": f"{i:02d}", "M": m})
                df_tmp = pd.DataFrame(scores).sort_values("M", ascending=False)
                df_tmp['R'] = range(1, 101)
                r_val = df_tmp[df_tmp['S'] == f"{val:02d}"]['R'].values[0]
            else: r_val = 0
            
            st.session_state.history.append({
                "Ngày": datetime.now().strftime("%d/%m"), "Kỳ": int(k_in), 
                "Số": f"{val:02d}", "Rank": int(r_val)
            })
            st.session_state.last_n = val
            st.rerun()

if st.session_state.history:
    probs = quantum_analyze(st.session_state.history, st.session_state.last_n)
    res_list = []
    for i in range(100):
        b = get_8bit(i)
        m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        res_list.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(res_list).sort_values("M", ascending=False)

    tab1, tab2 = st.tabs(["🎯 DÀN TINH ANH", "📊 NHẬT KÝ 11 CỘT"])
    
    with tab1:
        st.subheader(f"🔢 Nhịp gốc từ số: {st.session_state.last_n:02d}")
        cols = st.columns(8)
        for i, (label, p) in enumerate(zip(BIT_LABELS, probs)):
            cols[i].metric(label, f"{int(p*100)}%")
        
        st.divider()
        da, db = st.columns(2)
        da.markdown("**🔥 DÀN A (50 SỐ)**")
        da.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(50)['S'].tolist())}</div>", unsafe_allow_html=True)
        db.markdown("**💎 DÀN B (36 SỐ)**")
        db.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(36)['S'].tolist())}</div>", unsafe_allow_html=True)

    with tab2:
        display_data = []
        for h in reversed(st.session_state.history):
            b = get_8bit(h["Số"])
            display_data.append({
                "Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"],
                "Đ.CL": "L" if b[0] else "C", "Đu.CL": "L" if b[1] else "C", "T.CL": "L" if b[2] else "C",
                "Đ.TB": "T" if b[3] else "B", "Đu.TB": "T" if b[4] else "B", "T.TB": "T" if b[5] else "B",
                "Hệ": "Th" if b[6] else "Kp", "Hi.TB": "T" if b[7] else "B"
            })
        st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)

    st.divider()
    st.download_button("💾 TẢI FILE MASTER JSON", json.dumps({"history": st.session_state.history}), f"8bit_master.json")
