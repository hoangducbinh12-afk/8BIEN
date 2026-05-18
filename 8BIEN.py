import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from itertools import combinations

# --- 1. GIAO DIỆN (NỀN TRẮNG - NÚT XANH NAVY) ---
st.set_page_config(page_title="8-BIT QUANTUM V6.5", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { color: #000000 !important; background-color: #ffffff !important; font-size: 0.75rem !important; }
    .stButton button { 
        width: 100%; border-radius: 6px; height: 42px; font-weight: 700; 
        background-color: #000080 !important; color: #ffffff !important;
    }
    .dan-box { 
        background-color: #f1f5f9; border: 2px solid #000080; border-radius: 8px; 
        padding: 10px; font-family: 'Courier New', monospace; font-weight: 700; 
        color: #000080; text-align: center; font-size: 1rem;
    }
    .weight-card {
        background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px;
        padding: 8px; margin-bottom: 4px; font-size: 0.7rem;
    }
    .bit-title { color: #000080; font-weight: 800; border-bottom: 1px solid #000080; margin-bottom: 5px; }
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

# --- 3. PHÂN TÍCH CHI TIẾT TRỌNG SỐ ---
def analyze_with_weights(history, last_n):
    all_bits = np.array([get_8bit(h["Số"]) for h in history])
    curr_bits = np.array(get_8bit(last_n))
    
    final_results = []
    
    for i in range(8):
        # Tầng 1: Nhịp Chuỗi 3/4 kỳ (40%)
        seg4 = all_bits[-4:, i]; s_str = "".join(map(str, seg4.astype(int)))
        if s_str == "1111" or (s_str.count('1')==3 and s_str[-1]==1): p_seq = 0.82
        elif s_str == "0000" or (s_str.count('1')==1 and s_str[-1]==0): p_seq = 0.18
        elif s_str == "0101": p_seq = 0.85
        elif s_str == "1010": p_seq = 0.15
        else: p_seq = 0.5
        
        # Tầng 2: Momentum 10 kỳ (25%)
        p_mom = np.mean(all_bits[-10:, i])
        
        # Tầng 3: Lịch sử 22 kỳ (20%)
        p_pair = 0.5
        if len(history) >= 22:
            seg22 = all_bits[-23:]; pm = []
            for j in range(8):
                if i==j: continue
                m = [seg22[k+1, i] for k in range(len(seg22)-1) if seg22[k, i] == curr_bits[i] and seg22[k, j] == curr_bits[j]]
                if m: pm.append(np.mean(m))
            if pm: p_pair = np.mean(pm)
            
        # Tầng 4: DNA (15%) - Tính mặc định là trung tính cho bit, nhưng ảnh hưởng Rank
        p_dna = 0.5
        
        # Công thức tính xác suất cuối cùng
        f_prob = (p_seq * 0.40) + (p_mom * 0.25) + (p_pair * 0.20) + (p_dna * 0.15)
        
        final_results.append({
            "label": BIT_LABELS[i],
            "seq_str": s_str,
            "p_seq": int(p_seq*100),
            "p_mom": int(p_mom*100),
            "p_pair": int(p_pair*100),
            "f_prob": f_prob
        })
        
    return final_results

# --- 4. APP MAIN ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

st.title("🧬 QUANTUM TRANSPARENT V6.5")

with st.sidebar:
    st.header("📂 DỮ LIỆU")
    up = st.file_uploader("Nạp Master JSON:", type="json")
    if up:
        data = json.load(up); raw = data.get("history", [])
        st.session_state.history = sorted([{"Ngày": h.get("Ngày", "00/00"), "Kỳ": int(h.get("Kỳ", 0)), "Số": f"{int(h.get('Số', 0)):02d}", "Rank": h.get("Rank", 0)} for h in raw], key=lambda x: x["Kỳ"])
        if st.session_state.history: st.session_state.last_n = int(st.session_state.history[-1]["Số"])
    num_quan = st.number_input("Số quân lấy dàn:", value=50)
    if st.button("🔴 RESET"): st.session_state.history = []; st.rerun()

# NHẬP LIỆU
with st.container():
    c1, c2, c3 = st.columns(3)
    n_in = c1.text_input("Số nổ:")
    ky_in = c2.number_input("Kỳ:", value=st.session_state.history[-1]["Kỳ"] + 1 if st.session_state.history else 1)
    if st.button("🚀 PHÂN TÍCH TRỌNG SỐ"):
        if n_in:
            val = int(n_in[-2:])
            if st.session_state.history:
                results = analyze_with_weights(st.session_state.history, st.session_state.last_n)
                probs = [r["f_prob"] for r in results]
                scr = []
                for i in range(100):
                    b = get_8bit(i); m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
                    scr.append({"S": f"{i:02d}", "M": m})
                df_t = pd.DataFrame(scr).sort_values("M", ascending=False); df_t['R'] = range(1, 101)
                r_v = df_t[df_t['S'] == f"{val:02d}"]['R'].values[0]
            else: r_v = 0
            st.session_state.history.append({"Ngày": datetime.now().strftime("%d/%m"), "Kỳ": int(ky_in), "Số": f"{val:02d}", "Rank": int(r_v)})
            st.session_state.last_n = val; st.rerun()

# HIỂN THỊ
if st.session_state.history:
    results = analyze_with_weights(st.session_state.history, st.session_state.last_n)
    probs = [r["f_prob"] for r in results]
    
    res_rank = []
    for i in range(100):
        b = get_8bit(i); m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        res_rank.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(res_rank).sort_values("M", ascending=False)

    tab1, tab2 = st.tabs(["🎯 BẢNG SOI TRỌNG SỐ", "📊 NHẬT KÝ"])
    
    with tab1:
        st.write("### 🔍 Giải mã các lớp xác suất (%)")
        # Hiển thị 8 cột, mỗi cột là 1 Bit với các thông số bên trong
        cols = st.columns(8)
        for i, r in enumerate(results):
            with cols[i]:
                st.markdown(f"""
                <div class='bit-title'>{r['label']}</div>
                <div class='weight-card'><b>Nhịp 4k:</b> {r['seq_str']} -> {r['p_seq']}%</div>
                <div class='weight-card'><b>10 Kỳ:</b> {r['p_mom']}%</div>
                <div class='weight-card'><b>22 Kỳ:</b> {r['p_pair']}%</div>
                <div class='weight-card' style='background:#e0f2fe'><b>Hội tụ: {int(r['f_prob']*100)}%</b></div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown(f"**🔥 DÀN TINH ANH {num_quan} SỐ QUÂN**")
        st.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(int(num_quan))['S'].tolist())}</div>", unsafe_allow_html=True)

    with tab2:
        # Nhật ký siêu nén
        disp = []
        for h in reversed(st.session_state.history):
            b = get_8bit(h["Số"])
            disp.append({"Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"], "Mã DNA": "".join(map(str, b))})
        st.dataframe(pd.DataFrame(disp), use_container_width=True)
