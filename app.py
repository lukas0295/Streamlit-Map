import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import re

st.set_page_config(layout="wide")
st.title("📍 Live-Karte: Meldungen aus dem Google Sheet")

# 🔗 Google Sheet CSV-Link
sheet_url = "https://docs.google.com/spreadsheets/d/1Mr7nP-NOc_6YiS2eKsESH4pwJdaz6N3AJEX53iTW3iY/export?format=csv"

# 📥 Daten laden
data = pd.read_csv(sheet_url)

# 🛠️ Robuste Umrechnung der Koordinaten
def format_lat(val):
    """Erwartet z.B. 519617818 und gibt 51.9618 zurück"""
    if pd.isnull(val):
        return None
    val = re.sub(r"[^\d]", "", str(val))
    if len(val) < 6:
        return None
    return float(val[:2] + "." + val[2:6])

def format_lon(val):
    """Erwartet z.B. 76285726 und gibt 7.6286 zurück"""
    if pd.isnull(val):
        return None
    val = re.sub(r"[^\d]", "", str(val))
    if len(val) < 5:
        return None
    return float(val[:1] + "." + val[1:5])

# Koordinaten bereinigen
data["Latitude"] = data["Latitude"].apply(format_lat)
data["Longitude"] = data["Longitude"].apply(format_lon)

# 📅 Datum umformatieren
data["Datum"] = pd.to_datetime(data["Datum"], dayfirst=True, errors="coerce").dt.strftime("%d.%m.%Y")

# 🗺️ Karte erzeugen
m = folium.Map(location=[51.9625, 7.6256], zoom_start=13)

# 🎨 Farben nach Typ
type_color_mapping = {
    "Verbal": "orange",
    "Physisch": "darkred",
    "Schreien": "lightgreen"
}
default_color = "gray"

# 📍 Marker hinzufügen
for _, row in data.iterrows():
    if pd.notnull(row["Latitude"]) and pd.notnull(row["Longitude"]):
        popup = f"""
        <b>Datum:</b> {row['Datum']}<br>
        <b>Adresse:</b> {row['Adresse']}<br>
        <b>Typ:</b> {row['Type']}<br>
        <b>Zitat:</b> {row['Quote']}
        """
        color = type_color_mapping.get(row["Type"], default_color)
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(popup, max_width=300),
            icon=folium.Icon(color=color)
        ).add_to(m)

# 🔍 Rohdaten anzeigen
with st.expander("📄 Rohdaten anzeigen"):
    st.dataframe(data)

# ❗ Ungültige Koordinaten optional anzeigen
with st.expander("❗️ Ungültige Koordinaten"):
    st.dataframe(data[data["Latitude"].isnull() | data["Longitude"].isnull()])

# 🖼️ Karte anzeigen
folium_static(m)