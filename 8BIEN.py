import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from itertools import combinations

# --- 1. GIAO DIỆN CHUẨN V6.0 ---
st.set_page_config(page_title="8-BIT ULTIMATE V6.0", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { color: #000000 !important; background-color: #ffffff !important; font-size: 0.8rem !important; }
    .stButton button { 
        width: 100%; border-radius: 6px; height: 45px; font-weight: 700; 
        background-color: #000080 !important; color: #ffffff !important;
    }
    .dan-box { 
        background-color: #f8f9fa; border: 2px solid #000080; border-radius: 8px; 
        padding: 12px; font-family: monospace; font-weight: 700; color: #000080; text-align: center;
    }
    .metric-card { background: #eef2ff; border-radius: 8px; padding: 10px; border: 1px solid #c7d2fe; }
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

# --- 3. BỘ NÃO ĐA TẦNG (MULTI-FACTOR ENGINE) ---
def ultimate_analyze(history, last_n):
    if len(history) < 10: return [0.5]*8, {}
    
    all_bits = np.array([get_8bit(h["Số"]) for h in history])
    curr_bits = np.array(get_8bit(last_n))
    final_probs = np.zeros(8)
    
    # TRỌNG SỐ NHÂN (TỔNG = 1.0)
    W_SEQ = 0.40 # Nhịp chuỗi 4 kỳ
    W_MOM = 0.25 # Nhịp 10 kỳ
    W_PAIR = 0.20 # Cặp 22 kỳ
    W_DNA = 0.15 # DNA bầy đàn (tính trong Rank)

    seq_details = []

    for i in range(8):
        # 1. Tầng Sequence (4 kỳ)
        seg4 = all_bits[-4:, i]
        if np.array_equal(seg4, [1,1,1,1]): p_seq = 0.85
        elif np.array_equal(seg4, [0,0,0,0]): p_seq = 0.15
        elif np.array_equal(seg4, [0,1,0,1]): p_seq = 0.70
        elif np.array_equal(seg4, [1,0,1,0]): p_seq = 0.30
        else: p_seq = 0.5 # Nếu cân bằng, tầng này trả về trung tính
        
        # 2. Tầng Momentum (10 kỳ)
        p_mom = np.mean(all_bits[-10:, i])
        
        # 3. Tầng Pair (22 kỳ)
        p_pair = 0.5
        if len(history) >= 22:
            seg22 = all_bits[-23:]
            # Quét các cặp liên quan đến bit i
            pair_matches = []
            for j in range(8):
                if i == j: continue
                m = [seg22[k+1, i] for k in range(len(seg22)-1) if seg22[k, i] == curr_bits[i] and seg22[k, j] == curr_bits[j]]
                if m: pair_matches.append(np.mean(m))
            if pair_matches: p_pair = np.mean(pair_matches)

        # CÔNG THỨC NHÂN TRỌNG SỐ
        # Nếu nhịp chuỗi cân bằng (0.5), các yếu tố Mom và Pair sẽ chiếm quyền quyết định
        final_probs[i] = (p_seq * W_SEQ) + (p_mom * W_MOM) + (p_pair * W_PAIR) + (0.5 * W_DNA)
        seq_details.append(f"{''.join(map(str, seg4.astype(int)))}")

    return np.clip(final_probs, 0.05, 0.95).tolist(), seq_details

# --- 4. APP MAIN ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

st.title("🛡️ 8-BIT ULTIMATE QUANTUM V6.0")

# Sidebar: Nạp dữ liệu Master
with st.sidebar:
    st.header("📂 DỮ LIỆU")
    up = st.file_uploader("Nạp Master JSON:", type="json")
    if up:
        data = json.load(up); raw = data.get("history", [])
        st.session_state.history = sorted([{"Ngày": h.get("Ngày", "00/00"), "Kỳ": int(h.get("Kỳ", 0)), "Số": f"{int(h.get('Số', 0)):02d}", "Rank": h.get("Rank", 0)} for h in raw], key=lambda x: x["Kỳ"])
        if st.session_state.history: st.session_state.last_n = int(st.session_state.history[-1]["Số"])
    if st.button("🔴 RESET"): st.session_state.history = []; st.rerun()

# Nhập liệu
with st.container():
    c1, c2, c3 = st.columns(3)
    n_in = c1.text_input("Số vừa nổ (2 số cuối):")
    next_ky = st.session_state.history[-1]["Kỳ"] + 1 if st.session_state.history else 1
    k_in = c2.number_input("Kỳ:", value=next_ky)
    if st.button("🚀 PHÂN TÍCH ĐA TẦNG V6.0"):
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

# Hiển thị
if st.session_state.history:
    probs, seqs = ultimate_analyze(st.session_state.history, st.session_state.last_n)
    res = []
    for i in range(100):
        b = get_8bit(i); m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        res.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(res).sort_values("M", ascending=False)

    tab1, tab2 = st.tabs(["🎯 DÀN TINH ANH (HỘI TỤ)", "📊 GIẢI MÃ CHUỖI 4 KỲ"])
    
    with tab1:
        st.subheader(f"🔢 Nhịp từ số: {st.session_state.last_n:02d}")
        cols = st.columns(8)
        for i, (l, p) in enumerate(zip(BIT_LABELS, probs)):
            cols[i].metric(f"{l} ({seqs[i]})", f"{int(p*100)}%")
        
        st.divider()
        da, db = st.columns(2)
        da.markdown("**🔥 DÀN A (50 SỐ)**"); da.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(50)['S'].tolist())}</div>", unsafe_allow_html=True)
        db.markdown("**💎 DÀN B (36 SỐ)**"); db.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(36)['S'].tolist())}</div>", unsafe_allow_html=True)

    with tab2:
        st.write("### Phân tích sâu chuỗi Bit 4 kỳ gần nhất")
        # Image tag for visualization of binary sequences
        st.markdown("")
        display_data = []
        for h in reversed(st.session_state.history):
            b = get_8bit(h["Số"])
            display_data.append({"Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"], "Mã DNA": "".join(map(str, b))})
        st.dataframe(pd.DataFrame(display_data), use_container_width=True)
