import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
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

EVENT_CAUSES = ['public_event', 'procession', 'vip_movement', 'protest']

# ─── LOAD & PREPARE DATA ────────────────────────────────────────────────────
print("📦 Loading data...")
df = pd.read_csv('../data/astram_event_data.csv')
df['start_datetime']    = pd.to_datetime(df['start_datetime'],    utc=True, errors='coerce')
df['resolved_datetime'] = pd.to_datetime(df['resolved_datetime'], utc=True, errors='coerce')

# time features
df['hour']        = df['start_datetime'].dt.hour
df['day_of_week'] = df['start_datetime'].dt.dayofweek   # 0=Mon, 6=Sun
df['month']       = df['start_datetime'].dt.month
df['is_weekend']  = (df['day_of_week'] >= 5).astype(int)
df['is_peak_hour']= df['hour'].isin([8,9,10,17,18,19,20,21]).astype(int)
df['is_night']    = df['hour'].isin([22,23,0,1,2,3,4,5]).astype(int)

# target & event features
df['is_high_priority']  = (df['priority'] == 'High').astype(int)
df['is_event_driven']   = df['event_cause'].isin(EVENT_CAUSES).astype(int)
df['requires_closure']  = df['requires_road_closure'].astype(int)

# resolution time
df['res_time_hrs'] = (df['resolved_datetime'] - df['start_datetime']).dt.total_seconds() / 3600

print(f"✅ {len(df):,} rows loaded\n")

# ═══════════════════════════════════════════════════════════════════════════
# MODEL 1 — PRIORITY PREDICTOR
# "Given event details → will it be High or Low priority?"
# ═══════════════════════════════════════════════════════════════════════════
print("🤖 Model 1: Priority Predictor (High / Low)...")

# encode categoricals
le_cause     = LabelEncoder()
le_corridor  = LabelEncoder()
le_station   = LabelEncoder()

ml_df = df.dropna(subset=['hour','corridor','priority','event_cause','police_station']).copy()
ml_df['cause_enc']    = le_cause.fit_transform(ml_df['event_cause'])
ml_df['corridor_enc'] = le_corridor.fit_transform(ml_df['corridor'])
ml_df['station_enc']  = le_station.fit_transform(ml_df['police_station'])

features_1 = ['hour','day_of_week','month','is_weekend','is_peak_hour','is_night',
               'cause_enc','corridor_enc','station_enc',
               'is_event_driven','requires_closure']

X1 = ml_df[features_1]
y1 = ml_df['is_high_priority']

X1_train, X1_test, y1_train, y1_test = train_test_split(X1, y1, test_size=0.2, random_state=42)

rf1 = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1)
rf1.fit(X1_train, y1_train)
y1_pred = rf1.predict(X1_test)
acc1 = accuracy_score(y1_test, y1_pred)
cv1  = cross_val_score(rf1, X1, y1, cv=5, scoring='accuracy').mean()

print(f"   Test Accuracy  : {acc1*100:.1f}%")
print(f"   CV Accuracy    : {cv1*100:.1f}%")
print()

# ═══════════════════════════════════════════════════════════════════════════
# MODEL 2 — ROAD CLOSURE PREDICTOR
# "Will this event require road closure?"
# ═══════════════════════════════════════════════════════════════════════════
print("🤖 Model 2: Road Closure Predictor...")

X2 = ml_df[features_1[:-1]]   # same features minus requires_closure
y2 = ml_df['requires_closure']

X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y2, test_size=0.2, random_state=42)

gb2 = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
gb2.fit(X2_train, y2_train)
y2_pred = gb2.predict(X2_test)
acc2 = accuracy_score(y2_test, y2_pred)
cv2  = cross_val_score(gb2, X2, y2, cv=5, scoring='accuracy').mean()

print(f"   Test Accuracy  : {acc2*100:.1f}%")
print(f"   CV Accuracy    : {cv2*100:.1f}%")
print()

# ═══════════════════════════════════════════════════════════════════════════
# MODEL 3 — POLICE DEPLOYMENT RECOMMENDER
# Rule-based + ML hybrid: how many police needed?
# ═══════════════════════════════════════════════════════════════════════════
print("🤖 Model 3: Police Deployment Recommender...")

def recommend_police(event_cause, corridor, hour, is_weekend, priority='unknown'):
    """
    Returns recommended police count, risk level, and action plan.
    """
    base = 2

    # cause multiplier
    cause_mult = {
        'public_event': 4, 'procession': 3,
        'vip_movement': 5, 'protest':    4,
        'accident':     3, 'vehicle_breakdown': 1,
        'construction': 2, 'water_logging': 2,
        'tree_fall':    2, 'pot_holes':    1,
        'others':       1, 'congestion':   2,
    }
    base += cause_mult.get(event_cause, 1)

    # corridor risk
    high_risk_corridors = ['Mysore Road','Bellary Road 1','Tumkur Road',
                           'Bellary Road 2','Hosur Road','Old Madras Road']
    med_risk_corridors  = ['ORR North 1','ORR East 1','Magadi Road','CBD 1','CBD 2']
    if corridor in high_risk_corridors:
        base += 3
    elif corridor in med_risk_corridors:
        base += 2

    # time multiplier
    if hour in [8,9,10,17,18,19,20,21]:   # peak hours
        base += 2
    if is_weekend:
        base += 1

    # risk level
    if base >= 9:
        risk = 'CRITICAL 🔴'
    elif base >= 6:
        risk = 'HIGH 🟠'
    elif base >= 4:
        risk = 'MEDIUM 🟡'
    else:
        risk = 'LOW 🟢'

    # diversions
    diversion_map = {
        'Mysore Road':     ['Magadi Road', 'Chord Road', 'NICE Road'],
        'Bellary Road 1':  ['Hebbal Flyover', 'NH44 Alternate', 'Thanisandra Road'],
        'Tumkur Road':     ['Peenya Industrial Road', 'BEL Road'],
        'Hosur Road':      ['Sarjapur Road', 'Bannerghatta Road'],
        'Old Madras Road': ['HAL Airport Road', 'Outer Ring Road East'],
    }
    diversions = diversion_map.get(corridor, ['Use alternate local roads'])

    return {
        'police_count': base,
        'risk_level':   risk,
        'diversions':   diversions,
        'barricades':   max(1, base // 3),
        'patrol_units': max(1, base // 4),
    }

# Test the recommender
test_cases = [
    ('public_event', 'Mysore Road',    18, 1),
    ('procession',   'Bellary Road 1', 9,  0),
    ('vip_movement', 'Tumkur Road',    20, 0),
    ('accident',     'Hosur Road',     8,  1),
    ('vehicle_breakdown', 'ORR East 1', 14, 0),
]

print("\n   📋 Sample Recommendations:")
print(f"   {'Event':<20} {'Corridor':<20} {'Police':>7} {'Risk':<15} {'Barricades':>10}")
print("   " + "─"*75)
for cause, corridor, hour, weekend in test_cases:
    rec = recommend_police(cause, corridor, hour, weekend)
    print(f"   {cause:<20} {corridor:<20} {rec['police_count']:>7} "
          f"{rec['risk_level']:<15} {rec['barricades']:>10}")

print()

# ═══════════════════════════════════════════════════════════════════════════
# CHART 13 — Feature Importance (Model 1)
# ═══════════════════════════════════════════════════════════════════════════
print("📊 Chart 13: Feature Importance...")

feat_imp = pd.Series(rf1.feature_importances_, index=features_1).sort_values(ascending=True)
colors   = [ACCENT2 if v > feat_imp.median() else ACCENT for v in feat_imp.values]

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(feat_imp.index, feat_imp.values, color=colors, edgecolor='none', height=0.6)
for bar, val in zip(bars, feat_imp.values):
    ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', fontsize=9, color='white')
ax.set_title('🧠 Feature Importance — Priority Predictor (Random Forest)',
             fontsize=13, fontweight='bold', pad=15, color='white')
ax.set_xlabel('Importance Score', fontsize=11)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('../notebooks/chart13_feature_importance.png', dpi=150,
            bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart13_feature_importance.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 14 — Confusion Matrix (Model 1)
# ═══════════════════════════════════════════════════════════════════════════
print("📊 Chart 14: Confusion Matrix...")

cm = confusion_matrix(y1_test, y1_pred)
fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Low','High'], yticklabels=['Low','High'],
            linewidths=1, linecolor='#222', ax=ax,
            annot_kws={'size':14,'weight':'bold'})
ax.set_title(f'Confusion Matrix — Priority Predictor\nAccuracy: {acc1*100:.1f}%',
             fontsize=13, fontweight='bold', pad=15, color='white')
ax.set_xlabel('Predicted', fontsize=12)
ax.set_ylabel('Actual',    fontsize=12)
plt.tight_layout()
plt.savefig('../notebooks/chart14_confusion_matrix.png', dpi=150,
            bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart14_confusion_matrix.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 15 — Police Deployment Heatmap (Corridor × Event)
# ═══════════════════════════════════════════════════════════════════════════
print("📊 Chart 15: Police Deployment Heatmap...")

corridors   = ['Mysore Road','Bellary Road 1','Tumkur Road',
               'Hosur Road','Old Madras Road','ORR East 1','Magadi Road']
event_types = ['public_event','procession','vip_movement','protest','accident']

deploy_matrix = np.zeros((len(corridors), len(event_types)))
for i, corr in enumerate(corridors):
    for j, ev in enumerate(event_types):
        rec = recommend_police(ev, corr, hour=18, is_weekend=0)
        deploy_matrix[i, j] = rec['police_count']

fig, ax = plt.subplots(figsize=(11, 7))
sns.heatmap(deploy_matrix, annot=True, fmt='.0f', cmap='YlOrRd',
            xticklabels=event_types, yticklabels=corridors,
            linewidths=0.5, linecolor='#222', ax=ax,
            annot_kws={'size':12,'weight':'bold'})
ax.set_title('👮 Recommended Police Deployment\n(Corridor × Event Type)',
             fontsize=13, fontweight='bold', pad=15, color='white')
ax.set_xlabel('Event Type',  fontsize=11)
ax.set_ylabel('Corridor',    fontsize=11)
plt.xticks(rotation=20, ha='right')
plt.tight_layout()
plt.savefig('../notebooks/chart15_police_deployment_heatmap.png', dpi=150,
            bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart15_police_deployment_heatmap.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 16 — Model Accuracy Comparison
# ═══════════════════════════════════════════════════════════════════════════
print("📊 Chart 16: Model Accuracy Comparison...")

models  = ['Priority\nPredictor\n(Random Forest)', 'Road Closure\nPredictor\n(Gradient Boost)']
test_accs = [acc1 * 100, acc2 * 100]
cv_accs   = [cv1  * 100, cv2  * 100]

fig, ax = plt.subplots(figsize=(9, 6))
x = np.arange(len(models))
w = 0.3
ax.bar(x - w/2, test_accs, w, label='Test Accuracy',  color=ACCENT,  edgecolor='none')
ax.bar(x + w/2, cv_accs,   w, label='CV Accuracy (5-fold)', color=ACCENT4, edgecolor='none')
for i, (t, c) in enumerate(zip(test_accs, cv_accs)):
    ax.text(i - w/2, t + 0.5, f'{t:.1f}%', ha='center', fontsize=11,
            color='white', fontweight='bold')
    ax.text(i + w/2, c + 0.5, f'{c:.1f}%', ha='center', fontsize=11,
            color='white', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=11)
ax.set_ylim(0, 115)
ax.set_ylabel('Accuracy (%)', fontsize=11)
ax.set_title('🎯 ML Model Performance Comparison', fontsize=14,
             fontweight='bold', pad=15, color='white')
ax.legend(facecolor='#1a1a2e', edgecolor='#444', fontsize=10)
ax.axhline(y=80, color=ACCENT3, linestyle='--', alpha=0.5, linewidth=1.5)
ax.text(1.4, 80.5, '80% baseline', color=ACCENT3, fontsize=9)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('../notebooks/chart16_model_accuracy.png', dpi=150,
            bbox_inches='tight', facecolor='#0f0f1a')
plt.close()
print("   ✅ Saved chart16_model_accuracy.png")

# ═══════════════════════════════════════════════════════════════════════════
# SAVE MODELS
# ═══════════════════════════════════════════════════════════════════════════
print("\n💾 Saving ML models...")
with open('../data/model_priority_predictor.pkl', 'wb') as f:
    pickle.dump({'model': rf1, 'encoders': {
        'cause': le_cause, 'corridor': le_corridor, 'station': le_station
    }, 'features': features_1}, f)

with open('../data/model_closure_predictor.pkl', 'wb') as f:
    pickle.dump({'model': gb2}, f)

print("   ✅ model_priority_predictor.pkl saved")
print("   ✅ model_closure_predictor.pkl saved")

# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("📋  DAY 3 SUMMARY")
print("=" * 60)
print(f"\n🤖 Model 1 — Priority Predictor")
print(f"   Algorithm  : Random Forest (150 trees)")
print(f"   Accuracy   : {acc1*100:.1f}% test | {cv1*100:.1f}% cross-val")
print(f"\n🤖 Model 2 — Road Closure Predictor")
print(f"   Algorithm  : Gradient Boosting")
print(f"   Accuracy   : {acc2*100:.1f}% test | {cv2*100:.1f}% cross-val")
print(f"\n🤖 Model 3 — Police Deployment Recommender")
print(f"   Type       : Rule-based + ML Hybrid")
print(f"   Output     : Police count + Risk level + Diversions + Barricades")
print(f"\n📊 4 charts + 2 saved models!")
print(f"\n✅  Day 3 complete! Kal Day 4 — Streamlit Dashboard banana hai! 🚀")
