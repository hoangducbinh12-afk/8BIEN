import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. THIẾT LẬP GIAO DIỆN & CSS CHUYÊN NGHIỆP ---
st.set_page_config(page_title="8-BIT MASTER V3.0", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.72rem !important; color: #1e293b; }
    .dan-box { 
        background-color: #ffffff; border: 1.5px solid #1e3a8a; border-radius: 8px; 
        padding: 8px; margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; 
        font-weight: 700; color: #1e3a8a; text-align: center; font-size: 0.88rem;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .stDataFrame { border: 1px solid #cbd5e1; border-radius: 8px; }
    .stButton button { 
        width: 100%; border-radius: 8px; height: 38px; font-weight: 700; 
        background-color: #1e3a8a !important; color: white !important;
        border: none !important;
    }
    .stButton button:hover { background-color: #3b82f6 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HÀM MÃ HÓA & LOGIC TOÁN HỌC ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]

def get_8bit(n):
    try:
        val = int(n); d, u = val // 10, val % 10
        return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
                1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
                1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]
    except: return [0]*8

def hamming_dist(b1, b2):
    return sum(x != y for x, y in zip(b1, b2))

def calculate_rank(target, last_n):
    if last_n == -1: return 0
    last_b = get_8bit(last_n)
    scores = []
    for i in range(100):
        d = hamming_dist(last_b, get_8bit(i))
        w = abs(d - 4)
        if d == 0 and i != int(last_n): w += 10
        if d in [7, 8]: w += 20
        scores.append({"S": f"{i:02d}", "W": w})
    df = pd.DataFrame(scores).sort_values(["W", "S"])
    df['R'] = range(1, 101)
    res = df[df['S'] == f"{int(target):02d}"]['R'].values
    return int(res[0]) if len(res) > 0 else 100

# --- 3. HỆ THỐNG LƯU TRỮ TRUNG TÂM (CORE STORAGE) ---
if 'db_history' not in st.session_state:
    st.session_state.db_history = []
if 'db_last_n' not in st.session_state:
    st.session_state.db_last_n = -1

# Tự động đồng bộ số kỳ nhảy
max_ky = 0
if st.session_state.db_history:
    max_ky = max([int(h.get("Kỳ", 0)) for h in st.session_state.db_history])
    if st.session_state.db_last_n == -1:
        # Sắp xếp để lấy số mới nhất
        temp_hist = sorted(st.session_state.db_history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
        st.session_state.db_last_n = int(temp_hist[0].get("Số", -1))

# --- 4. GIAO DIỆN NHẬP LIỆU ---
st.title("🛡️ 8-BIT ARCHITECT V3.0")

with st.expander("📝 CẬP NHẬT KẾT QUẢ MỚI", expanded=True):
    c1, c2, c3 = st.columns([1.5, 1, 1.2])
    with c1: num_in = st.text_input("GĐB (2 số cuối):", key="n_in")
    with c2: ky_in = st.number_input("Kỳ:", value=max_ky + 1, step=1)
    with c3: day_in = st.text_input("Ngày:", datetime.now().strftime("%d/%m"))
    
    if st.button("🚀 LƯU VÀO HỆ THỐNG"):
        if len(num_in) >= 2:
            val = int(num_in[-2:])
            r_val = calculate_rank(val, st.session_state.db_last_n)
            
            # Ghi đè hoặc thêm mới dựa trên Kỳ
            new_item = {"Ngày": day_in, "Kỳ": int(ky_in), "Số": f"{val:02d}", "Rank": int(r_val)}
            
            # Kiểm tra xem kỳ này đã tồn tại chưa để tránh trùng
            exists = False
            for i, h in enumerate(st.session_state.db_history):
                if int(h.get("Kỳ")) == int(ky_in):
                    st.session_state.db_history[i] = new_item
                    exists = True
                    break
            if not exists:
                st.session_state.db_history.append(new_item)
            
            st.session_state.db_last_n = val
            st.success(f"Đã cập nhật Kỳ {ky_in}")
            st.rerun()

st.divider()

# --- 5. TABS HIỂN THỊ ---
if st.session_state.db_history:
    tab1, tab2 = st.tabs(["🎯 LẤY DÀN TINH ANH", "📊 NHẬT KÝ 11 CỘT"])
    
    with tab1:
        st.write(f"🔢 Nhịp đang xét từ số: **{st.session_state.db_last_n:02d}**")
        
        def gen_dan(size, last):
            lb = get_8bit(last)
            res = []
            for i in range(100):
                d = hamming_dist(lb, get_8bit(i))
                w = abs(d - 4)
                if d == 0 and i != last: w += 10
                if d in [7, 8]: w += 20
                res.append({"S": f"{i:02d}", "W": w})
            return pd.DataFrame(res).sort_values(["W", "S"]).head(size)["S"].tolist()

        c_a, c_b = st.columns(2)
        with c_a:
            n1 = st.number_input("Số lượng Dàn A:", 1, 100, 50, key="n1")
            st.markdown(f"<div class='dan-box'>{' '.join(gen_dan(n1, st.session_state.db_last_n))}</div>", unsafe_allow_html=True)
        with c_b:
            n2 = st.number_input("Số lượng Dàn B:", 1, 100, 36, key="n2")
            st.markdown(f"<div class='dan-box'>{' '.join(gen_dan(n2, st.session_state.db_last_n))}</div>", unsafe_allow_html=True)

    with tab2:
        # Xây dựng bảng 11 cột y hệt ảnh mẫu
        history_sorted = sorted(st.session_state.db_history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
        disp = []
        for h in history_sorted[:50]:
            b = get_8bit(h["Số"])
            disp.append({
                "Kỳ": int(h.get("Kỳ")), "Số": h.get("Số"), "R": int(h.get("Rank", 0)),
                "Đ.CL": "L" if b[0] else "C", "Đu.CL": "L" if b[1] else "C", "T.CL": "L" if b[2] else "C",
                "Đ.TB": "T" if b[3] else "B", "Đu.TB": "T" if b[4] else "B", "T.TB": "T" if b[5] else "B",
                "Hệ": "Th" if b[6] else "Kp", "Hi.TB": "T" if b[7] else "B"
            })
        st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ HỆ THỐNG")
    if st.button("🔴 RESET DỮ LIỆU"):
        st.session_state.db_history = []
        st.session_state.db_last_n = -1
        st.rerun()
    
    up = st.file_uploader("Nạp file dữ liệu:", type="json")
    if up:
        data = json.load(up)
        # Ép dữ liệu vào session
        st.session_state.db_history = data.get("history", [])
        st.session_state.db_last_n = int(data.get("last_n", -1))
        st.success("Đã nạp file!")
        st.rerun()
    
    st.divider()
    bk = {"history": st.session_state.db_history, "last_n": st.session_state.db_last_n}
    st.download_button("💾 backup_v3.json", json.dumps(bk), "8bit_master_v3.json", use_container_width=True)
