import streamlit as st
import pandas as pd
import numpy as np
import json

# --- 1. GIAO DIỆN CHUẨN V8.4 (GIỮ NGUYÊN HIỂN THỊ) ---
st.set_page_config(page_title="8-BIT QUANTUM V8.4", layout="wide")
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
    .sample-ok { color: #10b981; font-weight: bold; font-size: 0.62rem; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC V8.4 (CẤU HÌNH TRỌNG SỐ ĐỘNG) ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]
BIT_LABELS = ["Đ.CL", "Đu.CL", "T.CL", "Đ.TB", "Đu.TB", "T.TB", "Hệ", "Hi.TB"]

def get_8bit(n):
    val = int(n); d, u = val // 10, val % 10
    return [1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
            1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if (d+u) % 10 >= 5 else 0,
            1 if val in SO_THUONG else 0, 1 if (d-u+10) % 10 >= 5 else 0]

def analyze_v84(history, last_n):
    if len(history) < 10: return None
    all_bits = np.array([get_8bit(h["Số"]) for h in history])
    curr_bits = np.array(get_8bit(last_n))
    results = []
    
    # CẤU HÌNH V8.4: PHƯƠNG PHÁP CÀNG SÂU CÀNG GẮT
    LIMIT_3K = 15
    LIMIT_4K = 9
    WINDOW_22K = 60 # Chỉ quét tương quan trong 60 kỳ gần nhất (~2 tháng)
    MIN_SAMPLE = 3

    for i in range(8):
        # 3K (15 mẫu gần nhất)
        s3 = "".join(map(str, all_bits[-3:, i].astype(int)))
        m3 = [all_bits[k+3, i] for k in range(len(all_bits)-4) if "".join(map(str, all_bits[k:k+3, i].astype(int))) == s3]
        m3_lim = m3[-LIMIT_3K:]
        p3 = np.mean(m3_lim) if len(m3_lim) > 0 else 0.5

        # 4K (9 mẫu gần nhất - CỰC GẮT)
        s4 = "".join(map(str, all_bits[-4:, i].astype(int)))
        m4 = [all_bits[k+4, i] for k in range(len(all_bits)-5) if "".join(map(str, all_bits[k:k+4, i].astype(int))) == s4]
        m4_lim = m4[-LIMIT_4K:]
        p4 = np.mean(m4_lim) if len(m4_lim) > 0 else 0.5

        # 10K (Nhịp nóng - Trọng số cao)
        p_mom = np.mean(all_bits[-10:, i])

        # 22K (Tương quan cặp trong 60 kỳ gần nhất)
        hist_limited = all_bits[-WINDOW_22K:]
        all_matches_22k = []
        for j in range(8):
            if i == j: continue
            matches = [hist_limited[k+1, i] for k in range(len(hist_limited)-1) if hist_limited[k, i] == curr_bits[i] and hist_limited[k, j] == curr_bits[j]]
            all_matches_22k.extend(matches)
        
        p_pair = np.mean(all_matches_22k) if len(all_matches_22k) > 0 else 0.5

        # CÔNG THỨC HỘI TỤ ĐỘNG V8.4
        f_prob = (p4 * 0.50) + (p_mom * 0.30) + (p3 * 0.10) + (p_pair * 0.10)
        
        results.append({
            "l": BIT_LABELS[i], 
            "c3": len(m3_lim), "p3": p3, 
            "c4": len(m4_lim), "p4": p4, 
            "p_mom": p_mom, 
            "c_pair": len(all_matches_22k), "p_pair": p_pair, 
            "f": f_prob
        })
    return results

# --- 3. SESSION STATE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1
if 'num_quan' not in st.session_state: st.session_state.num_quan = 59
if 'next_ky' not in st.session_state: st.session_state.next_ky = 1

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("📂 HỆ THỐNG V8.4")
    up = st.file_uploader("Nạp Master (2278 kỳ):", type="json")
    if up:
        data = json.load(up); raw = data.get("history", [])
        st.session_state.history = sorted([{"Kỳ": int(h["Kỳ"]), "Số": f"{int(h['Số']):02d}", "Rank": int(h.get("Rank", 0))} for h in raw], key=lambda x: x["Kỳ"])
        st.session_state.last_n = int(st.session_state.history[-1]["Số"])
        st.session_state.next_ky = int(st.session_state.history[-1]["Kỳ"]) + 1
    if st.button("🔴 RESET"):
        st.session_state.history = []; st.session_state.last_n = -1; st.session_state.next_ky = 1; st.rerun()

# --- 5. NHẬP LIỆU ---
st.title("🛡️ 8-BIT QUANTUM V8.4 - DYNAMIC MOMENTUM")
c1, c2, c3, c4 = st.columns([1.5, 1, 1.5, 2])
n_in = c1.text_input("Số vừa nổ:", key="in_so_84")
ky_in = c2.number_input("Kỳ:", value=st.session_state.next_ky, step=1)

if c3.button("🚀 PHÂN TÍCH"):
    if n_in:
        val = int(n_in[-2:]); r_v = 0
        if st.session_state.history:
            res_temp = analyze_v84(st.session_state.history, st.session_state.last_n)
            if res_temp:
                p_t = [r["f"] for r in res_temp]
                scr = [{"S": f"{i:02d}", "M": sum(get_8bit(i)[j]*p_t[j] + (1-get_8bit(i)[j])*(1-p_t[j]) for j in range(8))} for i in range(100)]
                df_t = pd.DataFrame(scr).sort_values("M", ascending=False); df_t['R'] = range(1, 101)
                r_v = df_t[df_t['S'] == f"{val:02d}"]['R'].values[0]
        st.session_state.history.append({"Kỳ": int(ky_in), "Số": f"{val:02d}", "Rank": r_v})
        st.session_state.last_n = val; st.session_state.next_ky = int(ky_in) + 1; st.rerun()

# --- 6. HIỂN THỊ ---
if st.session_state.history:
    results = analyze_v84(st.session_state.history, st.session_state.last_n)
    if results:
        tab1, tab2 = st.tabs(["🎯 PHÂN TÍCH CHỐT", "📊 NHẬT KÝ ĐẦY ĐỦ"])
        with tab1:
            probs = [r["f"] for r in results]
            res_rank = [{"S": f"{i:02d}", "M": sum(get_8bit(i)[j]*probs[j] + (1-get_8bit(i)[j])*(1-probs[j]) for j in range(8))} for i in range(100)]
            df_rank = pd.DataFrame(res_rank).sort_values("M", ascending=False)
            cols = st.columns(8)
            for i, r in enumerate(results):
                with cols[i]:
                    st.markdown(f"""
                    <div class='bit-header'>{BIT_LABELS[i]}</div>
                    <div class='bit-card'><b>3K:</b> {int(r['p3']*100)}% <br><span class='sample-ok'>Mẫu: {r['c3']}</span></div>
                    <div class='bit-card'><b>4K:</b> {int(r['p4']*100)}% <br><span class='sample-ok'>Mẫu: {r['c4']}</span></div>
                    <div class='bit-card'><b>10K:</b> {int(r['p_mom']*100)}%</div>
                    <div class='bit-card'><b>22K:</b> {int(r['p_pair']*100)}% <br><span class='sample-ok'>Mẫu: {r['c_pair']}</span></div>
                    <div class='bit-card' style='background:#f1f5f9; border: 1px solid #000080'><b>Hội tụ: {int(r['f']*100)}%</b></div>
                    """, unsafe_allow_html=True)
            st.divider()
            ca, cb = st.columns([2, 1])
            st.session_state.num_quan = cb.number_input("Số quân:", value=st.session_state.num_quan, step=1)
            ca.markdown(f"### 🔥 DÀN TINH ANH {int(st.session_state.num_quan)} SỐ")
            st.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(int(st.session_state.num_quan))['S'].tolist())}</div>", unsafe_allow_html=True)
        with tab2:
            disp = []
            for h in sorted(st.session_state.history, key=lambda x: x['Kỳ'], reverse=True):
                b = get_8bit(h["Số"])
                disp.append({"Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"], "Đ.CL": "Lẻ" if b[0] else "Chẵn", "Đu.CL": "Lẻ" if b[1] else "Chẵn", "T.CL": "Lẻ" if b[2] else "Chẵn", "Đ.TB": "To" if b[3] else "Bé", "Đu.TB": "To" if b[4] else "Bé", "T.TB": "To" if b[5] else "Bé", "Hệ": "Thuận" if b[6] else "K.Phải", "Hiệu": "To" if b[7] else "Bé"})
            st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)
