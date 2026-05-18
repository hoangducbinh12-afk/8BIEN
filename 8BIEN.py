import streamlit as st
import pandas as pd
import numpy as np
import json

# --- 1. GIAO DIỆN NGUYÊN BẢN V8.5 (KHÔNG THÊM THẮT) ---
st.set_page_config(page_title="8 BIT V8.5", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="st-"] { color: #000000 !important; background-color: #ffffff !important; font-size: 0.72rem !important; }
    .stButton button { 
        width: 100%; border-radius: 4px; height: 38px; font-weight: 700; 
        background-color: #000080 !important; color: #ffffff !important;
    }
    .dan-box { 
        background-color: #f1f5f9; border: 1px solid #000080; border-radius: 5px; 
        padding: 8px; font-family: monospace; font-weight: 700; color: #000080; text-align: center; font-size: 1rem;
    }
    .bit-header { background: #000080; color: white; text-align: center; font-weight: bold; border-radius: 3px; margin-bottom: 2px; }
    .bit-card { 
        background-color: #ffffff; border: 1px solid #d1d5db; border-radius: 4px; 
        padding: 4px; margin-bottom: 2px; line-height: 1.1; 
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC 74 DẠNG BIT ---
SO_THUONG = [2,3,4,6,8,13,15,17,18,19,20,24,25,26,28,30,31,35,37,39,40,42,46,47,48,51,52,53,57,59,60,62,64,68,69,71,73,74,75,79,80,81,82,84,86,91,93,95,96,97]
BIT_LABELS = ["Đ.CL", "Đu.CL", "T.CL", "Đ.TB", "Đu.TB", "T.TB", "Hệ", "Hi.TB"]

def get_8bit(n):
    val = int(n); d, u = val // 10, val % 10
    t_dv, h_dv = (d + u) % 10, (d - u + 10) % 10
    return [
        1 if d % 2 != 0 else 0, 1 if u % 2 != 0 else 0, 1 if (d+u) % 2 != 0 else 0,
        1 if d >= 5 else 0, 1 if u >= 5 else 0, 1 if t_dv >= 5 else 0,
        1 if val in SO_THUONG else 0, 1 if h_dv >= 5 else 0
    ]

def get_8bit_str(n): return "".join(map(str, get_8bit(n)))

def analyze_v85(history, last_n):
    default_res = [{"l": b, "f": 0.5, "p4": 0.5, "p3": 0.5, "pb": 0.5, "c4": 0, "c3": 0, "cb": 0} for b in BIT_LABELS]
    if len(history) < 5: return default_res, []
    
    all_bits = np.array([get_8bit(h["Số"]) for h in history])
    curr_bits = np.array(get_8bit(last_n))
    bit_history_str = [get_8bit_str(h["Số"]) for h in history]
    
    # Phân cụm 74 dạng
    unique_clusters = {}
    for i in range(100):
        s_bit = get_8bit_str(i)
        if s_bit not in unique_clusters: unique_clusters[s_bit] = []
        unique_clusters[s_bit].append(f"{i:02d}")
    
    cluster_gan_data = []
    for s_bit, members in unique_clusters.items():
        try:
            last_idx = len(bit_history_str) - 1 - bit_history_str[::-1].index(s_bit)
            gan = len(bit_history_str) - 1 - last_idx
        except ValueError: gan = len(bit_history_str)
        cluster_gan_data.append({"bit": s_bit, "members": sorted(members), "gan": gan})

    results = []
    for i in range(8):
        s4, s3 = "".join(map(str, all_bits[-4:, i].astype(int))), "".join(map(str, all_bits[-3:, i].astype(int)))
        m4 = [all_bits[k+4, i] for k in range(len(all_bits)-5) if "".join(map(str, all_bits[k:k+4, i].astype(int))) == s4]
        m3 = [all_bits[k+3, i] for k in range(len(all_bits)-4) if "".join(map(str, all_bits[k:k+3, i].astype(int))) == s3]
        p4, p3 = np.mean(m4[-11:]) if m4 else 0.5, np.mean(m3[-22:]) if m3 else 0.5
        pm = []
        for j in range(8):
            if i==j: continue
            matches = [all_bits[k+1, i] for k in range(len(all_bits)-1) if all_bits[k, i] == curr_bits[i] and all_bits[k, j] == curr_bits[j]]
            pm.extend(matches[-66:])
        pb = np.mean(pm) if pm else 0.5
        f_prob = (p4 * 0.4) + (p3 * 0.2) + (pb * 0.2) + (np.mean(all_bits[-10:, i]) * 0.2)
        results.append({"l": BIT_LABELS[i], "f": f_prob, "p4": p4, "p3": p3, "pb": pb, "c4": len(m4), "c3": len(m3), "cb": len(pm)})
    return results, cluster_gan_data

# --- 3. SESSION ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_n' not in st.session_state: st.session_state.last_n = -1
if 'num_q' not in st.session_state: st.session_state.num_q = 59

with st.sidebar:
    st.header("⚙️ V8.5 LEGACY")
    up = st.file_uploader("Nạp Master:", type="json")
    if up:
        data = json.load(up); raw = data.get("history", [])
        st.session_state.history = sorted([{"Kỳ": int(h["Kỳ"]), "Số": f"{int(h['Số']):02d}", "Rank": int(h.get("Rank", 0))} for h in raw], key=lambda x: x["Kỳ"])
        st.session_state.last_n = int(st.session_state.history[-1]["Số"])
    if st.button("🔴 RESET"): st.session_state.history = []; st.rerun()

# --- 4. UI ---
st.title("🚨 CANH BAO 8 BIT V8.5 (74-BIT Core)")

c1, c2, c3 = st.columns([1,1,1.5])
n_in = c1.text_input("Số nổ (Nhập tay):")
ky_curr = int(st.session_state.history[-1]["Kỳ"])+1 if st.session_state.history else 1
ky_in = c2.number_input("Kỳ:", value=ky_curr)

results, cluster_gan = analyze_v85(st.session_state.history, st.session_state.last_n)

if c3.button("🚀 PHÂN TÍCH / LƯU"):
    if n_in:
        val = int(n_in[-2:]); r_v = 0
        if len(st.session_state.history) >= 5:
            probs = [r["f"] for r in results]
            gan_dict = {c['bit']: c['gan'] for c in cluster_gan}
            scr = [{"S":f"{i:02d}", "M":sum(get_8bit(i)[j]*probs[j]+(1-get_8bit(i)[j])*(1-probs[j]) for j in range(8))+(0.05*(gan_dict.get(get_8bit_str(i),0)/40))} for i in range(100)]
            df_t = pd.DataFrame(scr).sort_values("M", ascending=False); df_t['R'] = range(1,101)
            r_v = df_t[df_t['S']==f"{val:02d}"]['R'].values[0]
        st.session_state.history.append({"Kỳ": int(ky_in), "Số": f"{val:02d}", "Rank": r_v}); st.session_state.last_n = val; st.rerun()

tab1, tab2, tab3 = st.tabs(["🎯 PHÂN TÍCH & DÀN", "🕵️ 74 DẠNG CỤM", "📊 NHẬT KÝ V8.5"])

with tab1:
    cols = st.columns(8)
    for i, r in enumerate(results):
        with cols[i]:
            st.markdown(f"<div class='bit-header'>{BIT_LABELS[i]}</div><div class='bit-card'>4K:{int(r['p4']*100)}%<br>3K:{int(r['p3']*100)}%<br>Hậu:{int(r['pb']*100)}%<br><b>Hội tụ:{int(r['f']*100)}%</b></div>", unsafe_allow_html=True)
    st.divider()
    ca, cb = st.columns([3, 1])
    st.session_state.num_q = cb.number_input("Số quân lấy:", value=st.session_state.num_q, min_value=1)
    
    probs = [r["f"] for r in results]
    gan_dict = {c['bit']: c['gan'] for c in cluster_gan} if cluster_gan else {get_8bit_str(i):0 for i in range(100)}
    final_list = [{"S": f"{i:02d}", "M": sum(get_8bit(i)[j]*probs[j] + (1-get_8bit(i)[j])*(1-probs[j]) for j in range(8)) + (0.05 * (gan_dict.get(get_8bit_str(i),0)/40))} for i in range(100)]
    df_rank = pd.DataFrame(final_list).sort_values("M", ascending=False)
    
    ca.markdown(f"### 🔥 DÀN TINH ANH {st.session_state.num_q} SỐ")
    st.markdown(f"<div class='dan-box'>{' '.join(df_rank.head(st.session_state.num_q)['S'].tolist())}</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("🕵️ DANH SÁCH 74 CỤM BIT")
    if cluster_gan:
        for c in sorted(cluster_gan, key=lambda x: x['gan'], reverse=True):
            with st.expander(f"Mã: {c['bit']} — GAN: {c['gan']} kỳ ({len(c['members'])} số)"):
                st.write(f"**Thành viên:** {', '.join(c['members'])}")

with tab3:
    if st.session_state.history:
        disp = []
        for h in sorted(st.session_state.history, key=lambda x: x['Kỳ'], reverse=True):
            b = get_8bit(h["Số"])
            disp.append({"Kỳ": h["Kỳ"], "Số": h["Số"], "Rank": h["Rank"], "Đ.CL": "Lẻ" if b[0] else "Chẵn", "Đu.CL": "Lẻ" if b[1] else "Chẵn", "T.CL": "Lẻ" if b[2] else "Chẵn", "Đ.TB": "To" if b[3] else "Bé", "Đu.TB": "To" if b[4] else "Bé", "T.TB": "To" if b[5] else "Bé", "Hệ": "Thuận" if b[6] else "K.Phải", "Hiệu": "To" if b[7] else "Bé"})
        st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)
