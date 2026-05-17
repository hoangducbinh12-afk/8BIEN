import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. CONFIG GIAO DIỆN ---
st.set_page_config(page_title="8-BIT MASTER V3.5", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 0.72rem !important; }
    .dan-box { 
        background-color: #ffffff; border: 1.5px solid #1e3a8a; border-radius: 8px; 
        padding: 8px; margin-bottom: 10px; font-family: monospace; 
        font-weight: 700; color: #1e3a8a; text-align: center; font-size: 0.88rem;
    }
    .stDataFrame td, .stDataFrame th { padding: 1px 2px !important; font-size: 0.65rem !important; text-align: center !important; }
    .stButton button { width: 100%; border-radius: 8px; height: 38px; font-weight: 700; background-color: #1e3a8a !important; color: white !important; }
    .highlight-text { color: #f59e0b; font-weight: bold; }
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

# --- 3. MÁY QUÉT 8 LUỒNG (CHỈ XÉT 10 KỲ GẦN NHẤT) ---
def scan_10_kỳ_ma_trận(history, last_n):
    # ÉP BUỘC: Chỉ lấy 11 dòng cuối để có 10 cặp chuyển đổi
    # (Nếu history ít hơn 11 thì lấy hết)
    history_10 = history[:11] 
    
    if len(history_10) < 2 or last_n == -1:
        return [0.5]*8, []
    
    # Chuyển thành bit và đảo ngược để chạy từ cũ đến mới (cho đúng logic chuyển tiếp)
    bits_list = [get_8bit(h["Số"]) for h in history_10][::-1] 
    current_bits = get_8bit(last_n)
    
    master_scores = [0.0] * 8
    debug_info = []
    
    # Quét 8 luồng điều kiện dựa trên 10 kỳ gần nhất
    for b_idx in range(8):
        state = current_bits[b_idx]
        relevant_next = []
        for i in range(len(bits_list) - 1):
            if bits_list[i][b_idx] == state:
                relevant_next.append(bits_list[i+1])
        
        if relevant_next:
            matrix = np.array(relevant_next)
            ratios = np.mean(matrix, axis=0)
            for j in range(8):
                master_scores[j] += ratios[j]
            
            # Ghi nhật ký giải mã để mày check
            debug_info.append({
                "Bit Gốc": f"B{b_idx+1} ({BIT_LABELS[b_idx]})",
                "Trạng thái": "1 (Lẻ/To/Th)" if state else "0 (Chẵn/Bé/Kp)",
                "Số lần xuất hiện trong 10 kỳ": len(relevant_next),
                "Tỷ lệ 8 Bit kỳ sau": " | ".join([f"{int(r*100)}%" for r in ratios])
            })

    # Tính xác suất hội tụ (Trung bình cộng của 8 luồng)
    final_probs = [s / 8 for s in master_scores]
    return final_probs, debug_info

def get_v35_rank(history, last_n):
    probs, debug = scan_10_kỳ_ma_trận(history, last_n)
    scores = []
    for i in range(100):
        bits = get_8bit(i)
        # Chấm điểm dựa trên xác suất hội tụ (Match Score)
        match_val = sum(bits[j] * probs[j] + (1 - bits[j]) * (1 - probs[j]) for j in range(8))
        scores.append({"S": f"{i:02d}", "Match": match_val})
    
    df = pd.DataFrame(scores).sort_values("Match", ascending=False)
    df['R'] = range(1, 101)
    return df, probs, debug

# --- 4. HỆ THỐNG LƯU TRỮ ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

# --- 5. GIAO DIỆN ---
st.title("🧬 MATRIX SCAN V3.5 (10-KỲ ONLY)")

with st.expander("📝 CẬP NHẬT KỲ MỚI", expanded=True):
    max_k = max([int(h.get("Kỳ", 0)) for h in st.session_state.history]) if st.session_state.history else 0
    c1, c2, c3 = st.columns([1.5, 1, 1.2])
    with c1: num_in = st.text_input("GĐB vừa nổ:", key="n_in")
    with c2: ky_in = st.number_input("Kỳ:", value=max_k + 1, step=1)
    with c3: day_in = st.text_input("Ngày:", datetime.now().strftime("%d/%m"))
    
    if st.button("🚀 LƯU & GIẢI MÃ (QUÉT 10 KỲ)"):
        if len(num_in) >= 2:
            val = int(num_in[-2:])
            df_rank, _, _ = get_v35_rank(st.session_state.history, st.session_state.last_n)
            r_val = df_rank[df_rank['S'] == f"{val:02d}"]['R'].values[0] if not df_rank.empty else 0
            
            st.session_state.history.insert(0, {"Ngày": day_in, "Kỳ": int(ky_in), "Số": f"{val:02d}", "Rank": int(r_val)})
            st.session_state.last_n = val
            st.session_state.history = sorted(st.session_state.history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
            st.rerun()

st.divider()

if st.session_state.history:
    df_rank, probs, debug_info = get_v35_rank(st.session_state.history, st.session_state.last_n)
    t1, t2, t3 = st.tabs(["🎯 DÀN TINH ANH", "📊 NHẬT KÝ", "🔍 GIẢI MÃ 10 KỲ"])
    
    with t1:
        st.write(f"🔢 Gốc nhịp: **{st.session_state.last_n:02d}** (Căn cứ trên 10 kỳ gần nhất)")
        ca, cb = st.columns(2)
        with ca:
            n1 = st.number_input("Dàn A:", 1, 100, 50)
            st.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(n1)['S'].tolist())}</div>", unsafe_allow_html=True)
        with cb:
            n2 = st.number_input("Dàn B:", 1, 100, 36)
            st.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(n2)['S'].tolist())}</div>", unsafe_allow_html=True)

    with t2:
        disp = []
        for h in st.session_state.history[:50]:
            b = get_8bit(h["Số"])
            disp.append({
                "Kỳ": int(h.get("Kỳ")), "Số": h["Số"], "R": int(h.get("Rank", 0)),
                "Đ.CL": "L" if b[0] else "C", "Đu.CL": "L" if b[1] else "C", "T.CL": "L" if b[2] else "C",
                "Đ.TB": "T" if b[3] else "B", "Đu.TB": "T" if b[4] else "B", "T.TB": "T" if b[5] else "B",
                "Hệ": "Th" if b[6] else "Kp", "Hi.TB": "T" if b[7] else "B"
            })
        st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)

    with t3:
        st.info(f"Đang phân tích 8 luồng từ số gốc {st.session_state.last_n:02d} trong 10 kỳ gần nhất.")
        st.table(pd.DataFrame(debug_info))
        
        st.write("📊 **Xác suất hội tụ kỳ sau (Trung bình 8 luồng):**")
        cols = st.columns(4)
        for i, (label, p) in enumerate(zip(BIT_LABELS, probs)):
            cols[i%4].metric(label, f"{int(p*100)}%")

with st.sidebar:
    st.header("⚙️ DỮ LIỆU")
    if st.button("🔴 XOÁ SẠCH"):
        st.session_state.history = []; st.session_state.last_n = -1; st.rerun()
    up = st.file_uploader("Nạp file:", type="json")
    if up:
        data = json.load(up)
        st.session_state.history = data.get("history", [])
        if st.session_state.history:
            st.session_state.history = sorted(st.session_state.history, key=lambda x: int(x.get("Kỳ", 0)), reverse=True)
            st.session_state.last_n = int(st.session_state.history[0]["Số"])
        st.rerun()
    st.download_button("💾 Backup", json.dumps({"history": st.session_state.history, "last_n": st.session_state.last_n}), "8bit_v3.5.json")
