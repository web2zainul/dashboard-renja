import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import csv
import os

st.set_page_config(page_title="Dashboard Renja BKPSDM", layout="wide")
pd.set_option('future.no_silent_downcasting', True)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main > div { padding: 0rem 1rem; }
    .kpi-card {
        background: white; border-radius: 12px; padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06); text-align: center;
        border: 1px solid #f1f5f9;
    }
    .kpi-label { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
    .kpi-value { font-size: 1.3rem; font-weight: 700; margin-top: 2px; }
    .kpi-delta { font-size: 0.72rem; color: #64748b; margin-top: 2px; }
    .sec-title {
        font-size: 1rem; font-weight: 600; color: #0f172a;
        padding-bottom: 0.4rem; border-bottom: 2px solid #e2e8f0; margin: 1.2rem 0 0.8rem 0;
    }
    .detail-card {
        background: #f8fafc; border-radius: 10px; padding: 0.7rem 1rem;
        margin-bottom: 0.5rem; border-left: 4px solid #6366f1;
    }
    .stProgress > div > div > div > div { background-color: #6366f1; }
    tr:nth-child(even) { background-color: #f8fafc; }
    th { background-color: #f1f5f9 !important; font-weight: 600 !important; font-size: 0.75rem !important; color: #475569 !important; }
    td { font-size: 0.78rem !important; }
    .badge {
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-size: 0.7rem; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, 'file.csv')

@st.cache_data
def load_data():
    rows = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        for r in csv.reader(f):
            rows.append(r)

    def _rp(v):
        if v is None: return None
        v = str(v).strip().strip('"').strip()
        if not v or v in ['-', '--', '-   ', '.', '']: return None
        v = v.replace('.', '')
        v = v.replace(',', '.')
        try: return float(v)
        except: return None

    def _num(v):
        if v is None: return None
        v = str(v).strip().strip('"').strip()
        if not v or v in ['-', '--', '-   ', '%', '.', '']: return None
        v = v.replace('%', '').strip().replace(',', '.')
        if v in ['', '.']: return None
        try: return float(v)
        except: return None

    data = []
    prog = None
    keg = None

    for r in rows:
        if len(r) < 14: continue
        nama = str(r[5]).strip() if len(r) > 5 else ''
        kode4 = str(r[3]).strip() if len(r) > 3 else ''
        kode5 = str(r[4]).strip() if len(r) > 4 else ''
        if not nama: continue
        up = nama.upper()
        is_prog = up.startswith('PROGRAM')
        is_keg = up.startswith('KEGIATAN')
        is_sub = up.startswith('SUB KEGIATAN')

        if is_prog:
            lv = 'Program'
            prog = nama
            keg = None
        elif is_keg:
            lv = 'Kegiatan'
            keg = nama
        elif is_sub:
            lv = 'Sub Kegiatan'
        elif kode5 and not is_prog and not is_keg:
            lv = 'Sub Kegiatan'
        else:
            continue

        data.append({
            'program': prog,
            'kegiatan': keg if lv == 'Sub Kegiatan' else (nama if lv == 'Kegiatan' else prog),
            'nama': nama, 'level': lv,
            'indikator': str(r[6]).strip() if len(r) > 6 else '',
            'satuan': str(r[7]).strip() if len(r) > 7 else '',
            'target_rp': _rp(r[13]) if len(r) > 13 else None,
            'tw1_rp': _rp(r[15]) if len(r) > 15 else None,
            'tw2_rp': _rp(r[17]) if len(r) > 17 else None,
            'tw3_rp': _rp(r[19]) if len(r) > 19 else None,
            'tw4_rp': _rp(r[21]) if len(r) > 21 else None,
            'realisasi_rp': _rp(r[23]) if len(r) > 23 else None,
            'capaian_persen': _num(r[25]) if len(r) > 25 else None,
            'unit': str(r[30]).strip() if len(r) > 30 else '',
        })
    return pd.DataFrame(data)

df = load_data()

for col in ['target_rp','tw1_rp','tw2_rp','tw3_rp','tw4_rp','realisasi_rp','capaian_persen']:
    df[col] = df[col].fillna(0)

df_prog = df[df['level'] == 'Program'].copy()
df_keg = df[df['level'] == 'Kegiatan'].copy()
df_sub = df[df['level'] == 'Sub Kegiatan'].copy()

def fmt(v):
    if pd.isna(v) or v == 0: return 'Rp 0'
    return f'Rp {int(v):,}'.replace(',', '.')

def pct(v):
    return f'{v:.0f}%'

def color_pct(v):
    if v >= 75: return '#10b981'
    if v >= 50: return '#f59e0b'
    return '#ef4444'

# ── HEADER ──
st.markdown("""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:2px;">
    <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6); width:6px; height:36px; border-radius:4px;"></div>
    <div>
        <div style="font-size:1.2rem; font-weight:700; color:#0f172a;">BKPSDM Kota Cirebon — Realisasi Anggaran Renja 2026</div>
        <div style="font-size:0.75rem; color:#64748b;">Badan Kepegawaian dan Pengembangan Sumber Daya Manusia</div>
    </div>
</div>
<hr style="margin:0.4rem 0 1rem 0; opacity:0.15;">
""", unsafe_allow_html=True)

# ── FILTER ──
col_f1, col_f2, col_f3, _ = st.columns([1.5, 1.5, 1, 4])
with col_f1:
    prog_list = ['Semua'] + sorted(df_prog['nama'].tolist())
    sel_prog = st.selectbox('Program', prog_list, label_visibility='collapsed')
with col_f2:
    if sel_prog != 'Semua':
        keg_list = ['Semua'] + sorted(df_keg[df_keg['program'] == sel_prog]['nama'].tolist())
    else:
        keg_list = ['Semua']
    sel_keg = st.selectbox('Kegiatan', keg_list, label_visibility='collapsed')
with col_f3:
    min_cap = st.slider('Min. Capaian', 0, 100, 0, label_visibility='collapsed')

# ── FILTER APPLY ──
df_filtered = df.copy()
if sel_prog != 'Semua':
    df_filtered = df_filtered[df_filtered['program'] == sel_prog]
if sel_keg != 'Semua':
    df_filtered = df_filtered[df_filtered['kegiatan'] == sel_keg]

df_sub_f = df_filtered[df_filtered['level'] == 'Sub Kegiatan']
df_keg_f = df_filtered[df_filtered['level'] == 'Kegiatan']

# ── KPI ──
total_target = df_filtered[df_filtered['level'] == 'Sub Kegiatan']['target_rp'].sum()
total_real = df_filtered[df_filtered['level'] == 'Sub Kegiatan']['realisasi_rp'].sum()
total_tw1 = df_filtered[df_filtered['level'] == 'Sub Kegiatan']['tw1_rp'].sum()
total_tw2 = df_filtered[df_filtered['level'] == 'Sub Kegiatan']['tw2_rp'].sum()
total_tw3 = df_filtered[df_filtered['level'] == 'Sub Kegiatan']['tw3_rp'].sum()
total_tw4 = df_filtered[df_filtered['level'] == 'Sub Kegiatan']['tw4_rp'].sum()
capaian = (total_real / total_target * 100) if total_target else 0
sisa = total_target - total_real
jml_keg = df_keg_f['nama'].nunique()

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total Anggaran</div><div class='kpi-value' style='color:#6366f1;'>{fmt(total_target)}</div><div class='kpi-delta'>Target Renja 2026</div></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Realisasi</div><div class='kpi-value' style='color:#10b981;'>{fmt(total_real)}</div><div class='kpi-delta'>TW I + TW II</div></div>", unsafe_allow_html=True)
with k3:
    c = color_pct(capaian)
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Capaian</div><div class='kpi-value' style='color:{c};'>{pct(capaian)}</div><div class='kpi-delta'> dari target</div></div>", unsafe_allow_html=True)
with k4:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Sisa Anggaran</div><div class='kpi-value' style='color:#f59e0b;'>{fmt(sisa)}</div><div class='kpi-delta'>belum terealisasi</div></div>", unsafe_allow_html=True)
with k5:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Kegiatan</div><div class='kpi-value' style='color:#0ea5e9;'>{jml_keg}</div><div class='kpi-delta'>total kegiatan</div></div>", unsafe_allow_html=True)
with k6:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>TW I + TW II</div><div class='kpi-value' style='color:#8b5cf6;'>{fmt(total_tw1 + total_tw2)}</div><div class='kpi-delta'>TW I: {fmt(total_tw1)} | TW II: {fmt(total_tw2)}</div></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# CHART 1: TARGET vs REALISASI PER PROGRAM
# ════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Target vs Realisasi per Program</div>', unsafe_allow_html=True)

df_sub_f_prog = df_sub_f.groupby('program').agg(
    target_rp=('target_rp', 'sum'),
    realisasi_rp=('realisasi_rp', 'sum'),
).reset_index()
df_sub_f_prog['capaian_persen'] = df_sub_f_prog.apply(
    lambda r: (r['realisasi_rp'] / r['target_rp'] * 100) if r['target_rp'] > 0 else 0, axis=1
)
if sel_prog != 'Semua':
    df_sub_f_prog = df_sub_f_prog[df_sub_f_prog['program'] == sel_prog]

if not df_sub_f_prog.empty:
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=df_sub_f_prog['program'], y=df_sub_f_prog['target_rp'],
        name='Target', marker_color='#e0e7ff', marker_line_color='#6366f1', marker_line_width=1.5,
        text=[fmt(v) for v in df_sub_f_prog['target_rp']], textposition='outside', textfont=dict(size=10),
    ))
    fig1.add_trace(go.Bar(
        x=df_sub_f_prog['program'], y=df_sub_f_prog['realisasi_rp'],
        name='Realisasi', marker_color='#6366f1',
        text=[fmt(v) for v in df_sub_f_prog['realisasi_rp']], textposition='outside', textfont=dict(size=10, color='#6366f1'),
    ))
    fig1.add_trace(go.Scatter(
        x=df_sub_f_prog['program'], y=df_sub_f_prog['capaian_persen'],
        name='Capaian %', yaxis='y2',
        mode='lines+markers+text',
        text=[pct(v) for v in df_sub_f_prog['capaian_persen']],
        textposition='top center', textfont=dict(size=10, color='#ef4444'),
        line=dict(color='#ef4444', width=2, dash='dot'),
        marker=dict(color='#ef4444', size=8),
    ))
    fig1.update_layout(
        barmode='group', xaxis_tickangle=-15,
        yaxis=dict(title='Rp', gridcolor='#f1f5f9'),
        yaxis2=dict(overlaying='y', side='right', range=[0, 120], gridcolor='#f1f5f9'),
        legend=dict(orientation='h', yanchor='bottom', y=1.08, xanchor='right', x=1),
        hovermode='x unified', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=60, t=40, b=40), height=380,
    )
    st.plotly_chart(fig1, width='stretch')

# ════════════════════════════════════════════════════════
# CHART 2: REALISASI PER TRIWULAN
# ════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Realisasi per Triwulan</div>', unsafe_allow_html=True)

tw_df = pd.DataFrame({
    'Triwulan': ['TW I', 'TW II', 'TW III', 'TW IV'],
    'Realisasi': [total_tw1, total_tw2, total_tw3, total_tw4],
})
cum = []
s = 0
for v in tw_df['Realisasi']:
    s += v
    cum.append(s)
tw_df['Kumulatif'] = cum

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=tw_df['Triwulan'], y=tw_df['Realisasi'], name='Realisasi',
    marker_color=['#60a5fa', '#34d399', '#fbbf24', '#f87171'],
    text=[fmt(v) for v in tw_df['Realisasi']],
    textposition='outside', textfont=dict(size=10),
))
fig2.add_trace(go.Scatter(
    x=tw_df['Triwulan'], y=tw_df['Kumulatif'], name='Kumulatif',
    yaxis='y2', mode='lines+markers+text',
    text=[fmt(v) for v in tw_df['Kumulatif']],
    textposition='top center', textfont=dict(size=10, color='#6366f1'),
    line=dict(color='#6366f1', width=3), marker=dict(color='#6366f1', size=10),
))
fig2.add_hline(
    y=total_target, line_dash='dash', line_color='#ef4444',
    annotation_text=f'Target: {fmt(total_target)}', annotation_font=dict(color='#ef4444', size=10),
)
fig2.update_layout(
    yaxis=dict(title='Rp', gridcolor='#f1f5f9'),
    yaxis2=dict(overlaying='y', side='right', gridcolor='#f1f5f9'),
    legend=dict(orientation='h', yanchor='bottom', y=1.08, xanchor='right', x=1),
    hovermode='x unified', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=40, r=60, t=30, b=40), height=380,
)
st.plotly_chart(fig2, width='stretch')

# ════════════════════════════════════════════════════════
# CHART 3: CAPAIAN PER KEGIATAN (sorted horizontal)
# ════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Capaian Realisasi per Kegiatan</div>', unsafe_allow_html=True)

col_chart3, col_leg3 = st.columns([4, 1.5])

with col_chart3:
    df_cap = df_keg_f.copy()
    df_cap = df_cap[df_cap['target_rp'] > 0].sort_values('capaian_persen', ascending=True)

    if not df_cap.empty:
        colors = [color_pct(v) for v in df_cap['capaian_persen']]
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=df_cap['capaian_persen'], y=df_cap['nama'],
            orientation='h',
            marker_color=colors,
            text=[pct(v) for v in df_cap['capaian_persen']],
            textposition='outside', textfont=dict(size=10),
        ))
        fig3.add_vline(x=50, line_dash='dash', line_color='#94a3b8', opacity=0.5)
        fig3.add_vline(x=75, line_dash='dash', line_color='#94a3b8', opacity=0.5)
        fig3.update_layout(
            xaxis=dict(range=[0, 120], title='Capaian (%)', gridcolor='#f1f5f9'),
            yaxis=dict(gridcolor='#f1f5f9'),
            hovermode='y unified', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=40, t=10, b=10), height=min(380, max(200, len(df_cap) * 35)),
        )
        st.plotly_chart(fig3, width='stretch')
    else:
        st.info("Tidak ada data kegiatan dengan target > 0")

with col_leg3:
    st.markdown("""
    <div style="background:#f8fafc; border-radius:10px; padding:1rem; font-size:0.8rem;">
        <div style="font-weight:600; margin-bottom:0.8rem; color:#0f172a;">Legenda</div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
            <div style="width:14px; height:14px; border-radius:3px; background:#10b981;"></div>
            <span style="color:#475569;">≥ 75% (Baik)</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
            <div style="width:14px; height:14px; border-radius:3px; background:#f59e0b;"></div>
            <span style="color:#475569;">50% – 75% (Sedang)</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
            <div style="width:14px; height:14px; border-radius:3px; background:#ef4444;"></div>
            <span style="color:#475569;">&lt; 50% (Kurang)</span>
        </div>
        <div style="margin-top:1rem; padding-top:0.8rem; border-top:1px solid #e2e8f0; color:#64748b;">
            <div>Garis putus-putus:</div>
            <div style="display:flex; align-items:center; gap:6px;">
                <div style="width:20px; height:2px; border-top:2px dashed #94a3b8;"></div>
                Target 50% dan 75%
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# CHART 4: DISTRIBUSI ANGGARAN
# ════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Distribusi Anggaran per Program</div>', unsafe_allow_html=True)

col_pie, col_treemap = st.columns([1, 1])

with col_pie:
    df_pie = df_sub.groupby('program').agg(target_rp=('target_rp', 'sum')).reset_index()
    df_pie = df_pie[df_pie['target_rp'] > 0]
    if not df_pie.empty:
        fig4a = px.pie(
            df_pie, values='target_rp', names='program',
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.45,
        )
        fig4a.update_traces(
            textposition='outside', textinfo='percent+label',
            textfont=dict(size=10),
        )
        fig4a.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10), height=320,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig4a, width='stretch')
    else:
        st.info("Tidak ada data")

with col_treemap:
    df_tm = df_filtered[df_filtered['level'].isin(['Kegiatan'])].copy()
    df_tm = df_tm.groupby(['program','kegiatan']).agg(target_rp=('target_rp','sum'), realisasi_rp=('realisasi_rp','sum'), capaian_persen=('capaian_persen','mean')).reset_index()
    df_tm = df_tm[df_tm['target_rp'] > 0]
    if not df_tm.empty:
        df_tm['label'] = df_tm['kegiatan'].apply(lambda x: x[:40] + '...' if len(x) > 40 else x)
        df_tm['capaian_label'] = df_tm['capaian_persen'].apply(lambda x: f'{x:.0f}%')
        df_tm['text'] = df_tm.apply(lambda r: f"{r['label']}<br>{fmt(r['target_rp'])}<br>{r['capaian_label']}", axis=1)
        fig4b = px.treemap(
            df_tm, path=['program', 'kegiatan'], values='target_rp',
            color='capaian_persen',
            color_continuous_scale='RdYlGn', range_color=[0, 100],
            hover_data={'target_rp': ':,.0f', 'realisasi_rp': ':,.0f', 'capaian_persen': ':.0f'},
        )
        fig4b.update_traces(
            textinfo='label+value+percent root',
            textfont=dict(size=10),
            hovertemplate='<b>%{label}</b><br>Anggaran: Rp %{customdata[0]:,.0f}<br>Realisasi: Rp %{customdata[1]:,.0f}<br>Capaian: %{customdata[2]:.0f}%',
        )
        fig4b.update_layout(
            margin=dict(l=5, r=5, t=5, b=5), height=320,
        )
        st.plotly_chart(fig4b, width='stretch')

# ════════════════════════════════════════════════════════
# DETAIL PER PROGRAM (EXPANDER)
# ════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Rincian per Program</div>', unsafe_allow_html=True)

for prog_name in sorted(p for p in df_sub_f['program'].unique() if p):
    df_sub_prog = df_sub_f[df_sub_f['program'] == prog_name].copy()
    if df_sub_prog.empty: continue

    p_total = df_sub_prog['target_rp'].sum()
    p_real = df_sub_prog['realisasi_rp'].sum()
    p_cap = (p_real / p_total * 100) if p_total else 0

    with st.expander(f"**{prog_name}** — Target: {fmt(p_total)} — Realisasi: {fmt(p_real)} — Capaian: {pct(p_cap)}", expanded=False):
        for keg_nama in sorted(df_sub_prog['kegiatan'].unique()):
            df_sub_keg = df_sub_prog[df_sub_prog['kegiatan'] == keg_nama].copy()
            k_total = df_sub_keg['target_rp'].sum()
            k_real = df_sub_keg['realisasi_rp'].sum()
            k_cap = (k_real / k_total * 100) if k_total else 0

            st.markdown(f"""
            <div class="detail-card">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:4px;">
                    <div style="font-weight:600; font-size:0.85rem; color:#0f172a;">{keg_nama}</div>
                    <div style="display:flex; gap:1rem; font-size:0.78rem;">
                        <span>Target: <b>{fmt(k_total)}</b></span>
                        <span>Realisasi: <b style="color:#10b981;">{fmt(k_real)}</b></span>
                        <span class="badge" style="background:{color_pct(k_cap)}20; color:{color_pct(k_cap)};">{pct(k_cap)}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            tbl = df_sub_keg[['nama', 'target_rp', 'tw1_rp', 'tw2_rp', 'realisasi_rp']].copy()
            tbl = tbl[tbl['target_rp'] > 0]
            if not tbl.empty:
                tbl['Capaian'] = tbl.apply(lambda r: f"{min(r['realisasi_rp'] / r['target_rp'] * 100, 999):.0f}%" if r['target_rp'] > 0 else '0%', axis=1)
                tbl['nama'] = tbl['nama'].apply(lambda x: x.replace('Sub Kegiatan ', ''))
                tbl = tbl.rename(columns={
                    'nama': 'Sub Kegiatan', 'target_rp': 'Target (Rp)',
                    'tw1_rp': 'TW I (Rp)', 'tw2_rp': 'TW II (Rp)', 'realisasi_rp': 'Realisasi (Rp)',
                })
                for c in ['Target (Rp)', 'TW I (Rp)', 'TW II (Rp)', 'Realisasi (Rp)']:
                    tbl[c] = tbl[c].apply(lambda v: fmt(v))
                safe_keg = keg_nama.replace(' ', '_').replace(',', '').replace('/', '_')[:30]
                st.dataframe(tbl, width='stretch', hide_index=True, key=f"dt_{prog_name[:10]}_{safe_keg}")

st.markdown("""
<div style="text-align:center; padding:1.5rem 0 0.5rem 0; opacity:0.35; font-size:0.7rem; color:#94a3b8;">
    Dashboard Renja BKPSDM Kota Cirebon — Data: file.csv — Realisasi Anggaran 2026
</div>
""", unsafe_allow_html=True)
