import streamlit as st
import folium
from folium.plugins import DualMap
from streamlit_folium import folium_static
import geopandas as gpd
import pandas as pd
import pickle
import os
import matplotlib.pyplot as plt

# Load data
polygons_gdf = gpd.read_file((os.path.join('output_data','polygons_gdf.geojson')))
print(polygons_gdf.head())

# Ensure CRS is explicitly set if missing
if polygons_gdf.crs is None:
    polygons_gdf.set_crs('EPSG:4326', inplace=True)

# Load models
#with open('../models/kmeans_model.pkl', 'rb') as f:
#with open(os.path.join('models','kmeans_model.pkl'), 'rb') as f:
#    kmeans_model = pickle.load(f)

#with open('../models/agg_clustering_model.pkl', 'rb') as f:
#with open(os.path.join('models','agg_clustering_model.pkl'), 'rb') as f:
#    agg_model = pickle.load(f)

# --- SIDEBAR INTERACTIVO ---
with st.sidebar:
    # Foto e Información Personal
    st.image("input_data/cropped_carlos.png", width=150)  # Cambia por tu foto
    st.markdown("## About Me:")
    st.write("""
    **Name:** Carlos David García Hernández  
    **Rol:** Data Scientist @ Tec de Monterrey
             Teacher of regional economic analysis @ Universidad Nacional Autónoma de México
             
    **Contact:** [carlos.garcia.economist@gmail.com](mailto:carlos.garcia.economist@gmail.com)  
    """)

    # Enlace a LinkedIn
    st.markdown("### Connect with me:")
    st.markdown("[LinkedIn](https://www.linkedin.com/in/cgarcia8cg/)")  # Cambia tu URL
    st.markdown("[GitHub](https://cgarcia8cg.github.io/)")  # Cambia tu URL

    st.write("---")

    # Información sobre el Proyecto
    st.markdown("## About the proyect")
    st.write("""
    This project analyzes the robbery of a passer on public road with and without violence in Mexico City colonies on 2024 using k-means and agglomerative clustering to compare both methods.
    It is based on libraries such as **GeoPandas**, **Scikit-learn**, **Pysal** and **Folium** for interactive geospatial visualizations.
    """)

    st.write("**Objectives:**")
    st.markdown("- Identify clusters of robbery crime.")
    st.markdown("- Visualize the difference between methods.")
    st.markdown("- Reflect on public policies to improve the public safety.")

    st.write("---")
    st.write("Explore the results on the interactive map.")
    st.write("Pay particular attention to the way in which a method that considers geographic space improves the notion of clustering.")


# Function to assign colors to clusters
def get_cluster_colors(gdf, cluster_column):
    unique_clusters = gdf[cluster_column].unique()
    cmap = plt.get_cmap('tab10')  # Assign distinct colors for each cluster
    cluster_colors = {cluster: f'#{int(cmap(i)[0]*255):02x}{int(cmap(i)[1]*255):02x}{int(cmap(i)[2]*255):02x}' 
                      for i, cluster in enumerate(unique_clusters)}
    return cluster_colors

# Function to create folium dual map
def create_dual_map(gdf):
    kmeans_colors = get_cluster_colors(gdf, 'kmeans_cluster')
    agg_colors = get_cluster_colors(gdf, 'agg_cluster')

    # Initialize dual map
    dual_map = DualMap(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=10, control_scale=True)

    # Add polygons to both maps
    for _, row in gdf.iterrows():
        popup_content = f"""
        <b>Colonia:</b> {row['colonia']}<br>
        <b>Crime Count:</b> {row['crimen_count']}<br>
        <b>KMeans Cluster:</b> {row['kmeans_cluster']}<br>
        <b>Agglomerative Cluster:</b> {row['agg_cluster']}<br>
        """
        # KMeans Map
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x, color=kmeans_colors[row['kmeans_cluster']]: {
                'fillColor': color,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6,
            },
            highlight_function=lambda x: {'weight': 3, 'color': 'yellow'},
            tooltip=folium.Tooltip(popup_content)
        ).add_to(dual_map.m1)

        # Agglomerative Map
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x, color=agg_colors[row['agg_cluster']]: {
                'fillColor': color,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6,
            },
            highlight_function=lambda x: {'weight': 3, 'color': 'yellow'},
            tooltip=folium.Tooltip(popup_content)
        ).add_to(dual_map.m2)

    return dual_map

# Streamlit app layout
#st.set_page_config(layout="wide")  # Set wide layout for larger maps
st.title("Mexico City Robbery Crime Visualization")

# Subtitles for maps
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("K-means Clustering")
with col3:
    st.subheader("Agglomerative Clustering")

# Create dual map
dual_map = create_dual_map(polygons_gdf)
folium_static(dual_map, width=1100, height=950)