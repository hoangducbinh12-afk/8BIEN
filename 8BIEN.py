import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. CONFIG GIAO DIỆN SIÊU NHỎ CHO MOBILE ---
st.set_page_config(page_title="8-BIT MASTER V2.4", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.72rem !important; }
    .dan-box { 
        background-color: #ffffff; border: 1.5px solid #1e3a8a; border-radius: 8px; 
        padding: 8px; margin-bottom: 10px; font-family: monospace; 
        font-weight: 700; color: #1e3a8a; text-align: center; font-size: 0.85rem;
    }
    /* Ép bảng nhật ký siêu nhỏ giống ảnh mẫu */
    .stDataFrame td, .stDataFrame th { 
        padding: 1px 2px !important; font-size: 0.65rem !important; text-align: center !important;
    }
    .stButton button { 
        width: 100%; border-radius: 8px; height: 35px; font-weight: 700; 
        background-color: #1e3a8a !important; color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]

def encode_8bit(n):
    try:
        val = int(n); d, u = val // 10, val % 10
        return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
                1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
                1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]
    except: return [0]*8

def calculate_hamming(b1, b2):
    return sum(x != y for x, y in zip(b1, b2))

def get_rank_v24(target, last):
    if last is None or last == -1: return 0
    last_b = encode_8bit(last)
    scores = []
    for i in range(100):
        d = calculate_hamming(last_b, encode_8bit(i))
        w = abs(d - 4)
        if d == 0 and i != int(last): w += 10
        if d in [7, 8]: w += 20
        scores.append({"S": f"{i:02d}", "W": w})
    df = pd.DataFrame(scores).sort_values(["W", "S"])
    df['R'] = range(1, 101)
    res = df[df['S'] == f"{int(target):02d}"]['R'].values
    return int(res[0]) if len(res) > 0 else 100

# --- 3. KHỞI TẠO BỘ NHỚ VĨNH VIỄN ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_n' not in st.session_state:
    st.session_state.last_n = -1

# Tự động tính kỳ nhảy
suggest_ky = 1
if st.session_state.history:
    suggest_ky = max([int(h.get("Kỳ", 0)) for h in st.session_state.history]) + 1

# --- 4. GIAO DIỆN NHẬP LIỆU ---
st.title("🛡️ RHYTHM MASTER V2.4")

with st.expander("📝 CẬP NHẬT KẾT QUẢ", expanded=True):
    c1, c2, c3 = st.columns([1.5, 1, 1.2])
    with c1: num_in = st.text_input("GĐB (2 số):", key="num_box")
    with c2: ky_in = st.number_input("Kỳ:", value=suggest_ky, step=1)
    with c3: day_in = st.text_input("Ngày:", datetime.now().strftime("%d/%m"))
    
    if st.button("🚀 LƯU NHẬT KÝ & NHẢY KỲ"):
        if len(num_in) >= 2:
            target = int(num_in[-2:])
            rank_val = get_rank_v24(target, st.session_state.last_n)
            
            new_entry = {
                "Ngày": day_in, "Kỳ": int(ky_in), "Số": f"{target:02d}", "Rank": int(rank_val)
            }
            st.session_state.history.append(new_entry)
            st.session_state.last_n = target
            st.session_state.history = sorted(st.session_state.history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
            st.rerun()

st.divider()

# --- 5. HIỂN THỊ TABS ---
if st.session_state.history or st.session_state.last_n != -1:
    if st.session_state.last_n == -1 and st.session_state.history:
        st.session_state.last_n = int(st.session_state.history[0].get("Số", 0))

    tab1, tab2 = st.tabs(["🎯 DÀN TINH ANH", "📊 NHẬT KÝ 8 BIẾN"])
    
    with tab1:
        st.write(f"🔢 Gốc nhịp: **{st.session_state.last_n:02d}**")
        
        def generate_dan(n_size, last_n):
            last_b = encode_8bit(last_n)
            res = []
            for i in range(100):
                d = calculate_hamming(last_b, encode_8bit(i))
                w = abs(d - 4)
                if d == 0 and i != last_n: w += 10
                if d in [7, 8]: w += 20
                res.append({"S": f"{i:02d}", "W": w})
            df = pd.DataFrame(res).sort_values(["W", "S"])
            return df.head(n_size)["S"].tolist()

        ca, cb = st.columns(2)
        with ca:
            n1 = st.number_input("Số quân Dàn A:", 1, 100, 50, key="n1_v24")
            st.markdown(f"**DÀN {n1} SỐ:**")
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n1, st.session_state.last_n))}</div>", unsafe_allow_html=True)
        with cb:
            n2 = st.number_input("Số quân Dàn B:", 1, 100, 36, key="n2_v24")
            st.markdown(f"**DÀN {n2} SỐ:**")
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n2, st.session_state.last_n))}</div>", unsafe_allow_html=True)

    with tab2:
        # BẢNG NHẬT KÝ THEO ĐÚNG ẢNH MẪU CỦA MÀY
        disp = []
        for h in st.session_state.history[:50]:
            s_val = h.get("Số", "00")
            b = encode_8bit(s_val)
            disp.append({
                "Kỳ": int(h.get("Kỳ", 0)), 
                "Số": s_val, 
                "R": int(h.get("Rank", 0)),
                "Đ.CL": "L" if b[0] else "C", 
                "Đu.CL": "L" if b[1] else "C", 
                "T.CL": "L" if b[2] else "C",
                "Đ.TB": "T" if b[3] else "B", 
                "Đu.TB": "T" if b[4] else "B", 
                "T.TB": "T" if b[5] else "B",
                "Hệ": "Th" if b[6] else "Kp", 
                "Hi.TB": "T" if b[7] else "B"
            })
        st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)

# --- 6. SIDEBAR QUẢN LÝ ---
with st.sidebar:
    st.header("⚙️ DỮ LIỆU")
    if st.button("🔴 XOÁ SẠCH BỘ NHỚ"):
        st.session_state.history = []
        st.session_state.last_n = -1
        st.rerun()
    
    up_file = st.file_uploader("Nạp file JSON:", type="json")
    if up_file:
        data = json.load(up_file)
        st.session_state.history = data.get("history", [])
        if st.session_state.history:
            st.session_state.history = sorted(st.session_state.history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
            st.session_state.last_n = int(st.session_state.history[0].get("Số", -1))
        st.rerun()
    
    st.divider()
    backup = {"history": st.session_state.history, "last_n": st.session_state.last_n}
    st.download_button("💾 XUẤT BACKUP JSON", json.dumps(backup), "8bit_master_v2.4.json", use_container_width=True)
