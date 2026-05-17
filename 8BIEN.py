import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. CONFIG GIAO DIỆN SIÊU NHỎ CHO MOBILE ---
st.set_page_config(page_title="8-BIT MASTER V1.9", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.72rem !important; }
    .dan-box { 
        background-color: #ffffff; border: 1px solid #fbbf24; border-radius: 8px; 
        padding: 5px; margin-bottom: 5px; font-family: monospace; 
        font-weight: bold; color: #1e293b; text-align: center; font-size: 0.8rem;
    }
    .stTable td, .stTable th { 
        padding: 1px !important; 
        font-size: 0.62rem !important; 
        text-align: center !important;
        white-space: nowrap !important;
    }
    .stButton button { width: 100%; border-radius: 8px; height: 35px; font-weight: bold; background-color: #3b82f6; color: white; }
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

# --- 3. KHỞI TẠO BỘ NHỚ VĨNH VIỄN (PERSISTENT MEMORY) ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_n' not in st.session_state:
    st.session_state.last_n = -1

# Tự động tính kỳ tiếp theo dựa trên bộ nhớ
next_ky = 1
if st.session_state.history:
    next_ky = max([int(h.get("Kỳ", 0)) for h in st.session_state.history]) + 1

# --- 4. GIAO DIỆN NHẬP LIỆU ---
st.title("🧬 8-BIT RHYTHM V1.9")

with st.expander("➕ CẬP NHẬT KỲ MỚI", expanded=True):
    c1, c2, c3 = st.columns([1.5, 1, 1.2])
    with c1: gdb_in = st.text_input("Số cuối:", key="num_box")
    with c2: ky_in = st.number_input("Kỳ:", value=next_ky, step=1)
    with c3: day_in = st.text_input("Ngày:", datetime.now().strftime("%d/%m"))
    
    if st.button("🚀 XÁC NHẬN LƯU KẾT QUẢ"):
        if len(gdb_in) >= 2:
            num = int(gdb_in[-2:])
            # Tính Rank dựa trên mốc cũ trước khi cập nhật
            rank_val = get_rank(num, st.session_state.last_n)
            
            # Tạo bản ghi mới
            new_item = {
                "Ngày": str(day_in), 
                "Kỳ": int(ky_in), 
                "Số": f"{num:02d}", 
                "Rank": int(rank_val)
            }
            
            # Cập nhật vào kho lưu trữ bền vững
            st.session_state.history.append(new_item)
            st.session_state.last_n = num
            
            # Sắp xếp lại lịch sử
            st.session_state.history = sorted(st.session_state.history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
            
            # Thông báo và ép làm mới trang để lưu dữ liệu
            st.success(f"Đã lưu kỳ {ky_in}")
            st.rerun()

st.divider()

# --- 5. HIỂN THỊ DÀN VÀ NHẬT KÝ ---
if st.session_state.last_n != -1 or st.session_state.history:
    # Nếu nạp file lần đầu, cập nhật lại last_n từ kỳ mới nhất
    if st.session_state.last_n == -1 and st.session_state.history:
        st.session_state.last_n = int(st.session_state.history[0]["Số"])

    tab1, tab2 = st.tabs(["🎯 LẤY DÀN AI", "📊 NHẬT KÝ 8 CỘT"])
    
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

        c_a, c_b = st.columns(2)
        with c_a:
            n1 = st.number_input("Số quân Dàn A:", 1, 100, 50, key="n1_size")
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n1, st.session_state.last_n))}</div>", unsafe_allow_html=True)
        with c_b:
            n2 = st.number_input("Số quân Dàn B:", 1, 100, 36, key="n2_size")
            st.markdown(f"<div class='dan-box'>{' '.join(generate_dan(n2, st.session_state.last_n))}</div>", unsafe_allow_html=True)

    with tab2:
        if st.session_state.history:
            disp_data = []
            for h in st.session_state.history[:35]:
                b = encode_8bit(h["Số"])
                disp_data.append({
                    "Kỳ": int(h.get("Kỳ", 0)),
                    "Số": h["Số"],
                    "R": int(h.get("Rank", 0)),
                    "ĐL": "L" if b[0] else "C",
                    "ĐuL": "L" if b[1] else "C",
                    "TL": "L" if b[2] else "C",
                    "ĐT": "T" if b[3] else "B",
                    "UT": "T" if b[4] else "B",
                    "TT": "T" if b[5] else "B",
                    "Hệ": "Th" if b[6] else "Kp",
                    "HiT": "T" if b[7] else "B"
                })
            # Hiển thị bảng nhật ký đầy đủ 8 biến
            st.table(pd.DataFrame(disp_data))

# --- 6. SIDEBAR QUẢN LÝ ---
with st.sidebar:
    st.header("⚙️ DỮ LIỆU")
    if st.button("🔴 RESET TOÀN BỘ"):
        st.session_state.history = []
        st.session_state.last_n = -1
        st.rerun()
    
    st.divider()
    up_file = st.file_uploader("Nạp file JSON:", type="json")
    if up_file:
        raw_data = json.load(up_file)
        # Ép dữ liệu vào bộ nhớ bền vững
        st.session_state.history = raw_data.get("history", [])
        st.session_state.last_n = raw_data.get("last_n", -1)
        st.success("Đã nạp lịch sử!")
        st.rerun()
    
    st.divider()
    # Xuất file backup dựa trên bộ nhớ hiện tại
    backup_data = {"history": st.session_state.history, "last_n": st.session_state.last_n}
    st.download_button("💾 XUẤT BACKUP", json.dumps(backup_data), "8bit_data_v1.9.json")
