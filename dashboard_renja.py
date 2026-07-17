import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import re
import os

st.set_page_config(page_title="Dashboard Renja BKPSDM", layout="wide", page_icon="📊")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main > div { padding: 0rem 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 0; background: #f8fafc; padding: 4px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 20px; border-radius: 8px; border: none; font-weight: 500; font-size: 0.9rem; }
    .stTabs [aria-selected="true"] { background: white; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    .kpi-card { background: white; border-radius: 12px; padding: 1.2rem 1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); text-align: center; border: 1px solid #f1f5f9; }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .kpi-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem; font-weight: 600; }
    .kpi-value { font-size: 1.5rem; font-weight: 700; }
    .kpi-delta { font-size: 0.75rem; margin-top: 0.2rem; color: #64748b; }
    .section-title { font-size: 1.1rem; font-weight: 600; margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid #e2e8f0; color: #1e293b; }
</style>
""", unsafe_allow_html=True)

def fmt_rp(val):
    if pd.isna(val) or val is None or val == 0:
        return '-'
    int_part = f'{int(val):,}'.replace(',', '.')
    return f'Rp. {int_part},-'

SEED_FILE = 'seed_data.json'

if 'data_rows' not in st.session_state:
    st.session_state.data_rows = []
if 'programs' not in st.session_state:
    st.session_state.programs = {}
if 'kegiatans' not in st.session_state:
    st.session_state.kegiatans = {}
if 'seeded' not in st.session_state:
    st.session_state.seeded = False

if not st.session_state.seeded and os.path.exists(SEED_FILE):
    try:
        with open(SEED_FILE) as f:
            seed = json.load(f)
        st.session_state.programs = seed.get('programs', {})
        st.session_state.kegiatans = seed.get('kegiatans', {})
        st.session_state.data_rows = seed.get('data_rows', [])
        st.session_state.seeded = True
    except:
        pass

st.markdown(f"""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:4px;">
    <div style="background:linear-gradient(135deg, #6366f1, #8b5cf6); width:8px; height:40px; border-radius:4px;"></div>
    <div>
        <div style="font-size:1.3rem; font-weight:700; color:#0f172a;">Dashboard Renja BKPSDM Kota Cirebon</div>
        <div style="font-size:0.78rem; color:#64748b;">Input & Monitoring Realisasi Anggaran per Triwulan — 2026</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

tab_input, tab_dashboard = st.tabs(["📝 Input Data", "📊 Dashboard"])

# ===================== TAB INPUT =====================
with tab_input:
    st.markdown('<div class="section-title">Input Data Anggaran</div>', unsafe_allow_html=True)

    with st.expander("📌 Tambah Program", expanded=not bool(st.session_state.programs)):
        col_prog1, col_prog2 = st.columns([3, 1])
        with col_prog1:
            new_prog = st.text_input("Nama Program", placeholder="Contoh: PROGRAM KEPEGAWAIAN DAERAH", key="new_prog")
        with col_prog2:
            if st.button("➕ Tambah Program", type="primary", use_container_width=True) and new_prog.strip():
                key = new_prog.strip().upper()[:3]
                base = key
                i = 1
                while key in st.session_state.programs:
                    key = f"{base}{i}"
                    i += 1
                st.session_state.programs[key] = new_prog.strip()
                st.rerun()

    if st.session_state.programs:
        st.markdown("##### Program:")
        prog_cols = st.columns([3, 1] * len(st.session_state.programs))
        for idx, (k, v) in enumerate(st.session_state.programs.items()):
            col_name = idx * 2
            col_del = idx * 2 + 1
            with prog_cols[col_name]:
                st.markdown(f"**{v}**")
            with prog_cols[col_del]:
                if st.button("✕", key=f"del_prog_{k}"):
                    to_delete = [rk for rk, rv in st.session_state.data_rows if rv.get('program') == v]
                    for rk in to_delete:
                        st.session_state.data_rows.remove(rk)
                    del st.session_state.programs[k]
                    st.rerun()

        st.markdown("---")

        selected_prog_input = st.selectbox("Pilih Program untuk ditambah Kegiatan", list(st.session_state.programs.values()), key="sel_prog")
        with st.expander("📌 Tambah Kegiatan", expanded=True):
            col_keg1, col_keg2 = st.columns([3, 1])
            with col_keg1:
                new_keg = st.text_input("Nama Kegiatan", placeholder="Contoh: Kegiatan Pengembangan Kompetensi ASN", key="new_keg")
            with col_keg2:
                if st.button("➕ Tambah Kegiatan", type="primary", use_container_width=True) and new_keg.strip():
                    key = f"{selected_prog_input[:3]}_{new_keg.strip()[:3]}"
                    base = key
                    i = 1
                    while key in st.session_state.kegiatans:
                        key = f"{base}{i}"
                        i += 1
                    st.session_state.kegiatans[key] = {
                        'program': selected_prog_input,
                        'nama': new_keg.strip()
                    }
                    st.rerun()

    # Data entry table
    st.markdown("---")
    st.markdown('<div class="section-title">Entry Data Sub Kegiatan</div>', unsafe_allow_html=True)

    prog_options = list(st.session_state.programs.values())
    keg_options = [v['nama'] for v in st.session_state.kegiatans.values()]

    if not prog_options:
        st.info("Silakan tambah Program terlebih dahulu.")
    else:
        with st.form("entry_form", clear_on_submit=True):
            cols_row = st.columns([2, 2, 2, 1, 1, 1, 1, 1])
            with cols_row[0]:
                prog_sel = st.selectbox("Program", prog_options, key="ep_prog")
            with cols_row[1]:
                keg_filtered = [v['nama'] for v in st.session_state.kegiatans.values() if v['program'] == prog_sel]
                keg_sel = st.selectbox("Kegiatan", keg_filtered if keg_filtered else ['(Tambah kegiatan dulu)'], key="ep_keg")
            with cols_row[2]:
                sub_nama = st.text_input("Sub Kegiatan", placeholder="Nama Sub Kegiatan", key="ep_sub")
            with cols_row[3]:
                target = st.number_input("Target (Rp)", min_value=0, step=100000, format="%d", key="ep_target")
            with cols_row[4]:
                tw1 = st.number_input("TW I (Rp)", min_value=0, step=100000, format="%d", key="ep_tw1")
            with cols_row[5]:
                tw2 = st.number_input("TW II (Rp)", min_value=0, step=100000, format="%d", key="ep_tw2")
            with cols_row[6]:
                tw3 = st.number_input("TW III (Rp)", min_value=0, step=100000, format="%d", key="ep_tw3")
            with cols_row[7]:
                tw4 = st.number_input("TW IV (Rp)", min_value=0, step=100000, format="%d", key="ep_tw4")
            submitted = st.form_submit_button("💾 Simpan", type="primary", use_container_width=True)
            if submitted and sub_nama.strip() and keg_sel not in ['(Tambah kegiatan dulu)']:
                st.session_state.data_rows.append({
                    'program': prog_sel,
                    'kegiatan': keg_sel,
                    'sub_kegiatan': sub_nama.strip(),
                    'target': target,
                    'tw1': tw1,
                    'tw2': tw2,
                    'tw3': tw3,
                    'tw4': tw4,
                })
                st.success(f"✅ {sub_nama.strip()} tersimpan!")
                st.rerun()

    # Display entered data
    if st.session_state.data_rows:
        st.markdown("---")
        st.markdown('<div class="section-title">Data Tersimpan</div>', unsafe_allow_html=True)

        df_input = pd.DataFrame(st.session_state.data_rows)
        df_display = df_input.copy()
        for col in ['target', 'tw1', 'tw2', 'tw3', 'tw4']:
            df_display[col] = df_display[col].apply(lambda x: fmt_rp(x) if x else '-')
        df_display.columns = ['Program', 'Kegiatan', 'Sub Kegiatan', 'Target', 'TW I', 'TW II', 'TW III', 'TW IV']

        col_del_row, _ = st.columns([1, 5])
        with col_del_row:
            row_to_del = st.selectbox("Hapus baris", df_input.index.tolist(), format_func=lambda i: f"{i+1}. {df_input.iloc[i]['sub_kegiatan'][:30]}", key="del_row_sel")
            if st.button("✕ Hapus", type="secondary", use_container_width=True):
                st.session_state.data_rows.pop(row_to_del)
                st.rerun()

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Export/Import
        col_exp, col_imp, _ = st.columns([1, 1, 4])
        with col_exp:
            json_data = json.dumps({
                'programs': st.session_state.programs,
                'kegiatans': st.session_state.kegiatans,
                'data_rows': st.session_state.data_rows
            }, indent=2)
            st.download_button("⬇️ Download Data (JSON)", data=json_data,
                file_name=f"renja_data_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json")
        with col_imp:
            uploaded = st.file_uploader("Upload Data (JSON)", type=['json'])
            if uploaded:
                data = json.load(uploaded)
                st.session_state.programs = data.get('programs', {})
                st.session_state.kegiatans = data.get('kegiatans', {})
                st.session_state.data_rows = data.get('data_rows', [])
                st.rerun()
    else:
        st.info("Belum ada data. Silakan isi form di atas.")

# ===================== TAB DASHBOARD =====================
with tab_dashboard:
    if not st.session_state.data_rows:
        st.info("📋 Belum ada data. Silakan isi data di tab **📝 Input Data** terlebih dahulu.")
    else:
        df = pd.DataFrame(st.session_state.data_rows)
        df['realisasi'] = df['tw1'] + df['tw2'] + df['tw3'] + df['tw4']
        df['capaian_persen'] = df.apply(lambda r: (r['realisasi'] / r['target'] * 100) if r['target'] > 0 else 0, axis=1)

        # Sidebar filters
        st.sidebar.markdown("<div style='font-size:1rem; font-weight:600; margin-bottom:0.5rem;'>🔍 Filter</div>", unsafe_allow_html=True)
        prog_list = df['program'].unique().tolist()
        sel_prog = st.sidebar.selectbox("Program", ['Semua'] + prog_list, key="dash_prog")
        df_filtered = df.copy()
        if sel_prog != 'Semua':
            df_filtered = df_filtered[df_filtered['program'] == sel_prog]

        # KPI
        total_target = df_filtered['target'].sum()
        total_realisasi = df_filtered['realisasi'].sum()
        total_tw1 = df_filtered['tw1'].sum()
        total_tw2 = df_filtered['tw2'].sum()
        total_tw3 = df_filtered['tw3'].sum()
        total_tw4 = df_filtered['tw4'].sum()
        persen = (total_realisasi / total_target * 100) if total_target else 0

        st.markdown('<div class="section-title">Ringkasan Anggaran</div>', unsafe_allow_html=True)
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total Anggaran</div><div class='kpi-value' style='color:#6366f1;'>{fmt_rp(total_target)}</div><div class='kpi-delta'>{len(df_filtered)} Sub Kegiatan</div></div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total Realisasi</div><div class='kpi-value' style='color:#10b981;'>{fmt_rp(total_realisasi)}</div><div class='kpi-delta'>dari {fmt_rp(total_target)}</div></div>", unsafe_allow_html=True)
        with k3:
            c = "#10b981" if persen >= 50 else "#ef4444"
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Capaian</div><div class='kpi-value' style='color:{c};'>{persen:.1f}%</div><div class='kpi-delta'>{fmt_rp(total_realisasi)} terealisasi</div></div>", unsafe_allow_html=True)
        with k4:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>TW I</div><div class='kpi-value' style='color:#60a5fa;'>{fmt_rp(total_tw1)}</div><div class='kpi-delta'>{fmt_rp(total_tw2)}</div></div>", unsafe_allow_html=True)
        with k5:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>TW III</div><div class='kpi-value' style='color:#fbbf24;'>{fmt_rp(total_tw3)}</div><div class='kpi-delta'>{fmt_rp(total_tw4)}</div></div>", unsafe_allow_html=True)

        # Realisasi vs Target per Program
        st.markdown('<div class="section-title">Target vs Realisasi per Program</div>', unsafe_allow_html=True)
        df_prog = df_filtered.groupby('program').agg({'target': 'sum', 'realisasi': 'sum'}).reset_index()
        df_prog['capaian'] = df_prog.apply(lambda r: (r['realisasi'] / r['target'] * 100) if r['target'] > 0 else 0, axis=1)

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_prog['program'], y=df_prog['target'], name='Target',
            marker_color='#e0e7ff', marker_line_color='#6366f1', marker_line_width=1.5,
            text=df_prog['target'].apply(lambda x: fmt_rp(x)), textposition='outside', textfont=dict(size=9)))
        fig1.add_trace(go.Bar(x=df_prog['program'], y=df_prog['realisasi'], name='Realisasi',
            marker_color='#6366f1',
            text=df_prog['realisasi'].apply(lambda x: fmt_rp(x)), textposition='outside', textfont=dict(size=9, color='#6366f1')))
        fig1.add_trace(go.Scatter(x=df_prog['program'], y=df_prog['capaian'], name='Capaian %',
            yaxis='y2', mode='lines+markers+text',
            text=df_prog['capaian'].apply(lambda x: f'{x:.0f}%'), textposition='top center',
            line=dict(color='#ef4444', width=2, dash='dot'), marker=dict(color='#ef4444', size=8)))
        fig1.update_layout(barmode='group', xaxis_tickangle=-15,
            yaxis=dict(gridcolor='#f1f5f9'), yaxis2=dict(overlaying='y', side='right', range=[0, 120], gridcolor='#f1f5f9'),
            legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='right', x=1),
            hovermode='x unified', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=60, t=40, b=40))
        st.plotly_chart(fig1, use_container_width=True)

        # Per Program detail
        st.markdown('<div class="section-title">Rincian per Program</div>', unsafe_allow_html=True)
        for prog_name in df_filtered['program'].unique():
            df_p = df_filtered[df_filtered['program'] == prog_name]
            t_p = df_p['target'].sum()
            r_p = df_p['realisasi'].sum()
            c_p = (r_p / t_p * 100) if t_p else 0
            st.markdown(f"""<div style="background:linear-gradient(135deg, #f8fafc, #f1f5f9); border-radius:10px; padding:0.8rem 1rem; margin-bottom:1rem; border-left:4px solid #6366f1;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:5px;">
                    <div><b style="color:#0f172a;">{prog_name}</b></div>
                    <div style="display:flex; gap:1rem; font-size:0.85rem;">
                        <span>Target: <b>{fmt_rp(t_p)}</b></span>
                        <span>Realisasi: <b style="color:#10b981;">{fmt_rp(r_p)}</b></span>
                        <span>Capaian: <b style="color:{'#10b981' if c_p>=50 else '#ef4444'};">{c_p:.1f}%</b></span>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            for k名 in df_p['kegiatan'].unique():
                df_k = df_p[df_p['kegiatan'] == k名]
                t_k = df_k['target'].sum()
                r_k = df_k['realisasi'].sum()
                c_k = (r_k / t_k * 100) if t_k else 0

                st.markdown(f"""<div style="background:white; border-radius:8px; padding:0.6rem 1rem; margin-bottom:0.5rem; border-left:3px solid #6366f1; border:1px solid #f1f5f9;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:3px;">
                        <div style="font-weight:500; font-size:0.9rem;">{k名}</div>
                        <div style="display:flex; gap:0.8rem; font-size:0.8rem;">
                            <span>Target: <b>{fmt_rp(t_k)}</b></span>
                            <span>Realisasi: <b style="color:#10b981;">{fmt_rp(r_k)}</b></span>
                            <span>Capaian: <b style="color:{'#10b981' if c_k>=50 else '#ef4444'};">{c_k:.1f}%</b></span>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

                df_sub = df_k.sort_values('target', ascending=True)
                labels = df_sub['sub_kegiatan'].tolist()
                t_vals = df_sub['target'].tolist()
                r_vals = df_sub['realisasi'].tolist()
                fig_sub = go.Figure()
                fig_sub.add_trace(go.Bar(y=labels, x=t_vals, name='Target', orientation='h',
                    marker_color='#e0e7ff', marker_line_color='#6366f1', marker_line_width=1,
                    text=[fmt_rp(v) for v in t_vals], textposition='outside', textfont=dict(size=9)))
                fig_sub.add_trace(go.Bar(y=labels, x=r_vals, name='Realisasi', orientation='h',
                    marker_color='#6366f1',
                    text=[fmt_rp(v) for v in r_vals], textposition='outside', textfont=dict(size=9, color='#6366f1')))
                fig_sub.update_layout(barmode='group', height=max(120, len(df_sub)*40),
                    margin=dict(l=10, r=80, t=10, b=10), xaxis=dict(gridcolor='#f1f5f9'),
                    yaxis=dict(autorange='reversed', gridcolor='#f1f5f9'),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', hovermode='y unified')
                st.plotly_chart(fig_sub, use_container_width=True)

                # TW chart
                tw_df = pd.DataFrame({
                    'Triwulan': ['TW I', 'TW II', 'TW III', 'TW IV'],
                    'Realisasi': [df_k['tw1'].sum(), df_k['tw2'].sum(), df_k['tw3'].sum(), df_k['tw4'].sum()]
                })
                fig_tw = px.bar(tw_df, x='Triwulan', y='Realisasi', color='Triwulan',
                    color_discrete_map={'TW I': '#60a5fa', 'TW II': '#34d399', 'TW III': '#fbbf24', 'TW IV': '#f87171'},
                    text=[fmt_rp(v) for v in tw_df['Realisasi']], height=180)
                fig_tw.update_traces(textposition='outside', textfont=dict(size=9))
                fig_tw.update_layout(title=dict(text='Realisasi per Triwulan', font=dict(size=11), x=0.5),
                    showlegend=False, margin=dict(l=10, r=10, t=30, b=10),
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_tw, use_container_width=True)

        # Triwulan overview
        st.markdown('<div class="section-title">Realisasi per Triwulan</div>', unsafe_allow_html=True)
        tw_all = pd.DataFrame({
            'Triwulan': ['TW I', 'TW II', 'TW III', 'TW IV'],
            'Realisasi': [total_tw1, total_tw2, total_tw3, total_tw4]
        })
        cum = []
        s = 0
        for v in tw_all['Realisasi']:
            s += v
            cum.append(s)
        tw_all['Kumulatif'] = cum

        fig_tw_all = go.Figure()
        fig_tw_all.add_trace(go.Bar(x=tw_all['Triwulan'], y=tw_all['Realisasi'], name='Realisasi',
            marker_color=['#60a5fa','#34d399','#fbbf24','#f87171'],
            text=[fmt_rp(v) for v in tw_all['Realisasi']], textposition='outside', textfont=dict(size=10)))
        fig_tw_all.add_trace(go.Scatter(x=tw_all['Triwulan'], y=tw_all['Kumulatif'], name='Kumulatif',
            yaxis='y2', mode='lines+markers+text', text=[fmt_rp(v) for v in tw_all['Kumulatif']],
            textposition='top center', line=dict(color='#6366f1', width=3), marker=dict(color='#6366f1', size=10)))
        fig_tw_all.add_hline(y=total_target, line_dash='dash', line_color='#ef4444',
            annotation_text=f'Target: {fmt_rp(total_target)}', annotation_font=dict(color='#ef4444', size=10))
        fig_tw_all.update_layout(yaxis=dict(gridcolor='#f1f5f9'),
            yaxis2=dict(overlaying='y', side='right', gridcolor='#f1f5f9'),
            legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='right', x=1),
            hovermode='x unified', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=60, t=40, b=40), height=400)
        st.plotly_chart(fig_tw_all, use_container_width=True)

st.markdown("""
<div style="text-align:center; padding:2rem 0 0.5rem 0; opacity:0.4; font-size:0.7rem; color:#94a3b8;">
    Dashboard Renja BKPSDM Kota Cirebon — Input & Monitoring Realisasi Anggaran 2026
</div>
""", unsafe_allow_html=True)
