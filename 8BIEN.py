import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from itertools import combinations

# --- 1. GIAO DIỆN CHUẨN (NỀN TRẮNG - NÚT XANH NAVY) ---
st.set_page_config(page_title="8-BIT COMMANDER V6.2", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { color: #000000 !important; background-color: #ffffff !important; font-size: 0.78rem !important; }
    .stButton button { 
        width: 100%; border-radius: 6px; height: 42px; font-weight: 700; 
        background-color: #000080 !important; color: #ffffff !important;
    }
    .dan-box { 
        background-color: #f1f5f9; border: 2px solid #000080; border-radius: 8px; 
        padding: 10px; font-family: 'Courier New', monospace; font-weight: 700; 
        color: #000080; text-align: center; font-size: 1rem; line-height: 1.6;
    }
    .stMetric { background: #f8f9fa; border: 1px solid #d1d5db; border-radius: 8px; padding: 5px; }
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

def ultimate_engine_v62(history, last_n):
    if len(history) < 5: return [0.5]*8, ["0000"]*8
    all_bits = np.array([get_8bit(h["Số"]) for h in history])
    curr_bits = np.array(get_8bit(last_n))
    final_probs = np.zeros(8); seq_details = []
    
    # Trọng số nhân chuẩn đã kiểm chứng (Sequence 40% - Momentum 30% - Pair 30%)
    for i in range(8):
        # 1. Tầng Sequence 4 kỳ soi kỳ 5
        seg4 = all_bits[-4:, i]; s_str = "".join(map(str, seg4.astype(int)))
        if s_str == "1111": p_seq = 0.82
        elif s_str == "0000": p_seq = 0.18
        elif s_str == "0101": p_seq = 0.85 # Phá nhịp xen kẽ
        elif s_str == "1010": p_seq = 0.15 # Phá nhịp xen kẽ
        elif s_str.count('1') == 3 and s_str[-1] == 1: p_seq = 0.72 # Nhịp 1-3 bệt tiếp
        elif s_str.count('1') == 1 and s_str[-1] == 0: p_seq = 0.28 # Nhịp 1-3 bệt tiếp
        else: p_seq = 0.5
        
        # 2. Tầng Momentum (10 kỳ)
        p_mom = np.mean(all_bits[-10:, i])
        
        # 3. Tầng Pair Lịch sử (22 kỳ)
        p_pair = 0.5
        if len(history) >= 22:
            seg22 = all_bits[-23:]; pm = []
            for j in range(8):
                if i==j: continue
                m = [seg22[k+1, i] for k in range(len(seg22)-1) if seg22[k, i] == curr_bits[i] and seg22[k, j] == curr_bits[j]]
                if m: pm.append(np.mean(m))
            if pm: p_pair = np.mean(pm)
            
        final_probs[i] = (p_seq * 0.40) + (p_mom * 0.30) + (p_pair * 0.30)
        seq_details.append(s_str)
    return np.clip(final_probs, 0.05, 0.95).tolist(), seq_details

# --- 3. QUẢN LÝ APP ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1

st.title("🛡️ 8-BIT COMMANDER V6.2")

with st.sidebar:
    st.header("📂 DỮ LIỆU")
    up = st.file_uploader("Nạp Master JSON:", type="json")
    if up:
        data = json.load(up); raw = data.get("history", [])
        st.session_state.history = sorted([{"Ngày": h.get("Ngày", "00/00"), "Kỳ": int(h.get("Kỳ", 0)), "Số": f"{int(h.get('Số', 0)):02d}", "Rank": h.get("Rank", 0)} for h in raw], key=lambda x: x["Kỳ"])
        if st.session_state.history: st.session_state.last_n = int(st.session_state.history[-1]["Số"])
    if st.button("🔴 RESET"): st.session_state.history = []; st.rerun()

# --- KHU VỰC ĐIỀU KHIỂN TRUNG TÂM ---
with st.container():
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    n_in = c1.text_input("Số vừa nổ:", placeholder="VD: 62")
    ky_in = c2.number_input("Kỳ:", value=st.session_state.history[-1]["Kỳ"] + 1 if st.session_state.history else 1)
    # NÚT LẤY SỐ QUÂN (CHỖ NÀY MÀY CẦN ĐÂY)
    num_quan = c3.number_input("Lấy dàn (số quân):", value=50, step=1)
    
    if st.button("🚀 PHÂN TÍCH HỘI TỤ & LẤY DÀN"):
        if n_in:
            val = int(n_in[-2:])
            if st.session_state.history:
                p, _ = ultimate_engine_v62(st.session_state.history, st.session_state.last_n)
                scr = []
                for i in range(100):
                    b = get_8bit(i); m = sum(b[j]*p[j] + (1-b[j])*(1-p[j]) for j in range(8))
                    scr.append({"S": f"{i:02d}", "M": m})
                df_t = pd.DataFrame(scr).sort_values("M", ascending=False); df_t['R'] = range(1, 101)
                r_v = df_t[df_t['S'] == f"{val:02d}"]['R'].values[0]
            else: r_v = 0
            st.session_state.history.append({"Ngày": datetime.now().strftime("%d/%m"), "Kỳ": int(ky_in), "Số": f"{val:02d}", "Rank": int(r_v)})
            st.session_state.last_n = val; st.rerun()

# --- HIỂN THỊ KẾT QUẢ ---
if st.session_state.history:
    probs, seqs = ultimate_engine_v62(st.session_state.history, st.session_state.last_n)
    res = []
    for i in range(100):
        b = get_8bit(i); m = sum(b[j]*probs[j] + (1-b[j])*(1-probs[j]) for j in range(8))
        res.append({"S": f"{i:02d}", "M": m})
    df_rank = pd.DataFrame(res).sort_values("M", ascending=False)

    tab1, tab2 = st.tabs(["🎯 DÀN TINH ANH TÙY CHỈNH", "📊 NHẬT KÝ 11 CỘT NÉN"])
    
    with tab1:
        st.write(f"🔢 Nhịp gốc: **{st.session_state.last_n:02d}** | Đang lấy dàn: **{num_quan} số quân**")
        ms = st.columns(8)
        for i, (l, p) in enumerate(zip(BIT_LABELS, probs)):
            ms[i].metric(f"{l} ({seqs[i]})", f"{int(p*100)}%")
        
        st.divider()
        st.markdown(f"**🔥 DÀN TINH ANH {num_quan} SỐ (ƯU TIÊN THEO RANK HỘI TỤ)**")
        # Hiển thị đúng số quân mày chọn ở nút nhập liệu
        danh_sach_so = df_rank.head(int(num_quan))['S'].tolist()
        st.markdown(f"<div class='dan-box'>{' '.join(danh_sach_so)}</div>", unsafe_allow_html=True)
        
        st.write(f"💡 *Gợi ý: Dàn {num_quan} số quân này đã được nhân trọng số từ nhịp 4 kỳ {seqs} và momentum 10 kỳ.*")

    with tab2:
        disp = []
        for h in reversed(st.session_state.history):
            b = get_8bit(h["Số"])
            disp.append({"Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"], "Đ": "L" if b[0] else "C", "Đu": "L" if b[1] else "C", "T": "L" if b[2] else "C", "Đ.T": "T" if b[3] else "B", "Đu.T": "T" if b[4] else "B", "T.T": "T" if b[5] else "B", "Hệ": "Th" if b[6] else "Kp", "Hi": "T" if b[7] else "B"})
        st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)

    st.divider()
    st.download_button("💾 XUẤT MASTER BACKUP", json.dumps({"history": st.session_state.history}), f"8bit_v6.2_{datetime.now().strftime('%d%m')}.json")
