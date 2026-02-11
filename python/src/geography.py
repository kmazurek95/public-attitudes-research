# =============================================================================
# geography.py - Geographic Enhancement Module
# =============================================================================
"""
Functions for adding geographic names and creating map visualizations.

This module provides:
1. Geographic name lookup for buurt, wijk, and gemeente
2. Shapefile loading and processing for Dutch administrative boundaries
3. Choropleth map creation for visualizing spatial patterns

CBS Shapefiles Source:
- https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2018
- Or via PDOK: https://service.pdok.nl/cbs/wijkenbuurten/

Required packages:
- geopandas (for shapefiles)
- folium or plotly (for interactive maps)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import warnings

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_DIR, RAW_DIR, FIGURES_DIR


# =============================================================================
# Geographic Name Lookup
# =============================================================================

def create_name_lookup(admin_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Create lookup tables for geographic names from CBS data.

    The CBS data contains columns:
    - WijkenEnBuurten: Name of the buurt/wijk/gemeente
    - gemeente_name: Name of the gemeente
    - region_code: Code like "BU03630000" or "GM0363"

    Parameters
    ----------
    admin_data : pd.DataFrame
        Raw CBS administrative data

    Returns
    -------
    Dict with lookup DataFrames for each level
    """
    lookups = {}

    # Gemeente lookup
    gemeente_data = admin_data[admin_data['region_code'].str.startswith('GM', na=False)].copy()
    if len(gemeente_data) > 0:
        gemeente_data['gemeente_id'] = gemeente_data['region_code'].str[2:].str.strip()
        gemeente_lookup = gemeente_data[['gemeente_id', 'gemeente_name', 'WijkenEnBuurten']].copy()
        gemeente_lookup = gemeente_lookup.rename(columns={'WijkenEnBuurten': 'gemeente_name_full'})
        gemeente_lookup['gemeente_name'] = gemeente_lookup['gemeente_name'].str.strip()
        lookups['gemeente'] = gemeente_lookup.drop_duplicates('gemeente_id')
        print(f"  Created gemeente lookup: {len(lookups['gemeente'])} municipalities")

    # Wijk lookup
    wijk_data = admin_data[admin_data['region_code'].str.startswith('WK', na=False)].copy()
    if len(wijk_data) > 0:
        wijk_data['wijk_id'] = wijk_data['region_code'].str[2:].str.strip()
        wijk_data['gemeente_id'] = wijk_data['wijk_id'].str[:4]
        wijk_lookup = wijk_data[['wijk_id', 'gemeente_id', 'WijkenEnBuurten', 'gemeente_name']].copy()
        wijk_lookup = wijk_lookup.rename(columns={'WijkenEnBuurten': 'wijk_name'})
        wijk_lookup['wijk_name'] = wijk_lookup['wijk_name'].str.strip()
        wijk_lookup['gemeente_name'] = wijk_lookup['gemeente_name'].str.strip()
        lookups['wijk'] = wijk_lookup.drop_duplicates('wijk_id')
        print(f"  Created wijk lookup: {len(lookups['wijk'])} districts")

    # Buurt lookup
    buurt_data = admin_data[admin_data['region_code'].str.startswith('BU', na=False)].copy()
    if len(buurt_data) > 0:
        buurt_data['buurt_id'] = buurt_data['region_code'].str[2:].str.strip()
        buurt_data['wijk_id'] = buurt_data['buurt_id'].str[:6]
        buurt_data['gemeente_id'] = buurt_data['buurt_id'].str[:4]
        buurt_lookup = buurt_data[['buurt_id', 'wijk_id', 'gemeente_id', 'WijkenEnBuurten', 'gemeente_name']].copy()
        buurt_lookup = buurt_lookup.rename(columns={'WijkenEnBuurten': 'buurt_name'})
        buurt_lookup['buurt_name'] = buurt_lookup['buurt_name'].str.strip()
        buurt_lookup['gemeente_name'] = buurt_lookup['gemeente_name'].str.strip()
        lookups['buurt'] = buurt_lookup.drop_duplicates('buurt_id')
        print(f"  Created buurt lookup: {len(lookups['buurt'])} neighborhoods")

    return lookups


def add_geographic_names(
    data: pd.DataFrame,
    admin_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Add geographic names to the analysis dataset.

    Parameters
    ----------
    data : pd.DataFrame
        Analysis data with buurt_id, wijk_id, gemeente_id columns
    admin_data : pd.DataFrame
        Raw CBS administrative data with names

    Returns
    -------
    pd.DataFrame
        Data with added name columns:
        - buurt_name
        - wijk_name
        - gemeente_name
    """
    print("\nAdding geographic names...")

    # Create lookup tables
    lookups = create_name_lookup(admin_data)

    result = data.copy()

    # Add buurt names
    if 'buurt' in lookups and 'buurt_id' in result.columns:
        buurt_names = lookups['buurt'][['buurt_id', 'buurt_name']].copy()
        result['buurt_id'] = result['buurt_id'].astype(str).str.strip()
        buurt_names['buurt_id'] = buurt_names['buurt_id'].astype(str).str.strip()
        result = result.merge(buurt_names, on='buurt_id', how='left')
        n_matched = result['buurt_name'].notna().sum()
        print(f"  Buurt names: {n_matched}/{len(result)} matched ({100*n_matched/len(result):.1f}%)")

    # Add wijk names
    if 'wijk' in lookups and 'wijk_id' in result.columns:
        wijk_names = lookups['wijk'][['wijk_id', 'wijk_name']].copy()
        result['wijk_id'] = result['wijk_id'].astype(str).str.strip()
        wijk_names['wijk_id'] = wijk_names['wijk_id'].astype(str).str.strip()
        result = result.merge(wijk_names, on='wijk_id', how='left')
        n_matched = result['wijk_name'].notna().sum()
        print(f"  Wijk names: {n_matched}/{len(result)} matched ({100*n_matched/len(result):.1f}%)")

    # Add gemeente names (from buurt lookup or gemeente lookup)
    if 'buurt' in lookups and 'gemeente_id' in result.columns:
        # Get unique gemeente_id -> gemeente_name mapping
        gemeente_names = lookups['buurt'][['gemeente_id', 'gemeente_name']].drop_duplicates('gemeente_id')
        result['gemeente_id'] = result['gemeente_id'].astype(str).str.strip()
        gemeente_names['gemeente_id'] = gemeente_names['gemeente_id'].astype(str).str.strip()
        if 'gemeente_name' not in result.columns:
            result = result.merge(gemeente_names, on='gemeente_id', how='left')
        n_matched = result['gemeente_name'].notna().sum()
        print(f"  Gemeente names: {n_matched}/{len(result)} matched ({100*n_matched/len(result):.1f}%)")

    return result


# =============================================================================
# Shapefile Handling
# =============================================================================

def download_cbs_shapefiles(
    year: int = 2018,
    save_dir: Optional[Path] = None
) -> Dict[str, Path]:
    """
    Download CBS shapefile data for Dutch administrative boundaries.

    Note: This function provides instructions for manual download.
    Automated download requires handling CBS/PDOK specific formats.

    Parameters
    ----------
    year : int
        Year of the shapefile (matches CBS data year)
    save_dir : Path, optional
        Directory to save shapefiles

    Returns
    -------
    Dict with paths to downloaded shapefiles
    """
    if save_dir is None:
        save_dir = RAW_DIR / "shapefiles"

    save_dir.mkdir(parents=True, exist_ok=True)

    instructions = f"""
    ==========================================================================
    CBS Shapefiles Download Instructions
    ==========================================================================

    To add map visualizations, you need to download CBS geographic boundaries.

    Option 1: CBS Website (Recommended)
    ------------------------------------
    1. Go to: https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data
    2. Download "Wijk- en buurtkaart {year}"
    3. Extract to: {save_dir}

    Expected files after extraction:
    - buurt_{year}_v1.shp (neighborhoods)
    - wijk_{year}_v1.shp (districts)
    - gemeente_{year}_v1.shp (municipalities)

    Option 2: PDOK Web Service
    --------------------------
    URL: https://service.pdok.nl/cbs/wijkenbuurten/{year}/wfs

    You can use geopandas to fetch directly:
    ```python
    import geopandas as gpd

    url = "https://service.pdok.nl/cbs/wijkenbuurten/{year}/wfs"
    buurt_gdf = gpd.read_file(url, layer='cbs_buurten_{year}')
    ```

    Option 3: Download via Python (if geopandas installed)
    -------------------------------------------------------
    Run: python -c "from src.geography import fetch_pdok_shapefiles; fetch_pdok_shapefiles({year})"

    ==========================================================================
    """

    print(instructions)

    return {
        "buurt": save_dir / f"buurt_{year}_v1.shp",
        "wijk": save_dir / f"wijk_{year}_v1.shp",
        "gemeente": save_dir / f"gemeente_{year}_v1.shp",
    }


def fetch_pdok_shapefiles(
    year: int = 2018,
    save_dir: Optional[Path] = None,
    levels: list = ["gemeente", "wijk", "buurt"]
) -> Dict[str, Any]:
    """
    Fetch shapefiles from PDOK web service using geopandas.

    Parameters
    ----------
    year : int
        Year of boundaries
    save_dir : Path, optional
        Directory to save shapefiles
    levels : list
        Geographic levels to fetch

    Returns
    -------
    Dict with GeoDataFrames for each level
    """
    try:
        import geopandas as gpd
    except ImportError:
        print("geopandas not installed. Run: pip install geopandas")
        print("Also requires: pip install pyproj shapely fiona")
        return {}

    if save_dir is None:
        save_dir = RAW_DIR / "shapefiles"
    save_dir.mkdir(parents=True, exist_ok=True)

    # PDOK WFS URL for CBS wijken en buurten
    base_url = f"https://service.pdok.nl/cbs/wijkenbuurten/{year}/wfs"

    layer_mapping = {
        "buurt": f"wijkenbuurten:cbs_buurten_{year}",
        "wijk": f"wijkenbuurten:cbs_wijken_{year}",
        "gemeente": f"wijkenbuurten:cbs_gemeenten_{year}",
    }

    gdfs = {}

    for level in levels:
        if level not in layer_mapping:
            continue

        layer = layer_mapping[level]
        print(f"Fetching {level} boundaries from PDOK...")

        try:
            gdf = gpd.read_file(
                base_url,
                layer=layer
            )

            # Save locally
            shp_path = save_dir / f"{level}_{year}.shp"
            gdf.to_file(shp_path)
            print(f"  Saved {len(gdf)} {level} polygons to {shp_path}")

            gdfs[level] = gdf

        except Exception as e:
            print(f"  Error fetching {level}: {e}")
            print(f"  Try manual download from CBS website")

    return gdfs


def load_shapefile(
    level: str,
    year: int = 2018,
    shapefile_dir: Optional[Path] = None
) -> Any:
    """
    Load a shapefile for a geographic level.

    Parameters
    ----------
    level : str
        Geographic level ('buurt', 'wijk', 'gemeente')
    year : int
        Year of the shapefile
    shapefile_dir : Path, optional
        Directory containing shapefiles

    Returns
    -------
    GeoDataFrame or None
    """
    try:
        import geopandas as gpd
    except ImportError:
        print("geopandas not installed. Run: pip install geopandas")
        return None

    if shapefile_dir is None:
        shapefile_dir = RAW_DIR / "shapefiles"

    # Try different filename patterns and subdirectories
    patterns = [
        # Extracted CBS v3 format (in subdirectory)
        f"WijkBuurtkaart_{year}_v3/{level}_{year}_v3.shp",
        # Extracted CBS v2/v1 format
        f"WijkBuurtkaart_{year}_v2/{level}_{year}_v2.shp",
        f"WijkBuurtkaart_{year}_v1/{level}_{year}_v1.shp",
        # Direct in shapefiles folder
        f"{level}_{year}_v3.shp",
        f"{level}_{year}_v2.shp",
        f"{level}_{year}_v1.shp",
        f"{level}_{year}.shp",
        f"cbs_{level}en_{year}.shp",
    ]

    for pattern in patterns:
        path = shapefile_dir / pattern
        if path.exists():
            print(f"Loading shapefile: {path}")
            gdf = gpd.read_file(path)
            print(f"  Loaded {len(gdf)} polygons")
            return gdf

    print(f"Shapefile not found for {level} {year}")
    print(f"Searched patterns in: {shapefile_dir}")
    print(f"Expected pattern: WijkBuurtkaart_{year}_v3/{level}_{year}_v3.shp")
    print(f"Run download_cbs_shapefiles() for instructions")
    return None


# =============================================================================
# Map Visualization Functions
# =============================================================================

def create_choropleth_map(
    data: pd.DataFrame,
    shapefile: Any,
    value_column: str,
    geo_id_column: str = "buurt_id",
    title: str = "Choropleth Map",
    cmap: str = "RdYlBu_r",
    save_path: Optional[Path] = None
) -> Any:
    """
    Create a choropleth map showing spatial distribution of a variable.

    Parameters
    ----------
    data : pd.DataFrame
        Data with values to map
    shapefile : GeoDataFrame
        Geographic boundaries
    value_column : str
        Column name to visualize
    geo_id_column : str
        Column linking data to shapefile
    title : str
        Map title
    cmap : str
        Colormap name
    save_path : Path, optional
        Path to save the map

    Returns
    -------
    Figure object (matplotlib or plotly)
    """
    try:
        import geopandas as gpd
        import matplotlib.pyplot as plt
    except ImportError:
        print("geopandas and matplotlib required. Run: pip install geopandas matplotlib")
        return None

    if shapefile is None:
        print("No shapefile provided")
        return None

    # Prepare data for joining
    map_data = data[[geo_id_column, value_column]].copy()
    map_data[geo_id_column] = map_data[geo_id_column].astype(str)

    # Aggregate if multiple observations per area
    map_data = map_data.groupby(geo_id_column)[value_column].mean().reset_index()

    # Identify the ID column in shapefile
    shp = shapefile.copy()
    id_candidates = ['statcode', 'BU_CODE', 'WK_CODE', 'GM_CODE', 'code', 'buurtnaam']

    shp_id_col = None
    for col in id_candidates:
        if col in shp.columns:
            shp_id_col = col
            break

    if shp_id_col is None:
        print(f"Could not identify ID column in shapefile. Columns: {shp.columns.tolist()}")
        return None

    # Clean IDs for joining
    shp['_join_id'] = shp[shp_id_col].astype(str).str.replace('BU', '').str.replace('WK', '').str.replace('GM', '').str.strip()
    map_data['_join_id'] = map_data[geo_id_column].astype(str).str.strip()

    # Merge
    merged = shp.merge(map_data, on='_join_id', how='left')

    n_matched = merged[value_column].notna().sum()
    print(f"Matched {n_matched}/{len(merged)} geographic units for mapping")

    # Create map
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    merged.plot(
        column=value_column,
        ax=ax,
        cmap=cmap,
        legend=True,
        legend_kwds={'label': value_column, 'orientation': 'horizontal'},
        missing_kwds={'color': 'lightgrey', 'label': 'No data'},
        edgecolor='white',
        linewidth=0.1
    )

    ax.set_title(title, fontsize=14)
    ax.axis('off')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved map to {save_path}")

    return fig


def create_interactive_map(
    data: pd.DataFrame,
    shapefile: Any,
    value_column: str,
    geo_id_column: str = "gemeente_id",
    name_column: Optional[str] = "gemeente_name",
    title: str = "Interactive Map",
    save_path: Optional[Path] = None
) -> Any:
    """
    Create an interactive choropleth map using Plotly.

    Parameters
    ----------
    data : pd.DataFrame
        Data with values to map
    shapefile : GeoDataFrame
        Geographic boundaries
    value_column : str
        Column to visualize
    geo_id_column : str
        ID column for joining
    name_column : str, optional
        Column with place names for hover
    title : str
        Map title
    save_path : Path, optional
        Path to save HTML

    Returns
    -------
    Plotly figure
    """
    try:
        import plotly.express as px
        import geopandas as gpd
        import json
    except ImportError:
        print("plotly and geopandas required")
        return None

    if shapefile is None:
        print("No shapefile provided")
        return None

    # Prepare data
    map_data = data.copy()
    if name_column and name_column in map_data.columns:
        map_data = map_data[[geo_id_column, value_column, name_column]].drop_duplicates(geo_id_column)
    else:
        map_data = map_data[[geo_id_column, value_column]].groupby(geo_id_column).mean().reset_index()
        name_column = geo_id_column

    # Convert shapefile to GeoJSON
    shp = shapefile.copy()

    # Find ID column
    id_candidates = ['statcode', 'GM_CODE', 'WK_CODE', 'BU_CODE', 'code']
    shp_id_col = None
    for col in id_candidates:
        if col in shp.columns:
            shp_id_col = col
            break

    if shp_id_col is None:
        print("Could not find ID column in shapefile")
        return None

    # Clean IDs
    shp['_id'] = shp[shp_id_col].astype(str).str.replace('GM', '').str.replace('WK', '').str.replace('BU', '').str.strip()
    map_data[geo_id_column] = map_data[geo_id_column].astype(str).str.strip()

    # Merge for hover data
    shp_merged = shp.merge(map_data, left_on='_id', right_on=geo_id_column, how='left')

    # Convert to GeoJSON
    geojson = json.loads(shp_merged.to_json())

    # Create figure
    fig = px.choropleth_mapbox(
        map_data,
        geojson=geojson,
        locations=geo_id_column,
        featureidkey="properties._id",
        color=value_column,
        hover_name=name_column,
        hover_data=[value_column],
        color_continuous_scale="RdYlBu_r",
        mapbox_style="carto-positron",
        zoom=6,
        center={"lat": 52.1326, "lon": 5.2913},  # Center of Netherlands
        opacity=0.7,
        title=title
    )

    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_x=0.5
    )

    if save_path:
        fig.write_html(save_path)
        print(f"Saved interactive map to {save_path}")

    return fig


# =============================================================================
# Analysis Summary by Geography
# =============================================================================

def summarize_by_geography(
    data: pd.DataFrame,
    level: str = "gemeente",
    dv_column: str = "DV_single",
    key_pred_column: str = "b_perc_low40_hh"
) -> pd.DataFrame:
    """
    Create summary statistics by geographic unit.

    Parameters
    ----------
    data : pd.DataFrame
        Analysis data with geographic IDs and names
    level : str
        Geographic level ('buurt', 'wijk', 'gemeente')
    dv_column : str
        Dependent variable column
    key_pred_column : str
        Key predictor column

    Returns
    -------
    pd.DataFrame
        Summary by geographic unit
    """
    id_col = f"{level}_id"
    name_col = f"{level}_name"

    if id_col not in data.columns:
        print(f"Column {id_col} not found")
        return pd.DataFrame()

    # Group and aggregate
    agg_dict = {
        dv_column: ['mean', 'std', 'count'],
        key_pred_column: 'mean'
    }

    summary = data.groupby(id_col).agg(agg_dict).reset_index()
    summary.columns = [id_col, 'dv_mean', 'dv_std', 'n_respondents', 'key_pred_mean']

    # Add names if available
    if name_col in data.columns:
        names = data[[id_col, name_col]].drop_duplicates(id_col)
        summary = summary.merge(names, on=id_col, how='left')

    # Sort by sample size
    summary = summary.sort_values('n_respondents', ascending=False)

    return summary


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("Geographic Enhancement Module")
    print("=" * 50)

    # Load raw CBS data
    admin_path = RAW_DIR / "indicators_buurt_wijk_gemeente.csv"
    if admin_path.exists():
        admin_data = pd.read_csv(admin_path)
        print(f"Loaded CBS data: {len(admin_data)} rows")

        # Create name lookups
        lookups = create_name_lookup(admin_data)

        print("\nSample gemeente names:")
        if 'gemeente' in lookups:
            print(lookups['gemeente'].head(10))
    else:
        print(f"CBS data not found at {admin_path}")

    # Print shapefile download instructions
    print("\n")
    download_cbs_shapefiles()
