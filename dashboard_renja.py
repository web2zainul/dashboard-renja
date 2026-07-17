import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import csv
import re

st.set_page_config(page_title="Dashboard Renja BKPSDM Kota Cirebon", layout="wide")
st.title("Dashboard Renja BKPSDM Kota Cirebon - 2026")

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
            return str(val).strip().replace('\n', ' ')

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
        
        row = {
            'kode1': clean_str(r[0]),
            'kode2': clean_str(r[1]),
            'kode3': clean_str(r[2]),
            'kode4': clean_str(r[3]),
            'nama': clean_str(r[5]),
            'indikator': clean_str(r[6]),
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

df = load_data()

# ============= SIDEBAR =============
st.sidebar.header("Filter")
level_filter = st.sidebar.selectbox("Level", ['Semua', 'Program', 'Kegiatan', 'Sub Kegiatan'])

if level_filter != 'Semua':
    df_filtered = df[df['level'] == level_filter].copy()
else:
    df_filtered = df.copy()

programs = sorted([p for p in df_filtered['nama'].unique() if p])
program_filter = st.sidebar.multiselect("Cari Program/Kegiatan", programs, default=[])
if program_filter:
    df_filtered = df_filtered[df_filtered['nama'].isin(program_filter)]

# ============= METRICS =============
st.subheader("Ringkasan")
col1, col2, col3, col4 = st.columns(4)

total_anggaran = df_filtered['target_2026_anggaran'].sum()
realisasi_anggaran = df_filtered['realisasi_2026_anggaran'].sum()
total_kegiatan = len(df_filtered[df_filtered['level'] == 'Kegiatan'])
avg_capaian_kinerja = df_filtered[df_filtered['capaian_2026_kinerja_persen'].notna()]['capaian_2026_kinerja_persen'].mean()

with col1:
    st.metric("Total Anggaran 2026", f"Rp {total_anggaran:,.0f}" if total_anggaran else "N/A")
with col2:
    st.metric("Realisasi Anggaran 2026", f"Rp {realisasi_anggaran:,.0f}" if realisasi_anggaran else "N/A")
with col3:
    st.metric("Jumlah Kegiatan", total_kegiatan)
with col4:
    st.metric("Rata-rata Capaian Kinerja", f"{avg_capaian_kinerja:.1f}%" if not pd.isna(avg_capaian_kinerja) else "N/A")

# ============= CHART 1: Anggaran per Program =============
st.subheader("Anggaran per Program")

df_program = df[df['level'] == 'Program'].copy()
if not df_program.empty:
    fig1 = px.bar(
        df_program,
        x='nama',
        y='target_2026_anggaran',
        title='Target Anggaran 2026 per Program',
        labels={'nama': 'Program', 'target_2026_anggaran': 'Anggaran (Rp)'},
        text_auto='.0s',
        color='nama',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig1.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig1, width='stretch')

# ============= CHART 2: Realisasi per Triwulan (Kegiatan) =============
st.subheader("Realisasi Anggaran per Triwulan (Kegiatan)")

df_kegiatan = df[df['level'].isin(['Kegiatan', 'Program'])].copy()
if not df_kegiatan.empty:
    df_tw = df_kegiatan.melt(
        id_vars=['nama'],
        value_vars=['realisasi_tw1_anggaran', 'realisasi_tw2_anggaran', 'realisasi_tw3_anggaran', 'realisasi_tw4_anggaran'],
        var_name='Triwulan',
        value_name='Anggaran'
    )
    df_tw['Triwulan'] = df_tw['Triwulan'].map({
        'realisasi_tw1_anggaran': 'TW I',
        'realisasi_tw2_anggaran': 'TW II',
        'realisasi_tw3_anggaran': 'TW III',
        'realisasi_tw4_anggaran': 'TW IV'
    })
    df_tw = df_tw.dropna(subset=['Anggaran'])
    
    if not df_tw.empty:
        fig2 = px.bar(
            df_tw,
            x='nama',
            y='Anggaran',
            color='Triwulan',
            title='Realisasi Anggaran per Triwulan',
            labels={'nama': 'Kegiatan', 'Anggaran': 'Rp'},
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, width='stretch')

# ============= CHART 3: Capaian Kinerja (%) =============
st.subheader("Capaian Kinerja 2026 (%)")

df_capaian = df_filtered[df_filtered['capaian_2026_kinerja_persen'].notna()].copy()
if not df_capaian.empty:
    fig3 = px.bar(
        df_capaian,
        x='nama',
        y='capaian_2026_kinerja_persen',
        title='Capaian Kinerja 2026 per Kegiatan (%)',
        labels={'nama': 'Kegiatan', 'capaian_2026_kinerja_persen': 'Capaian (%)'},
        text='capaian_2026_kinerja_persen',
        color='capaian_2026_kinerja_persen',
        color_continuous_scale='RdYlGn',
        range_color=[0, 120]
    )
    fig3.update_layout(xaxis_tickangle=-45)
    fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig3, width='stretch')

# ============= CHART 4: Pie Chart Anggaran per Kegiatan =============
st.subheader("Distribusi Anggaran per Kegiatan")

df_kegiatan_pie = df[df['level'].isin(['Kegiatan', 'Program'])].dropna(subset=['target_2026_anggaran'])
if not df_kegiatan_pie.empty:
    fig4 = px.pie(
        df_kegiatan_pie,
        values='target_2026_anggaran',
        names='nama',
        title='Proporsi Anggaran 2026'
    )
    st.plotly_chart(fig4, width='stretch')

# ============= CHART 5: Perbandingan Target vs Realisasi =============
st.subheader("Target vs Realisasi Anggaran 2026")

df_compare = df_filtered[df_filtered['level'].isin(['Kegiatan', 'Program'])].copy()
df_compare = df_compare.dropna(subset=['target_2026_anggaran', 'realisasi_2026_anggaran'])
if not df_compare.empty:
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=df_compare['nama'],
        y=df_compare['target_2026_anggaran'],
        name='Target',
        marker_color='lightblue'
    ))
    fig5.add_trace(go.Bar(
        x=df_compare['nama'],
        y=df_compare['realisasi_2026_anggaran'],
        name='Realisasi',
        marker_color='orange'
    ))
    fig5.update_layout(
        title='Perbandingan Target vs Realisasi Anggaran 2026',
        xaxis_tickangle=-45,
        barmode='group'
    )
    st.plotly_chart(fig5, width='stretch')

# ============= DATA TABLE =============
with st.expander("Lihat Data Mentah"):
    st.dataframe(df_filtered, width='stretch')

# ============= CHART 6: Capaian per Triwulan (line) =============
st.subheader("Perkembangan Realisasi Anggaran per Triwulan")

df_tw_line = df_kegiatan.melt(
    id_vars=['nama'],
    value_vars=['realisasi_tw1_anggaran', 'realisasi_tw2_anggaran', 'realisasi_tw3_anggaran', 'realisasi_tw4_anggaran'],
    var_name='Triwulan',
    value_name='Anggaran'
)
df_tw_line['Triwulan'] = df_tw_line['Triwulan'].map({
    'realisasi_tw1_anggaran': 'TW I',
    'realisasi_tw2_anggaran': 'TW II',
    'realisasi_tw3_anggaran': 'TW III',
    'realisasi_tw4_anggaran': 'TW IV'
})
df_tw_line = df_tw_line.dropna(subset=['Anggaran'])

if not df_tw_line.empty:
    fig6 = px.line(
        df_tw_line,
        x='Triwulan',
        y='Anggaran',
        color='nama',
        markers=True,
        title='Trend Realisasi Anggaran per Triwulan',
        labels={'Anggaran': 'Rp', 'nama': 'Kegiatan'}
    )
    st.plotly_chart(fig6, width='stretch')
