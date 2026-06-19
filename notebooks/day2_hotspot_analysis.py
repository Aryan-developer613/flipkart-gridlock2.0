import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import folium
from folium.plugins import HeatMap, MarkerCluster
import warnings
warnings.filterwarnings('ignore')

# ─── SETTINGS ───────────────────────────────────────────────────────────────
plt.rcParams['figure.facecolor'] = '#0f0f1a'
plt.rcParams['axes.facecolor']   = '#1a1a2e'
plt.rcParams['text.color']       = 'white'
plt.rcParams['axes.labelcolor']  = 'white'
plt.rcParams['xtick.color']      = 'white'
plt.rcParams['ytick.color']      = 'white'
plt.rcParams['axes.edgecolor']   = '#444'
plt.rcParams['grid.color']       = '#333'

ACCENT  = '#00d4ff'
ACCENT2 = '#ff6b6b'
ACCENT3 = '#ffd93d'
ACCENT4 = '#6bcb77'

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
print("📦 Loading data...")
df = pd.read_csv('../data/astram_event_data.csv')
df['start_datetime']    = pd.to_datetime(df['start_datetime'],    utc=True, errors='coerce')
df['resolved_datetime'] = pd.to_datetime(df['resolved_datetime'], utc=True, errors='coerce')
df['hour']      = df['start_datetime'].dt.hour
df['day_name']  = df['start_datetime'].dt.day_name()
df['month']     = df['start_datetime'].dt.month
df['res_time_hrs'] = (df['resolved_datetime'] - df['start_datetime']).dt.total_seconds() / 3600

# clean coordinates
df_geo = df[(df['latitude'].between(12.7, 13.2)) & (df['longitude'].between(77.4, 77.8))].copy()
print(f"✅ {len(df):,} total rows | {len(df_geo):,} rows with valid GPS\n")

EVENT_CAUSES = ['public_event', 'procession', 'vip_movement', 'protest']

# ═══════════════════════════════════════════════════════════════════════════════
# MAP 1 — INTERACTIVE HEATMAP (All Events)
# ═══════════════════════════════════════════════════════════════════════════════
print("🗺️  Map 1: Interactive Heatmap (All Events)...")

m1 = folium.Map(location=[12.97, 77.59], zoom_start=11,
                tiles='CartoDB dark_matter')

# heatmap layer — all events
heat_data = df_geo[['latitude','longitude']].dropna().values.tolist()
HeatMap(heat_data, radius=12, blur=15, max_zoom=13,
        gradient={'0.2':'blue','0.4':'cyan','0.6':'lime','0.8':'yellow','1.0':'red'}
        ).add_to(m1)

# mark top 5 worst corridors
top_corridors = df_geo[df_geo['corridor'] != 'Non-corridor'].groupby('corridor').agg(
    count=('id','count'),
    lat=('latitude','mean'),
    lon=('longitude','mean')
).nlargest(5,'count').reset_index()

for _, row in top_corridors.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(f"<b>{row['corridor']}</b><br>{row['count']} events", max_width=200),
        icon=folium.Icon(color='red', icon='exclamation-sign', prefix='glyphicon')
    ).add_to(m1)

m1.save('../notebooks/map1_all_events_heatmap.html')
print("   ✅ Saved map1_all_events_heatmap.html")

# ═══════════════════════════════════════════════════════════════════════════════
# MAP 2 — EVENT-DRIVEN INCIDENTS (public_event / procession / vip / protest)
# ═══════════════════════════════════════════════════════════════════════════════
print("🗺️  Map 2: Event-Driven Incidents Map...")

event_df = df_geo[df_geo['event_cause'].isin(EVENT_CAUSES)].copy()

m2 = folium.Map(location=[12.97, 77.59], zoom_start=11,
                tiles='CartoDB dark_matter')

color_map = {
    'public_event': 'orange',
    'procession':   'blue',
    'vip_movement': 'purple',
    'protest':      'red'
}
icon_map = {
    'public_event': 'star',
    'procession':   'road',
    'vip_movement': 'flag',
    'protest':      'bullhorn'
}

cluster = MarkerCluster().add_to(m2)
for _, row in event_df.iterrows():
    cause = row['event_cause']
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(
            f"<b>{cause.upper()}</b><br>"
            f"Priority: {row['priority']}<br>"
            f"Corridor: {row['corridor']}<br>"
            f"Zone: {row['zone']}<br>"
            f"Station: {row['police_station']}",
            max_width=220
        ),
        icon=folium.Icon(color=color_map.get(cause,'gray'),
                         icon=icon_map.get(cause,'info-sign'),
                         prefix='glyphicon')
    ).add_to(cluster)

# legend
legend_html = """
<div style="position:fixed; bottom:30px; left:30px; z-index:9999;
     background:#1a1a2e; padding:14px 18px; border-radius:10px;
     border:1px solid #444; font-family:Arial; color:white;">
  <b style="font-size:13px;">Event Types</b><br><br>
  <span style="color:orange;">⬤</span> Public Event &nbsp;
  <span style="color:#6699ff;">⬤</span> Procession<br><br>
  <span style="color:#a855f7;">⬤</span> VIP Movement &nbsp;
  <span style="color:#ff6b6b;">⬤</span> Protest
</div>
"""
m2.get_root().html.add_child(folium.Element(legend_html))
m2.save('../notebooks/map2_event_incidents.html')
print("   ✅ Saved map2_event_incidents.html")

# ═══════════════════════════════════════════════════════════════════════════════
# MAP 3 — HIGH PRIORITY HOTSPOTS
# ═══════════════════════════════════════════════════════════════════════════════
print("🗺️  Map 3: High Priority Hotspots...")

high_df = df_geo[df_geo['priority'] == 'High']
m3 = folium.Map(location=[12.97, 77.59], zoom_start=11, tiles='CartoDB dark_matter')
HeatMap(
    high_df[['latitude','longitude']].dropna().values.tolist(),
    radius=14, blur=18,
    gradient={'0.3':'yellow','0.6':'orange','1.0':'red'}
).add_to(m3)
m3.save('../notebooks/map3_highpriority_hotspots.html')
print("   ✅ Saved map3_highpriority_hotspots.html")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 9 — Event Impact: Avg Resolution Time
# ═══════════════════════════════════════════════════════════════════════════════
print("📊 Chart 9: Event Impact — Resolution Time...")

resolved = df[df['res_time_hrs'].between(0, 48)].copy()
cause_res = resolved.groupby('event_cause')['res_time_hrs'].mean().sort_values(ascending=False).head(10)

fig, ax = plt.subplots(figsize=(12, 6))
colors = [ACCENT2 if c in EVENT_CAUSES else ACCENT for c in cause_res.index]
bars = ax.barh(cause_res.index[::-1], cause_res.values[::-1],
               color=colors[::-1], edgecolor='none', height=0.6)
for bar, val in zip(bars, cause_res.values[::-1]):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}h', va='center', fontsize=10, color='white', fontweight='bold')
ax.set_title('⏱️ Average Resolution Time by Event Cause (hrs)', fontsize=14,
             fontweight='bold', pad=15, color='white')
ax.set_xlabel('Avg Resolution Time (hours)', fontsize=11)
ax.set_xlim(0, cause_res.max() * 1.2)
ax.grid(axis='x', alpha=0.3)
highlight = mpatches.Patch(color=ACCENT2, label='Event-Driven Causes')
normal    = mpatches.Patch(color=ACCENT,  label='Other Causes')
ax.legend(handles=[highlight, normal], facecolor='#1a1a2e', edgecolor='#444')
plt.tight_layout()
plt.savefig('../notebooks/chart9_resolution_time.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart9_resolution_time.png")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 10 — Corridor Risk Score
# ═══════════════════════════════════════════════════════════════════════════════
print("📊 Chart 10: Corridor Risk Score...")

corridor_df = df[df['corridor'] != 'Non-corridor'].copy()
corridor_stats = corridor_df.groupby('corridor').agg(
    total_events   = ('id',       'count'),
    high_priority  = ('priority', lambda x: (x == 'High').sum()),
    event_driven   = ('event_cause', lambda x: x.isin(EVENT_CAUSES).sum()),
    accidents      = ('event_cause', lambda x: (x == 'accident').sum()),
).reset_index()

# risk score = weighted sum
corridor_stats['risk_score'] = (
    corridor_stats['total_events']  * 1.0 +
    corridor_stats['high_priority'] * 2.0 +
    corridor_stats['event_driven']  * 3.0 +
    corridor_stats['accidents']     * 2.5
)
corridor_stats = corridor_stats.sort_values('risk_score', ascending=False).head(12)

fig, ax = plt.subplots(figsize=(13, 7))
bar_colors = [ACCENT2 if i < 3 else ACCENT3 if i < 6 else '#555'
              for i in range(len(corridor_stats))]
bars = ax.barh(corridor_stats['corridor'][::-1],
               corridor_stats['risk_score'][::-1],
               color=bar_colors[::-1], edgecolor='none', height=0.65)
for bar, val in zip(bars, corridor_stats['risk_score'][::-1]):
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
            f'{val:.0f}', va='center', fontsize=10, color='white', fontweight='bold')

ax.set_title('🚨 Corridor Risk Score (Weighted)', fontsize=14,
             fontweight='bold', pad=15, color='white')
ax.set_xlabel('Risk Score', fontsize=11)
ax.set_xlim(0, corridor_stats['risk_score'].max() * 1.15)
ax.grid(axis='x', alpha=0.3)
r1 = mpatches.Patch(color=ACCENT2, label='🔴 Critical Risk')
r2 = mpatches.Patch(color=ACCENT3, label='🟡 High Risk')
r3 = mpatches.Patch(color='#555',  label='🟢 Moderate Risk')
ax.legend(handles=[r1, r2, r3], facecolor='#1a1a2e', edgecolor='#444', fontsize=10)
plt.tight_layout()
plt.savefig('../notebooks/chart10_corridor_risk.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart10_corridor_risk.png")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 11 — Police Station Load
# ═══════════════════════════════════════════════════════════════════════════════
print("📊 Chart 11: Police Station Load...")

station_load = df.groupby('police_station').agg(
    total=('id','count'),
    high=('priority', lambda x: (x=='High').sum()),
    events=('event_cause', lambda x: x.isin(EVENT_CAUSES).sum())
).nlargest(12,'total').reset_index()

fig, ax = plt.subplots(figsize=(13, 7))
x     = np.arange(len(station_load))
w     = 0.28
ax.bar(x - w,   station_load['total'],  w, label='Total Events', color=ACCENT,  edgecolor='none')
ax.bar(x,       station_load['high'],   w, label='High Priority', color=ACCENT2, edgecolor='none')
ax.bar(x + w,   station_load['events'], w, label='Event-Driven',  color=ACCENT3, edgecolor='none')
ax.set_xticks(x)
ax.set_xticklabels(station_load['police_station'], rotation=35, ha='right', fontsize=9)
ax.set_title('👮 Police Station Workload Analysis', fontsize=14,
             fontweight='bold', pad=15, color='white')
ax.set_ylabel('Number of Events', fontsize=11)
ax.legend(facecolor='#1a1a2e', edgecolor='#444', fontsize=10)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('../notebooks/chart11_station_load.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart11_station_load.png")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 12 — Event Cause × Hour Heatmap
# ═══════════════════════════════════════════════════════════════════════════════
print("📊 Chart 12: Event × Hour Heatmap...")

top_causes = df['event_cause'].value_counts().head(8).index.tolist()
pivot = df[df['event_cause'].isin(top_causes)].groupby(['event_cause','hour']).size().unstack(fill_value=0)
pivot = pivot.reindex(top_causes)

fig, ax = plt.subplots(figsize=(16, 6))
sns.heatmap(pivot, cmap='YlOrRd', linewidths=0.3, linecolor='#111',
            ax=ax, annot=True, fmt='d', annot_kws={'size':8})
ax.set_title('🕐 Event Cause vs Hour of Day Heatmap', fontsize=14,
             fontweight='bold', pad=15, color='white')
ax.set_xlabel('Hour of Day', fontsize=11)
ax.set_ylabel('Event Cause',  fontsize=11)
plt.tight_layout()
plt.savefig('../notebooks/chart12_cause_hour_heatmap.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart12_cause_hour_heatmap.png")

# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("📋  DAY 2 KEY INSIGHTS")
print("=" * 60)
top5 = corridor_stats.head(5)
print(f"\n🚨 Top 5 High-Risk Corridors:")
for _, r in top5.iterrows():
    print(f"   {r['corridor']:25s} → Risk Score: {r['risk_score']:.0f}")

print(f"\n📍 Event-Driven Incidents: {len(event_df)} (GPS-valid)")
print(f"   Public Events : {(df['event_cause']=='public_event').sum()}")
print(f"   Processions   : {(df['event_cause']=='procession').sum()}")
print(f"   VIP Movements : {(df['event_cause']=='vip_movement').sum()}")
print(f"   Protests      : {(df['event_cause']=='protest').sum()}")

top_station = station_load.iloc[0]
print(f"\n👮 Most Loaded Police Station: {top_station['police_station']} ({top_station['total']} events)")

print()
print("✅  4 charts + 3 interactive maps saved!")
print("🚀  Day 2 complete! Kal Day 3 — Prediction Model banana hai!")
