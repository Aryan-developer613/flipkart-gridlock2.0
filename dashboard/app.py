import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
import pickle
import warnings
warnings.filterwarnings('ignore')

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gridlock AI — Bengaluru Traffic Intelligence",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f0f1a; color: white; }
    .stApp { background-color: #0f0f1a; }
    .block-container { padding-top: 1rem; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #1a1a2e;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="metric-container"] label { color: #aaa !important; font-size: 13px; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #00d4ff !important; font-size: 28px; font-weight: 700;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 12px; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #1a1a2e; border-right: 1px solid #333; }
    [data-testid="stSidebar"] * { color: white !important; }

    /* Title */
    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Section headers */
    .section-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #00d4ff;
        border-left: 4px solid #00d4ff;
        padding-left: 10px;
        margin: 1rem 0 0.8rem 0;
    }

    /* Risk badge */
    .risk-critical { background:#ff4444; color:white; padding:6px 16px;
                     border-radius:20px; font-weight:700; font-size:1rem; }
    .risk-high     { background:#ff8800; color:white; padding:6px 16px;
                     border-radius:20px; font-weight:700; font-size:1rem; }
    .risk-medium   { background:#ffcc00; color:#111;  padding:6px 16px;
                     border-radius:20px; font-weight:700; font-size:1rem; }
    .risk-low      { background:#22cc66; color:white; padding:6px 16px;
                     border-radius:20px; font-weight:700; font-size:1rem; }

    /* Recommendation box */
    .rec-box {
        background: #1a1a2e;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 18px;
        margin: 8px 0;
    }
    .rec-title { color: #ffd93d; font-weight: 700; font-size: 1rem; margin-bottom: 8px; }
    .rec-value { color: white; font-size: 1.6rem; font-weight: 800; }
    .rec-sub   { color: #888; font-size: 0.85rem; margin-top: 4px; }

    /* Tab styling */
    .stTabs [data-baseweb="tab"] { color: #888; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #00d4ff !important; }

    /* Selectbox, slider */
    .stSelectbox > div, .stSlider { color: white; }
</style>
""", unsafe_allow_html=True)

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('../data/astram_event_data.csv')
    df['start_datetime']    = pd.to_datetime(df['start_datetime'],    utc=True, errors='coerce')
    df['resolved_datetime'] = pd.to_datetime(df['resolved_datetime'], utc=True, errors='coerce')
    df['hour']        = df['start_datetime'].dt.hour
    df['day_of_week'] = df['start_datetime'].dt.dayofweek
    df['month']       = df['start_datetime'].dt.month
    df['is_weekend']  = (df['day_of_week'] >= 5).astype(int)
    df['is_peak_hour']= df['hour'].isin([8,9,10,17,18,19,20,21]).astype(int)
    df['res_time_hrs']= (df['resolved_datetime'] - df['start_datetime']).dt.total_seconds() / 3600
    df['is_high_priority'] = (df['priority'] == 'High').astype(int)
    return df

@st.cache_resource
def load_model():
    try:
        with open('../data/model_priority_predictor.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return None

df       = load_data()
model_data = load_model()

EVENT_CAUSES    = ['public_event','procession','vip_movement','protest']
ALL_CORRIDORS   = sorted(df[df['corridor'] != 'Non-corridor']['corridor'].unique().tolist())
ALL_STATIONS    = sorted(df['police_station'].dropna().unique().tolist())
ALL_ZONES       = sorted(df['zone'].dropna().unique().tolist())

HIGH_RISK_CORRIDORS = ['Mysore Road','Bellary Road 1','Tumkur Road',
                       'Bellary Road 2','Hosur Road','Old Madras Road']
DIVERSION_MAP = {
    'Mysore Road':     ['Magadi Road', 'Chord Road', 'NICE Road'],
    'Bellary Road 1':  ['Hebbal Flyover', 'NH44 Alternate', 'Thanisandra Road'],
    'Tumkur Road':     ['Peenya Industrial Road', 'BEL Road'],
    'Hosur Road':      ['Sarjapur Road', 'Bannerghatta Road'],
    'Old Madras Road': ['HAL Airport Road', 'Outer Ring Road East'],
    'Bellary Road 2':  ['Hebbal Flyover', 'Yelahanka Road'],
}

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚦 Gridlock AI")
    st.markdown("**Bengaluru Traffic Intelligence**")
    st.markdown("---")
    st.markdown("### 📌 Navigation")
    page = st.radio("", [
        "🏠 Overview Dashboard",
        "🗺️ Hotspot Maps",
        "🤖 AI Recommender",
        "📊 Deep Analysis",
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### 🔎 Global Filters")
    sel_zone = st.multiselect("Zone", ALL_ZONES, default=[])
    sel_cause= st.multiselect("Event Cause", df['event_cause'].unique().tolist(), default=[])
    st.markdown("---")
    st.caption("📅 Data: Nov 2023 — Apr 2024")
    st.caption("🏙️ Source: Bengaluru Traffic Police")
    st.caption("Built for Flipkart Gridlock 2.0 🔥")

# apply global filters
fdf = df.copy()
if sel_zone:  fdf = fdf[fdf['zone'].isin(sel_zone)]
if sel_cause: fdf = fdf[fdf['event_cause'].isin(sel_cause)]

# ─── TITLE ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🚦 Gridlock AI — Bengaluru Traffic Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Event-Driven Congestion Forecasting & Smart Deployment Recommendation System</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview Dashboard":

    # KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Events",     f"{len(fdf):,}",  f"{len(fdf[fdf['is_high_priority']==1]):,} high priority")
    c2.metric("High Priority",    f"{fdf['is_high_priority'].mean()*100:.1f}%", "of all events")
    c3.metric("Event-Driven",     f"{fdf['event_cause'].isin(EVENT_CAUSES).sum()}", "planned events")
    c4.metric("Corridors Affected", f"{fdf[fdf['corridor']!='Non-corridor']['corridor'].nunique()}", "unique corridors")
    c5.metric("Police Stations",  f"{fdf['police_station'].nunique()}", "across Bengaluru")

    st.markdown("---")

    # Row 1: Event Causes + Hourly
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">🚨 Top Event Causes</div>', unsafe_allow_html=True)
        cause_counts = fdf['event_cause'].value_counts().head(8)
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#1a1a2e')
        colors = ['#ff6b6b' if i < 2 else '#00d4ff' for i in range(len(cause_counts))]
        ax.barh(cause_counts.index[::-1], cause_counts.values[::-1],
                color=colors[::-1], edgecolor='none', height=0.6)
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.tick_params(colors='white'); ax.xaxis.label.set_color('white')
        ax.grid(axis='x', alpha=0.2, color='white')
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with col2:
        st.markdown('<div class="section-header">⏰ Events by Hour of Day</div>', unsafe_allow_html=True)
        hour_counts = fdf.groupby('hour').size().reindex(range(24), fill_value=0)
        peak = hour_counts.nlargest(3).index.tolist()
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#1a1a2e')
        colors = ['#ff6b6b' if h in peak else '#00d4ff' for h in range(24)]
        ax.bar(range(24), hour_counts.values, color=colors, edgecolor='none', width=0.75)
        ax.set_xticks(range(0,24,2))
        ax.set_xticklabels([f'{h}h' for h in range(0,24,2)], color='white', fontsize=8)
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.tick_params(colors='white')
        ax.grid(axis='y', alpha=0.2, color='white')
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    # Row 2: Zone Heatmap + Day of week
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header">🗺️ Zone × Priority Heatmap</div>', unsafe_allow_html=True)
        zone_p = fdf.groupby(['zone','priority']).size().unstack(fill_value=0)
        zone_p = zone_p.loc[zone_p.sum(axis=1).nlargest(8).index]
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#1a1a2e')
        sns.heatmap(zone_p, annot=True, fmt='d', cmap='YlOrRd',
                    linewidths=0.5, linecolor='#111', ax=ax,
                    annot_kws={'size':10,'weight':'bold'})
        ax.tick_params(colors='white')
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with col4:
        st.markdown('<div class="section-header">📅 Events by Day of Week</div>', unsafe_allow_html=True)
        day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        day_counts = fdf['day_name'].value_counts().reindex(
            [d for d in day_order if d in fdf['day_name'].unique()], fill_value=0)
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#1a1a2e')
        colors = ['#ff6b6b' if d in ['Friday','Saturday'] else '#00d4ff' for d in day_counts.index]
        ax.bar(day_counts.index, day_counts.values, color=colors, edgecolor='none', width=0.6)
        ax.set_xticklabels(day_counts.index, rotation=30, ha='right', color='white', fontsize=9)
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.tick_params(colors='white')
        ax.grid(axis='y', alpha=0.2, color='white')
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    # Top Corridors Table
    st.markdown('<div class="section-header">🛣️ Top Risk Corridors</div>', unsafe_allow_html=True)
    corridor_stats = fdf[fdf['corridor'] != 'Non-corridor'].groupby('corridor').agg(
        Total_Events=('id','count'),
        High_Priority=('priority', lambda x: (x=='High').sum()),
        Event_Driven=('event_cause', lambda x: x.isin(EVENT_CAUSES).sum()),
    ).reset_index()
    corridor_stats['Risk_Score'] = (
        corridor_stats['Total_Events']   * 1.0 +
        corridor_stats['High_Priority']  * 2.0 +
        corridor_stats['Event_Driven']   * 3.0
    )
    corridor_stats = corridor_stats.sort_values('Risk_Score', ascending=False).head(10)
    corridor_stats['Risk_Level'] = corridor_stats['Risk_Score'].apply(
        lambda x: '🔴 Critical' if x > 1500 else '🟠 High' if x > 800 else '🟡 Medium'
    )
    st.dataframe(corridor_stats.reset_index(drop=True), use_container_width=True, height=300)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — HOTSPOT MAPS
# ════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Hotspot Maps":
    st.markdown('<div class="section-header">🗺️ Interactive Traffic Hotspot Maps</div>', unsafe_allow_html=True)

    map_type = st.selectbox("Select Map Type", [
        "🔥 All Events Heatmap",
        "📍 Event-Driven Incidents",
        "🚨 High Priority Hotspots",
    ])

    df_geo = fdf[(fdf['latitude'].between(12.7,13.2)) & (fdf['longitude'].between(77.4,77.8))].copy()
    st.info(f"📍 Showing **{len(df_geo):,}** events with valid GPS coordinates")

    if map_type == "🔥 All Events Heatmap":
        m = folium.Map(location=[12.97, 77.59], zoom_start=11, tiles='CartoDB dark_matter')
        heat_data = df_geo[['latitude','longitude']].dropna().values.tolist()
        HeatMap(heat_data, radius=12, blur=15,
                gradient={'0.2':'blue','0.4':'cyan','0.6':'lime','0.8':'yellow','1.0':'red'}
                ).add_to(m)
        top_c = df_geo[df_geo['corridor']!='Non-corridor'].groupby('corridor').agg(
            count=('id','count'), lat=('latitude','mean'), lon=('longitude','mean')
        ).nlargest(5,'count').reset_index()
        for _, row in top_c.iterrows():
            folium.Marker([row['lat'],row['lon']],
                popup=folium.Popup(f"<b>{row['corridor']}</b><br>{row['count']} events",max_width=200),
                icon=folium.Icon(color='red',icon='exclamation-sign',prefix='glyphicon')
            ).add_to(m)
        st_folium(m, width=None, height=550, use_container_width=True)

    elif map_type == "📍 Event-Driven Incidents":
        event_geo = df_geo[df_geo['event_cause'].isin(EVENT_CAUSES)]
        m = folium.Map(location=[12.97, 77.59], zoom_start=11, tiles='CartoDB dark_matter')
        color_map = {'public_event':'orange','procession':'blue','vip_movement':'purple','protest':'red'}
        cluster = MarkerCluster().add_to(m)
        for _, row in event_geo.iterrows():
            cause = row['event_cause']
            folium.Marker([row['latitude'],row['longitude']],
                popup=folium.Popup(
                    f"<b>{cause.upper()}</b><br>Priority: {row['priority']}<br>"
                    f"Corridor: {row['corridor']}<br>Station: {row['police_station']}",
                    max_width=220),
                icon=folium.Icon(color=color_map.get(cause,'gray'),icon='info-sign',prefix='glyphicon')
            ).add_to(cluster)
        st_folium(m, width=None, height=550, use_container_width=True)
        st.info(f"🎯 Showing {len(event_geo)} event-driven incidents (public events, processions, VIP, protests)")

    elif map_type == "🚨 High Priority Hotspots":
        high_geo = df_geo[df_geo['priority']=='High']
        m = folium.Map(location=[12.97, 77.59], zoom_start=11, tiles='CartoDB dark_matter')
        HeatMap(high_geo[['latitude','longitude']].dropna().values.tolist(),
                radius=14, blur=18,
                gradient={'0.3':'yellow','0.6':'orange','1.0':'red'}
                ).add_to(m)
        st_folium(m, width=None, height=550, use_container_width=True)
        st.warning(f"🔴 {len(high_geo):,} High Priority events shown")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 — AI RECOMMENDER
# ════════════════════════════════════════════════════════════════════════════
elif page == "🤖 AI Recommender":
    st.markdown('<div class="section-header">🤖 AI-Powered Event Impact & Deployment Recommender</div>',
                unsafe_allow_html=True)
    st.markdown("Enter event details below to get AI-powered recommendations for police deployment, diversions, and risk assessment.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📋 Event Details")
        event_cause = st.selectbox("Event Type", [
            'public_event','procession','vip_movement','protest',
            'accident','vehicle_breakdown','construction','water_logging',
            'tree_fall','congestion'
        ])
        corridor = st.selectbox("Corridor / Location", ALL_CORRIDORS)
        zone     = st.selectbox("Zone", ALL_ZONES)
        hour     = st.slider("Event Hour (24h)", 0, 23, 18)
        is_weekend = st.toggle("Weekend?", value=False)
        large_crowd= st.toggle("Large Crowd Expected?", value=False)

    with col2:
        st.markdown("#### 🎯 AI Recommendation")

        # compute recommendation
        def get_recommendation(event_cause, corridor, hour, is_weekend, large_crowd):
            cause_mult = {
                'public_event':3,'procession':3,'vip_movement':5,'protest':4,
                'accident':3,'vehicle_breakdown':1,'construction':2,
                'water_logging':2,'tree_fall':2,'congestion':2,'others':1
            }
            base = 2 + cause_mult.get(event_cause, 1)
            if corridor in HIGH_RISK_CORRIDORS: base += 3
            elif corridor in ['ORR North 1','ORR East 1','Magadi Road','CBD 1','CBD 2']: base += 2
            if hour in [8,9,10,17,18,19,20,21]: base += 2
            if is_weekend:   base += 1
            if large_crowd:  base += 2

            if base >= 10: risk = ('CRITICAL', 'risk-critical', '🔴')
            elif base >= 7: risk = ('HIGH',     'risk-high',     '🟠')
            elif base >= 4: risk = ('MEDIUM',   'risk-medium',   '🟡')
            else:           risk = ('LOW',       'risk-low',      '🟢')

            diversions = DIVERSION_MAP.get(corridor, ['Use alternate local roads'])
            barricades = max(1, base // 3)
            patrol     = max(1, base // 4)
            road_closure = base >= 9 or event_cause in ['vip_movement','procession'] and base >= 6

            return {
                'police': base, 'risk': risk,
                'diversions': diversions, 'barricades': barricades,
                'patrol': patrol, 'road_closure': road_closure
            }

        rec = get_recommendation(event_cause, corridor, hour, is_weekend, large_crowd)

        # Risk badge
        r_level, r_class, r_icon = rec['risk']
        st.markdown(f'<div style="margin:10px 0"><span class="{r_class}">{r_icon} {r_level} RISK</span></div>',
                    unsafe_allow_html=True)

        # Metric cards
        m1, m2, m3 = st.columns(3)
        m1.metric("👮 Police Required", rec['police'])
        m2.metric("🚧 Barricades",      rec['barricades'])
        m3.metric("🚔 Patrol Units",    rec['patrol'])

        st.markdown("#### 🔀 Recommended Diversions")
        for d in rec['diversions']:
            st.markdown(f"- 🛣️ **{d}**")

        if rec['road_closure']:
            st.error("⚠️ **Road Closure Recommended** — Deploy barricades at entry points")
        else:
            st.success("✅ Road closure likely not needed — Traffic flow manageable")

        st.markdown("#### 📋 Action Checklist")
        checklist = [
            f"Deploy {rec['police']} police personnel",
            f"Set up {rec['barricades']} barricade point(s)",
            f"Activate {rec['patrol']} patrol unit(s)",
            f"Divert traffic via: {', '.join(rec['diversions'][:2])}",
            "Alert Bengaluru Traffic Police control room",
            "Monitor CCTV feeds on affected corridors",
        ]
        if rec['road_closure']:
            checklist.append("Issue road closure advisory on Bengaluru Traffic Police social media")
        for item in checklist:
            st.checkbox(item, value=False)

    # Scenario Comparison
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Scenario Comparison</div>', unsafe_allow_html=True)
    scenarios = [
        ('public_event', 'Mysore Road',    18, 1, True),
        ('procession',   'Bellary Road 1', 9,  0, False),
        ('vip_movement', 'Tumkur Road',    20, 0, False),
        ('accident',     'Hosur Road',     8,  1, False),
        ('vehicle_breakdown','ORR East 1', 14, 0, False),
        ('protest',      'Old Madras Road',16, 1, True),
    ]
    rows = []
    for cause, corr, hr, wknd, crowd in scenarios:
        r = get_recommendation(cause, corr, hr, wknd, crowd)
        rows.append({
            'Event Type': cause, 'Corridor': corr, 'Hour': f'{hr}:00',
            'Weekend': '✅' if wknd else '❌',
            'Police Needed': r['police'],
            'Barricades': r['barricades'],
            'Risk Level': f"{r['risk'][2]} {r['risk'][0]}",
            'Road Closure': '⚠️ Yes' if r['road_closure'] else '✅ No',
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, height=260)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 — DEEP ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
elif page == "📊 Deep Analysis":
    st.markdown('<div class="section-header">📊 Deep Analysis</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🛣️ Corridor Analysis", "👮 Station Load", "📈 Time Trends"])

    with tab1:
        corridor_stats = fdf[fdf['corridor'] != 'Non-corridor'].groupby('corridor').agg(
            Total=('id','count'),
            High=('priority', lambda x:(x=='High').sum()),
            EventDriven=('event_cause', lambda x:x.isin(EVENT_CAUSES).sum()),
            Accidents=('event_cause', lambda x:(x=='accident').sum()),
        ).reset_index()
        corridor_stats['Risk'] = (
            corridor_stats['Total']       * 1.0 +
            corridor_stats['High']        * 2.0 +
            corridor_stats['EventDriven'] * 3.0 +
            corridor_stats['Accidents']   * 2.5
        )
        top12 = corridor_stats.nlargest(12,'Risk')

        fig, ax = plt.subplots(figsize=(11, 6))
        fig.patch.set_facecolor('#1a1a2e'); ax.set_facecolor('#1a1a2e')
        colors = ['#ff6b6b' if i<3 else '#ffd93d' if i<6 else '#555' for i in range(len(top12))]
        ax.barh(top12['corridor'][::-1], top12['Risk'][::-1],
                color=colors[::-1], edgecolor='none', height=0.65)
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.tick_params(colors='white', labelsize=9)
        ax.grid(axis='x', alpha=0.2, color='white')
        ax.set_title('Corridor Risk Score', color='white', fontweight='bold', fontsize=13)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with tab2:
        station_load = fdf.groupby('police_station').agg(
            Total=('id','count'),
            High=('priority', lambda x:(x=='High').sum()),
            Events=('event_cause', lambda x:x.isin(EVENT_CAUSES).sum())
        ).nlargest(12,'Total').reset_index()

        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('#1a1a2e'); ax.set_facecolor('#1a1a2e')
        x = np.arange(len(station_load)); w = 0.28
        ax.bar(x-w,   station_load['Total'],  w, label='Total',        color='#00d4ff', edgecolor='none')
        ax.bar(x,     station_load['High'],   w, label='High Priority', color='#ff6b6b', edgecolor='none')
        ax.bar(x+w,   station_load['Events'], w, label='Event-Driven',  color='#ffd93d', edgecolor='none')
        ax.set_xticks(x)
        ax.set_xticklabels(station_load['police_station'], rotation=35, ha='right', color='white', fontsize=8)
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.tick_params(colors='white')
        ax.grid(axis='y', alpha=0.2, color='white')
        ax.legend(facecolor='#1a1a2e', edgecolor='#444', labelcolor='white', fontsize=9)
        ax.set_title('Police Station Workload', color='white', fontweight='bold', fontsize=13)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with tab3:
        # Monthly trend
        monthly = fdf.groupby(fdf['start_datetime'].dt.to_period('M')).size()
        monthly.index = monthly.index.astype(str)

        fig, ax = plt.subplots(figsize=(11, 5))
        fig.patch.set_facecolor('#1a1a2e'); ax.set_facecolor('#1a1a2e')
        ax.plot(monthly.index, monthly.values, color='#00d4ff',
                linewidth=2.5, marker='o', markersize=8,
                markerfacecolor='#ff6b6b', markeredgecolor='white', markeredgewidth=1.5)
        ax.fill_between(monthly.index, monthly.values, alpha=0.1, color='#00d4ff')
        for i, (x, y) in enumerate(zip(monthly.index, monthly.values)):
            ax.text(i, y+8, str(y), ha='center', fontsize=9, color='white', fontweight='bold')
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.tick_params(colors='white')
        ax.grid(alpha=0.2, color='white')
        ax.set_title('Monthly Event Trend', color='white', fontweight='bold', fontsize=13)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

        # Cause × Hour heatmap
        st.markdown('<div class="section-header">🕐 Event Cause × Hour Heatmap</div>', unsafe_allow_html=True)
        top_causes = fdf['event_cause'].value_counts().head(7).index
        pivot = fdf[fdf['event_cause'].isin(top_causes)].groupby(
            ['event_cause','hour']).size().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(14, 5))
        fig.patch.set_facecolor('#1a1a2e'); ax.set_facecolor('#1a1a2e')
        sns.heatmap(pivot, cmap='YlOrRd', linewidths=0.3, linecolor='#111',
                    ax=ax, annot=True, fmt='d', annot_kws={'size':8})
        ax.tick_params(colors='white', labelsize=9)
        ax.set_title('Event Cause vs Hour of Day', color='white', fontweight='bold', fontsize=12)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()
