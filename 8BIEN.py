import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from itertools import combinations

# --- 1. GIAO DIỆN CHUẨN (NỀN TRẮNG - NÚT XANH NAVY) ---
st.set_page_config(page_title="8-BIT MOMENTUM V5.5", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { color: #000000 !important; background-color: #ffffff !important; font-size: 0.8rem !important; }
    .stButton button { 
        width: 100%; border-radius: 6px; height: 45px; font-weight: 700; 
        background-color: #000080 !important; color: #ffffff !important; border: none !important;
    }
    .dan-box { 
        background-color: #f8f9fa; border: 2px solid #000080; border-radius: 8px; 
        padding: 12px; font-family: 'Courier New', monospace; font-weight: 700; 
        color: #000080; text-align: center; font-size: 1.1rem;
    }
    .metric-card { background-color: #f0f4f8; border: 1px solid #d1d5db; border-radius: 8px; padding: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC (44 DẠNG DNA) ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]
BIT_LABELS = ["Đ.CL", "Đu.CL", "T.CL", "Đ.TB", "Đu.TB", "T.TB", "Hệ", "Hi.TB"]

@st.cache_data
def get_8bit(n):
    val = int(n); d, u = val // 10, val % 10
    return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
            1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
            1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]

# --- 3. BỘ NÃO MOMENTUM V5.5 (TÍNH TOÁN THEO Ý MÀY) ---
def analyze_momentum_quantum(history, last_n):
    if len(history) < 2: return [0.5]*8, []
    
    all_bits = np.array([get_8bit(h["Số"]) for h in history])
    current_bits = np.array(get_8bit(last_n))
    
    # 1. TÍNH XÁC SUẤT BỆT 10 KỲ (MOMENTUM)
    seg10 = all_bits[-10:]
    momentum_probs = np.mean(seg10, axis=0) # Tỷ lệ nổ 1 trong 10 kỳ
    
    # 2. QUÉT TRẠNG THÁI KỲ SAU (TRANSITION)
    final_probs = np.zeros(8)
    
    # Tầng 1: Nếu nhịp đang bệt (Tỷ lệ > 60% hoặc < 40%), ưu tiên bệt tiếp
    for i in range(8):
        if momentum_probs[i] >= 0.6: final_probs[i] += 0.7  # Xu hướng bệt 1
        elif momentum_probs[i] <= 0.4: final_probs[i] += 0.3 # Xu hướng bệt 0
        else: final_probs[i] += 0.5 # Nhịp loạn
    
    # Tầng 2: Đối chiếu lịch sử 22 kỳ (Cố định 2-Bit)
    insights = []
    if len(history) >= 22:
        seg22 = all_bits[-23:]
        for i, j in combinations(range(8), 2):
            matches = [seg22[k+1] for k in range(len(seg22)-1) if seg22[k][i] == current_bits[i] and seg22[k][j] == current_bits[j]]
            if matches:
                r = np.mean(matches, axis=0)
                final_probs += r * 0.5
                if np.max(r) >= 0.85:
                    insights.append(f"{BIT_LABELS[i]}-{BIT_LABELS[j]}: {int(np.max(r)*100)}%")

    return np.clip(final_probs / 1.5, 0.05, 0.95).tolist(), insights

# --- 4. APP MAIN ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

st.title("🛡️ 8-BIT MOMENTUM DNA V5.5")

with st.sidebar:
    st.header("📂 DỮ LIỆU")
    up = st.file_uploader("Nạp Master JSON:", type="json")
    if up:
        data = json.load(up); raw = data.get("history", [])
        st.session_state.history = sorted([{"Ngày": h.get("Ngày", "00/00"), "Kỳ": int(h.get("Kỳ", 0)), "Số": f"{int(h.get('Số', 0)):02d}", "Rank": h.get("Rank", 0)} for h in raw], key=lambda x: x["Kỳ"])
        if st.session_state.history: st.session_state.last_n = int(st.session_state.history[-1]["Số"])
    if st.button("🔴 RESET"): st.session_state.history = []; st.rerun()

# NHẬP LIỆU
with st.container():
    c1, c2, c3 = st.columns(3)
    n_in = c1.text_input("Số vừa về:")
    next_ky = st.session_state.history[-1]["Kỳ"] + 1 if st.session_state.history else 1
    k_in = c2.number_input("Kỳ tiếp theo:", value=next_ky)
    
    if st.button("🚀 PHÂN TÍCH NHỊP BỆT"):
        if n_in:
            val = int(n_in[-2:])
            if st.session_state.history:
                p, _ = analyze_momentum_quantum(st.session_state.history, st.session_state.last_n)
                scr = []
                for i in range(100):
                    b = get_8bit(i); m = sum(b[j]*p[j] + (1-b[j])*(1-p[j]) for j in range(8))
                    scr.append({"S": f"{i:02d}", "M": m})
                df_t = pd.DataFrame(scr).sort_values("M", ascending=False); df_t['R'] = range(1, 101)
                r_v = df_t[df_t['S'] == f"{val:02d}"]['R'].values[0]
            else: r_v = 0
            st.session_state.history.append({"Ngày": datetime.now().strftime("%d/%m"), "Kỳ": int(k_in)-1, "Số": f"{val:02d}", "Rank": int(r_v)})
            st.session_state.last_n = val; st.rerun()

if st.session_state.history:
    probs, insights = analyze_momentum_quantum(st.session_state.history, st.session_state.last_n)
    res = []
    for i in range(100):
        b = get_8bit(i); m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        res.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(res).sort_values("M", ascending=False)

    tab1, tab2 = st.tabs(["🎯 DÀN TINH ANH (MOMENTUM)", "📊 NHẬT KÝ 11 CỘT"])
    
    with tab1:
        st.subheader(f"🔢 Nhịp bệt từ số: {st.session_state.last_n:02d}")
        cols = st.columns(8)
        for i, (l, p) in enumerate(zip(BIT_LABELS, probs)):
            cols[i].metric(l, f"{int(p*100)}%")
        
        st.divider()
        da, db = st.columns(2)
        da.markdown("**🔥 DÀN A (50 SỐ)**"); da.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(50)['S'].tolist())}</div>", unsafe_allow_html=True)
        db.markdown("**💎 DÀN B (36 SỐ)**"); db.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(36)['S'].tolist())}</div>", unsafe_allow_html=True)
        if insights: st.info("⚡ Tổ hợp 2-bit bùng nổ: " + " | ".join(insights[:5]))

    with tab2:
        disp = []
        for h in reversed(st.session_state.history):
            b = get_8bit(h["Số"])
            disp.append({
                "Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"],
                "Đ.CL": "L" if b[0] else "C", "Đu.CL": "L" if b[1] else "C", "T.CL": "L" if b[2] else "C",
                "Đ.TB": "T" if b[3] else "B", "Đu.TB": "T" if b[4] else "B", "T.TB": "T" if b[5] else "B",
                "Hệ": "Th" if b[6] else "Kp", "Hi.TB": "T" if b[7] else "B"
            })
        st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)
