import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from itertools import combinations

# --- 1. GIAO DIỆN CHUẨN: NỀN TRẮNG - CHỮ ĐEN - NÚT XANH CHỮ TRẮNG ---
st.set_page_config(page_title="8-BIT QUANTUM V5.1", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.8rem !important; color: #000000 !important; background-color: #ffffff !important; }
    .stButton button { 
        width: 100%; border-radius: 8px; height: 45px; font-weight: 700; 
        background-color: #0047AB !important; color: #ffffff !important; border: none !important;
    }
    .dan-box { 
        background-color: #f8f9fa; border: 2px solid #0047AB; border-radius: 10px; 
        padding: 15px; font-family: monospace; font-weight: 700; color: #0047AB; 
        text-align: center; font-size: 1.1rem; margin-bottom: 10px;
    }
    .priority-card {
        background-color: #e3f2fd; border-left: 5px solid #0047AB; padding: 10px; margin-bottom: 5px; color: #000000;
    }
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

# --- 3. MÁY QUÉT ĐA TẦNG VÀ HIỂN THỊ ƯU TIÊN ---
def get_quantum_insights(history, last_n):
    if len(history) < 2: return [0.5]*8, []
    
    current_bits = get_8bit(last_n)
    all_bits = [get_8bit(h["Số"]) for h in history]
    final_probs = np.zeros(8)
    insights = []

    # Tầng 1: 1-Bit (10 kỳ)
    seg10 = all_bits[-11:]
    for i in range(8):
        matches = [seg10[k+1] for k in range(len(seg10)-1) if seg10[k][i] == current_bits[i]]
        if matches: final_probs += np.mean(matches, axis=0) * 0.3

    # Tầng 2: 2-Bit (22 kỳ)
    if len(history) >= 22:
        seg22 = all_bits[-23:]
        combos2 = list(combinations(range(8), 2))
        for cb in combos2:
            target = [current_bits[i] for i in cb]
            matches = [seg22[k+1] for k in range(len(seg22)-1) if all(seg22[k][cb[m]] == target[m] for m in range(2))]
            if matches:
                ratios = np.mean(matches, axis=0)
                final_probs += ratios * 0.4
                if np.max(ratios) >= 0.85 or np.min(ratios) <= 0.15:
                    insights.append({"Loại": "2-BIT", "Tổ hợp": f"{BIT_LABELS[cb[0]]}-{BIT_LABELS[cb[1]]}", "Mẫu": len(matches), "Tỷ lệ": np.max(ratios) if np.max(ratios) >= 0.85 else 1-np.min(ratios)})

    # Tầng 3: 3-Bit (60 kỳ)
    if len(history) >= 60:
        seg60 = all_bits[-61:]
        combos3 = list(combinations(range(8), 3))
        for cb in combos3:
            target = [current_bits[i] for i in cb]
            matches = [seg60[k+1] for k in range(len(seg60)-1) if all(seg60[k][cb[m]] == target[m] for m in range(3))]
            if matches:
                ratios = np.mean(matches, axis=0)
                final_probs += ratios * 0.3
                if np.max(ratios) >= 0.9:
                    insights.append({"Loại": "3-BIT", "Tổ hợp": f"{BIT_LABELS[cb[0]]}-{BIT_LABELS[cb[1]]}-{BIT_LABELS[cb[2]]}", "Mẫu": len(matches), "Tỷ lệ": np.max(ratios)})

    return np.clip(final_probs / 1.0, 0.05, 0.95).tolist(), sorted(insights, key=lambda x: x['Tỷ lệ'], reverse=True)

# --- 4. GIAO DIỆN ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

st.title("🛡️ 8-BIT QUANTUM MASTER V5.1")

with st.sidebar:
    st.header("📂 DỮ LIỆU")
    up = st.file_uploader("Nạp file Master (.json):", type="json")
    if up:
        data = json.load(up)
        raw = data.get("history", []) if isinstance(data, dict) else data
        st.session_state.history = sorted([{"Ngày": h.get("Ngày", "00/00"), "Kỳ": int(h.get("Kỳ", 0)), "Số": f"{int(h.get('Số', 0)):02d}", "Rank": int(h.get("Rank", 0))} for h in raw], key=lambda x: x["Kỳ"])
        if st.session_state.history: st.session_state.last_n = int(st.session_state.history[-1]["Số"])
    if st.button("🔴 RESET"): st.session_state.history = []; st.session_state.last_n = -1; st.rerun()

# NHẬP LIỆU
with st.container():
    c1, c2, c3 = st.columns(3)
    n_in = c1.text_input("Số vừa về:")
    next_ky = st.session_state.history[-1]["Kỳ"] + 1 if st.session_state.history else 1
    k_in = c2.number_input("Kỳ vừa về:", value=next_ky)
    if st.button("🔥 PHÂN TÍCH & ƯU TIÊN"):
        if n_in:
            val = int(n_in[-2:])
            if st.session_state.history:
                probs, _ = get_quantum_insights(st.session_state.history, st.session_state.last_n)
                scores = []
                for i in range(100):
                    b = get_8bit(i); m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
                    scores.append({"S": f"{i:02d}", "M": m})
                df_tmp = pd.DataFrame(scores).sort_values("M", ascending=False); df_tmp['R'] = range(1, 101)
                r_val = df_tmp[df_tmp['S'] == f"{val:02d}"]['R'].values[0]
            else: r_val = 0
            st.session_state.history.append({"Ngày": datetime.now().strftime("%d/%m"), "Kỳ": int(k_in), "Số": f"{val:02d}", "Rank": int(r_val)})
            st.session_state.last_n = val; st.rerun()

if st.session_state.history:
    probs, insights = get_quantum_insights(st.session_state.history, st.session_state.last_n)
    res_list = []
    for i in range(100):
        b = get_8bit(i); m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        res_list.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(res_list).sort_values("M", ascending=False)

    tab1, tab2, tab3 = st.tabs(["🎯 DÀN TINH ANH", "📈 ƯU TIÊN ĐA TẦNG", "📊 NHẬT KÝ"])
    
    with tab1:
        st.write(f"🔢 Nhịp từ số: **{st.session_state.last_n:02d}**")
        cols = st.columns(8)
        for i, (label, p) in enumerate(zip(BIT_LABELS, probs)): cols[i].metric(label, f"{int(p*100)}%")
        st.divider()
        da, db = st.columns(2)
        da.markdown("**🔥 DÀN A (50 SỐ)**"); da.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(50)['S'].tolist())}</div>", unsafe_allow_html=True)
        db.markdown("**💎 DÀN B (36 SỐ)**"); db.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(36)['S'].tolist())}</div>", unsafe_allow_html=True)

    with tab2:
        st.subheader("🚀 CÁC TỔ HỢP CỐ ĐỊNH CÓ TỶ LỆ CAO")
        if insights:
            for ins in insights:
                st.markdown(f"<div class='priority-card'>⭐ <b>{ins['Loại']}</b>: Cố định [{ins['Tổ hợp']}] -> Mẫu {ins['Mẫu']} kỳ -> Tỷ lệ nổ: <b>{int(ins['Tỷ lệ']*100)}%</b></div>", unsafe_allow_html=True)
        else:
            st.warning("Dữ liệu chưa đủ lớn để phát hiện tổ hợp 2-bit/3-bit có tỷ lệ nổ > 85%. Hãy tiếp tục nhập thêm kỳ!")

    with tab3:
        display_data = []
        for h in reversed(st.session_state.history):
            b = get_8bit(h["Số"])
            display_data.append({"Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"], "Đ.CL": "L" if b[0] else "C", "Đu.CL": "L" if b[1] else "C", "T.CL": "L" if b[2] else "C", "Đ.TB": "T" if b[3] else "B", "Đu.TB": "T" if b[4] else "B", "T.TB": "T" if b[5] else "B", "Hệ": "Th" if b[6] else "Kp", "Hi.TB": "T" if b[7] else "B"})
        st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)
