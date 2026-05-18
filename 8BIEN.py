import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. THIẾT LẬP GIAO DIỆN CHUYÊN NGHIỆP ---
st.set_page_config(page_title="8-BIT QUANTUM V4.9", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.72rem !important; color: #1e293b; }
    .dan-box { 
        background-color: #ffffff; border: 2px solid #1e3a8a; border-radius: 8px; 
        padding: 10px; font-family: 'JetBrains Mono', monospace; 
        font-weight: 700; color: #1e3a8a; text-align: center; font-size: 1rem;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .stButton button { 
        width: 100%; border-radius: 6px; height: 42px; font-weight: 700; 
        background-color: #1e3a8a !important; color: white !important;
    }
    .status-ok { color: #10b981; font-weight: bold; }
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

# --- 3. BỘ NÃO QUANTUM (PHÂN TÍCH 10k & 22k) ---
def quantum_analyze(history_list, last_n):
    if len(history_list) < 2: return [0.5]*8
    
    # Ép dữ liệu về dạng bit (Mảng Numpy để tính siêu tốc)
    bits_data = np.array([get_8bit(h["Số"]) for h in history_list]) # index cuối là số mới nhất
    current_bits = np.array(get_8bit(last_n))
    
    final_probs = np.zeros(8)
    
    # Tầng 1: 1-Bit (10 kỳ) - Trọng số 0.4
    seg10 = bits_data[-11:]
    if len(seg10) > 1:
        for i in range(8):
            matches = [seg10[k+1] for k in range(len(seg10)-1) if seg10[k][i] == current_bits[i]]
            if matches: final_probs += np.mean(matches, axis=0) * 0.4
            else: final_probs += 0.5 * 0.4

    # Tầng 2: 2-Bit (22 kỳ) - Trọng số 0.6
    seg22 = bits_data[-23:]
    if len(seg22) > 1:
        p_scores = np.zeros(8); hits = 0
        for i in range(8):
            for j in range(i+1, 8):
                matches = [seg22[k+1] for k in range(len(seg22)-1) if seg22[k][i] == current_bits[i] and seg22[k][j] == current_bits[j]]
                if matches: p_scores += np.mean(matches, axis=0); hits += 1
        if hits > 0: final_probs += (p_scores / hits) * 0.6
        else: final_probs += 0.5 * 0.6
    
    return np.clip(final_probs, 0.05, 0.95).tolist()

# --- 4. KHỞI TẠO BỘ NHỚ ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

# --- 5. GIAO DIỆN CHÍNH ---
st.title("🛡️ 8-BIT MASTER V4.9 (UNBREAKABLE)")

with st.sidebar:
    st.header("📂 HỆ THỐNG DỮ LIỆU")
    up = st.file_uploader("Nạp file Master (.json):", type="json")
    if up:
        try:
            data = json.load(up)
            raw = data.get("history", []) if isinstance(data, dict) else data
            # Làm sạch dữ liệu: Ép kiểu Số và Kỳ về Int
            st.session_state.history = sorted([
                {"Ngày": h.get("Ngày", "00/00"), "Kỳ": int(h.get("Kỳ", 0)), 
                 "Số": f"{int(h.get('Số', 0)):02d}", "Rank": int(h.get("Rank", 0))} 
                for h in raw
            ], key=lambda x: x["Kỳ"])
            if st.session_state.history:
                st.session_state.last_n = int(st.session_state.history[-1]["Số"])
            st.success(f"Đã nạp {len(st.session_state.history)} kỳ!")
        except:
            st.error("Lỗi định dạng file! Hãy kiểm tra lại.")
    
    st.divider()
    if st.button("🔴 RESET TOÀN BỘ"):
        st.session_state.history = []; st.session_state.last_n = -1; st.rerun()

# NHẬP LIỆU
with st.container():
    c1, c2, c3 = st.columns([1, 1, 1])
    n_in = c1.text_input("Số vừa nổ (GĐB):", placeholder="Ví dụ: 62")
    
    # Tự động nhảy số Kỳ
    next_ky = st.session_state.history[-1]["Kỳ"] + 1 if st.session_state.history else 1
    k_in = c2.number_input("Kỳ vừa nổ đó là:", value=next_ky, step=1)
    
    if st.button("🚀 PHÂN TÍCH & LƯU"):
        if n_in:
            val = int(n_in[-2:])
            # Tính Rank dựa trên dữ liệu hiện tại TRƯỚC KHI lưu số mới
            if st.session_state.history:
                probs = quantum_analyze(st.session_state.history, st.session_state.last_n)
                scores = []
                for i in range(100):
                    b = get_8bit(i)
                    m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
                    scores.append({"S": f"{i:02d}", "M": m})
                df_tmp = pd.DataFrame(scores).sort_values("M", ascending=False)
                df_tmp['R'] = range(1, 101)
                r_val = df_tmp[df_tmp['S'] == f"{val:02d}"]['R'].values[0]
            else: r_val = 0
            
            # Thêm vào lịch sử (Luôn thêm vào cuối)
            st.session_state.history.append({
                "Ngày": datetime.now().strftime("%d/%m"), "Kỳ": int(k_in), 
                "Số": f"{val:02d}", "Rank": int(r_val)
            })
            st.session_state.last_n = val
            st.rerun()

# HIỂN THỊ KẾT QUẢ PHÂN TÍCH
if st.session_state.history:
    # Lấy nhịp từ số cuối cùng
    probs = quantum_analyze(st.session_state.history, st.session_state.last_n)
    
    # Tính Rank cho kỳ tiếp theo
    res_list = []
    for i in range(100):
        b = get_8bit(i)
        m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        res_list.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(res_list).sort_values("M", ascending=False)

    t1, t2 = st.tabs(["🎯 DÀN TINH ANH", "📊 NHẬT KÝ 11 CỘT"])
    
    with t1:
        st.write(f"🔢 Nhịp từ số: **{st.session_state.last_n:02d}** (Kỳ {st.session_state.history[-1]['Kỳ']})")
        # Hiển thị % hội tụ cho 8 bit
        cols = st.columns(8)
        for i, (label, p) in enumerate(zip(BIT_LABELS, probs)):
            cols[i].metric(label, f"{int(p*100)}%")
        
        st.divider()
        da, db = st.columns(2)
        da.subheader("🔥 Dàn A (50 số)")
        da.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(50)['S'].tolist())}</div>", unsafe_allow_html=True)
        db.subheader("💎 Dàn B (36 số)")
        db.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(36)['S'].tolist())}</div>", unsafe_allow_html=True)

    with t2:
        # Nhật ký: Đảo ngược danh sách để kỳ mới nhất lên đầu
        display_data = []
        for h in reversed(st.session_state.history):
            b = get_8bit(h["Số"])
            display_data.append({
                "Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"],
                "Đ.CL": "L" if b[0] else "C", "Đu.CL": "L" if b[1] else "C", "T.CL": "L" if b[2] else "C",
                "Đ.TB": "T" if b[3] else "B", "Đu.TB": "T" if b[4] else "B", "T.TB": "T" if b[5] else "B",
                "Hệ": "Th" if b[6] else "Kp", "Hi.TB": "T" if b[7] else "B"
            })
        st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)

    # Backup
    st.divider()
    st.download_button("💾 XUẤT MASTER BACKUP", json.dumps({"history": st.session_state.history}), f"8bit_master_{datetime.now().strftime('%d%m')}.json")
