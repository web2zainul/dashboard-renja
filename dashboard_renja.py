import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import csv
from datetime import datetime
from logo_data import LOGO_KOTA_B64, LOGO_BKPSDM_B64

st.set_page_config(page_title="Dashboard Renja BKPSDM Kota Cirebon", layout="wide", page_icon="📊")

st.markdown("""
<style>
    .main > div { padding: 0rem 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 16px; border-radius: 4px 4px 0 0; }
    .kpi-card { background: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; }
    .kpi-label { font-size: 0.85rem; color: #6b7280; margin-bottom: 0.3rem; }
    .kpi-value { font-size: 1.8rem; font-weight: 700; }
    .kpi-delta { font-size: 0.9rem; margin-top: 0.2rem; }
    .section-title { font-size: 1.2rem; font-weight: 600; margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid #e5e7eb; }
    .sub-section-title { font-size: 1rem; font-weight: 500; margin: 1rem 0 0.5rem 0; color: #374151; }
    .header-logo { display: flex; align-items: center; gap: 15px; }
    .header-logo img { height: 55px; width: auto; object-fit: contain; }
    @media (max-width: 768px) {
        .header-logo img { height: 40px; }
        .header-title { font-size: 1.2rem !important; }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    rows = []
    with open('file.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for r in reader:
            rows.append(r)

    data = []
    for i in range(4, len(rows)):
        r = rows[i]
        if not r[5].strip() and not r[6].strip():
            continue
        
        def clean_num(val):
            v = str(val).strip().replace(' ', '').replace(',', '.').replace('\u2013', '-').replace('\u2014', '-')
            if v in ['', '-', '--', '0%', '-%']:
                return None
            v = v.replace('%', '')
            try:
                return float(v)
            except:
                try:
                    v = v.replace('.', '').replace(',', '.')
                    return float(v)
                except:
                    return None

        def clean_rp(val):
            v = str(val).strip()
            if not v or v in ['-', '--', '-   ']:
                return None
            v = v.replace('.', '')
            v = v.replace(',', '.')
            v = v.strip()
            try:
                return float(v)
            except:
                return None

        def clean_str(val):
            return str(val).strip().replace('\n', ' ').replace('\u00a0', ' ')

        def compress_space(s):
            import re
            return re.sub(r'\s+', ' ', s)

        nama_upper = clean_str(r[5]).upper()
        if nama_upper.startswith('SUB KEGIATAN'):
            level = 'Sub Kegiatan'
        elif nama_upper.startswith('KEGIATAN'):
            level = 'Kegiatan'
        elif nama_upper.startswith('PROGRAM'):
            level = 'Program'
        elif 'BIDANG' in nama_upper or nama_upper.startswith('URUSAN'):
            level = 'Bidang'
        else:
            level = 'Sub Kegiatan'

        nama = compress_space(clean_str(r[5]))
        if nama.upper().startswith('SUB KEGIATAN '):
            nama = nama[13:].strip()
        elif nama.upper().startswith('KEGIATAN '):
            nama = nama[9:].strip()
        elif nama.upper().startswith('PROGRAM '):
            nama = nama[8:].strip()

        row = {
            'kode1': clean_str(r[0]),
            'kode2': clean_str(r[1]),
            'kode3': clean_str(r[2]),
            'kode4': clean_str(r[3]),
            'kode5': clean_str(r[4]),
            'nama': nama,
            'nama_lengkap': compress_space(clean_str(r[5])),
            'indikator': compress_space(clean_str(r[6])),
            'satuan': clean_str(r[7]),
            'level': level,
            'target_renstra_2029_kinerja': clean_num(r[8]),
            'target_renstra_2029_anggaran': clean_rp(r[9]),
            'realisasi_2025_kinerja': clean_num(r[10]),
            'realisasi_2025_anggaran': clean_rp(r[11]),
            'target_2026_kinerja': clean_num(r[12]),
            'target_2026_anggaran': clean_rp(r[13]),
            'realisasi_tw1_kinerja': clean_num(r[14]),
            'realisasi_tw1_anggaran': clean_rp(r[15]),
            'realisasi_tw2_kinerja': clean_num(r[16]),
            'realisasi_tw2_anggaran': clean_rp(r[17]),
            'realisasi_tw3_kinerja': clean_num(r[18]),
            'realisasi_tw3_anggaran': clean_rp(r[19]),
            'realisasi_tw4_kinerja': clean_num(r[20]),
            'realisasi_tw4_anggaran': clean_rp(r[21]),
            'realisasi_2026_kinerja': clean_num(r[22]),
            'realisasi_2026_anggaran': clean_rp(r[23]),
            'capaian_2026_kinerja_persen': clean_num(r[24]),
            'capaian_2026_anggaran_persen': clean_num(r[25]),
            'realisasi_sd_2026_kinerja': clean_num(r[26]),
            'realisasi_sd_2026_anggaran': clean_rp(r[27]),
            'capaian_sd_2026_kinerja_persen': clean_num(r[28]),
            'capaian_sd_2026_anggaran_persen': clean_num(r[29]),
            'unit_penanggung_jawab': clean_str(r[30]) if len(r) > 30 else '',
            'evidence_tw1': clean_str(r[31]) if len(r) > 31 else '',
            'evidence_tw2': clean_str(r[32]) if len(r) > 32 else '',
        }
        data.append(row)
    return pd.DataFrame(data)

def build_hierarchy(df):
    programs = {}
    kegiatans = {}
    for _, row in df.iterrows():
        if row['level'] == 'Program':
            programs[row['kode3']] = {'nama': row['nama'], 'kode3': row['kode3']}
        elif row['level'] == 'Kegiatan':
            kegiatans[row['kode4']] = {
                'nama': row['nama'],
                'kode3': row['kode3'],
                'kode4': row['kode4']
            }

    df['program_nama'] = None
    df['kegiatan_nama'] = None
    df['kegiatan_kode4'] = None

    for idx, row in df.iterrows():
        if row['level'] == 'Sub Kegiatan':
            k4 = row['kode4']
            if k4 in kegiatans:
                df.at[idx, 'kegiatan_nama'] = kegiatans[k4]['nama']
                df.at[idx, 'kegiatan_kode4'] = k4
                k3 = kegiatans[k4]['kode3']
                if k3 in programs:
                    df.at[idx, 'program_nama'] = programs[k3]['nama']
        elif row['level'] == 'Kegiatan':
            k3 = row['kode3']
            if k3 in programs:
                df.at[idx, 'program_nama'] = programs[k3]['nama']

    return df

df = load_data()
df = build_hierarchy(df)

PROGRAM_COLORS = {
    'PROGRAM PENUNJANG URUSAN PEMERINTAHAN DAERAH KABUPATEN/KOTA': '#6366f1',
    'PROGRAM KEPEGAWAIAN DAERAH': '#10b981',
    'PROGRAM PENGEMBANGAN SUMBER DAYA MANUSIA': '#f59e0b',
}

KEGIATAN_COLORS = [
    '#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899',
    '#f43f5e', '#ef4444', '#f97316', '#f59e0b', '#eab308',
    '#84cc16', '#22c55e', '#10b981', '#14b8a6', '#06b6d4',
    '#0ea5e9', '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7',
]

TW_COLORS = ['#60a5fa', '#34d399', '#fbbf24', '#f87171']

st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px; flex-wrap:wrap; gap:10px;">
    <div class="header-logo">
        <img src="data:image/png;base64,{LOGO_KOTA_B64}" alt="Kota Cirebon" title="Pemerintah Kota Cirebon">
        <div>
            <div class="header-title" style="font-size:1.4rem; font-weight:700; color:#1f2937;">Dashboard Renja BKPSDM</div>
            <div style="font-size:0.8rem; color:#6b7280;">Evaluasi Renja Perangkat Daerah — Periode Pelaksanaan 2026</div>
        </div>
    </div>
    <img src="data:image/png;base64,{LOGO_BKPSDM_B64}" alt="BKPSDM" title="BKPSDM Kota Cirebon" style="height:55px; width:auto; object-fit:contain;">
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)

# ============ SIDEBAR ============
st.sidebar.markdown("""
<div style="font-size:1.1rem; font-weight:600; margin-bottom:0.5rem;">🔍 Filter Dashboard</div>
""", unsafe_allow_html=True)

programs_list = sorted(df[df['level'] == 'Program']['nama'].unique())
selected_program = st.sidebar.selectbox('Program', ['Semua Program'] + programs_list)

if selected_program != 'Semua Program':
    df_prog = df[df['program_nama'] == selected_program].copy()
else:
    df_prog = df.copy()

kegiatans_list = sorted(df_prog[df_prog['level'] == 'Kegiatan']['nama'].unique())
selected_kegiatan = st.sidebar.multiselect('Kegiatan', kegiatans_list, default=[],
    placeholder='Pilih kegiatan (opsional)')

if selected_kegiatan:
    df_prog = df_prog[
        df_prog['kegiatan_nama'].isin(selected_kegiatan) |
        df_prog['nama'].isin(selected_kegiatan)
    ]

st.sidebar.markdown("<hr style='margin:1rem 0; opacity:0.3;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style="font-size:0.75rem; color:#9ca3af; line-height:1.4;">
    <b>Sumber Data:</b> BKPSDM Kota Cirebon<br>
    <b>Terakhir Update:</b> 14 Juli 2026
</div>
""", unsafe_allow_html=True)

# ============ KPI RINGKASAN ============
total_target = df_prog['target_2026_anggaran'].sum() or 0
total_realisasi = df_prog['realisasi_2026_anggaran'].sum() or 0
total_realisasi_tw1 = df_prog['realisasi_tw1_anggaran'].sum() or 0
total_realisasi_tw2 = df_prog['realisasi_tw2_anggaran'].sum() or 0
total_realisasi_tw3 = df_prog['realisasi_tw3_anggaran'].sum() or 0
total_realisasi_tw4 = df_prog['realisasi_tw4_anggaran'].sum() or 0
persen_realisasi = (total_realisasi / total_target * 100) if total_target else 0
total_kegiatan = len(df_prog[df_prog['level'] == 'Kegiatan'])
total_sub = len(df_prog[df_prog['level'] == 'Sub Kegiatan'])

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Anggaran</div>
        <div class="kpi-value" style="color:#6366f1;">Rp {total_target/1e9:.2f} M</div>
        <div class="kpi-delta" style="color:#6b7280;">{total_kegiatan} Kegiatan · {total_sub} Sub Kegiatan</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Realisasi</div>
        <div class="kpi-value" style="color:#10b981;">Rp {total_realisasi/1e9:.2f} M</div>
        <div class="kpi-delta" style="color:#6b7280;">dari target Rp {total_target/1e9:.2f} M</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    delta_color = "color:#10b981;" if persen_realisasi >= 50 else "color:#ef4444;"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Capaian Anggaran</div>
        <div class="kpi-value" style="{delta_color}">{persen_realisasi:.1f}%</div>
        <div class="kpi-delta" style="color:#6b7280;">{(persen_realisasi/100)*total_target/1e9:.2f} M terealisasi</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Realisasi Triwulan I</div>
        <div class="kpi-value" style="color:#60a5fa;">Rp {total_realisasi_tw1/1e9:.2f} M</div>
        <div class="kpi-delta" style="color:#6b7280;">{(total_realisasi_tw1/total_target*100) if total_target else 0:.1f}% dari target</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Realisasi Triwulan II</div>
        <div class="kpi-value" style="color:#34d399;">Rp {total_realisasi_tw2/1e9:.2f} M</div>
        <div class="kpi-delta" style="color:#6b7280;">{(total_realisasi_tw2/total_target*100) if total_target else 0:.1f}% dari target</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============ TAB LAYOUT ============
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Realisasi Anggaran",
    "📈 Per Program & Kegiatan",
    "📅 Per Triwulan",
    "📋 Tabel Data"
])

# ===================== TAB 1: REALISASI ANGGARAN =====================
with tab1:
    st.markdown('<div class="section-title">Realisasi Anggaran Keseluruhan</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        df_program_agg = df_prog[df_prog['level'] == 'Program'].copy()
        if not df_program_agg.empty:
            fig_target_vs_realisasi = go.Figure()
            fig_target_vs_realisasi.add_trace(go.Bar(
                x=df_program_agg['nama'],
                y=df_program_agg['target_2026_anggaran'],
                name='Target Anggaran',
                marker_color='#e0e7ff',
                marker_line_color='#6366f1',
                marker_line_width=1.5,
                text=df_program_agg['target_2026_anggaran'].apply(lambda x: f'Rp{x/1e9:.2f}M' if pd.notna(x) else ''),
                textposition='outside',
                textfont=dict(size=11),
                hovertemplate='<b>%{x}</b><br>Target: Rp%{y:,.0f}<extra></extra>'
            ))
            fig_target_vs_realisasi.add_trace(go.Bar(
                x=df_program_agg['nama'],
                y=df_program_agg['realisasi_2026_anggaran'],
                name='Realisasi',
                marker_color='#6366f1',
                text=df_program_agg['realisasi_2026_anggaran'].apply(lambda x: f'Rp{x/1e9:.2f}M' if pd.notna(x) else ''),
                textposition='outside',
                textfont=dict(size=11, color='#6366f1'),
                hovertemplate='<b>%{x}</b><br>Realisasi: Rp%{y:,.0f}<extra></extra>'
            ))
            fig_target_vs_realisasi.add_trace(go.Scatter(
                x=df_program_agg['nama'],
                y=df_program_agg['capaian_2026_anggaran_persen'],
                name='Capaian %',
                yaxis='y2',
                mode='lines+markers+text',
                text=df_program_agg['capaian_2026_anggaran_persen'].apply(lambda x: f'{x:.0f}%' if pd.notna(x) else ''),
                textposition='top center',
                textfont=dict(size=11, color='#ef4444'),
                line=dict(color='#ef4444', width=2.5, dash='dot'),
                marker=dict(color='#ef4444', size=9, symbol='diamond'),
                hovertemplate='<b>%{x}</b><br>Capaian: %{y:.1f}%<extra></extra>'
            ))
            fig_target_vs_realisasi.update_layout(
                xaxis_tickangle=-20,
                barmode='group',
                bargap=0.3,
                yaxis=dict(title='Anggaran (Rp)', gridcolor='#f3f4f6'),
                yaxis2=dict(title='Capaian (%)', overlaying='y', side='right', range=[0, 120],
                           gridcolor='#f3f4f6', tickfont=dict(color='#ef4444')),
                legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='right', x=1),
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=60, t=40, b=40),
            )
            st.plotly_chart(fig_target_vs_realisasi, use_container_width=True)

    with col_right:
        df_program_pie = df_prog[df_prog['level'] == 'Program'].copy()
        if not df_program_pie.empty:
            colors_pie = [PROGRAM_COLORS.get(p, '#6366f1') for p in df_program_pie['nama']]
            fig_pie = go.Figure(data=[go.Pie(
                labels=df_program_pie['nama'],
                values=df_program_pie['target_2026_anggaran'],
                hole=0.55,
                marker=dict(colors=colors_pie, line=dict(color='white', width=2)),
                textinfo='label+percent',
                textfont=dict(size=12),
                hovertemplate='<b>%{label}</b><br>Anggaran: Rp%{value:,.0f}<br>Persentase: %{percent}<extra></extra>'
            )])
            fig_pie.update_layout(
                title=dict(text='<b>Alokasi Anggaran per Program</b>', font=dict(size=14), x=0.5),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=50, b=20),
                annotations=[dict(text=f'Rp{total_target/1e9:.2f}M', x=0.5, y=0.5, font=dict(size=16, color='#374151'), showarrow=False)]
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # DONUT REALISASI
    st.markdown('<div class="section-title">Tingkat Realisasi Anggaran</div>', unsafe_allow_html=True)
    col_gauge1, col_gauge2, col_gauge3 = st.columns(3)

    with col_gauge1:
        fig_gauge = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=persen_realisasi,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': 'Realisasi Anggaran 2026', 'font': {'size': 14}},
            delta={'reference': 100, 'position': 'bottom'},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': 'darkgray'},
                'bar': {'color': '#6366f1', 'thickness': 0.3},
                'bgcolor': 'white',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 33], 'color': '#fee2e2'},
                    {'range': [33, 66], 'color': '#fef3c7'},
                    {'range': [66, 100], 'color': '#d1fae5'}],
                'threshold': {
                    'line': {'color': '#ef4444', 'width': 3},
                    'thickness': 0.6,
                    'value': 50
                }
            }
        ))
        fig_gauge.update_layout(
            height=250,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_gauge2:
        capaian_kinerja = df_prog['capaian_2026_kinerja_persen'].mean()
        if pd.isna(capaian_kinerja):
            capaian_kinerja = 0
        fig_gauge2 = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=capaian_kinerja,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': 'Capaian Kinerja 2026', 'font': {'size': 14}},
            delta={'reference': 100, 'position': 'bottom'},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': 'darkgray'},
                'bar': {'color': '#10b981', 'thickness': 0.3},
                'bgcolor': 'white',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 33], 'color': '#fee2e2'},
                    {'range': [33, 66], 'color': '#fef3c7'},
                    {'range': [66, 100], 'color': '#d1fae5'}],
                'threshold': {
                    'line': {'color': '#ef4444', 'width': 3},
                    'thickness': 0.6,
                    'value': 50
                }
            }
        ))
        fig_gauge2.update_layout(
            height=250,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_gauge2, use_container_width=True)

    with col_gauge3:
        sisa_anggaran = total_target - total_realisasi
        fig_gauge3 = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=sisa_anggaran / 1e6 if sisa_anggaran > 0 else 0,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': 'Sisa Anggaran (Rp Juta)', 'font': {'size': 14}},
            delta={'reference': total_target / 1e6, 'position': 'bottom'},
            gauge={
                'axis': {'range': [None, total_target / 1e6 if total_target > 0 else 1], 'tickwidth': 1, 'tickcolor': 'darkgray'},
                'bar': {'color': '#f59e0b', 'thickness': 0.3},
                'bgcolor': 'white',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, total_target / 3e6 if total_target > 0 else 1], 'color': '#d1fae5'},
                    {'range': [total_target / 3e6 if total_target > 0 else 1, total_target / 1.5e6 if total_target > 0 else 1], 'color': '#fef3c7'},
                    {'range': [total_target / 1.5e6 if total_target > 0 else 1, total_target / 1e6 if total_target > 0 else 1], 'color': '#fee2e2'}],
            }
        ))
        fig_gauge3.update_layout(
            height=250,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_gauge3, use_container_width=True)

    # Treemap
    df_treemap = df_prog[df_prog['level'] == 'Sub Kegiatan'].copy()
    if not df_treemap.empty:
        st.markdown('<div class="section-title">Hierarki Anggaran (Treemap)</div>', unsafe_allow_html=True)
        df_treemap['label_display'] = df_treemap['nama'].apply(lambda x: x[:35] + '...' if len(x) > 35 else x)
        df_treemap['anggaran_m'] = df_treemap['target_2026_anggaran'].apply(lambda x: round(x/1e6, 1) if pd.notna(x) else 0)
        fig_treemap = px.treemap(
            df_treemap,
            path=[px.Constant('BKPSDM Kota Cirebon'), 'program_nama', 'kegiatan_nama', 'label_display'],
            values='target_2026_anggaran',
            color='capaian_2026_anggaran_persen',
            color_continuous_scale=['#ef4444', '#fbbf24', '#34d399', '#10b981'],
            color_continuous_midpoint=50,
            hover_data={'target_2026_anggaran': ':,.0f', 'realisasi_2026_anggaran': ':,.0f', 'capaian_2026_anggaran_persen': ':.1f'},
        )
        fig_treemap.update_traces(
            textinfo='label+value+percent root',
            textfont=dict(size=12),
            hovertemplate='<b>%{label}</b><br>Anggaran: Rp%{customdata[0]:,.0f}<br>Realisasi: Rp%{customdata[1]:,.0f}<br>Capaian: %{customdata[2]:.1f}%<extra></extra>'
        )
        fig_treemap.update_layout(
            margin=dict(l=10, r=10, t=30, b=10),
            height=500,
        )
        st.plotly_chart(fig_treemap, use_container_width=True)

# ===================== TAB 2: PER PROGRAM & KEGIATAN =====================
with tab2:
    st.markdown('<div class="section-title">Rincian per Program dan Kegiatan</div>', unsafe_allow_html=True)

    for _, prog in df[df['level'] == 'Program'].iterrows():
        if selected_program != 'Semua Program' and prog['nama'] != selected_program:
            continue
        k3 = prog['kode3']
        prog_color = PROGRAM_COLORS.get(prog['nama'], '#6366f1')

        prog_target = prog['target_2026_anggaran'] or 0
        prog_realisasi = prog['realisasi_2026_anggaran'] or 0
        prog_capaian = prog['capaian_2026_anggaran_persen']
        prog_capaian_str = f"{prog_capaian:.1f}%" if pd.notna(prog_capaian) else "N/A"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg, {prog_color}15, {prog_color}08); border-radius:10px; padding:1rem 1.2rem; margin-bottom:1.5rem; border-left:4px solid {prog_color};">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:1rem; font-weight:600; color:#1f2937;">{prog['nama']}</div>
                    <div style="font-size:0.8rem; color:#6b7280; margin-top:2px;">{prog['indikator']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.2rem; font-weight:700; color:{prog_color};">Rp {prog_target/1e9:.2f} M</div>
                    <div style="font-size:0.8rem; color:#6b7280;">Target · Realisasi: Rp {prog_realisasi/1e9:.2f} M · {prog_capaian_str}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        kegiatans = df[(df['level'] == 'Kegiatan') & (df['kode3'] == k3)]
        if selected_kegiatan:
            kegiatans = kegiatans[kegiatans['nama'].isin(selected_kegiatan)]

        for keg_idx, (_, keg) in enumerate(kegiatans.iterrows()):
            k4 = keg['kode4']
            keg_color = KEGIATAN_COLORS[keg_idx % len(KEGIATAN_COLORS)]
            sub_keg = df[(df['level'] == 'Sub Kegiatan') & (df['kode4'] == k4)]

            keg_target = keg['target_2026_anggaran'] or 0
            keg_realisasi = keg['realisasi_2026_anggaran'] or 0
            keg_capaian = keg['capaian_2026_anggaran_persen']
            keg_capaian_str = f"{keg_capaian:.1f}%" if pd.notna(keg_capaian) else "N/A"

            keg_realisasi_tw1 = keg['realisasi_tw1_anggaran'] or 0
            keg_realisasi_tw2 = keg['realisasi_tw2_anggaran'] or 0
            keg_realisasi_tw3 = keg['realisasi_tw3_anggaran'] or 0
            keg_realisasi_tw4 = keg['realisasi_tw4_anggaran'] or 0

            st.markdown(f"""
            <div style="background:white; border-radius:8px; padding:0.8rem 1rem; margin-bottom:0.8rem; box-shadow:0 1px 3px rgba(0,0,0,0.06); border-left:3px solid {keg_color};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:500; color:#374151;">{keg['nama']}</div>
                    <div style="display:flex; gap:1.5rem; font-size:0.85rem;">
                        <span>Target: <b style="color:{keg_color};">Rp{keg_target/1e9:.2f}M</b></span>
                        <span>Realisasi: <b style="color:#10b981;">Rp{keg_realisasi/1e9:.2f}M</b></span>
                        <span>Capaian: <b style="color:{'#10b981' if pd.notna(keg_capaian) and keg_capaian >= 50 else '#ef4444'};">{keg_capaian_str}</b></span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if not sub_keg.empty:
                # Bar chart for sub kegiatan
                sub_sorted = sub_keg.sort_values('target_2026_anggaran', ascending=True)
                labels = sub_sorted['nama'].apply(lambda x: x[:40] + '...' if len(x) > 40 else x).tolist()
                target_vals = sub_sorted['target_2026_anggaran'].fillna(0).tolist()
                realisasi_vals = sub_sorted['realisasi_2026_anggaran'].fillna(0).tolist()

                fig_sub = go.Figure()
                fig_sub.add_trace(go.Bar(
                    y=labels,
                    x=target_vals,
                    name='Target',
                    orientation='h',
                    marker_color='#e0e7ff',
                    marker_line_color=keg_color,
                    marker_line_width=1,
                    text=target_vals,
                    texttemplate='Rp%{x:,.0f}',
                    textposition='outside',
                    textfont=dict(size=10),
                    hovertemplate='<b>%{y}</b><br>Target: Rp%{x:,.0f}<extra></extra>'
                ))
                fig_sub.add_trace(go.Bar(
                    y=labels,
                    x=realisasi_vals,
                    name='Realisasi',
                    orientation='h',
                    marker_color=keg_color,
                    text=realisasi_vals,
                    texttemplate='Rp%{x:,.0f}',
                    textposition='outside',
                    textfont=dict(size=10, color=keg_color),
                    hovertemplate='<b>%{y}</b><br>Realisasi: Rp%{x:,.0f}<extra></extra>'
                ))
                fig_sub.update_layout(
                    barmode='group',
                    height=max(180, len(sub_keg) * 45),
                    margin=dict(l=10, r=80, t=10, b=10),
                    xaxis=dict(title='Anggaran (Rp)', gridcolor='#f3f4f6'),
                    yaxis=dict(autorange='reversed', gridcolor='#f3f4f6'),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    hovermode='y unified',
                )
                st.plotly_chart(fig_sub, use_container_width=True)

                # Small TW chart for each kegiatan
                tw_data = pd.DataFrame({
                    'Triwulan': ['TW I', 'TW II', 'TW III', 'TW IV'],
                    'Realisasi': [keg_realisasi_tw1, keg_realisasi_tw2, keg_realisasi_tw3, keg_realisasi_tw4]
                })
                fig_tw_keg = px.bar(
                    tw_data, x='Triwulan', y='Realisasi',
                    color='Triwulan',
                    color_discrete_map={'TW I': '#60a5fa', 'TW II': '#34d399', 'TW III': '#fbbf24', 'TW IV': '#f87171'},
                    text_auto='.2s',
                    height=200,
                )
                fig_tw_keg.update_traces(
                    texttemplate='Rp%{y:,.0f}',
                    textposition='outside',
                    textfont=dict(size=10),
                )
                fig_tw_keg.update_layout(
                    title=dict(text='Realisasi per Triwulan', font=dict(size=12), x=0.5),
                    showlegend=False,
                    margin=dict(l=10, r=10, t=30, b=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(gridcolor='#f3f4f6'),
                    yaxis=dict(gridcolor='#f3f4f6'),
                )
                st.plotly_chart(fig_tw_keg, use_container_width=True)

                # Detail table for sub kegiatan
                detail_data = []
                for _, sub in sub_keg.iterrows():
                    detail_data.append({
                        'Sub Kegiatan': sub['nama'],
                        'Indikator': sub['indikator'],
                        'Satuan': sub['satuan'],
                        'Target (Rp)': f"Rp {sub['target_2026_anggaran']:,.0f}" if pd.notna(sub['target_2026_anggaran']) else '-',
                        'Realisasi (Rp)': f"Rp {sub['realisasi_2026_anggaran']:,.0f}" if pd.notna(sub['realisasi_2026_anggaran']) else '-',
                        'Capaian (%)': f"{sub['capaian_2026_anggaran_persen']:.1f}%" if pd.notna(sub['capaian_2026_anggaran_persen']) else '-',
                        'Unit': sub['unit_penanggung_jawab'],
                    })
                df_detail = pd.DataFrame(detail_data)
                st.dataframe(df_detail, use_container_width=True, hide_index=True,
                    column_config={col: st.column_config.TextColumn(col, width='medium') for col in df_detail.columns})

            st.markdown("<hr style='margin:1.2rem 0; opacity:0.2;'>", unsafe_allow_html=True)

# ===================== TAB 3: PER TRIWULAN =====================
with tab3:
    st.markdown('<div class="section-title">Analisis Realisasi per Triwulan</div>', unsafe_allow_html=True)

    # Aggregate by triwulan
    tw_data = {
        'Triwulan': ['Triwulan I', 'Triwulan II', 'Triwulan III', 'Triwulan IV'],
        'Realisasi': [
            df_prog['realisasi_tw1_anggaran'].sum() or 0,
            df_prog['realisasi_tw2_anggaran'].sum() or 0,
            df_prog['realisasi_tw3_anggaran'].sum() or 0,
            df_prog['realisasi_tw4_anggaran'].sum() or 0,
        ]
    }
    df_tw = pd.DataFrame(tw_data)
    cumulative = 0
    cum_data = []
    for v in df_tw['Realisasi']:
        cumulative += v
        cum_data.append(cumulative)
    df_tw['Kumulatif'] = cum_data
    df_tw['% Target'] = df_tw['Kumulatif'] / total_target * 100

    col_tw1, col_tw2 = st.columns([3, 2])

    with col_tw1:
        fig_tw_main = go.Figure()
        fig_tw_main.add_trace(go.Bar(
            x=df_tw['Triwulan'],
            y=df_tw['Realisasi'],
            name='Realisasi',
            marker_color=TW_COLORS,
            text=df_tw['Realisasi'].apply(lambda x: f'Rp{x/1e9:.2f}M' if x > 0 else 'Rp 0'),
            textposition='outside',
            textfont=dict(size=12),
            hovertemplate='<b>%{x}</b><br>Realisasi: Rp%{y:,.0f}<extra></extra>'
        ))
        fig_tw_main.add_trace(go.Scatter(
            x=df_tw['Triwulan'],
            y=df_tw['Kumulatif'],
            name='Kumulatif',
            yaxis='y2',
            mode='lines+markers+text',
            text=df_tw['Kumulatif'].apply(lambda x: f'Rp{x/1e9:.2f}M'),
            textposition='top center',
            line=dict(color='#6366f1', width=3),
            marker=dict(color='#6366f1', size=10, symbol='circle'),
            hovertemplate='<b>%{x}</b><br>Kumulatif: Rp%{y:,.0f}<extra></extra>'
        ))
        fig_tw_main.add_hline(
            y=total_target, line_dash='dash', line_color='#ef4444',
            annotation_text=f'Target: Rp{total_target/1e9:.2f}M',
            annotation_font=dict(color='#ef4444', size=11),
            line_width=2
        )
        fig_tw_main.update_layout(
            xaxis_tickangle=0,
            yaxis=dict(title='Realisasi (Rp)', gridcolor='#f3f4f6'),
            yaxis2=dict(title='Kumulatif (Rp)', overlaying='y', side='right', gridcolor='#f3f4f6'),
            legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='right', x=1),
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=60, t=40, b=40),
            height=450,
        )
        st.plotly_chart(fig_tw_main, use_container_width=True)

    with col_tw2:
        fig_tw_pie = go.Figure(data=[go.Pie(
            labels=df_tw['Triwulan'],
            values=df_tw['Realisasi'],
            marker=dict(colors=TW_COLORS, line=dict(color='white', width=2)),
            hole=0.5,
            textinfo='label+percent',
            textfont=dict(size=12),
            hovertemplate='<b>%{label}</b><br>Rp%{value:,.0f}<extra></extra>'
        )])
        fig_tw_pie.update_layout(
            title=dict(text='<b>Proporsi Realisasi per Triwulan</b>', font=dict(size=14), x=0.5),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=50, b=20),
            height=400,
            annotations=[dict(text=f'Rp{total_realisasi/1e9:.2f}M', x=0.5, y=0.5, font=dict(size=14, color='#374151'), showarrow=False)]
        )
        st.plotly_chart(fig_tw_pie, use_container_width=True)

    # TW per program
    st.markdown('<div class="section-title">Realisasi per Triwulan per Program</div>', unsafe_allow_html=True)

    df_prog_tw = df[df['level'] == 'Program'].copy()
    if selected_program != 'Semua Program':
        df_prog_tw = df_prog_tw[df_prog_tw['nama'] == selected_program]

    fig_tw_prog = go.Figure()
    for idx, (_, prog) in enumerate(df_prog_tw.iterrows()):
        prog_color = PROGRAM_COLORS.get(prog['nama'], KEGIATAN_COLORS[idx % len(KEGIATAN_COLORS)])
        tw_vals = [
            prog['realisasi_tw1_anggaran'] or 0,
            prog['realisasi_tw2_anggaran'] or 0,
            prog['realisasi_tw3_anggaran'] or 0,
            prog['realisasi_tw4_anggaran'] or 0,
        ]
        fig_tw_prog.add_trace(go.Scatter(
            x=['TW I', 'TW II', 'TW III', 'TW IV'],
            y=tw_vals,
            name=prog['nama'],
            mode='lines+markers',
            line=dict(width=2.5),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>%{legendgroup}: Rp%{y:,.0f}<extra></extra>'
        ))
    fig_tw_prog.update_layout(
        xaxis_tickangle=0,
        yaxis=dict(title='Realisasi (Rp)', gridcolor='#f3f4f6'),
        legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='right', x=1),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=30, b=40),
        height=400,
    )
    st.plotly_chart(fig_tw_prog, use_container_width=True)

    # TW detailed breakdown per kegiatan
    st.markdown('<div class="section-title">Rincian Triwulan per Kegiatan</div>', unsafe_allow_html=True)

    df_keg_tw = df_prog[df_prog['level'] == 'Kegiatan'].copy()
    if not df_keg_tw.empty:
        tw_keg_data = []
        for _, keg in df_keg_tw.iterrows():
            tw_keg_data.append({
                'Kegiatan': keg['nama'],
                'TW I': keg['realisasi_tw1_anggaran'] or 0,
                'TW II': keg['realisasi_tw2_anggaran'] or 0,
                'TW III': keg['realisasi_tw3_anggaran'] or 0,
                'TW IV': keg['realisasi_tw4_anggaran'] or 0,
                'Total': (keg['realisasi_tw1_anggaran'] or 0) +
                         (keg['realisasi_tw2_anggaran'] or 0) +
                         (keg['realisasi_tw3_anggaran'] or 0) +
                         (keg['realisasi_tw4_anggaran'] or 0),
            })
        df_tw_keg = pd.DataFrame(tw_keg_data)
        df_tw_keg_sorted = df_tw_keg.sort_values('Total', ascending=True)

        fig_tw_keg_h = go.Figure()
        for tw_name, tw_color in [('TW I', '#60a5fa'), ('TW II', '#34d399'), ('TW III', '#fbbf24'), ('TW IV', '#f87171')]:
            fig_tw_keg_h.add_trace(go.Bar(
                y=df_tw_keg_sorted['Kegiatan'],
                x=df_tw_keg_sorted[tw_name],
                name=tw_name,
                orientation='h',
                marker_color=tw_color,
                hovertemplate='<b>%{y}</b><br>%{x}<br>%{legendgroup}: Rp%{x:,.0f}<extra></extra>'
            ))
        fig_tw_keg_h.update_layout(
            barmode='stack',
            height=max(250, len(df_tw_keg_sorted) * 40),
            margin=dict(l=10, r=20, t=10, b=10),
            xaxis=dict(title='Realisasi (Rp)', gridcolor='#f3f4f6'),
            yaxis=dict(autorange='reversed', gridcolor='#f3f4f6'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='y unified',
        )
        st.plotly_chart(fig_tw_keg_h, use_container_width=True)

    # TW table
    st.markdown('<div class="sub-section-title">Tabel Realisasi per Triwulan</div>', unsafe_allow_html=True)
    tw_table_data = df_prog[df_prog['level'].isin(['Kegiatan', 'Sub Kegiatan'])][
        ['nama', 'level', 'target_2026_anggaran', 'realisasi_tw1_anggaran',
         'realisasi_tw2_anggaran', 'realisasi_tw3_anggaran', 'realisasi_tw4_anggaran',
         'realisasi_2026_anggaran', 'capaian_2026_anggaran_persen']
    ].copy()
    tw_table_data.columns = [
        'Nama', 'Level', 'Target', 'TW I', 'TW II', 'TW III', 'TW IV',
        'Total Realisasi', 'Capaian %'
    ]
    for col in ['Target', 'TW I', 'TW II', 'TW III', 'TW IV', 'Total Realisasi']:
        tw_table_data[col] = tw_table_data[col].apply(
            lambda x: f'Rp {x:,.0f}' if pd.notna(x) and x != 0 else '-'
        )
    tw_table_data['Capaian %'] = tw_table_data['Capaian %'].apply(
        lambda x: f'{x:.1f}%' if pd.notna(x) else '-'
    )
    st.dataframe(tw_table_data, use_container_width=True, hide_index=True,
        column_config={col: st.column_config.TextColumn(col, width='medium') for col in tw_table_data.columns})

# ===================== TAB 4: TABEL DATA =====================
with tab4:
    st.markdown('<div class="section-title">Data Lengkap</div>', unsafe_allow_html=True)

    col_filter1, col_filter2, _ = st.columns([1, 1, 2])
    with col_filter1:
        level_filter = st.selectbox('Level', ['Semua', 'Program', 'Kegiatan', 'Sub Kegiatan'],
            key='level_filter')
    with col_filter2:
        sort_by = st.selectbox('Urut Berdasarkan',
            ['Nama', 'Target Anggaran', 'Realisasi Anggaran', 'Capaian %'],
            key='sort_by')

    df_table = df_prog.copy()
    if level_filter != 'Semua':
        df_table = df_table[df_table['level'] == level_filter]

    table_data = df_table[['nama', 'level', 'program_nama', 'kegiatan_nama', 'indikator',
                           'target_2026_anggaran', 'realisasi_2026_anggaran',
                           'capaian_2026_anggaran_persen', 'capaian_2026_kinerja_persen',
                           'unit_penanggung_jawab']].copy()
    table_data.columns = ['Nama', 'Level', 'Program', 'Kegiatan', 'Indikator',
                          'Target (Rp)', 'Realisasi (Rp)', 'Capaian Anggaran (%)',
                          'Capaian Kinerja (%)', 'Unit']

    for col in ['Target (Rp)', 'Realisasi (Rp)']:
        table_data[col] = table_data[col].apply(lambda x: f'Rp {x:,.0f}' if pd.notna(x) else '-')
    for col in ['Capaian Anggaran (%)', 'Capaian Kinerja (%)']:
        table_data[col] = table_data[col].apply(lambda x: f'{x:.1f}%' if pd.notna(x) else '-')

    if sort_by == 'Target Anggaran':
        sort_col = 'Target (Rp)'
    elif sort_by == 'Realisasi Anggaran':
        sort_col = 'Realisasi (Rp)'
    elif sort_by == 'Capaian %':
        sort_col = 'Capaian Anggaran (%)'
    else:
        sort_col = 'Nama'
    table_data = table_data.sort_values(sort_col)

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            'Nama': st.column_config.TextColumn('Nama', width='large'),
            'Program': st.column_config.TextColumn('Program', width='medium'),
        }
    )

    csv_data = table_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label='⬇️ Download CSV',
        data=csv_data,
        file_name=f'dashboard_renja_data_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
        type='secondary',
    )

st.markdown("""
<div style="text-align:center; padding:2rem 0 0.5rem 0; opacity:0.5; font-size:0.75rem; color:#9ca3af;">
    Dashboard Renja BKPSDM Kota Cirebon — Data Evaluasi RKPD dan Renja 2026
</div>
""", unsafe_allow_html=True)
