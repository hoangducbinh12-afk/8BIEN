import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. CONFIG GIAO DIỆN MOBILE ---
st.set_page_config(page_title="8-BIT MASTER V2.0", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.75rem !important; }
    .dan-box { 
        background-color: #ffffff; border: 1px solid #fbbf24; border-radius: 8px; 
        padding: 8px; margin-bottom: 10px; font-family: monospace; 
        font-weight: bold; color: #1e293b; text-align: center; font-size: 0.9rem;
    }
    .stDataFrame td { font-size: 0.7rem !important; font-weight: bold !important; }
    .stButton button { width: 100%; border-radius: 10px; height: 38px; font-weight: bold; background-color: #10b981; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC 8 BIẾN ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]

def encode_8bit(n):
    try:
        n = int(n); d, u = n // 10, n % 10
        return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
                1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
                1 if n in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]
    except: return [0]*8

def calculate_hamming(bits1, bits2):
    return sum(b1 != b2 for b1, b2 in zip(bits1, bits2))

def get_rank(target, last):
    if last == -1: return 0
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

# --- 3. CƠ CHẾ LƯU TRỮ VĨNH VIỄN TRÊN SESSION ---
# Khởi tạo một lần duy nhất
if 'master_history' not in st.session_state:
    st.session_state.master_history = []
if 'last_num_v2' not in st.session_state:
    st.session_state.last_num_v2 = -1

# Tính kỳ tự động dựa trên history
next_ky = 1
if st.session_state.master_history:
    next_ky = max([int(h.get("Kỳ", 0)) for h in st.session_state.master_history]) + 1

# --- 4. GIAO DIỆN NHẬP LIỆU ---
st.title("🧬 8-BIT RHYTHM V2.0")

with st.form("nhap_lieu_form", clear_on_submit=True):
    st.write("➕ **NHẬP KẾT QUẢ MỚI**")
    c1, c2, c3 = st.columns([1.5, 1, 1.2])
    with c1: gdb_in = st.text_input("GĐB (Số cuối):", key="gdb")
    with c2: ky_in = st.number_input("Kỳ:", value=next_ky, step=1, key="ky")
    with c3: day_in = st.text_input("Ngày:", datetime.now().strftime("%d/%m"), key="ngay")
    
    submitted = st.form_submit_button("🚀 XÁC NHẬN LƯU")
    
    if submitted:
        if len(gdb_in) >= 2:
            num = int(gdb_in[-2:])
            # Lấy rank dựa trên số cũ nhất trong bộ nhớ
            rank_val = get_rank(num, st.session_state.last_num_v2)
            
            # Đẩy vào history
            st.session_state.master_history.append({
                "Ngày": day_in,
                "Kỳ": int(ky_in),
                "Số": f"{num:02d}",
                "Rank": int(rank_val)
            })
            # Cập nhật số cuối cùng
            st.session_state.last_num_v2 = num
            st.success(f"Đã lưu kỳ {ky_in} thành công!")
            st.rerun()

st.divider()

# --- 5. HIỂN THỊ DÀN VÀ NHẬT KÝ ---
history = sorted(st.session_state.master_history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)

if st.session_state.last_num_v2 != -1 or history:
    # Đồng bộ lại last_num nếu mới nạp file
    if st.session_state.last_num_v2 == -1 and history:
        st.session_state.last_num_v2 = int(history[0]["Số"])

    t1, t2 = st.tabs(["🎯 DÀN AI", "📊 NHẬT KÝ 8 BIẾN"])
    
    with t1:
        st.write(f"🔢 Nhịp từ số: **{st.session_state.last_num_v2:02d}**")
        
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
            n1 = st.number_input("Dàn 50s:", 1, 100, 50)
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n1, st.session_state.last_num_v2))}</div>", unsafe_allow_html=True)
        with cb:
            n2 = st.number_input("Dàn 36s:", 1, 100, 36)
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n2, st.session_state.last_num_v2))}</div>", unsafe_allow_html=True)

    with t2:
        if history:
            disp = []
            for h in history[:30]:
                b = encode_8bit(h["Số"])
                disp.append({
                    "Kỳ": int(h["Kỳ"]), "Số": h["Số"], "Rank": int(h["Rank"]),
                    "Đ.Lẻ": "L" if b[0] else "C", "Đu.Lẻ": "L" if b[1] else "C", "T.Lẻ": "L" if b[2] else "C",
                    "Đ.To": "T" if b[3] else "B", "Đu.To": "T" if b[4] else "B", "T.To": "T" if b[5] else "B",
                    "Hệ": "Th" if b[6] else "Kp", "Hi.T": "T" if b[7] else "B"
                })
            # Hiển thị bảng dạng DataFrame để thu nhỏ cột tự động
            st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)

# --- 6. SIDEBAR QUẢN LÝ ---
with st.sidebar:
    st.header("⚙️ DỮ LIỆU")
    if st.button("🔴 XOÁ SẠCH BỘ NHỚ"):
        st.session_state.master_history = []
        st.session_state.last_num_v2 = -1
        st.rerun()
    
    up = st.file_uploader("Nạp file dữ liệu:", type="json")
    if up:
        data = json.load(up)
        # Ép trộn dữ liệu (Merge) chứ không chỉ gán đè
        st.session_state.master_history = data.get("history", [])
        st.session_state.last_num_v2 = data.get("last_n", -1)
        st.success("Đã nạp file thành công!")
        st.rerun()
    
    backup = {"history": st.session_state.master_history, "last_n": st.session_state.last_num_v2}
    st.download_button("💾 TẢI BACKUP", json.dumps(backup), "8bit_master_v2.json")
