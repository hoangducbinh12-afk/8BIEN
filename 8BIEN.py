import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. GIAO DIỆN CHUẨN V6.7 ---
st.set_page_config(page_title="8-BIT QUANTUM V6.7", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { color: #000000 !important; background-color: #ffffff !important; font-size: 0.72rem !important; }
    .stButton button { 
        width: 100%; border-radius: 4px; height: 38px; font-weight: 700; 
        background-color: #000080 !important; color: #ffffff !important;
    }
    .dan-box { 
        background-color: #f1f5f9; border: 1px solid #000080; border-radius: 5px; 
        padding: 8px; font-family: monospace; font-weight: 700; color: #000080; text-align: center; font-size: 0.95rem;
    }
    .bit-card {
        background-color: #ffffff; border: 1px solid #d1d5db; border-radius: 5px;
        padding: 4px; margin-bottom: 2px; line-height: 1.1;
    }
    .bit-header { background: #000080; color: white; text-align: center; font-weight: bold; border-radius: 3px; margin-bottom: 2px; }
    .stNumberInput input, .stTextInput input { height: 38px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]
BIT_LABELS = ["Đ.CL", "Đu.CL", "T.CL", "Đ.TB", "Đu.TB", "T.TB", "Hệ", "Hi.TB"]

def get_8bit(n):
    val = int(n); d, u = val // 10, val % 10
    return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
            1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
            1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]

def analyze_full_v67(history, last_n):
    all_bits = np.array([get_8bit(h["Số"]) for h in history])
    curr_bits = np.array(get_8bit(last_n))
    results = []
    
    for i in range(8):
        # Mã chuỗi
        s3 = "".join(map(str, all_bits[-3:, i].astype(int)))
        s4 = "".join(map(str, all_bits[-4:, i].astype(int)))
        
        # % Nhịp 3K (Tư duy 3 kỳ)
        if s3 == "111": p3 = 0.75
        elif s3 == "000": p3 = 0.25
        elif s3 == "101": p3 = 0.62
        elif s3 == "010": p3 = 0.38
        else: p3 = 0.5
        
        # % Nhịp 4K (Tư duy 4 kỳ)
        if s4 == "1111" or (s4.count('1')==3 and s4[-1]==1): p4 = 0.82
        elif s4 == "0000" or (s4.count('1')==1 and s4[-1]==0): p4 = 0.18
        elif s4 == "0101": p4 = 0.85
        elif s4 == "1010": p4 = 0.15
        else: p4 = 0.5
        
        p_mom = np.mean(all_bits[-10:, i]) # 10 kỳ
        
        p_pair = 0.5 # 22 kỳ
        if len(history) >= 22:
            seg22 = all_bits[-23:]; pm = []
            for j in range(8):
                if i==j: continue
                m = [seg22[k+1, i] for k in range(len(seg22)-1) if seg22[k, i] == curr_bits[i] and seg22[k, j] == curr_bits[j]]
                if m: pm.append(np.mean(m))
            if pm: p_pair = np.mean(pm)
            
        f_prob = (p4 * 0.40) + (p_mom * 0.25) + (p_pair * 0.20) + (0.5 * 0.15)
        results.append({"l": BIT_LABELS[i], "s3": s3, "p3": p3, "s4": s4, "p4": p4, "p_mom": p_mom, "p_pair": p_pair, "f": f_prob})
    return results

# --- 3. SESSION STATE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

# --- 4. VÙNG CHỈ HUY (DÒNG 1: NHẬP & PHÂN TÍCH) ---
st.title("🛡️ QUANTUM MASTER V6.7")
with st.container():
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1, 2])
    n_in = c1.text_input("Số nổ:", placeholder="VD: 62")
    if c2.button("🚀 PHÂN TÍCH"):
        if n_in:
            val = int(n_in[-2:])
            ky_val = st.session_state.history[-1]["Kỳ"] + 1 if st.session_state.history else 1
            if st.session_state.history:
                res = analyze_full_v67(st.session_state.history, st.session_state.last_n)
                p = [r["f"] for r in res]
                scr = []
                for i in range(100):
                    b = get_8bit(i); m = sum(b[j]*p[j] + (1-b[j])*(1-p[j]) for j in range(8))
                    scr.append({"S": f"{i:02d}", "M": m})
                df_t = pd.DataFrame(scr).sort_values("M", ascending=False); df_t['R'] = range(1, 101)
                r_v = df_t[df_t['S'] == f"{val:02d}"]['R'].values[0]
            else: r_v = 0
            st.session_state.history.append({"Ngày": datetime.now().strftime("%d/%m"), "Kỳ": int(ky_val), "Số": f"{val:02d}", "Rank": int(r_v)})
            st.session_state.last_n = val; st.rerun()
    st.write("") # Khoảng trống

# --- 5. HIỂN THỊ CHÍNH ---
if st.session_state.history:
    results = analyze_full_v67(st.session_state.history, st.session_state.last_n)
    probs = [r["f"] for r in results]
    
    res_rank = []
    for i in range(100):
        b = get_8bit(i); m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        res_rank.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(res_rank).sort_values("M", ascending=False)

    tab1, tab2 = st.tabs(["🎯 DÀN TINH ANH & TRỌNG SỐ", "📊 NHẬT KÝ SIÊU NÉN"])
    
    with tab1:
        # Bảng trọng số đa tầng
        cols = st.columns(8)
        for i, r in enumerate(results):
            with cols[i]:
                st.markdown(f"""
                <div class='bit-header'>{r['l']}</div>
                <div class='bit-card'><b>3K ({r['s3']}):</b> {int(r['p3']*100)}%</div>
                <div class='bit-card'><b>4K ({r['s4']}):</b> {int(r['p4']*100)}%</div>
                <div class='bit-card'><b>10K:</b> {int(r['p_mom']*100)}%</div>
                <div class='bit-card'><b>22K:</b> {int(r['p_pair']*100)}%</div>
                <div class='bit-card' style='background:#e0f2fe; border: 1px solid #000080'><b>Hội tụ: {int(r['f']*100)}%</b></div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # DÒNG TIÊU ĐỀ DÀN & Ô LẤY QUÂN
        ca, cb = st.columns([2, 1])
        num_quan = cb.number_input("Số quân lấy dàn:", value=50, step=1, key="num_quan_dan")
        ca.markdown(f"### 🔥 DÀN TINH ANH {int(num_quan)} SỐ")
        
        st.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(int(num_quan))['S'].tolist())}</div>", unsafe_allow_html=True)

    with tab2:
        display_data = []
        for h in reversed(st.session_state.history):
            b = get_8bit(h["Số"])
            display_data.append({
                "Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"],
                "Đ": "L" if b[0] else "C", "Đu": "L" if b[1] else "C", "T": "L" if b[2] else "C",
                "Đ.T": "T" if b[3] else "B", "Đu.T": "T" if b[4] else "B", "T.T": "T" if b[5] else "B",
                "Hệ": "Th" if b[6] else "Kp", "Hi": "T" if b[7] else "B"
            })
        st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)

with st.sidebar:
    st.header("📂 HỆ THỐNG")
    up = st.file_uploader("Nạp Master JSON:", type="json")
    if up:
        data = json.load(up); raw = data.get("history", [])
        st.session_state.history = sorted([{"Ngày": h.get("Ngày", "00/00"), "Kỳ": int(h.get("Kỳ", 0)), "Số": f"{int(h.get('Số', 0)):02d}", "Rank": h.get("Rank", 0)} for h in raw], key=lambda x: x["Kỳ"])
        if st.session_state.history: st.session_state.last_n = int(st.session_state.history[-1]["Số"])
        st.rerun()
    st.divider()
    if st.button("🔴 RESET"): st.session_state.history = []; st.rerun()
    if st.session_state.history:
        st.download_button("💾 XUẤT BACKUP", json.dumps({"history": st.session_state.history}), f"8bit_v6.7_{datetime.now().strftime('%d%m')}.json")
