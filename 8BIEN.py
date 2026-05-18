import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from itertools import combinations

# --- 1. CONFIG & CSS (Giữ nguyên phong cách V3.5) ---
st.set_page_config(page_title="8-BIT QUANTUM V4.6", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.75rem !important; }
    .dan-box { background-color: #f0f2f6; border: 1px solid #1e3a8a; border-radius: 8px; padding: 10px; font-family: monospace; font-weight: 700; color: #1e3a8a; text-align: center; font-size: 1.1rem; word-wrap: break-word; }
    .stButton button { width: 100%; border-radius: 5px; font-weight: 700; background-color: #1e3a8a !important; color: white !important; }
    .metric-card { background: #1e293b; padding: 10px; border-radius: 8px; color: #00d9ff; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC (44 Dạng Bit & DNA) ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]
BIT_LABELS = ["Đ.CL", "Đu.CL", "T.CL", "Đ.TB", "Đu.TB", "T.TB", "Hệ", "Hi.TB"]

def get_8bit(n):
    try:
        val = int(n); d, u = val // 10, val % 10
        return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
                1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
                1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]
    except: return [0]*8

# --- 3. INFINITE SCAN ENGINE (Cải tiến để không treo App) ---
def quantum_engine(history, last_n):
    if not history: return [0.5]*8, []
    
    current_bits = get_8bit(last_n)
    all_bits = [get_8bit(h["Số"]) for h in history][::-1]
    final_probs = np.zeros(8)
    total_w = 0.0
    deep_insights = []

    # Định nghĩa các tầng quét (Mốc kỳ theo yêu cầu của mày)
    configs = [
        {"n": 1, "k": 10, "w": 0.3}, # Tầng 1: 10 kỳ
        {"n": 2, "k": 22, "w": 0.4}, # Tầng 2: 22 kỳ (Mốc quan trọng)
        {"n": 3, "k": 60, "w": 0.3}  # Tầng 3: 60 kỳ
    ]

    for cfg in configs:
        if len(all_bits) < cfg["k"]: continue
        seg = all_bits[-cfg["k"]:]
        layer_scores = np.zeros(8)
        layer_matches = 0
        
        # Chỉ quét tổ hợp nếu n > 1
        combos = list(combinations(range(8), cfg["n"]))
        for cb in combos:
            target = [current_bits[i] for i in cb]
            matches = [seg[m+1] for m in range(len(seg)-1) if all(seg[m][cb[i]] == target[i] for i in range(len(cb)))]
            if matches:
                layer_scores += np.mean(matches, axis=0)
                layer_matches += 1
                # Lưu Insight cho tầng sâu
                if cfg["n"] >= 2 and (np.max(np.mean(matches, axis=0)) > 0.85):
                    deep_insights.append({"Loại": f"{cfg['n']}-Bit", "Tổ hợp": cb, "Tỷ lệ": np.max(np.mean(matches, axis=0))})

        if layer_matches > 0:
            final_probs += (layer_scores / layer_matches) * cfg["w"]
            total_w += cfg["w"]

    res = (final_probs / total_w) if total_w > 0 else [0.5]*8
    return res.tolist(), deep_insights

# --- 4. GIAO DIỆN (Lấy lại bản V3.5) ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

st.title("🧬 8-BIT QUANTUM V4.6 (MASTER EDITION)")

# Sidebar Quản lý File
with st.sidebar:
    st.header("📁 DỮ LIỆU MASTER")
    uploaded_file = st.file_uploader("Nạp file Master .json", type="json")
    if uploaded_file:
        data = json.load(uploaded_file)
        st.session_state.history = sorted(data.get("history", []), key=lambda x: int(x["Kỳ"]), reverse=True)
        st.session_state.last_n = int(st.session_state.history[0]["Số"])
        st.success(f"Đã nạp {len(st.session_state.history)} kỳ!")
    
    st.divider()
    if st.button("🔴 RESET TOÀN BỘ"):
        st.session_state.history = []
        st.session_state.last_n = -1
        st.rerun()

# Khu vực nhập liệu (V3.5 style)
with st.container():
    c1, c2, c3 = st.columns([1,1,1])
    n_in = c1.text_input("GĐB (Số cuối):", placeholder="Ví dụ: 84")
    k_in = c2.number_input("Kỳ quay:", value=len(st.session_state.history)+1)
    if st.button("🚀 PHÂN TÍCH ĐA TẦNG"):
        if n_in:
            val = int(n_in[-2:])
            st.session_state.history.insert(0, {"Ngày": datetime.now().strftime("%d/%m"), "Kỳ": int(k_in), "Số": f"{val:02d}"})
            st.session_state.last_n = val
            st.rerun()

# Hiển thị Tabs chức năng
if st.session_state.history:
    probs, insights = quantum_engine(st.session_state.history, st.session_state.last_n)
    
    # Tính toán Rank
    rank_list = []
    for i in range(100):
        b = get_8bit(i)
        m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        rank_list.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(rank_list).sort_values("M", ascending=False)

    tab1, tab2, tab3 = st.tabs(["🎯 DÀN TINH ANH", "🔍 DEEP SCAN (3-BIT)", "📊 LỊCH SỬ"])

    with tab1:
        st.subheader("Bảng xác suất hội tụ (Phễu 10-22-60 kỳ)")
        cols = st.columns(8)
        for i, (label, p) in enumerate(zip(BIT_LABELS, probs)):
            cols[i].metric(label, f"{int(p*100)}%")
        
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("🔥 **Dàn A (50 số):**")
            st.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(50)['S'].tolist())}</div>", unsafe_allow_html=True)
        with col_b:
            st.write("💎 **Dàn B (36 số):**")
            st.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(36)['S'].tolist())}</div>", unsafe_allow_html=True)

    with tab2:
        st.header("⚡ Cảnh báo tổ hợp nòng cốt")
        if insights:
            for ins in insights[:10]:
                bits_name = [BIT_LABELS[i] for i in ins['Tổ hợp']]
                st.info(f"Phát hiện tổ hợp **{ins['Loại']}** [{', '.join(bits_name)}] có tỷ lệ lặp lại **{int(ins['Tỷ lệ']*100)}%**")
        else:
            st.warning("Cần thêm dữ liệu (>60 kỳ) để kích hoạt Deep Scan 3-Bit.")

    with tab3:
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
