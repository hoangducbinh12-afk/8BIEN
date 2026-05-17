import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. CONFIG GIAO DIỆN & CSS SIÊU NHỎ ---
st.set_page_config(page_title="8-BIT RHYTHM MASTER V2.2", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.72rem !important; }
    .dan-box { 
        background-color: #ffffff; border: 1px solid #10b981; border-radius: 6px; 
        padding: 6px; margin-bottom: 5px; font-family: monospace; 
        font-weight: bold; color: #064e3b; text-align: center; font-size: 0.85rem;
    }
    .stDataFrame { border: 1px solid #e2e8f0; }
    .stButton button { width: 100%; border-radius: 6px; height: 35px; font-weight: bold; background-color: #10b981; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIC TOÁN HỌC ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]

def encode_8bit(n):
    try:
        val = int(n)
        d, u = val // 10, val % 10
        return [
            1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
            1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
            1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0
        ]
    except: return [0]*8

def calculate_hamming(b1, b2):
    return sum(x != y for x, y in zip(b1, b2))

def get_rank_v2(target, last):
    if last is None or last == -1: return 0
    last_b = encode_8bit(last)
    scores = []
    for i in range(100):
        d = calculate_hamming(last_b, encode_8bit(i))
        w = abs(d - 4)
        if d == 0 and i != int(last): w += 10
        if d in [7, 8]: w += 20
        # FIX: Không dùng toán tử Walrus (:=) ở đây
        scores.append({"S": f"{i:02d}", "W": w})
    
    df = pd.DataFrame(scores).sort_values(["W", "S"])
    df['R'] = range(1, 101)
    res = df[df['S'] == f"{int(target):02d}"]['R'].values
    return int(res[0]) if len(res) > 0 else 100

# --- 3. CƠ CHẾ LƯU TRỮ VỮNG CHẮC ---
# Khởi tạo session state nếu chưa có
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_n' not in st.session_state:
    st.session_state.last_n = -1

# --- 4. NHẬP LIỆU ---
st.title("🛡️ RHYTHM MASTER V2.2")

with st.expander("📝 CẬP NHẬT KẾT QUẢ", expanded=True):
    # Tính kỳ tiếp theo từ history hiện có
    if st.session_state.history:
        suggest_ky = max([int(h.get("Kỳ", 0)) for h in st.session_state.history]) + 1
    else:
        suggest_ky = 1
        
    c1, c2, c3 = st.columns([1.5, 1, 1.2])
    with c1: num_in = st.text_input("GĐB (2 số cuối):", key="input_so")
    with c2: ky_in = st.number_input("Kỳ:", value=suggest_ky, step=1, key="input_ky")
    with c3: day_in = st.text_input("Ngày:", datetime.now().strftime("%d/%m"), key="input_ngay")
    
    if st.button("🚀 LƯU VÀO NHẬT KÝ"):
        if len(num_in) >= 2:
            target = int(num_in[-2:])
            # Tính rank dựa trên last_n cũ
            rank_val = get_rank_v2(target, st.session_state.last_n)
            
            new_entry = {
                "Ngày": str(day_in),
                "Kỳ": int(ky_in),
                "Số": f"{target:02d}",
                "Rank": int(rank_val)
            }
            # Ghi vào session state
            st.session_state.history.append(new_entry)
            st.session_state.last_n = target
            # Sắp xếp lại
            st.session_state.history = sorted(st.session_state.history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
            st.rerun()

st.divider()

# --- 5. HIỂN THỊ ---
if st.session_state.history:
    # Nếu vừa load file, lấy last_n từ kỳ mới nhất
    if st.session_state.last_n == -1:
        st.session_state.history = sorted(st.session_state.history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
        st.session_state.last_n = int(st.session_state.history[0].get("Số", 0))

    tab1, tab2 = st.tabs(["🎯 LẤY DÀN AI", "📊 NHẬT KÝ 8 BIẾN"])
    
    with tab1:
        st.write(f"🔢 Nhịp từ số: **{st.session_state.last_n:02d}**")
        
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
            n1 = st.number_input("Dàn A (Quân):", 1, 100, 50, key="n1_v22")
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n1, st.session_state.last_n))}</div>", unsafe_allow_html=True)
        with cb:
            n2 = st.number_input("Dàn B (Quân):", 1, 100, 36, key="n2_v22")
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n2, st.session_state.last_n))}</div>", unsafe_allow_html=True)

    with tab2:
        disp = []
        for h in st.session_state.history:
            s_val = h.get("Số", "00")
            b = encode_8bit(s_val)
            disp.append({
                "Kỳ": int(h.get("Kỳ", 0)),
                "Số": s_val,
                "R": int(h.get("Rank", 0)),
                "Đ.L": "L" if b[0] else "C",
                "Đu.L": "L" if b[1] else "C",
                "T.L": "L" if b[2] else "C",
                "Đ.T": "T" if b[3] else "B",
                "Đu.T": "T" if b[4] else "B",
                "T.T": "T" if b[5] else "B",
                "Hệ": "Th" if b[6] else "Kp",
                "Hi.T": "T" if b[7] else "B"
            })
        st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)

# --- 6. SIDEBAR QUẢN LÝ ---
with st.sidebar:
    st.header("⚙️ DATA")
    if st.button("🔴 XOÁ SẠCH BỘ NHỚ"):
        st.session_state.history = []
        st.session_state.last_n = -1
        st.rerun()
    
    up_f = st.file_uploader("Nạp file JSON:", type="json")
    if up_f:
        data = json.load(up_f)
        st.session_state.history = data.get("history", [])
        if st.session_state.history:
            st.session_state.history = sorted(st.session_state.history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
            st.session_state.last_n = int(st.session_state.history[0].get("Số", -1))
        st.rerun()
    
    st.divider()
    backup = {"history": st.session_state.history, "last_n": st.session_state.last_n}
    st.download_button("💾 XUẤT BACKUP JSON", json.dumps(backup), "8bit_master_v22.json", use_container_width=True)
