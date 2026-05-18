import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. THIẾT LẬP GIAO DIỆN ---
st.set_page_config(page_title="8-BIT MASTER V4.8", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.75rem !important; }
    .dan-box { background-color: #ffffff; border: 2px solid #1e3a8a; border-radius: 8px; padding: 10px; font-family: monospace; font-weight: 700; color: #1e3a8a; text-align: center; font-size: 1rem; }
    .stButton button { width: 100%; border-radius: 5px; height: 45px; font-weight: 700; background-color: #1e3a8a !important; color: white !important; }
    .stMetric { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIC 8-BIT DNA ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]
BIT_LABELS = ["Đ.CL", "Đu.CL", "T.CL", "Đ.TB", "Đu.TB", "T.TB", "Hệ", "Hi.TB"]

def get_8bit(n):
    try:
        val = int(n); d, u = val // 10, val % 10
        return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
                1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
                1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]
    except: return [0]*8

# --- 3. LÕI PHÂN TÍCH (QUÉT 10k & 22k) ---
def analyze_engine(history_bits, current_bits):
    if len(history_bits) < 2: return [0.5]*8
    
    final_probs = np.zeros(8)
    
    # Tầng 1: 1-Bit (10 kỳ) - Trọng số 0.4
    seg10 = history_bits[-11:]
    for i in range(8):
        matches = [seg10[k+1] for k in range(len(seg10)-1) if seg10[k][i] == current_bits[i]]
        if matches: final_probs += np.mean(matches, axis=0) * 0.4
        else: final_probs += 0.5 * 0.4
        
    # Tầng 2: 2-Bit (22 kỳ) - Trọng số 0.6
    seg22 = history_bits[-23:]
    pair_scores = np.zeros(8)
    pair_hits = 0
    for i in range(8):
        for j in range(i+1, 8):
            matches = [seg22[k+1] for k in range(len(seg22)-1) if seg22[k][i] == current_bits[i] and seg22[k][j] == current_bits[j]]
            if matches:
                pair_scores += np.mean(matches, axis=0)
                pair_hits += 1
    
    if pair_hits > 0: final_probs += (pair_scores / pair_hits) * 0.6
    else: final_probs += 0.5 * 0.6
    
    return np.clip(final_probs, 0.05, 0.95).tolist()

# --- 4. QUẢN LÝ TRẠNG THÁI ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

# --- 5. GIAO DIỆN ---
st.title("🛡️ 8-BIT MASTER V4.8 (STABLE)")

with st.sidebar:
    st.header("📂 DỮ LIỆU MASTER")
    uploaded = st.file_uploader("Nạp file .json", type="json")
    if uploaded:
        data = json.load(uploaded)
        raw_hist = data.get("history", [])
        # Làm sạch và sắp xếp: Kỳ cũ nhất ở index 0, mới nhất ở cuối để tính toán
        clean_hist = sorted(raw_hist, key=lambda x: int(x.get("Kỳ", 0)))
        st.session_state.history = clean_hist
        if clean_hist:
            st.session_state.last_n = int(clean_hist[-1]["Số"])
        st.success(f"Đã nạp {len(clean_hist)} kỳ!")

    if st.button("🔴 XOÁ HẾT DỮ LIỆU"):
        st.session_state.history = []
        st.session_state.last_n = -1
        st.rerun()

# Khu vực nhập liệu
with st.container():
    c1, c2, c3 = st.columns([1,1,1])
    num_in = c1.text_input("Số vừa nổ:", placeholder="Ví dụ: 62")
    ky_in = c2.number_input("Kỳ vừa nổ đó là:", value=int(st.session_state.history[-1].get("Kỳ", 0)) + 1 if st.session_state.history else 1)
    
    if st.button("🚀 PHÂN TÍCH & LƯU NHẬT KÝ"):
        if num_in:
            val = int(num_in[-2:])
            
            # 1. Tính Rank cho số vừa nhập dựa trên lịch sử trước đó
            hist_bits = [get_8bit(h["Số"]) for h in st.session_state.history]
            if st.session_state.history:
                last_bits = get_8bit(st.session_state.last_n)
                probs = analyze_engine(hist_bits, last_bits)
                # Tính Rank 1-100
                scores = []
                for i in range(100):
                    b = get_8bit(i)
                    m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
                    scores.append({"S": f"{i:02d}", "M": m})
                df_temp = pd.DataFrame(scores).sort_values("M", ascending=False)
                df_temp['R'] = range(1, 101)
                rank_val = df_temp[df_temp['S'] == f"{val:02d}"]['R'].values[0]
            else:
                rank_val = 0

            # 2. Lưu vào lịch sử
            new_entry = {
                "Ngày": datetime.now().strftime("%d/%m"),
                "Kỳ": int(ky_in),
                "Số": f"{val:02d}",
                "Rank": int(rank_val)
            }
            st.session_state.history.append(new_entry)
            st.session_state.last_n = val
            st.rerun()

# HIỂN THỊ KẾT QUẢ
if st.session_state.history:
    # Lấy nhịp từ số cuối cùng trong danh sách
    hist_bits = [get_8bit(h["Số"]) for h in st.session_state.history]
    current_bits = get_8bit(st.session_state.last_n)
    probs = analyze_engine(hist_bits, current_bits)
    
    # Tính toán dàn
    rank_final = []
    for i in range(100):
        b = get_8bit(i)
        m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        rank_final.append({"S": f"{i:02d}", "M": m})
    df_final = pd.DataFrame(rank_final).sort_values("M", ascending=False)

    tab1, tab2 = st.tabs(["🎯 DÀN TINH ANH", "📊 NHẬT KÝ 11 CỘT"])
    
    with tab1:
        st.write(f"🔢 Số gốc: **{st.session_state.last_n:02d}** | Tổng dữ liệu: **{len(st.session_state.history)} kỳ**")
        # Hiển thị % hội tụ
        ms = st.columns(8)
        for i, (label, p) in enumerate(zip(BIT_LABELS, probs)):
            ms[i].metric(label, f"{int(p*100)}%")
        
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("🔥 Dàn A (50 số)")
            st.markdown(f"<div class='dan-box'>{' '.join(df_final.head(50)['S'].tolist())}</div>", unsafe_allow_html=True)
        with col_b:
            st.subheader("💎 Dàn B (36 số)")
            st.markdown(f"<div class='dan-box'>{' '.join(df_final.head(36)['S'].tolist())}</div>", unsafe_allow_html=True)

    with tab2:
        # Nhật ký 11 cột (Hiển thị mới nhất lên đầu cho dễ nhìn)
        display_hist = []
        for h in reversed(st.session_state.history):
            b = get_8bit(h["Số"])
            display_hist.append({
                "Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h.get("Rank", "-"),
                "Đ.CL": "L" if b[0] else "C", "Đu.CL": "L" if b[1] else "C", "T.CL": "L" if b[2] else "C",
                "Đ.TB": "T" if b[3] else "B", "Đu.TB": "T" if b[4] else "B", "T.TB": "T" if b[5] else "B",
                "Hệ": "Th" if b[6] else "Kp", "Hi.TB": "T" if b[7] else "B"
            })
        st.dataframe(pd.DataFrame(display_hist), use_container_width=True, hide_index=True)

    # Nút Download backup ở cuối
    st.divider()
    backup = {"history": st.session_state.history, "last_n": st.session_state.last_n}
    st.download_button("💾 XUẤT BACKUP JSON", json.dumps(backup), f"8bit_backup_{datetime.now().strftime('%d%m')}.json")
