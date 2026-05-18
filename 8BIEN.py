import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. GIAO DIỆN V7.8 (GIỮ NGUYÊN GIAO DIỆN V7.7) ---
st.set_page_config(page_title="8-BIT QUANTUM V7.8", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { color: #000000 !important; background-color: #ffffff !important; font-size: 0.72rem !important; }
    .stButton button { 
        width: 100%; border-radius: 4px; height: 38px; font-weight: 700; 
        background-color: #000080 !important; color: #ffffff !important;
    }
    div[data-testid="stTextInput"] input {
        font-size: 1.6rem !important; font-weight: bold !important;
        color: #ff0000 !important; text-align: center;
    }
    .dan-box { 
        background-color: #f1f5f9; border: 1px solid #000080; border-radius: 5px; 
        padding: 8px; font-family: monospace; font-weight: 700; color: #000080; text-align: center; font-size: 1rem;
    }
    .bit-card {
        background-color: #ffffff; border: 1px solid #d1d5db; border-radius: 5px;
        padding: 4px; margin-bottom: 2px; line-height: 1.1;
    }
    .bit-header { background: #000080; color: white; text-align: center; font-weight: bold; border-radius: 3px; margin-bottom: 2px; }
    .sample-low { color: #94a3b8; font-style: italic; font-size: 0.62rem; }
    .sample-ok { color: #10b981; font-weight: bold; font-size: 0.62rem; }
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

def analyze_v78(history, last_n):
    if len(history) < 5: return None
    all_bits = np.array([get_8bit(h["Số"]) for h in history])
    curr_bits = np.array(get_8bit(last_n))
    results = []
    MIN_SAMPLE = 10 
    for i in range(8):
        s3 = "".join(map(str, all_bits[-3:, i].astype(int)))
        m3 = [all_bits[k+3, i] for k in range(len(all_bits)-4) if "".join(map(str, all_bits[k:k+3, i].astype(int))) == s3]
        p3 = np.mean(m3) if len(m3) >= MIN_SAMPLE else 0.5
        s4 = "".join(map(str, all_bits[-4:, i].astype(int)))
        m4 = [all_bits[k+4, i] for k in range(len(all_bits)-5) if "".join(map(str, all_bits[k:k+4, i].astype(int))) == s4]
        p4 = np.mean(m4) if len(m4) >= MIN_SAMPLE else 0.5
        p_mom = np.mean(all_bits[-10:, i])
        pm_pair = []
        if len(history) >= 22:
            seg22 = all_bits[-23:]
            for j in range(8):
                if i == j: continue
                m = [seg22[k+1, i] for k in range(len(seg22)-1) if seg22[k, i] == curr_bits[i] and seg22[k, j] == curr_bits[j]]
                pm_pair.extend(m)
        p_pair = np.mean(pm_pair) if len(pm_pair) >= MIN_SAMPLE else 0.5
        f_prob = (p4 * 0.40) + (p3 * 0.20) + (p_mom * 0.25) + (p_pair * 0.15)
        results.append({"l": BIT_LABELS[i], "s3": s3, "c3": len(m3), "p3": p3, "s4": s4, "c4": len(m4), "p4": p4, "p_mom": p_mom, "c_pair": len(pm_pair), "p_pair": p_pair, "f": f_prob})
    return results

# --- 3. KHỞI TẠO BỘ NHỚ ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1
if 'num_quan' not in st.session_state: st.session_state.num_quan = 50
if 'next_ky' not in st.session_state: st.session_state.next_ky = 1
if 'last_up' not in st.session_state: st.session_state.last_up = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("📂 HỆ THỐNG")
    up = st.file_uploader("Nạp Master JSON:", type="json")
    if up is not None and up != st.session_state.last_up:
        data = json.load(up); raw = data.get("history", [])
        st.session_state.history = sorted([{"Kỳ": int(h.get("Kỳ", 0)), "Số": f"{int(h.get('Số', 0)):02d}", "Rank": int(h.get("Rank", 0))} for h in raw], key=lambda x: x["Kỳ"])
        if st.session_state.history:
            st.session_state.last_n = int(st.session_state.history[-1]["Số"])
            st.session_state.next_ky = int(st.session_state.history[-1]["Kỳ"]) + 1
        st.session_state.last_up = up; st.rerun()
    if st.button("🔴 RESET"):
        st.session_state.history = []; st.session_state.last_n = -1; st.session_state.next_ky = 1; st.session_state.last_up = None; st.rerun()
    if st.session_state.history:
        st.download_button("💾 XUẤT BACKUP", json.dumps({"history": st.session_state.history}), f"8bit_v7.8.json")

# --- 5. NHẬP LIỆU & TỰ ĐỘNG NHẢY KỲ (FIXED) ---
st.title("🛡️ 8-BIT QUANTUM V7.8")
with st.container():
    c1, c2, c3, c4 = st.columns([1.5, 1, 1.5, 2])
    n_in = c1.text_input("Số vừa nổ:", placeholder="75", key="in_so_78")
    
    # SỬA LỖI NHẢY KỲ: Dùng session_state trực tiếp không thông qua widget key tĩnh
    ky_in = c2.number_input("Kỳ:", value=st.session_state.next_ky, step=1)
    
    if c3.button("🚀 PHÂN TÍCH & LƯU"):
        if n_in:
            val = int(n_in[-2:]); r_v = 0
            if st.session_state.history:
                res_temp = analyze_v78(st.session_state.history, st.session_state.last_n)
                if res_temp:
                    p_t = [r["f"] for r in res_temp]
                    scr = [{"S": f"{i:02d}", "M": sum(get_8bit(i)[j]*p_t[j] + (1-get_8bit(i)[j])*(1-p_t[j]) for j in range(8))} for i in range(100)]
                    df_t = pd.DataFrame(scr).sort_values("M", ascending=False); df_t['R'] = range(1, 101)
                    r_v = df_t[df_t['S'] == f"{val:02d}"]['R'].values[0]
            
            # Cập nhật lịch sử
            st.session_state.history.append({"Kỳ": int(ky_in), "Số": f"{val:02d}", "Rank": int(r_v)})
            st.session_state.last_n = val
            # Cập nhật Kỳ tiếp theo vào bộ nhớ
            st.session_state.next_ky = int(ky_in) + 1
            # Ép App chạy lại để nhận giá trị next_ky mới cho ô number_input
            st.rerun()

# --- 6. HIỂN THỊ ---
if st.session_state.history:
    results = analyze_v78(st.session_state.history, st.session_state.last_n)
    tab1, tab2 = st.tabs(["🎯 DÀN TINH ANH & PHÂN TÍCH AI", "📊 NHẬT KÝ ĐẦY ĐỦ"])
    
    with tab1:
        if results:
            probs = [r["f"] for r in results]
            res_rank = [{"S": f"{i:02d}", "M": sum(get_8bit(i)[j]*probs[j] + (1-get_8bit(i)[j])*(1-probs[j]) for j in range(8))} for i in range(100)]
            df_rank = pd.DataFrame(res_rank).sort_values("M", ascending=False)
            cols = st.columns(8)
            for i, r in enumerate(results):
                with cols[i]:
                    s3_cl = "sample-ok" if r['c3'] >= 10 else "sample-low"
                    s4_cl = "sample-ok" if r['c4'] >= 10 else "sample-low"
                    pr_cl = "sample-ok" if r['c_pair'] >= 10 else "sample-low"
                    st.markdown(f"""
                    <div class='bit-header'>{r['l']}</div>
                    <div class='bit-card'><b>3K ({r['s3']}):</b> {int(r['p3']*100)}%<br><span class='{s3_cl}'>Mẫu: {r['c3']}</span></div>
                    <div class='bit-card'><b>4K ({r['s4']}):</b> {int(r['p4']*100)}%<br><span class='{s4_cl}'>Mẫu: {r['c4']}</span></div>
                    <div class='bit-card'><b>10K:</b> {int(r['p_mom']*100)}%</div>
                    <div class='bit-card'><b>22K:</b> {int(r['p_pair']*100)}%<br><span class='{pr_cl}'>Mẫu: {r['c_pair']}</span></div>
                    <div class='bit-card' style='background:#e0f2fe; border: 1px solid #000080'><b>Hội tụ: {int(r['f']*100)}%</b></div>
                    """, unsafe_allow_html=True)
            st.divider()
            ca, cb = st.columns([2, 1])
            st.session_state.num_quan = cb.number_input("Số quân:", value=st.session_state.num_quan, step=1, key="nq_78")
            ca.markdown(f"### 🔥 DÀN TINH ANH {int(st.session_state.num_quan)} SỐ")
            st.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(int(st.session_state.num_quan))['S'].tolist())}</div>", unsafe_allow_html=True)

    with tab2:
        disp = []
        for h in sorted(st.session_state.history, key=lambda x: x['Kỳ'], reverse=True):
            b = get_8bit(h["Số"])
            disp.append({"Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"], "Đ.CL": "Lẻ" if b[0] else "Chẵn", "Đu.CL": "Lẻ" if b[1] else "Chẵn", "T.CL": "Lẻ" if b[2] else "Chẵn", "Đ.TB": "To" if b[3] else "Bé", "Đu.TB": "To" if b[4] else "Bé", "T.TB": "To" if b[5] else "Bé", "Hệ": "Thuận" if b[6] else "K.Phải", "Hiệu": "To" if b[7] else "Bé"})
        if disp:
            st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)
