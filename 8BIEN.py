import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from itertools import combinations

# --- 1. GIAO DIỆN CHUẨN V6.1 (NỀN TRẮNG - NÚT XANH NAVY) ---
st.set_page_config(page_title="8-BIT ULTIMATE V6.1", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { color: #000000 !important; background-color: #ffffff !important; font-size: 0.78rem !important; }
    .stButton button { 
        width: 100%; border-radius: 6px; height: 42px; font-weight: 700; 
        background-color: #000080 !important; color: #ffffff !important;
    }
    .dan-box { 
        background-color: #f1f5f9; border: 2px solid #000080; border-radius: 8px; 
        padding: 10px; font-family: 'Courier New', monospace; font-weight: 700; 
        color: #000080; text-align: center; font-size: 1rem; line-height: 1.6;
    }
    /* Thu nhỏ bảng nhật ký */
    .stDataFrame td, .stDataFrame th { padding: 2px 5px !important; font-size: 0.72rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC (DNA & BITS) ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]
BIT_LABELS = ["Đ.CL", "Đu.CL", "T.CL", "Đ.TB", "Đu.TB", "T.TB", "Hệ", "Hi.TB"]

def get_8bit(n):
    val = int(n); d, u = val // 10, val % 10
    return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
            1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
            1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]

def ultimate_analyze(history, last_n):
    if len(history) < 5: return [0.5]*8, ["0000"]*8
    all_bits = np.array([get_8bit(h["Số"]) for h in history])
    curr_bits = np.array(get_8bit(last_n))
    final_probs = np.zeros(8); seq_details = []
    
    W_SEQ, W_MOM, W_PAIR = 0.40, 0.30, 0.30

    for i in range(8):
        seg4 = all_bits[-4:, i]; s_str = "".join(map(str, seg4.astype(int)))
        # Logic Sequence 4 kỳ
        if s_str == "1111": p_seq = 0.85
        elif s_str == "0000": p_seq = 0.15
        elif s_str in ["0101", "1010"]: p_seq = 0.75 if s_str == "0101" else 0.25
        else: p_seq = 0.5
        
        p_mom = np.mean(all_bits[-10:, i])
        p_pair = 0.5
        if len(history) >= 22:
            seg22 = all_bits[-23:]; pm = []
            for j in range(8):
                if i==j: continue
                m = [seg22[k+1, i] for k in range(len(seg22)-1) if seg22[k, i] == curr_bits[i] and seg22[k, j] == curr_bits[j]]
                if m: pm.append(np.mean(m))
            if pm: p_pair = np.mean(pm)
        
        final_probs[i] = (p_seq * W_SEQ) + (p_mom * W_MOM) + (p_pair * W_PAIR)
        seq_details.append(s_str)
    return np.clip(final_probs, 0.05, 0.95).tolist(), seq_details

# --- 3. QUẢN LÝ DỮ LIỆU ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

st.title("🚀 8-BIT ULTIMATE V6.1 (PERFECT VIEW)")

with st.sidebar:
    st.header("📂 DỮ LIỆU MASTER")
    up = st.file_uploader("Nạp file .json:", type="json")
    if up:
        data = json.load(up); raw = data.get("history", [])
        st.session_state.history = sorted([{"Ngày": h.get("Ngày", "00/00"), "Kỳ": int(h.get("Kỳ", 0)), "Số": f"{int(h.get('Số', 0)):02d}", "Rank": h.get("Rank", 0)} for h in raw], key=lambda x: x["Kỳ"])
        if st.session_state.history: st.session_state.last_n = int(st.session_state.history[-1]["Số"])
    
    st.divider()
    num_dan_a = st.slider("Số lượng Dàn A:", 10, 90, 50)
    num_dan_b = st.slider("Số lượng Dàn B:", 10, 60, 36)
    
    if st.button("🔴 RESET"): st.session_state.history = []; st.rerun()

# NHẬP LIỆU
with st.container():
    c1, c2, c3 = st.columns([1,1,1])
    n_in = c1.text_input("Số vừa nổ:")
    next_ky = st.session_state.history[-1]["Kỳ"] + 1 if st.session_state.history else 1
    k_in = c2.number_input("Kỳ:", value=next_ky)
    if st.button("🚀 PHÂN TÍCH HỘI TỤ"):
        if n_in:
            val = int(n_in[-2:])
            if st.session_state.history:
                p, _ = ultimate_analyze(st.session_state.history, st.session_state.last_n)
                scr = []
                for i in range(100):
                    b = get_8bit(i); m = sum(b[j]*p[j] + (1-b[j])*(1-p[j]) for j in range(8))
                    scr.append({"S": f"{i:02d}", "M": m})
                df_t = pd.DataFrame(scr).sort_values("M", ascending=False); df_t['R'] = range(1, 101)
                r_v = df_t[df_t['S'] == f"{val:02d}"]['R'].values[0]
            else: r_v = 0
            st.session_state.history.append({"Ngày": datetime.now().strftime("%d/%m"), "Kỳ": int(k_in), "Số": f"{val:02d}", "Rank": int(r_v)})
            st.session_state.last_n = val; st.rerun()

# HIỂN THỊ
if st.session_state.history:
    probs, seqs = ultimate_analyze(st.session_state.history, st.session_state.last_n)
    res = []
    for i in range(100):
        b = get_8bit(i); m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        res.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(res).sort_values("M", ascending=False)

    tab1, tab2 = st.tabs(["🎯 DÀN TINH ANH & HỘI TỤ", "📊 NHẬT KÝ SIÊU NÉN"])
    
    with tab1:
        st.write(f"🔢 Nhịp gốc từ số: **{st.session_state.last_n:02d}** | Dữ liệu: **{len(st.session_state.history)} kỳ**")
        cols = st.columns(8)
        for i, (l, p) in enumerate(zip(BIT_LABELS, probs)):
            cols[i].metric(f"{l} ({seqs[i]})", f"{int(p*100)}%")
        
        st.divider()
        da, db = st.columns(2)
        da.markdown(f"**🔥 DÀN A ({num_dan_a} SỐ)**")
        da.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(num_dan_a)['S'].tolist())}</div>", unsafe_allow_html=True)
        db.markdown(f"**💎 DÀN B ({num_dan_b} SỐ)**")
        db.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(num_dan_b)['S'].tolist())}</div>", unsafe_allow_html=True)

    with tab2:
        # Nhật ký siêu nén
        disp = []
        for h in reversed(st.session_state.history):
            b = get_8bit(h["Số"])
            disp.append({
                "Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"],
                "Đ": "L" if b[0] else "C", "Đu": "L" if b[1] else "C", "T": "L" if b[2] else "C",
                "Đ.T": "T" if b[3] else "B", "Đu.T": "T" if b[4] else "B", "T.T": "T" if b[5] else "B",
                "Hệ": "Th" if b[6] else "Kp", "Hi": "T" if b[7] else "B"
            })
        st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)

    st.divider()
    st.download_button("💾 XUẤT BACKUP MASTER", json.dumps({"history": st.session_state.history}), f"8bit_v6.1_{datetime.now().strftime('%d%m')}.json")
