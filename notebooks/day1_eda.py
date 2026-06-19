import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
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

ACCENT   = '#00d4ff'
ACCENT2  = '#ff6b6b'
ACCENT3  = '#ffd93d'
ACCENT4  = '#6bcb77'

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
print("📦 Loading data...")
df = pd.read_csv('../data/astram_event_data.csv')
df['start_datetime'] = pd.to_datetime(df['start_datetime'], utc=True, errors='coerce')
df['hour']      = df['start_datetime'].dt.hour
df['day_name']  = df['start_datetime'].dt.day_name()
df['month_name']= df['start_datetime'].dt.strftime('%b %Y')
df['date']      = df['start_datetime'].dt.date

# Resolution time in hours
df['resolved_datetime'] = pd.to_datetime(df['resolved_datetime'], utc=True, errors='coerce')
df['resolution_hrs'] = (df['resolved_datetime'] - df['start_datetime']).dt.total_seconds() / 3600

print(f"✅ Loaded {len(df):,} rows | {df['start_datetime'].min().date()} → {df['start_datetime'].max().date()}")
print()

# ─── CHART 1: Event Cause Breakdown ──────────────────────────────────────────
print("📊 Chart 1: Event Causes...")
cause_counts = df['event_cause'].value_counts().head(10)
colors = [ACCENT if i == 0 else ACCENT2 if i == 1 else '#555' for i in range(len(cause_counts))]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(cause_counts.index[::-1], cause_counts.values[::-1], color=colors[::-1], edgecolor='none', height=0.6)
for bar, val in zip(bars, cause_counts.values[::-1]):
    ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
            f'{val:,}', va='center', fontsize=10, color='white', fontweight='bold')
ax.set_title('🚨 Top 10 Traffic Event Causes — Bengaluru', fontsize=15, fontweight='bold', pad=15, color='white')
ax.set_xlabel('Number of Events', fontsize=11)
ax.set_xlim(0, cause_counts.max() * 1.18)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('../notebooks/chart1_event_causes.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart1_event_causes.png")

# ─── CHART 2: Hourly Distribution ────────────────────────────────────────────
print("📊 Chart 2: Hourly Distribution...")
hour_counts = df.groupby('hour').size().reindex(range(24), fill_value=0)
peak_hours  = hour_counts.nlargest(3).index.tolist()

fig, ax = plt.subplots(figsize=(13, 5))
bar_colors = [ACCENT2 if h in peak_hours else ACCENT for h in range(24)]
ax.bar(range(24), hour_counts.values, color=bar_colors, edgecolor='none', width=0.75)
ax.set_xticks(range(24))
ax.set_xticklabels([f'{h:02d}:00' for h in range(24)], rotation=45, ha='right', fontsize=9)
ax.set_title('⏰ Traffic Events by Hour of Day', fontsize=15, fontweight='bold', pad=15, color='white')
ax.set_xlabel('Hour', fontsize=11)
ax.set_ylabel('Number of Events', fontsize=11)
ax.grid(axis='y', alpha=0.3)
peak_patch = mpatches.Patch(color=ACCENT2, label=f'Peak Hours: {sorted(peak_hours)}')
ax.legend(handles=[peak_patch], loc='upper left', facecolor='#1a1a2e', edgecolor='#444')
plt.tight_layout()
plt.savefig('../notebooks/chart2_hourly.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart2_hourly.png")

# ─── CHART 3: Day of Week ────────────────────────────────────────────────────
print("📊 Chart 3: Day of Week...")
day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
day_counts = df['day_name'].value_counts().reindex(day_order, fill_value=0)

fig, ax = plt.subplots(figsize=(10, 5))
bar_colors = [ACCENT2 if d in ['Friday','Saturday'] else ACCENT for d in day_order]
ax.bar(day_counts.index, day_counts.values, color=bar_colors, edgecolor='none', width=0.6)
for i, (d, v) in enumerate(zip(day_counts.index, day_counts.values)):
    ax.text(i, v + 10, str(v), ha='center', fontsize=10, color='white', fontweight='bold')
ax.set_title('📅 Traffic Events by Day of Week', fontsize=15, fontweight='bold', pad=15, color='white')
ax.set_ylabel('Number of Events', fontsize=11)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('../notebooks/chart3_dayofweek.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart3_dayofweek.png")

# ─── CHART 4: Top Corridors ──────────────────────────────────────────────────
print("📊 Chart 4: Top Corridors...")
corridor_counts = df[df['corridor'] != 'Non-corridor']['corridor'].value_counts().head(10)

fig, ax = plt.subplots(figsize=(12, 6))
bar_colors = [ACCENT3 if i < 3 else '#555' for i in range(len(corridor_counts))]
bars = ax.barh(corridor_counts.index[::-1], corridor_counts.values[::-1],
               color=bar_colors[::-1], edgecolor='none', height=0.6)
for bar, val in zip(bars, corridor_counts.values[::-1]):
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
            str(val), va='center', fontsize=10, color='white', fontweight='bold')
ax.set_title('🛣️ Top 10 Most Congested Corridors', fontsize=15, fontweight='bold', pad=15, color='white')
ax.set_xlabel('Number of Events', fontsize=11)
ax.set_xlim(0, corridor_counts.max() * 1.15)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('../notebooks/chart4_corridors.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart4_corridors.png")

# ─── CHART 5: Zone-wise Priority Heatmap ─────────────────────────────────────
print("📊 Chart 5: Zone × Priority Heatmap...")
zone_priority = df.groupby(['zone','priority']).size().unstack(fill_value=0)
zone_priority = zone_priority.loc[zone_priority.sum(axis=1).nlargest(10).index]

fig, ax = plt.subplots(figsize=(10, 7))
sns.heatmap(zone_priority, annot=True, fmt='d', cmap='YlOrRd',
            linewidths=0.5, linecolor='#222', ax=ax,
            annot_kws={'size': 11, 'weight': 'bold'})
ax.set_title('🗺️ Zone-wise Event Priority Heatmap', fontsize=15, fontweight='bold', pad=15, color='white')
ax.set_xlabel('Priority', fontsize=11)
ax.set_ylabel('Zone', fontsize=11)
plt.tight_layout()
plt.savefig('../notebooks/chart5_zone_heatmap.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart5_zone_heatmap.png")

# ─── CHART 6: Event Type — Planned vs Unplanned ──────────────────────────────
print("📊 Chart 6: Planned vs Unplanned by Cause...")
top_causes = df['event_cause'].value_counts().head(8).index
planned_df = df[df['event_cause'].isin(top_causes)]
cross = planned_df.groupby(['event_cause','event_type']).size().unstack(fill_value=0)
cross = cross.reindex(top_causes)

fig, ax = plt.subplots(figsize=(12, 6))
x     = np.arange(len(cross))
width = 0.35
ax.bar(x - width/2, cross.get('unplanned', 0), width, label='Unplanned', color=ACCENT2, edgecolor='none')
ax.bar(x + width/2, cross.get('planned',   0), width, label='Planned',   color=ACCENT4, edgecolor='none')
ax.set_xticks(x)
ax.set_xticklabels(cross.index, rotation=30, ha='right', fontsize=10)
ax.set_title('📌 Planned vs Unplanned Events by Cause', fontsize=15, fontweight='bold', pad=15, color='white')
ax.set_ylabel('Number of Events', fontsize=11)
ax.legend(facecolor='#1a1a2e', edgecolor='#444', fontsize=11)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('../notebooks/chart6_planned_unplanned.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart6_planned_unplanned.png")

# ─── CHART 7: Monthly Trend ───────────────────────────────────────────────────
print("📊 Chart 7: Monthly Trend...")
monthly = df.groupby('month_name').size()
month_order = ['Nov 2023','Dec 2023','Jan 2024','Feb 2024','Mar 2024','Apr 2024']
monthly = monthly.reindex([m for m in month_order if m in monthly.index])

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(monthly.index, monthly.values, color=ACCENT, linewidth=2.5, marker='o',
        markersize=8, markerfacecolor=ACCENT2, markeredgecolor='white', markeredgewidth=1.5)
ax.fill_between(monthly.index, monthly.values, alpha=0.15, color=ACCENT)
for i, (x, y) in enumerate(zip(monthly.index, monthly.values)):
    ax.text(i, y + 15, str(y), ha='center', fontsize=10, color='white', fontweight='bold')
ax.set_title('📈 Monthly Traffic Event Trend', fontsize=15, fontweight='bold', pad=15, color='white')
ax.set_ylabel('Number of Events', fontsize=11)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('../notebooks/chart7_monthly_trend.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart7_monthly_trend.png")

# ─── CHART 8: Vehicle Type Distribution ──────────────────────────────────────
print("📊 Chart 8: Vehicle Types...")
veh_counts = df['veh_type'].value_counts().dropna().head(8)
explode = [0.05] * len(veh_counts)
colors_pie = [ACCENT, ACCENT2, ACCENT3, ACCENT4, '#a78bfa', '#fb923c', '#34d399', '#f472b6']

fig, ax = plt.subplots(figsize=(9, 9))
wedges, texts, autotexts = ax.pie(
    veh_counts.values, labels=veh_counts.index, autopct='%1.1f%%',
    colors=colors_pie[:len(veh_counts)], explode=explode,
    startangle=140, pctdistance=0.75,
    textprops={'color': 'white', 'fontsize': 11},
    wedgeprops={'edgecolor': '#0f0f1a', 'linewidth': 2}
)
for at in autotexts:
    at.set_fontsize(10)
    at.set_fontweight('bold')
ax.set_title('🚌 Vehicle Type Distribution in Events', fontsize=15, fontweight='bold', pad=20, color='white')
plt.tight_layout()
plt.savefig('../notebooks/chart8_vehicle_types.png', dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart8_vehicle_types.png")

# ─── SUMMARY STATS ────────────────────────────────────────────────────────────
print()
print("=" * 55)
print("📋  KEY INSIGHTS FROM EDA")
print("=" * 55)
print(f"  Total Events       : {len(df):,}")
print(f"  High Priority      : {(df['priority']=='High').sum():,} ({(df['priority']=='High').mean()*100:.1f}%)")
print(f"  Top Cause          : {df['event_cause'].value_counts().index[0]} ({df['event_cause'].value_counts().iloc[0]:,})")
print(f"  Worst Corridor     : {df[df['corridor']!='Non-corridor']['corridor'].value_counts().index[0]}")
print(f"  Worst Zone         : {df['zone'].value_counts().index[0]}")
print(f"  Peak Hour          : {hour_counts.idxmax()}:00")
print(f"  Busiest Day        : {df['day_name'].value_counts().index[0]}")
print(f"  Public Events      : {(df['event_cause']=='public_event').sum()}")
print(f"  Processions        : {(df['event_cause']=='procession').sum()}")
print(f"  VIP Movements      : {(df['event_cause']=='vip_movement').sum()}")
print()
print("✅  All 8 charts saved in notebooks/ folder!")
print("🚀  Day 1 complete! Kal Day 2 — Hotspot Analysis shuru karenge.")
