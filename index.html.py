import pandas as pd
import folium

from folium.plugins import MarkerCluster
from branca.element import Element

# ==================================================
# 1. LOAD DATA
# ==================================================

OPEN_FILE = "Open Barriers.xlsx"
RESOLVED_FILE = "Resolved Barriers.xlsx"

open_df = pd.read_excel(OPEN_FILE)
resolved_df = pd.read_excel(RESOLVED_FILE)

# ==================================================
# 2. CLEAN DATA
# ==================================================

for df in [open_df, resolved_df]:

    df["XCoordinate"] = pd.to_numeric(
        df["XCoordinate"],
        errors="coerce"
    )

    df["YCoordinate"] = pd.to_numeric(
        df["YCoordinate"],
        errors="coerce"
    )

    df["CostEst"] = pd.to_numeric(
        df["CostEst"],
        errors="coerce"
    )

    df.dropna(
        subset=["XCoordinate", "YCoordinate"],
        inplace=True
    )

open_df["Status"] = "Open"
resolved_df["Status"] = "Resolved"

# ==================================================
# 3. EXECUTIVE METRICS
# ==================================================

open_count = len(open_df)
resolved_count = len(resolved_df)

open_cost = open_df["CostEst"].fillna(0).sum()
resolved_cost = resolved_df["CostEst"].fillna(0).sum()

total_count = open_count + resolved_count

if total_count > 0:
    resolution_rate = (
        resolved_count /
        total_count
    ) * 100
else:
    resolution_rate = 0

# ==================================================
# 4. CREATE MAP
# ==================================================

m = folium.Map(
    location=[37.7989, -122.4662],
    zoom_start=14,
    tiles="CartoDB positron"
)

# ==================================================
# 5. EXECUTIVE SUMMARY PANEL
# ==================================================

summary_html = f"""
<div style="
position: fixed;
top: 15px;
left: 15px;
width: 340px;
z-index: 9999;
background-color: white;
padding: 15px;
border: 2px solid #444;
border-radius: 8px;
box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
font-family: Arial;
">

<h3 style="margin-top:0;">
Presidio Accessibility Dashboard
</h3>

<hr>

<b>Open Barriers</b><br>
{open_count:,}

<br><br>

<b>Resolved Barriers</b><br>
{resolved_count:,}

<br><br>

<b>Resolution Rate</b><br>
{resolution_rate:.1f}%

<br><br>

<b>Remaining Liability</b><br>
${open_cost:,.0f}

<br><br>

<b>Resolved Investment</b><br>
${resolved_cost:,.0f}

</div>
"""

m.get_root().html.add_child(
    Element(summary_html)
)

# ==================================================
# 6. OPEN BARRIERS LAYER
# ==================================================

open_cluster = MarkerCluster(
    name="Open Barriers",
    disableClusteringAtZoom=18
).add_to(m)

for _, row in open_df.iterrows():

    barrier_num = row.get("BarrierNumber", "")
    barrier_area = row.get("BarrierArea", "")
    cost = row.get("CostEst", "")

    popup_html = f"""
    <b>Status:</b> Open<br>
    <b>Barrier Number:</b> {barrier_num}<br>
    <b>Barrier Area:</b> {barrier_area}<br>
    <b>Cost Estimate:</b> ${cost:,.0f}
    """

    folium.CircleMarker(
        location=[
            row["YCoordinate"],
            row["XCoordinate"]
        ],
        radius=5,
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.7,
        weight=1,
        popup=folium.Popup(
            popup_html,
            max_width=300
        ),
        tooltip=f"Open Barrier {barrier_num}"
    ).add_to(open_cluster)

# ==================================================
# 7. RESOLVED BARRIERS LAYER
# ==================================================

resolved_cluster = MarkerCluster(
    name="Resolved Barriers",
    disableClusteringAtZoom=18
).add_to(m)

for _, row in resolved_df.iterrows():

    barrier_num = row.get("BarrierNumber", "")
    barrier_area = row.get("BarrierArea", "")
    cost = row.get("CostEst", "")

    popup_html = f"""
    <b>Status:</b> Resolved<br>
    <b>Barrier Number:</b> {barrier_num}<br>
    <b>Barrier Area:</b> {barrier_area}<br>
    <b>Cost Estimate:</b> ${cost:,.0f}
    """

    folium.CircleMarker(
        location=[
            row["YCoordinate"],
            row["XCoordinate"]
        ],
        radius=5,
        color="green",
        fill=True,
        fill_color="green",
        fill_opacity=0.7,
        weight=1,
        popup=folium.Popup(
            popup_html,
            max_width=300
        ),
        tooltip=f"Resolved Barrier {barrier_num}"
    ).add_to(resolved_cluster)

# ==================================================
# 8. FIT TO ALL DATA
# ==================================================

combined = pd.concat(
    [open_df, resolved_df],
    ignore_index=True
)

bounds = [
    [
        combined["YCoordinate"].min(),
        combined["XCoordinate"].min()
    ],
    [
        combined["YCoordinate"].max(),
        combined["XCoordinate"].max()
    ]
]

m.fit_bounds(bounds)

# ==================================================
# 9. LAYER CONTROL
# ==================================================

folium.LayerControl(
    collapsed=False
).add_to(m)

# ==================================================
# 10. SAVE
# ==================================================

output_file = (
    "Presidio_Accessibility_Dashboard.html"
)

m.save(output_file)

print(f"Saved: {output_file}")