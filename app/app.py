# ============================================================
# APL LOGISTICS ANALYTICS DASHBOARD
# Complete Integration (Overview, Risk & 9 Add-on Modules)
# ============================================================

import base64
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# 1. PROJECT PATHS
# ============================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

FEATURE_DATA_DIR = PROJECT_ROOT / "data" / "feature_data"
ANALYSIS_DATA_DIR = PROJECT_ROOT / "data" / "analysis_data"

DATA_FILE = FEATURE_DATA_DIR / "APL_Day3_Feature_Engineered.csv"
MASTER_KPI_FILE = ANALYSIS_DATA_DIR / "APL_Day15_Master_KPIs.csv"
DASHBOARD_INVENTORY_FILE = (
    ANALYSIS_DATA_DIR / "APL_Day15_Dashboard_Data_Inventory.csv"
)

# ============================================================
# 2. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="APL Logistics Analytics Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 3. CUSTOM DASHBOARD STYLING & BACKGROUND
# ============================================================

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

img_name = "wallpaperflare.com_wallpaper.jpg"
possible_paths = [
    PROJECT_ROOT / img_name,
    APP_DIR / img_name,
    Path(img_name).resolve()
]

bg_img_base64 = None
for img_path in possible_paths:
    if img_path.is_file():
        bg_img_base64 = get_base64_image(img_path)
        break

if bg_img_base64:
    bg_css = f"""
    [data-testid="stAppViewContainer"] > .main, .stApp {{
        background-image: url('data:image/jpeg;base64,{bg_img_base64}'); 
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}
    """
else:
    bg_css = """
    .stApp { background-color: #F5F7FB; }
    """

st.markdown(
    f"""
    <style>
    {bg_css}
    .block-container {{ 
        padding-top: 4rem; 
        padding-bottom: 2rem;
        background-color: rgba(245, 247, 251, 0.88); 
        border-radius: 15px;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }}
    [data-testid="stSidebar"] {{ background-color: #102A43; }}
    [data-testid="stSidebar"] * {{ color: #FFFFFF; }}
    
    /* Style the radio button group to look exactly like the multiselect boxes */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {{
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #E3EAF2;
    }}
    /* Ensure the text inside the white radio box is dark and readable */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div * {{
        color: #16324F !important;
    }}
    
    .dashboard-title {{
        font-size: 2.1rem; font-weight: 750; color: #16324F;
        margin-top: 1rem;
        margin-bottom: 0.1rem;
    }}
    .dashboard-subtitle {{
        font-size: 1rem; color: #627D98; margin-bottom: 1.2rem;
    }}
    div[data-testid="stMetric"] {{
        background-color: #FFFFFF; border: 1px solid #E3EAF2;
        border-radius: 12px; padding: 18px;
        box-shadow: 0 2px 5px rgba(20, 40, 70, 0.04);
    }}
    div[data-testid="stMetricLabel"] {{ color: #486581; font-weight: 600; }}
    div[data-testid="stMetricValue"] {{ color: #16324F; font-weight: 750; }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 12px; }}
    h2, h3 {{ color: #16324F; }}
    .dashboard-footer {{
        text-align: center; color: #829AB1; font-size: 0.85rem;
        padding-top: 20px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 4. DATA LOADING
# ============================================================

@st.cache_data(show_spinner="Loading logistics data...")
def load_logistics_data(file_path, modified_time):
    if not file_path.exists():
        return pd.DataFrame()
    try:
        data = pd.read_csv(
            file_path,
            encoding="cp1252",
            low_memory=False
        )
        data.columns = data.columns.astype(str).str.strip()
        return data
    except Exception as error:
        st.error(f"Unable to load the logistics dataset: {error}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_optional_csv(file_path, modified_time):
    if not file_path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(file_path, encoding="utf-8-sig")
    except Exception:
        try:
            return pd.read_csv(file_path, encoding="cp1252")
        except Exception:
            return pd.DataFrame()

data = load_logistics_data(
    DATA_FILE,
    DATA_FILE.stat().st_mtime if DATA_FILE.exists() else 0
)
master_kpis = load_optional_csv(
    MASTER_KPI_FILE,
    MASTER_KPI_FILE.stat().st_mtime if MASTER_KPI_FILE.exists() else 0
)
dashboard_inventory = load_optional_csv(
    DASHBOARD_INVENTORY_FILE,
    DASHBOARD_INVENTORY_FILE.stat().st_mtime
    if DASHBOARD_INVENTORY_FILE.exists() else 0
)

if data.empty:
    st.title("🚚 APL Logistics Analytics Dashboard")
    st.error("The primary logistics dataset could not be loaded.")
    st.stop()

# ============================================================
# 5. COLUMN DETECTION
# ============================================================

def find_column(dataframe, possible_names):
    normalized_columns = {
        str(column).strip().lower(): column
        for column in dataframe.columns
    }
    for name in possible_names:
        key = name.strip().lower()
        if key in normalized_columns:
            return normalized_columns[key]
    return None

SHIPPING_MODE_COL = find_column(data, ["Shipping Mode", "Shipping_Mode"])
REGION_COL = find_column(data, ["Order Region", "Order_Region"])
MARKET_COL = find_column(data, ["Market"])
SEGMENT_COL = find_column(data, ["Customer Segment", "Customer_Segment"])
COUNTRY_COL = find_column(data, ["Order Country", "Order_Country"])
DELIVERY_STATUS_COL = find_column(data, ["Delivery Status", "Delivery_Status"])
ORDER_DATE_COL = find_column(data, ["order date (DateOrders)", "Order Date", "Order_Date", "OrderDate", "order_date"])
SHIPMENT_DELAY_COL = find_column(data, ["Shipping_Delay_Days", "Shipping Delay Days"])
REAL_SHIPPING_DAYS_COL = find_column(data, ["Days for shipping (real)", "Days_for_shipping_real"])
SCHEDULED_SHIPPING_DAYS_COL = find_column(data, ["Days for shipment (scheduled)", "Days_for_shipment_scheduled"])
IS_DELAYED_COL = find_column(data, ["Is_Delayed", "Is Delayed"])
LATE_RISK_COL = find_column(data, ["Late_delivery_risk", "Late Delivery Risk"])
DELAY_SEVERITY_COL = find_column(data, ["Delay_Severity", "Delay Severity"])
SALES_COL = find_column(data, ["Sales"])
PROFIT_COL = find_column(data, ["Order Profit Per Order", "Order_Profit_Per_Order"])
ORDER_ID_COL = find_column(data, ["Order Id", "Order ID", "Order Id (Order)", "Order_Id"])
CUSTOMER_ID_COL = find_column(data, ["Customer Id", "Customer ID", "CustomerId", "Customer_Id"])

# ============================================================
# 6. PREPARE DASHBOARD DATA
# ============================================================

df = data.copy()

if ORDER_DATE_COL is not None:
    df[ORDER_DATE_COL] = pd.to_datetime(df[ORDER_DATE_COL], errors="coerce")

if SHIPMENT_DELAY_COL is None:
    if REAL_SHIPPING_DAYS_COL is not None and SCHEDULED_SHIPPING_DAYS_COL is not None:
        df["Shipping_Delay_Days"] = (
            pd.to_numeric(df[REAL_SHIPPING_DAYS_COL], errors="coerce")
            - pd.to_numeric(df[SCHEDULED_SHIPPING_DAYS_COL], errors="coerce")
        )
        SHIPMENT_DELAY_COL = "Shipping_Delay_Days"

# ============================================================
# 7. FILTER HELPER FUNCTION
# ============================================================

def apply_dashboard_filters(df_target, filter_mapping):
    """
    Applies a dictionary of filters to the dataframe.
    Treats an empty list as 'no restriction' (returns all valid records for that field).
    """
    filtered = df_target.copy()
    
    for col, selected_options in filter_mapping.items():
        if col is not None and col in filtered.columns:
            if selected_options:
                filtered = filtered[filtered[col].astype(str).isin(selected_options)]
                
    return filtered

# ============================================================
# 8. SIDEBAR NAVIGATION & FILTERS
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding:10px 0 22px 0;">
            <div style="font-size:2.8rem;">🚚</div>
            <div style="font-size:1.25rem;font-weight:750;">APL LOGISTICS</div>
            <div style="font-size:0.8rem;color:#BCCCDC;">
                Analytics & Intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("### Navigation")
    dashboard_pages = [
        "Overview", "Delivery Performance", "Delay Risk",
        "Shipping Efficiency", "Financial Performance",
        "Regional Analysis", "Market Analysis", "Country Analysis",
        "Customer Segments", "Product & Category", "Relationship Analysis"
    ]
    selected_page = st.radio("Select Dashboard", dashboard_pages, index=0)

    st.divider()

    st.markdown("### Integrated Filters ⬇️")
    
    # 1. Date Filter
    selected_date_range = None
    if ORDER_DATE_COL is not None:
        valid_dates = df[ORDER_DATE_COL].dropna()
        if not valid_dates.empty:
            min_date, max_date = valid_dates.min().date(), valid_dates.max().date()
            selected_date_range = st.date_input(
                "Order Date Range", 
                value=(min_date, max_date), 
                min_value=min_date, 
                max_value=max_date
            )

    # 2. Multiselect Filters
    filter_dict = {}
    
    if SHIPPING_MODE_COL is not None:
        shipping_options = sorted(df[SHIPPING_MODE_COL].dropna().astype(str).unique().tolist())
        filter_dict[SHIPPING_MODE_COL] = st.multiselect("Shipping Mode", shipping_options, default=shipping_options)
        
    if REGION_COL is not None:
        region_options = sorted(df[REGION_COL].dropna().astype(str).unique().tolist())
        filter_dict[REGION_COL] = st.multiselect("Order Region", region_options, default=region_options)
        
    if MARKET_COL is not None:
        market_options = sorted(df[MARKET_COL].dropna().astype(str).unique().tolist())
        filter_dict[MARKET_COL] = st.multiselect("Market", market_options, default=market_options)
        
    if SEGMENT_COL is not None:
        segment_options = sorted(df[SEGMENT_COL].dropna().astype(str).unique().tolist())
        filter_dict[SEGMENT_COL] = st.multiselect("Customer Segment", segment_options, default=segment_options)

    st.divider()
    st.caption("Delivery Performance, Delay Risk, and Logistics Efficiency Analysis")
    st.caption("Project data: APL Logistics")

# ============================================================
# 9. APPLY GLOBAL FILTERS
# ============================================================

filtered_df = df.copy()
if selected_date_range is not None and isinstance(selected_date_range, (tuple, list)) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    filtered_df = filtered_df[filtered_df[ORDER_DATE_COL].dt.date.between(start_date, end_date)]

filtered_df = apply_dashboard_filters(filtered_df, filter_dict)

st.markdown('<div class="dashboard-title">APL Logistics Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">Delivery Performance | Delay Risk | Logistics Efficiency</div>', unsafe_allow_html=True)
st.divider()

# ============================================================
# SHARED ANALYTICAL DATA & HELPER FUNCTIONS
# ============================================================

CHART_BG = "rgba(0,0,0,0)"

def resolve_column(df_target, candidates):
    if df_target is None or df_target.empty:
        return None
    lookup = {str(c).strip().lower(): c for c in df_target.columns}
    for candidate in candidates:
        if candidate.strip().lower() in lookup:
            return lookup[candidate.strip().lower()]
    return None

def numeric_series(df_target, column):
    if column is None or column not in df_target.columns:
        return pd.Series(np.nan, index=df_target.index, dtype=float)
    return pd.to_numeric(df_target[column], errors="coerce")

def chart_layout(fig, height=420):
    fig.update_layout(
        height=height,
        margin=dict(l=15, r=15, t=45, b=15),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
    )
    return fig

def show_unavailable(message):
    st.info(message)

def format_currency(value):
    return f"${value:,.2f}"

def actual_delay_flag(df_target):
    result = pd.Series(np.nan, index=df_target.index, dtype=float)

    engineered_col = resolve_column(df_target, ["Is_Delayed", "Is Delayed"])
    if engineered_col is not None:
        engineered = numeric_series(df_target, engineered_col)
        valid_engineered = engineered.isin([0, 1])
        result.loc[valid_engineered] = engineered.loc[valid_engineered]

    actual_col = resolve_column(
        df_target, ["Days for shipping (real)", "Days_for_shipping_real", "Actual Shipping Days"]
    )
    scheduled_col = resolve_column(
        df_target, ["Days for shipment (scheduled)", "Days_for_shipment_scheduled", "Scheduled Shipping Days"]
    )
    if actual_col is not None and scheduled_col is not None:
        actual = numeric_series(df_target, actual_col)
        scheduled = numeric_series(df_target, scheduled_col)
        valid_duration = actual.notna() & scheduled.notna() & actual.ge(0) & scheduled.ge(0)
        needs_fallback = result.isna() & valid_duration
        result.loc[needs_fallback] = (actual.loc[needs_fallback] > scheduled.loc[needs_fallback]).astype(float)

    status_col = resolve_column(df_target, ["Delivery Status", "Delivery_Status"])
    if status_col is not None:
        status = df_target[status_col].astype("string").str.strip().str.lower()
        status_mapping = {
            "late delivery": 1.0,
            "advance shipping": 0.0,
            "shipping on time": 0.0,
            "on time": 0.0,
            "on-time": 0.0,
            "early": 0.0,
            "delivered early": 0.0,
        }
        mapped_status = status.map(status_mapping)
        needs_status_fallback = result.isna() & mapped_status.notna()
        result.loc[needs_status_fallback] = mapped_status.loc[needs_status_fallback]

    return result

def prepare_dashboard_data(df_target):
    result = df_target.copy()

    sales_col = resolve_column(result, ["Sales", "Sales Amount"])
    profit_col = resolve_column(result, ["Order Profit Per Order", "Profit"])
    quantity_col = resolve_column(result, ["Order Item Quantity", "Quantity"])
    actual_col = resolve_column(result, ["Days for shipping (real)", "Actual Shipping Days"])
    scheduled_col = resolve_column(result, ["Days for shipment (scheduled)", "Scheduled Shipping Days"])
    status_col = resolve_column(result, ["Delivery Status", "Delivery_Status"])
    delay_col = resolve_column(result, ["Shipping_Delay_Days", "Shipping Delay Days"])
    risk_col = resolve_column(result, ["Late_delivery_risk", "Late Delivery Risk"])

    result["_DASH_Sales"] = numeric_series(result, sales_col)
    result["_DASH_Profit"] = numeric_series(result, profit_col)
    result["_DASH_Quantity"] = numeric_series(result, quantity_col)
    result["_DASH_Actual_Days"] = numeric_series(result, actual_col)
    result["_DASH_Scheduled_Days"] = numeric_series(result, scheduled_col)

    if delay_col is not None:
        result["_DASH_Delay_Days"] = numeric_series(result, delay_col)
    elif actual_col is not None and scheduled_col is not None:
        result["_DASH_Delay_Days"] = result["_DASH_Actual_Days"] - result["_DASH_Scheduled_Days"]
    else:
        result["_DASH_Delay_Days"] = np.nan

    result["_DASH_Actual_Delay_Flag"] = actual_delay_flag(result)
    result["_DASH_Late_Risk"] = numeric_series(result, risk_col) if risk_col is not None else np.nan
    result["_DASH_Status"] = result[status_col] if status_col is not None else pd.Series(pd.NA, index=result.index)

    return result

def add_outcome_flags(frame):
    frame = frame.copy()
    frame["_Actual_Delay_Flag"] = actual_delay_flag(frame)
    frame["_On_Time_Flag"] = (1.0 - frame["_Actual_Delay_Flag"]).where(
        frame["_Actual_Delay_Flag"].isin([0, 1]), np.nan
    )
    return frame

df = add_outcome_flags(df)
filtered_df = add_outcome_flags(filtered_df)
dashboard_df = prepare_dashboard_data(filtered_df) if isinstance(filtered_df, pd.DataFrame) else pd.DataFrame()


# ============================================================
# DASHBOARD MODULE ROUTING
# ============================================================

if filtered_df.empty:
    st.warning("No shipment records match the selected filters. Please adjust your selections.")
else:
    if selected_page == "Overview":
    
        # --- KPI CALCULATIONS FOR OVERVIEW ---
        total_shipments = len(filtered_df)
        valid_on_time = filtered_df["_On_Time_Flag"].dropna()
        valid_actual_delay = filtered_df["_Actual_Delay_Flag"].dropna()
        on_time_rate = valid_on_time.mean() * 100 if not valid_on_time.empty else np.nan
        actual_delay_rate = valid_actual_delay.mean() * 100 if not valid_actual_delay.empty else np.nan
    
        if SHIPMENT_DELAY_COL is not None:
            delay_series = pd.to_numeric(filtered_df[SHIPMENT_DELAY_COL], errors="coerce")
            positive_delays = delay_series[delay_series > 0]
            average_delay = positive_delays.mean() if not positive_delays.empty else np.nan
        else:
            average_delay = np.nan
    
        if SALES_COL is not None:
            sales_series = pd.to_numeric(filtered_df[SALES_COL], errors="coerce")
            total_sales = sales_series.sum()
        else:
            total_sales = None
    
        # --- KPI CARDS ---
        st.subheader("Executive Overview")
        kpi_columns = st.columns(5)
        with kpi_columns[0]:
            st.metric("📦 Total Shipment Records", f"{total_shipments:,}")
        with kpi_columns[1]:
            st.metric("✅ On-Time / Early Rate", f"{on_time_rate:.2f}%" if pd.notna(on_time_rate) else "N/A")
        with kpi_columns[2]:
            st.metric("⚠️ Actual Late Delivery Rate", f"{actual_delay_rate:.2f}%" if pd.notna(actual_delay_rate) else "N/A")
        with kpi_columns[3]:
            st.metric("🕒 Avg Delay Among Late Records", f"{average_delay:.2f} days" if pd.notna(average_delay) else "N/A")
        with kpi_columns[4]:
            if total_sales is not None:
                st.metric("💰 Total Sales", f"${total_sales:,.0f}")
            else:
                st.metric("💰 Total Sales", "Unavailable")
        st.divider()
    
        # --- CHART HELPER FUNCTIONS ---
        def show_empty_chart_ov(message):
            st.info(message)
    
        def show_bar_chart_ov(dataframe, category_column, title, color=None, top_n=None):
            if category_column is None:
                show_empty_chart_ov(f"Required category column unavailable for {title}.")
                return
            if dataframe.empty:
                show_empty_chart_ov("No data matches the selected filters.")
                return
            summary = (dataframe.groupby(category_column, dropna=False).size().reset_index(name="Shipments").sort_values("Shipments", ascending=False))
            if top_n is not None:
                summary = summary.head(top_n)
            fig = px.bar(summary, x=category_column, y="Shipments", title=title, color=color, text_auto=True)
            fig.update_layout(height=350, margin=dict(l=15, r=15, t=55, b=15), showlegend=False, xaxis_title="", yaxis_title="Shipments", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
    
        # --- OVERVIEW CHARTS ---
        chart_col1, chart_col2, chart_col3 = st.columns(3)
        with chart_col1:
            st.markdown("#### Shipments by Shipping Mode")
            show_bar_chart_ov(filtered_df, SHIPPING_MODE_COL, "Shipment Volume by Mode")
        with chart_col2:
            st.markdown("#### Delivery Status Distribution")
            if DELIVERY_STATUS_COL is not None:
                status_counts = filtered_df[DELIVERY_STATUS_COL].fillna("Unknown").astype(str).value_counts().reset_index()
                status_counts.columns = ["Delivery Status", "Shipments"]
                fig = px.pie(status_counts, names="Delivery Status", values="Shipments", hole=0.58)
                fig.update_layout(height=350, margin=dict(l=10, r=10, t=25, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                show_empty_chart_ov("Delivery Status column is unavailable.")
        with chart_col3:
            st.markdown("#### Shipments by Region")
            show_bar_chart_ov(filtered_df, REGION_COL, "Shipment Volume by Region")
    
        st.divider()
        chart_col4, chart_col5, chart_col6 = st.columns(3)
        with chart_col4:
            st.markdown("#### Delivery Performance by Shipping Mode")
            if SHIPPING_MODE_COL is not None and not filtered_df.empty:
                shipping_mode_analysis = (
                    filtered_df.groupby(SHIPPING_MODE_COL, dropna=False)
                    .agg(
                        Shipment_Records=(SHIPPING_MODE_COL, "size"),
                        Valid_Delay_Outcome_Records=("_Actual_Delay_Flag", "count"),
                        Delayed_Shipments=("_Actual_Delay_Flag", "sum"),
                        Valid_On_Time_Outcome_Records=("_On_Time_Flag", "count"),
                        On_Time_or_Early_Shipments=("_On_Time_Flag", "sum"),
                    )
                    .reset_index()
                )
                shipping_mode_analysis["Delay_Rate_%"] = (
                    shipping_mode_analysis["Delayed_Shipments"]
                    / shipping_mode_analysis["Valid_Delay_Outcome_Records"].replace(0, np.nan)
                    * 100
                ).round(2)
                fig = px.bar(shipping_mode_analysis, x=SHIPPING_MODE_COL, y="Delay_Rate_%", title="Actual Delay Rate by Shipping Mode", text_auto=".1f", hover_data=["Shipment_Records", "Valid_Delay_Outcome_Records", "Delayed_Shipments", "Valid_On_Time_Outcome_Records", "On_Time_or_Early_Shipments"])
                fig.update_layout(height=350, xaxis_title="Shipping Mode", yaxis_title="Actual Delay Rate (%)", margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                show_empty_chart_ov("Shipping Mode data is unavailable or no records match the filters.")
        with chart_col5:
            st.markdown("#### Top 5 Markets by Shipments")
            show_bar_chart_ov(filtered_df, MARKET_COL, "Top Markets", top_n=5)
        with chart_col6:
            st.markdown("#### Delay Severity Distribution")
            if DELAY_SEVERITY_COL is not None:
                severity_counts = filtered_df[DELAY_SEVERITY_COL].fillna("Unknown").astype(str).value_counts().reset_index()
                severity_counts.columns = ["Delay Severity", "Shipments"]
                fig = px.pie(severity_counts, names="Delay Severity", values="Shipments", hole=0.58)
                fig.update_layout(height=350, margin=dict(l=10, r=10, t=25, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                show_empty_chart_ov("Delay Severity column is unavailable in the dataset.")
    
        st.divider()
        chart_col7, chart_col8, chart_col9 = st.columns(3)
        with chart_col7:
            st.markdown("#### Actual Delay Rate by Region")
            if REGION_COL is not None and not filtered_df.empty:
                regional_summary = (
                    filtered_df.groupby(REGION_COL, dropna=False)
                    .agg(
                        Shipment_Records=(REGION_COL, "size"),
                        Valid_Delay_Outcome_Records=("_Actual_Delay_Flag", "count"),
                        Delay_Rate=("_Actual_Delay_Flag", "mean"),
                    )
                    .reset_index()
                )
                regional_summary["Delay_Rate"] *= 100
                regional_summary = regional_summary.sort_values("Delay_Rate", ascending=False)
                fig = px.bar(regional_summary, x=REGION_COL, y="Delay_Rate", text_auto=".1f", title="Actual Delay Rate by Region")
                fig.update_layout(height=350, xaxis_title="", yaxis_title="Actual Delay Rate (%)", margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                show_empty_chart_ov("Region column is unavailable.")
        with chart_col8:
            st.markdown("#### Sales by Market")
            if MARKET_COL is not None and SALES_COL is not None:
                financial_df = filtered_df.copy()
                financial_df[SALES_COL] = pd.to_numeric(financial_df[SALES_COL], errors="coerce")
                sales_summary = (financial_df.groupby(MARKET_COL, dropna=False)[SALES_COL].sum().reset_index().sort_values(SALES_COL, ascending=False))
                fig = px.bar(sales_summary, x=MARKET_COL, y=SALES_COL, title="Total Sales by Market", text_auto=".2s")
                fig.update_layout(height=350, xaxis_title="", yaxis_title="Sales", margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                show_empty_chart_ov("Market or Sales column is unavailable.")
        with chart_col9:
            st.markdown("#### Late Delivery Risk Classification")
            if LATE_RISK_COL is not None:
                risk_values = pd.to_numeric(filtered_df[LATE_RISK_COL], errors="coerce")
                risk_labels = risk_values.map({0: "Lower Risk", 1: "Higher Risk"}).fillna("Unknown")
                risk_counts = risk_labels.value_counts().reset_index()
                risk_counts.columns = ["Risk Category", "Shipments"]
                fig = px.pie(risk_counts, names="Risk Category", values="Shipments", hole=0.58)
                fig.update_layout(height=350, margin=dict(l=10, r=10, t=25, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                show_empty_chart_ov("Late delivery risk column is unavailable.")
    
        st.divider()
        st.subheader("Sample Shipment Records")
        if not filtered_df.empty:
            recent_df = filtered_df.copy()
            if ORDER_DATE_COL is not None:
                recent_df = recent_df.sort_values(ORDER_DATE_COL, ascending=False, na_position="last")
            preferred_columns = [ORDER_ID_COL, ORDER_DATE_COL, SHIPPING_MODE_COL, REGION_COL, MARKET_COL, COUNTRY_COL, DELIVERY_STATUS_COL, SHIPMENT_DELAY_COL, SALES_COL]
            display_columns = [column for column in preferred_columns if column is not None and column in recent_df.columns]
            if display_columns:
                st.dataframe(recent_df[display_columns].head(15), use_container_width=True, hide_index=True)
            else:
                st.dataframe(recent_df.head(15), use_container_width=True, hide_index=True)
        else:
            st.info("No shipment records match the selected filters.")
    
    elif selected_page == "Delay Risk":
    
        st.title("Delay Risk Dashboard")
        st.caption(
            "Late_delivery_risk is the dataset's risk label, while actual delay is derived from "
            "validated Is_Delayed values where available, then actual-versus-scheduled shipping "
            "days, and finally recognized delivery-status labels. This is a descriptive comparison, "
            "not an independent model-performance evaluation."
        )
    
        with st.expander("Delay Risk Data Validation", expanded=False):
            required_risk_columns = [
                "Late_delivery_risk", "Shipping Mode", "Order Region", "Market", "Order Country"
            ]
            for column in required_risk_columns:
                detected_column = find_column(data, [column])
                if detected_column is not None:
                    st.success(f"Available: {column}")
                else:
                    st.warning(f"Missing or differently named: {column}")
            
            st.write("Dataset shape:", data.shape)
            if LATE_RISK_COL is not None:
                st.write("Late delivery risk values:", sorted(data[LATE_RISK_COL].dropna().unique().tolist()))
    
        risk_df = filtered_df.copy()
        if LATE_RISK_COL is not None:
            risk_df["_Risk_Value"] = pd.to_numeric(risk_df[LATE_RISK_COL], errors="coerce")
            risk_df = risk_df[risk_df["_Risk_Value"].isin([0, 1])].copy()
            risk_df["_Risk_Label"] = risk_df["_Risk_Value"].map({0: "Lower Risk", 1: "Higher Risk"})
    
            total_valid_risk = len(risk_df)
            high_risk_count = int(risk_df["_Risk_Value"].eq(1).sum())
            lower_risk_count = int(risk_df["_Risk_Value"].eq(0).sum())
            
            high_risk_percentage = (high_risk_count / total_valid_risk * 100 if total_valid_risk > 0 else 0.0)
    
            risk_df["_Actual_Delay_Validated"] = actual_delay_flag(risk_df)
            valid_actual_delay = risk_df["_Actual_Delay_Validated"].dropna()
            actual_delay_rate = valid_actual_delay.mean() * 100 if not valid_actual_delay.empty else np.nan
    
            st.subheader("Delay Risk — Executive Summary")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1:
                st.metric("Valid Risk Records", f"{total_valid_risk:,}")
            with kpi2:
                st.metric("High-Risk Records", f"{high_risk_count:,}")
            with kpi3:
                st.metric("High-Risk Percentage", f"{high_risk_percentage:.2f}%")
            with kpi4:
                st.metric("Actual Delay Rate", f"{actual_delay_rate:.2f}%" if pd.notna(actual_delay_rate) else "Unavailable")
        else:
            st.warning("The Late_delivery_risk column is unavailable.")
    
        st.markdown("---")
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.subheader("Risk Classification Distribution")
            if LATE_RISK_COL is not None and not risk_df.empty:
                risk_distribution = (
                    risk_df["_Risk_Value"].map({0: "Lower Risk", 1: "Higher Risk"})
                    .value_counts().rename_axis("Risk Category").reset_index(name="Shipment Records")
                )
                fig_pie = px.pie(
                    risk_distribution, names="Risk Category", values="Shipment Records",
                    hole=0.55, title="Lower-Risk vs Higher-Risk Records"
                )
                fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                fig_pie.update_layout(height=400, margin=dict(l=15, r=15, t=55, b=15), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No valid risk records are available for the selected filters.")
    
        with col2:
            st.subheader("High-Risk Records by Shipping Mode")
            if SHIPPING_MODE_COL is not None and not risk_df.empty:
                mode_risk = (
                    risk_df.groupby(SHIPPING_MODE_COL, dropna=False)
                    .agg(Total_Records=("_Risk_Value", "size"), High_Risk_Records=("_Risk_Value", lambda v: v.eq(1).sum()))
                    .reset_index()
                )
                mode_risk["High_Risk_Percentage"] = (mode_risk["High_Risk_Records"] / mode_risk["Total_Records"].replace(0, np.nan) * 100)
                mode_risk = mode_risk.sort_values("High_Risk_Records", ascending=False)
                
                fig_mode = px.bar(
                    mode_risk, x=SHIPPING_MODE_COL, y="High_Risk_Records", text_auto=True,
                    hover_data=["Total_Records", "High_Risk_Percentage"], title="High-Risk Record Count by Shipping Mode"
                )
                fig_mode.update_layout(height=400, xaxis_title="Shipping Mode", yaxis_title="High-Risk Records", margin=dict(l=15, r=15, t=55, b=15), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_mode, use_container_width=True)
                
                risk_summary_csv = mode_risk.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="Download Shipping Mode Risk Summary",
                    data=risk_summary_csv, file_name="APL_Shipping_Mode_Risk_Summary.csv", mime="text/csv"
                )
            else:
                st.info("Shipping Mode or valid risk records are unavailable.")
    
        st.markdown("---")
    
        col3, col4 = st.columns(2)
    
        with col3:
            st.subheader("High-Risk Records by Region")
            if REGION_COL is not None and not risk_df.empty:
                region_risk = (
                    risk_df.groupby(REGION_COL, dropna=False)
                    .agg(Total_Records=("_Risk_Value", "size"), High_Risk_Records=("_Risk_Value", lambda v: v.eq(1).sum()))
                    .reset_index()
                )
                region_risk["High_Risk_Percentage"] = (region_risk["High_Risk_Records"] / region_risk["Total_Records"].replace(0, np.nan) * 100)
                region_risk = region_risk.sort_values("High_Risk_Percentage", ascending=False)
                
                fig_reg = px.bar(
                    region_risk, x=REGION_COL, y="High_Risk_Percentage", text_auto=".1f",
                    hover_data=["Total_Records", "High_Risk_Records"], title="High-Risk Percentage by Region"
                )
                fig_reg.update_layout(height=420, xaxis_title="Order Region", yaxis_title="High-Risk Records (%)", margin=dict(l=15, r=15, t=55, b=15), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_reg, use_container_width=True)
            else:
                st.info("Regional data or valid risk records are unavailable.")
    
        with col4:
            st.subheader("High-Risk Records by Market")
            if MARKET_COL is not None and not risk_df.empty:
                market_risk = (
                    risk_df.groupby(MARKET_COL, dropna=False)
                    .agg(Total_Records=("_Risk_Value", "size"), High_Risk_Records=("_Risk_Value", lambda v: v.eq(1).sum()))
                    .reset_index()
                )
                market_risk["High_Risk_Percentage"] = (market_risk["High_Risk_Records"] / market_risk["Total_Records"].replace(0, np.nan) * 100)
                market_risk = market_risk.sort_values("High_Risk_Percentage", ascending=True)
                
                fig_mkt = px.bar(
                    market_risk, x="High_Risk_Percentage", y=MARKET_COL, orientation="h", text_auto=".1f",
                    hover_data=["Total_Records", "High_Risk_Records"], title="High-Risk Percentage by Market"
                )
                fig_mkt.update_layout(height=450, xaxis_title="High-Risk Records (%)", yaxis_title="Market", margin=dict(l=15, r=15, t=55, b=15), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_mkt, use_container_width=True)
            else:
                st.info("Market data or valid risk records are unavailable.")
    
        st.markdown("---")
    
        col5, col6 = st.columns(2)
    
        with col5:
            st.subheader("Risk Classification vs Actual Delivery Delays")
            if LATE_RISK_COL is not None and not risk_df.empty:
                comparison_df = risk_df.copy()
                comparison_df["_Actual_Delay"] = actual_delay_flag(comparison_df)
                comparison_df = comparison_df[comparison_df["_Actual_Delay"].isin([0, 1])].copy()
                comparison_df["_Actual_Delay_Label"] = comparison_df["_Actual_Delay"].map({0: "Not Delayed", 1: "Delayed"})
                
                comparison_summary = (
                    comparison_df.groupby(["_Risk_Value", "_Actual_Delay_Label"], dropna=False)
                    .size().reset_index(name="Shipment Records")
                )
                comparison_summary["Risk Category"] = comparison_summary["_Risk_Value"].map({0: "Lower Risk", 1: "Higher Risk"})
                
                fig_comp = px.bar(
                    comparison_summary, x="Risk Category", y="Shipment Records", color="_Actual_Delay_Label",
                    barmode="group", text_auto=True, title="Actual Delay Counts Within Each Risk Category"
                )
                fig_comp.update_layout(height=420, xaxis_title="Risk Classification", yaxis_title="Shipment Records", legend_title="Actual Delivery Outcome", margin=dict(l=15, r=15, t=55, b=15), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_comp, use_container_width=True)
                st.caption(
                    "Because the risk label may be based on information related to actual delivery outcomes, "
                    "this chart should not be interpreted as an independent predictive-model accuracy score."
                )
            else:
                st.info("This comparison requires valid risk labels and at least one usable actual-outcome source: Is_Delayed, actual/scheduled durations, or recognized delivery status.")
    
        with col6:
            st.subheader("Actual vs Scheduled Shipping Duration")
            if REAL_SHIPPING_DAYS_COL is not None and SCHEDULED_SHIPPING_DAYS_COL is not None:
                duration_df = filtered_df.copy()
                duration_df["_Actual_Shipping_Days"] = pd.to_numeric(duration_df[REAL_SHIPPING_DAYS_COL], errors="coerce")
                duration_df["_Scheduled_Shipping_Days"] = pd.to_numeric(duration_df[SCHEDULED_SHIPPING_DAYS_COL], errors="coerce")
                duration_df = duration_df.dropna(subset=["_Actual_Shipping_Days", "_Scheduled_Shipping_Days"])
                
                if not duration_df.empty:
                    duration_summary = pd.DataFrame({
                        "Shipping Duration": ["Scheduled", "Actual"],
                        "Average Days": [duration_df["_Scheduled_Shipping_Days"].mean(), duration_df["_Actual_Shipping_Days"].mean()]
                    })
                    fig_dur = px.bar(
                        duration_summary, x="Shipping Duration", y="Average Days", text_auto=".2f",
                        title="Average Actual vs Scheduled Shipping Days"
                    )
                    fig_dur.update_layout(height=380, xaxis_title="", yaxis_title="Average Days", margin=dict(l=15, r=15, t=55, b=15), paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_dur, use_container_width=True)
                else:
                    st.info("No valid actual and scheduled shipping-duration records are available.")
            else:
                st.info("Actual or scheduled shipping-duration columns are unavailable.")
    
        st.markdown("---")
    
        st.subheader("Top 10 Countries by High-Risk Records")
        if COUNTRY_COL is not None and not risk_df.empty:
            country_risk = (
                risk_df.groupby(COUNTRY_COL, dropna=False)
                .agg(Total_Records=("_Risk_Value", "size"), High_Risk_Records=("_Risk_Value", lambda v: v.eq(1).sum()))
                .reset_index()
            )
            country_risk["High_Risk_Percentage"] = (country_risk["High_Risk_Records"] / country_risk["Total_Records"].replace(0, np.nan) * 100)
            top_countries = (country_risk.sort_values("High_Risk_Records", ascending=False).head(10).sort_values("High_Risk_Records", ascending=True))
            
            fig_country = px.bar(
                top_countries, x="High_Risk_Records", y=COUNTRY_COL, orientation="h", text_auto=True,
                hover_data=["Total_Records", "High_Risk_Percentage"], title="Top 10 Countries by High-Risk Record Count"
            )
            fig_country.update_layout(height=500, xaxis_title="High-Risk Records", yaxis_title="Order Country", margin=dict(l=15, r=15, t=55, b=15), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_country, use_container_width=True)
        else:
            st.info("Country data or valid risk records are unavailable.")
    
        st.markdown("---")
    
        st.subheader("High-Risk Shipment Records")
        if LATE_RISK_COL is not None:
            high_risk_records = filtered_df.copy()
            high_risk_records["_Risk_Value"] = pd.to_numeric(high_risk_records[LATE_RISK_COL], errors="coerce")
            high_risk_records = high_risk_records[high_risk_records["_Risk_Value"].eq(1)].copy()
            
            preferred_columns = [
                ORDER_ID_COL, SHIPPING_MODE_COL, REGION_COL, MARKET_COL, COUNTRY_COL,
                DELIVERY_STATUS_COL, SHIPMENT_DELAY_COL, REAL_SHIPPING_DAYS_COL,
                SCHEDULED_SHIPPING_DAYS_COL, LATE_RISK_COL
            ]
            display_columns = [col for col in preferred_columns if col is not None and col in high_risk_records.columns]
            
            st.write(f"High-risk records found: {len(high_risk_records):,}")
            
            if not high_risk_records.empty:
                st.dataframe(high_risk_records[display_columns].head(100), use_container_width=True, hide_index=True)
                csv_data = high_risk_records[display_columns].to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="Download High-Risk Records CSV",
                    data=csv_data, file_name="APL_High_Risk_Records.csv", mime="text/csv"
                )
            else:
                st.info("No high-risk records match the selected global filters.")
        else:
            st.warning("The Late_delivery_risk column is unavailable.")
    
    elif selected_page == "Delivery Performance":
        st.title("Delivery Performance Analysis")
        st.markdown("Analyze delivery status, actual shipment delays, and late-delivery risk.")
    
        if not dashboard_df.empty:
            df = dashboard_df.copy()
            total_shipments = len(df)
            delay_flag = df["_DASH_Actual_Delay_Flag"]
            valid_delay = delay_flag.dropna()
            delayed_count = int((valid_delay == 1).sum())
            actual_delay_rate = (valid_delay.mean() * 100 if not valid_delay.empty else np.nan)
    
            status_col = resolve_column(df, ["Delivery Status", "Delivery_Status"])
            risk_col = resolve_column(df, ["Late_delivery_risk", "Late Delivery Risk"])
    
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Shipment Records", f"{total_shipments:,}")
            k2.metric("Records with Known Outcome", f"{len(valid_delay):,}")
            k3.metric("Actual Delayed Shipments", f"{delayed_count:,}")
    
            if risk_col is not None:
                risk = pd.to_numeric(df[risk_col], errors="coerce")
                risk_valid = risk.isin([0, 1])
                high_risk_count = int((risk[risk_valid] == 1).sum())
                k4.metric("Actual Delay Rate", f"{actual_delay_rate:.2f}%" if pd.notna(actual_delay_rate) else "N/A")
            else:
                k4.metric("Actual Delay Rate", f"{actual_delay_rate:.2f}%" if pd.notna(actual_delay_rate) else "N/A")
    
            st.markdown("---")
    
            col1, col2 = st.columns(2)
    
            with col1:
                st.subheader("Delivery Status Breakdown")
                if status_col is not None:
                    status_summary = (
                        df[status_col]
                        .fillna("Unknown")
                        .value_counts()
                        .rename_axis("Delivery Status")
                        .reset_index(name="Shipments")
                    )
                    fig = px.pie(status_summary, names="Delivery Status", values="Shipments", hole=0.45)
                    chart_layout(fig)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_unavailable("Delivery Status column is unavailable.")
    
            with col2:
                st.subheader("Actual Shipping Delay Distribution")
                delay_values = df["_DASH_Delay_Days"].dropna()
                if not delay_values.empty:
                    delay_plot = pd.DataFrame({"Delay Days": delay_values})
                    fig = px.histogram(delay_plot, x="Delay Days", nbins=30)
                    chart_layout(fig)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_unavailable("Actual shipping-delay data is unavailable.")
    
            st.subheader("Delivery Performance by Shipping Mode")
            mode_col = resolve_column(df, ["Shipping Mode", "Shipping_Mode"])
            if mode_col is not None:
                mode_df = df.dropna(subset=[mode_col]).copy()
                mode_summary = (
                    mode_df.groupby(mode_col)
                    .agg(
                        Shipment_Records=(mode_col, "size"),
                        Valid_Delay_Outcome_Records=("_DASH_Actual_Delay_Flag", "count"),
                        Delay_Rate=("_DASH_Actual_Delay_Flag", "mean"),
                        Average_Actual_Days=("_DASH_Actual_Days", "mean"),
                    )
                    .reset_index()
                )
                mode_summary["Delay Rate (%)"] = (mode_summary["Delay_Rate"] * 100)
                fig = px.bar(mode_summary, x=mode_col, y="Delay Rate (%)", text_auto=".1f", hover_data=["Shipment_Records", "Valid_Delay_Outcome_Records"])
                chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)
            else:
                show_unavailable("Shipping Mode column is unavailable.")
    
        else:
            show_unavailable("No shipment records match the selected filters.")
    
    elif selected_page == "Shipping Efficiency":
        st.title("Shipping Efficiency Dashboard")
        st.markdown("Compare actual shipping duration with scheduled delivery timelines.")
    
        if not dashboard_df.empty:
            df = dashboard_df.copy()
            duration_pair_present = df["_DASH_Actual_Days"].notna() & df["_DASH_Scheduled_Days"].notna()
            valid_duration_mask = (
                duration_pair_present
                & df["_DASH_Actual_Days"].ge(0)
                & df["_DASH_Scheduled_Days"].ge(0)
            )
            eff_df = df.loc[valid_duration_mask].copy()
            missing_duration_count = int((~duration_pair_present).sum())
            invalid_negative_count = int((duration_pair_present & (
                df["_DASH_Actual_Days"].lt(0) | df["_DASH_Scheduled_Days"].lt(0)
            )).sum())
            zero_actual_count = int((eff_df["_DASH_Actual_Days"] == 0).sum())
    
            st.caption(
                f"Duration validation: {len(eff_df):,} valid records; "
                f"{missing_duration_count:,} records missing one or both durations; "
                f"{invalid_negative_count:,} records with negative durations excluded. "
                f"Zero-day actual durations ({zero_actual_count:,}) are retained as observed, not automatically discarded."
            )
    
            if not eff_df.empty:
                avg_actual = eff_df["_DASH_Actual_Days"].mean()
                avg_scheduled = eff_df["_DASH_Scheduled_Days"].mean()
                avg_variation = avg_actual - avg_scheduled
                on_schedule_pct = (eff_df["_DASH_Actual_Days"] <= eff_df["_DASH_Scheduled_Days"]).mean() * 100
    
                k1, k2, k3, k4, k5 = st.columns(5)
                k1.metric("Valid Duration Records", f"{len(eff_df):,}")
                k2.metric("Average Actual Days", f"{avg_actual:.2f}")
                k3.metric("Average Scheduled Days", f"{avg_scheduled:.2f}")
                k4.metric("Average Variation", f"{avg_variation:+.2f} days", delta_color="inverse")
                k5.metric("On-Schedule Rate", f"{on_schedule_pct:.2f}%")
    
                status_col = resolve_column(df, ["Delivery Status", "Delivery_Status"])
                if status_col is not None:
                    status_norm = df[status_col].astype("string").str.strip().str.lower()
                    status_delayed = status_norm.eq("late delivery")
                    duration_delayed = df["_DASH_Actual_Days"].gt(df["_DASH_Scheduled_Days"])
                    consistency_mask = valid_duration_mask & status_norm.isin([
                        "late delivery", "advance shipping", "shipping on time", "on time", "on-time", "early", "delivered early"
                    ])
                    mismatch_count = int((status_delayed[consistency_mask] != duration_delayed[consistency_mask]).sum())
                    compared_count = int(consistency_mask.sum())
                    if compared_count:
                        st.caption(
                            f"Source consistency check: {mismatch_count:,} of {compared_count:,} records "
                            "differ between the delivery-status label and actual-versus-scheduled durations. "
                            "Review the source definitions before treating either field as ground truth."
                        )
    
                st.markdown("---")
    
                col1, col2 = st.columns(2)
    
                with col1:
                    st.subheader("Actual vs Scheduled Shipping Days")
                    scatter_df = eff_df.sample(n=min(2000, len(eff_df)), random_state=42)
                    fig = px.scatter(
                        scatter_df,
                        x="_DASH_Scheduled_Days",
                        y="_DASH_Actual_Days",
                        opacity=0.55,
                        labels={
                            "_DASH_Scheduled_Days": "Scheduled Days",
                            "_DASH_Actual_Days": "Actual Days"
                        }
                    )
                    
                    fig.update_layout(
                        title="Actual vs Scheduled Shipping Days",
                        xaxis_title="Scheduled Shipping Days",
                        yaxis_title="Actual Shipping Days",
                        height=420,
                        margin=dict(l=15, r=15, t=45, b=15),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
                with col2:
                    st.subheader("Actual Shipping Days by Mode")
                    mode_col = resolve_column(eff_df, ["Shipping Mode", "Shipping_Mode"])
                    if mode_col is not None:
                        fig = px.box(eff_df, x=mode_col, y="_DASH_Actual_Days", color=mode_col, points=False)
                        fig.update_layout(showlegend=False)
                        chart_layout(fig)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        show_unavailable("Shipping Mode column is unavailable.")
    
                st.subheader("Shipping Efficiency by Mode")
                if mode_col is not None:
                    mode_efficiency = (
                        eff_df.groupby(mode_col)
                        .agg(
                            Total_Shipments=(mode_col, "size"),
                            Actual_Days=("_DASH_Actual_Days", "mean"),
                            Scheduled_Days=("_DASH_Scheduled_Days", "mean"),
                        )
                        .reset_index()
                    )
                    mode_efficiency["Variation"] = (mode_efficiency["Actual_Days"] - mode_efficiency["Scheduled_Days"])
                    st.dataframe(mode_efficiency.round(2), use_container_width=True, hide_index=True)
    
            else:
                show_unavailable("No valid actual and scheduled shipping durations are available for the selected filters.")
    
        else:
            show_unavailable("No shipment records match the selected filters.")
    
    elif selected_page == "Financial Performance":
        st.title("Financial Performance Analysis")
        st.markdown("Analyze sales, order profitability, and financial performance.")
    
        if not dashboard_df.empty:
            df = dashboard_df.copy()
            valid_sales = df["_DASH_Sales"].dropna()
            valid_profit = df["_DASH_Profit"].dropna()
    
            if valid_sales.empty:
                show_unavailable("Sales data is unavailable.")
            else:
                total_sales = valid_sales.sum()
                total_profit = (valid_profit.sum() if not valid_profit.empty else np.nan)
                paired_financial = df[["_DASH_Sales", "_DASH_Profit"]].dropna()
                paired_sales = paired_financial["_DASH_Sales"].sum() if not paired_financial.empty else np.nan
                paired_profit = paired_financial["_DASH_Profit"].sum() if not paired_financial.empty else np.nan
                recorded_profit_to_sales = (
                    paired_profit / paired_sales * 100
                    if pd.notna(paired_profit) and pd.notna(paired_sales) and paired_sales != 0
                    else np.nan
                )
    
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Total Sales", format_currency(total_sales))
                k2.metric("Total Recorded Profit", format_currency(total_profit) if pd.notna(total_profit) else "N/A")
                k3.metric("Recorded Profit-to-Sales Ratio", f"{recorded_profit_to_sales:.2f}%" if pd.notna(recorded_profit_to_sales) else "N/A")
                k4.metric("Records with Paired Sales & Profit", f"{len(paired_financial):,}")
    
                st.caption(
                    "Recorded profit-to-sales ratio = sum of recorded Order Profit Per Order divided by sum of Sales "
                    "for rows where both values are present. It is a descriptive dataset ratio, not necessarily an "
                    "accounting profit margin; verify the source field definition before financial reporting."
                )
                st.markdown("---")
    
                col1, col2 = st.columns(2)
                market_col = resolve_column(df, ["Market"])
    
                with col1:
                    st.subheader("Sales and Profit by Market")
                    if market_col is not None:
                        market_fin = (
                            df.groupby(market_col, dropna=False)
                            .agg(Sales=("_DASH_Sales", "sum"), Profit=("_DASH_Profit", "sum"))
                            .reset_index()
                        )
                        market_fin = market_fin.melt(
                            id_vars=[market_col], value_vars=["Sales", "Profit"],
                            var_name="Metric", value_name="Amount"
                        )
                        fig = px.bar(market_fin, x=market_col, y="Amount", color="Metric", barmode="group", labels={"Amount": "Amount (USD)"})
                        chart_layout(fig)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        show_unavailable("Market column is unavailable.")
    
                with col2:
                    st.subheader("Sales vs Recorded Profit")
                    scatter_df = df.dropna(subset=["_DASH_Sales", "_DASH_Profit"])
                    if not scatter_df.empty:
                        scatter_df = scatter_df.sample(n=min(3000, len(scatter_df)), random_state=42)
                        fig = px.scatter(
                            scatter_df, x="_DASH_Sales", y="_DASH_Profit", opacity=0.6,
                            labels={"_DASH_Sales": "Sales", "_DASH_Profit": "Recorded Profit"}
                        )
                        chart_layout(fig)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        show_unavailable("There are no records with both sales and profit.")
    
                st.subheader("Top 15 Products by Sales")
                product_col = resolve_column(df, ["Product Name", "Product", "Product_Name"])
                if product_col is not None:
                    product_sales = (
                        df.groupby(product_col, dropna=False)
                        .agg(Sales=("_DASH_Sales", "sum"), Profit=("_DASH_Profit", "sum"))
                        .reset_index()
                        .sort_values("Sales", ascending=False)
                        .head(15)
                    )
                    fig = px.bar(
                        product_sales.sort_values("Sales"), x="Sales", y=product_col,
                        orientation="h", hover_data=["Profit"]
                    )
                    chart_layout(fig, 500)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_unavailable("Product Name is unavailable. Check whether a product-level field exists.")
    
        else:
            show_unavailable("No shipment records match the selected filters.")
    
    elif selected_page == "Regional Analysis":
        st.title("Regional Analysis")
        st.markdown("Identify regional shipment volumes, delay patterns, and financial performance.")
    
        if not dashboard_df.empty:
            df = dashboard_df.copy()
            region_col = resolve_column(df, ["Order Region", "Region", "Order_Region"])
    
            if region_col is not None:
                regional = (
                    df.groupby(region_col, dropna=False)
                    .agg(
                        Total_Shipments=(region_col, "size"),
                        Delay_Rate=("_DASH_Actual_Delay_Flag", "mean"),
                        Average_Delay_Days=("_DASH_Delay_Days", "mean"),
                        Total_Sales=("_DASH_Sales", "sum"),
                        Total_Profit=("_DASH_Profit", "sum"),
                    )
                    .reset_index()
                )
                regional["Delay Rate (%)"] = (regional["Delay_Rate"] * 100)
    
                k1, k2, k3 = st.columns(3)
                k1.metric("Regions Represented", f"{regional[region_col].nunique(dropna=True):,}")
                k2.metric("Total Shipments", f"{len(df):,}")
                overall_delay = df["_DASH_Actual_Delay_Flag"].mean()
                k3.metric("Actual Delay Rate", f"{overall_delay * 100:.2f}%" if pd.notna(overall_delay) else "N/A")
    
                st.markdown("---")
    
                col1, col2 = st.columns(2)
    
                with col1:
                    st.subheader("Shipment Volume by Region")
                    fig = px.bar(
                        regional.sort_values("Total_Shipments"),
                        x="Total_Shipments", y=region_col, orientation="h", text_auto=True
                    )
                    chart_layout(fig, 500)
                    st.plotly_chart(fig, use_container_width=True)
    
                with col2:
                    st.subheader("Actual Delay Rate by Region")
                    valid_regional = regional.dropna(subset=["Delay Rate (%)"])
                    if not valid_regional.empty:
                        fig = px.bar(
                            valid_regional.sort_values("Delay Rate (%)"),
                            x="Delay Rate (%)", y=region_col, orientation="h", text_auto=".1f"
                        )
                        chart_layout(fig, 500)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        show_unavailable("Actual delay status is unavailable for this dataset.")
    
                st.subheader("Regional Performance Summary")
                display_cols = [region_col, "Total_Shipments", "Delay Rate (%)", "Average_Delay_Days", "Total_Sales", "Total_Profit"]
                st.dataframe(regional[display_cols].round(2), use_container_width=True, hide_index=True)
    
                state_col = resolve_column(df, ["Order State", "State", "Order_State"])
                if state_col is not None:
                    st.subheader("Top 15 States by Shipment Volume")
                    state_summary = (
                        df.groupby(state_col, dropna=False)
                        .size()
                        .reset_index(name="Shipments")
                        .sort_values("Shipments", ascending=False)
                        .head(15)
                    )
                    fig = px.bar(
                        state_summary.sort_values("Shipments"),
                        x="Shipments", y=state_col, orientation="h", text_auto=True
                    )
                    chart_layout(fig, 500)
                    st.plotly_chart(fig, use_container_width=True)
    
            else:
                show_unavailable("Order Region is unavailable in the filtered dataset.")
    
        else:
            show_unavailable("No shipment records match the selected filters.")
    
    elif selected_page == "Market Analysis":
        st.title("Market Analysis")
        st.markdown("Compare shipping volume, delivery delays, sales, and profitability across markets.")
    
        if not dashboard_df.empty:
            df = dashboard_df.copy()
            market_col = resolve_column(df, ["Market"])
    
            if market_col is not None:
                market_summary = (
                    df.groupby(market_col, dropna=False)
                    .agg(
                        Total_Shipments=(market_col, "size"),
                        Delay_Rate=("_DASH_Actual_Delay_Flag", "mean"),
                        Average_Delay=("_DASH_Delay_Days", "mean"),
                        Sales=("_DASH_Sales", "sum"),
                        Profit=("_DASH_Profit", "sum"),
                    )
                    .reset_index()
                )
                market_summary["Delay Rate (%)"] = (market_summary["Delay_Rate"] * 100)
    
                k1, k2, k3 = st.columns(3)
                k1.metric("Markets Represented", f"{market_summary[market_col].nunique(dropna=True)}")
                k2.metric("Total Shipments", f"{len(df):,}")
                k3.metric("Total Sales", format_currency(df["_DASH_Sales"].sum(skipna=True)))
    
                st.markdown("---")
    
                col1, col2 = st.columns(2)
    
                with col1:
                    st.subheader("Shipment Distribution by Market")
                    fig = px.pie(market_summary, names=market_col, values="Total_Shipments", hole=0.45)
                    chart_layout(fig)
                    st.plotly_chart(fig, use_container_width=True)
    
                with col2:
                    st.subheader("Actual Delay Rate by Market")
                    valid = market_summary.dropna(subset=["Delay Rate (%)"])
                    if not valid.empty:
                        fig = px.bar(valid, x=market_col, y="Delay Rate (%)", text_auto=".1f")
                        chart_layout(fig)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        show_unavailable("Actual delay data is unavailable.")
    
                col3, col4 = st.columns(2)
    
                with col3:
                    st.subheader("Sales and Profit by Market")
                    market_money = market_summary.melt(
                        id_vars=[market_col], value_vars=["Sales", "Profit"],
                        var_name="Metric", value_name="Amount"
                    )
                    fig = px.bar(market_money, x=market_col, y="Amount", color="Metric", barmode="group")
                    chart_layout(fig)
                    st.plotly_chart(fig, use_container_width=True)
    
                with col4:
                    st.subheader("Shipping Modes by Market")
                    mode_col = resolve_column(df, ["Shipping Mode", "Shipping_Mode"])
                    if mode_col is not None:
                        mode_summary = (
                            df.groupby([market_col, mode_col], dropna=False)
                            .size()
                            .reset_index(name="Shipments")
                        )
                        fig = px.bar(mode_summary, x=market_col, y="Shipments", color=mode_col, barmode="stack")
                        chart_layout(fig)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        show_unavailable("Shipping Mode is unavailable.")
    
                st.subheader("Market Performance Summary")
                st.dataframe(market_summary.round(2), use_container_width=True, hide_index=True)
    
            else:
                show_unavailable("Market column is unavailable.")
    
        else:
            show_unavailable("No shipment records match the selected filters.")
    
    elif selected_page == "Country Analysis":
        st.title("Country-Level Operations Analysis")
        st.markdown("Identify country-level shipment volumes, delays, and financial trends.")
    
        if not dashboard_df.empty:
            df = dashboard_df.copy()
            country_col = resolve_column(df, ["Order Country", "Country", "Order_Country"])
    
            if country_col is not None:
                country_summary = (
                    df.groupby(country_col, dropna=False)
                    .agg(
                        Shipments=(country_col, "size"),
                        Delay_Rate=("_DASH_Actual_Delay_Flag", "mean"),
                        Average_Delay=("_DASH_Delay_Days", "mean"),
                        Sales=("_DASH_Sales", "sum"),
                        Profit=("_DASH_Profit", "sum"),
                    )
                    .reset_index()
                )
                country_summary["Delay Rate (%)"] = (country_summary["Delay_Rate"] * 100)
    
                k1, k2, k3 = st.columns(3)
                k1.metric("Countries Represented", f"{country_summary[country_col].nunique(dropna=True):,}")
                k2.metric("Total Shipments", f"{len(df):,}")
                k3.metric("Total Sales", format_currency(df["_DASH_Sales"].sum(skipna=True)))
    
                st.markdown("---")
    
                top_countries = country_summary.nlargest(15, "Shipments")
    
                col1, col2 = st.columns(2)
    
                with col1:
                    st.subheader("Top 15 Countries by Shipment Volume")
                    fig = px.bar(
                        top_countries.sort_values("Shipments"),
                        x="Shipments", y=country_col, orientation="h", text_auto=True
                    )
                    chart_layout(fig, 550)
                    st.plotly_chart(fig, use_container_width=True)
    
                with col2:
                    st.subheader("Actual Delay Rate — Top 15 Countries")
                    valid_countries = top_countries.dropna(subset=["Delay Rate (%)"])
                    if not valid_countries.empty:
                        fig = px.bar(
                            valid_countries.sort_values("Delay Rate (%)"),
                            x="Delay Rate (%)", y=country_col, orientation="h", text_auto=".1f"
                        )
                        chart_layout(fig, 550)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        show_unavailable("Actual delay status is unavailable.")
    
                st.subheader("Country-Level Financial Performance")
                country_fin = country_summary.nlargest(15, "Sales")
                fig = px.bar(
                    country_fin.sort_values("Sales"),
                    x="Sales", y=country_col, orientation="h", hover_data=["Profit", "Shipments"]
                )
                chart_layout(fig, 550)
                st.plotly_chart(fig, use_container_width=True)
    
                st.subheader("Country Performance Table")
                st.dataframe(
                    country_summary.sort_values("Shipments", ascending=False).round(2),
                    use_container_width=True, hide_index=True
                )
    
            else:
                show_unavailable("Order Country is unavailable.")
    
        else:
            show_unavailable("No shipment records match the selected filters.")
    
    elif selected_page == "Customer Segments":
        st.title("Customer Segment Analysis")
        st.markdown("Analyze customer groups, shipment activity, sales, and profitability.")
    
        if not dashboard_df.empty:
            df = dashboard_df.copy()
            segment_col = resolve_column(df, ["Customer Segment", "Customer Segment Name", "Customer_Segment", "Segment"])
            customer_col = resolve_column(df, ["Customer Id", "Customer ID", "CustomerId", "Customer_Id"])
    
            if segment_col is not None:
                segment_summary = (
                    df.groupby(segment_col, dropna=False)
                    .agg(
                        Shipment_Records=(segment_col, "size"),
                        Sales=("_DASH_Sales", "sum"),
                        Profit=("_DASH_Profit", "sum"),
                        Average_Quantity=("_DASH_Quantity", "mean"),
                    )
                    .reset_index()
                )
    
                if customer_col is not None:
                    customers = (
                        df.groupby(segment_col, dropna=False)[customer_col]
                        .nunique()
                        .reset_index(name="Unique Customers")
                    )
                    segment_summary = segment_summary.merge(customers, on=segment_col, how="left")
    
                k1, k2, k3 = st.columns(3)
                k1.metric("Segment Categories", f"{segment_summary[segment_col].nunique(dropna=True):,}")
                k2.metric("Shipment Records", f"{len(df):,}")
                k3.metric("Unique Customers", f"{df[customer_col].nunique(dropna=True):,}" if customer_col is not None else "Unavailable")
                st.caption(
                    "Customer Segment is treated as the existing category in the source dataset. "
                    "Shipment Records count rows, not unique shipments; Unique Customers counts distinct customer IDs when available."
                )
                if customer_col is None:
                    st.info("No customer ID column was detected, so unique-customer counts cannot be calculated.")
    
                st.markdown("---")
    
                col1, col2 = st.columns(2)
    
                with col1:
                    st.subheader("Shipment Distribution by Segment")
                    fig = px.pie(segment_summary, names=segment_col, values="Shipment_Records", hole=0.45)
                    chart_layout(fig)
                    st.plotly_chart(fig, use_container_width=True)
    
                with col2:
                    st.subheader("Sales by Customer Segment")
                    fig = px.bar(segment_summary, x=segment_col, y="Sales", text_auto=".2s", color=segment_col)
                    fig.update_layout(showlegend=False)
                    chart_layout(fig)
                    st.plotly_chart(fig, use_container_width=True)
    
                st.subheader("Profit by Customer Segment")
                fig = px.bar(segment_summary, x=segment_col, y="Profit", text_auto=".2s")
                chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)
    
                st.subheader("Customer Segment Summary")
                st.dataframe(segment_summary.round(2), use_container_width=True, hide_index=True)
    
            else:
                show_unavailable(
                    "No dedicated customer-segment column was detected. Your APL Logistics dataset may not contain "
                    "predefined customer segments. Add a documented segmentation method before presenting segment-level conclusions."
                )
    
        else:
            show_unavailable("No shipment records match the selected filters.")
    
    elif selected_page == "Product & Category":
        st.title("Product & Category Analysis")
        st.markdown("Evaluate product shipment volumes, sales, quantities, and profitability.")
    
        if not dashboard_df.empty:
            df = dashboard_df.copy()
            category_col = resolve_column(df, ["Category Name", "Category", "Category_Name"])
            product_col = resolve_column(df, ["Product Name", "Product", "Product_Name"])
    
            if category_col is not None:
                category_summary = (
                    df.groupby(category_col, dropna=False)
                    .agg(
                        Shipments=(category_col, "size"),
                        Quantity=("_DASH_Quantity", "sum"),
                        Sales=("_DASH_Sales", "sum"),
                        Profit=("_DASH_Profit", "sum"),
                    )
                    .reset_index()
                )
    
                k1, k2, k3 = st.columns(3)
                k1.metric("Categories Represented", f"{category_summary[category_col].nunique(dropna=True):,}")
                k2.metric("Total Quantity", f"{df['_DASH_Quantity'].sum(skipna=True):,.0f}")
                k3.metric("Total Sales", format_currency(df["_DASH_Sales"].sum(skipna=True)))
    
                st.markdown("---")
    
                col1, col2 = st.columns(2)
    
                with col1:
                    st.subheader("Top 20 Categories by Shipment Volume")
                    top_categories = category_summary.nlargest(20, "Shipments")
                    fig = px.bar(
                        top_categories.sort_values("Shipments"),
                        x="Shipments", y=category_col, orientation="h", text_auto=True
                    )
                    chart_layout(fig, 600)
                    st.plotly_chart(fig, use_container_width=True)
    
                with col2:
                    st.subheader("Sales by Category")
                    fig = px.bar(
                        category_summary.sort_values("Sales", ascending=False).head(20),
                        x="Sales", y=category_col, orientation="h", hover_data=["Profit", "Quantity"]
                    )
                    chart_layout(fig, 600)
                    st.plotly_chart(fig, use_container_width=True)
    
                st.subheader("Profit by Category")
                fig = px.bar(
                    category_summary.sort_values("Profit", ascending=False).head(20),
                    x=category_col, y="Profit", text_auto=".2s"
                )
                chart_layout(fig, 450)
                st.plotly_chart(fig, use_container_width=True)
    
                st.subheader("Top Products by Sales")
                if product_col is not None:
                    product_summary = (
                        df.groupby(product_col, dropna=False)
                        .agg(
                            Shipments=(product_col, "size"),
                            Quantity=("_DASH_Quantity", "sum"),
                            Sales=("_DASH_Sales", "sum"),
                            Profit=("_DASH_Profit", "sum"),
                        )
                        .reset_index()
                        .nlargest(20, "Sales")
                    )
                    fig = px.bar(
                        product_summary.sort_values("Sales"),
                        x="Sales", y=product_col, orientation="h", hover_data=["Quantity", "Profit"]
                    )
                    chart_layout(fig, 600)
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(product_summary.round(2), use_container_width=True, hide_index=True)
                else:
                    show_unavailable("A product-name column is unavailable. Category-level analysis is still available.")
    
            else:
                show_unavailable("Category Name is unavailable. Check your actual dataset and analysis outputs before adding category charts.")
    
        else:
            show_unavailable("No shipment records match the selected filters.")
    
    elif selected_page == "Relationship Analysis":
        st.title("Multivariate Relationship Analysis")
        st.markdown("Explore correlations between financial metrics, shipping duration, and actual delivery delays.")
    
        if not dashboard_df.empty:
            df = dashboard_df.copy()
            numeric_cols = [
                "_DASH_Sales", "_DASH_Profit", "_DASH_Quantity",
                "_DASH_Actual_Days", "_DASH_Scheduled_Days", "_DASH_Delay_Days",
            ]
            numeric_df = df[numeric_cols].copy()
            numeric_df = numeric_df.rename(
                columns={
                    "_DASH_Sales": "Sales",
                    "_DASH_Profit": "Recorded Profit",
                    "_DASH_Quantity": "Order Quantity",
                    "_DASH_Actual_Days": "Actual Shipping Days",
                    "_DASH_Scheduled_Days": "Scheduled Shipping Days",
                    "_DASH_Delay_Days": "Shipping Delay Days",
                }
            )
    
            usable_cols = [
                col for col in numeric_df.columns
                if numeric_df[col].notna().sum() >= 2 and numeric_df[col].nunique(dropna=True) > 1
            ]
    
            if len(usable_cols) >= 2:
                corr_df = numeric_df[usable_cols].corr(method="pearson")
    
                st.subheader("Numerical Correlation Heatmap")
                fig = px.imshow(
                    corr_df, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r", zmin=-1, zmax=1
                )
                chart_layout(fig, 600)
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Pearson correlation measures linear association. Correlation does not establish causation.")
    
                col1, col2 = st.columns(2)
    
                with col1:
                    st.subheader("Sales vs Recorded Profit")
                    scatter_df = numeric_df.dropna(subset=["Sales", "Recorded Profit"])
                    if not scatter_df.empty:
                        scatter_df = scatter_df.sample(n=min(3000, len(scatter_df)), random_state=42)
                        fig = px.scatter(
                            scatter_df, x="Sales", y="Recorded Profit", opacity=0.6
                        )
                        chart_layout(fig)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        show_unavailable("Sales and recorded profit are not jointly available.")
    
                with col2:
                    st.subheader("Actual Shipping Days vs Delay Days")
                    scatter_df = numeric_df.dropna(subset=["Actual Shipping Days", "Shipping Delay Days"])
                    if not scatter_df.empty:
                        scatter_df = scatter_df.sample(n=min(3000, len(scatter_df)), random_state=42)
                        fig = px.scatter(
                            scatter_df, x="Actual Shipping Days", y="Shipping Delay Days", opacity=0.6
                        )
                        chart_layout(fig)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        show_unavailable("Shipping duration and delay fields are unavailable.")
    
                st.subheader("Correlation Matrix")
                st.dataframe(corr_df.round(3), use_container_width=True)
    
            else:
                show_unavailable("At least two varying numerical metrics are required to generate a correlation matrix.")
    
        else:
            show_unavailable("No shipment records match the selected filters.")
    
    else:
        st.subheader(selected_page)
        st.info("This dashboard module has not yet been implemented.")

# ============================================================
# FOOTERS AND DIAGNOSTICS
# ============================================================

with st.expander("Dashboard Inventory", expanded=False):
    if not dashboard_inventory.empty:
        st.dataframe(
            dashboard_inventory, use_container_width=True, hide_index=True
        )
    else:
        st.info("The dashboard inventory file was not found.")

with st.expander("Application Data Information", expanded=False):
    actual_delay_valid_count = int(df["_Actual_Delay_Flag"].notna().sum())
    actual_delay_unknown_count = int(df["_Actual_Delay_Flag"].isna().sum())
    source_duration_valid = (
        numeric_series(df, REAL_SHIPPING_DAYS_COL).notna()
        & numeric_series(df, SCHEDULED_SHIPPING_DAYS_COL).notna()
        & numeric_series(df, REAL_SHIPPING_DAYS_COL).ge(0)
        & numeric_series(df, SCHEDULED_SHIPPING_DAYS_COL).ge(0)
    )
    status_duration_mismatches = "Unavailable"
    status_col_diag = resolve_column(df, ["Delivery Status", "Delivery_Status"])
    if status_col_diag is not None and source_duration_valid.any():
        status_diag = df[status_col_diag].astype("string").str.strip().str.lower()
        recognized_status = status_diag.isin([
            "late delivery", "advance shipping", "shipping on time", "on time", "on-time", "early", "delivered early"
        ])
        check_mask = source_duration_valid & recognized_status
        if check_mask.any():
            duration_delayed = numeric_series(df, REAL_SHIPPING_DAYS_COL).gt(numeric_series(df, SCHEDULED_SHIPPING_DAYS_COL))
            status_delayed = status_diag.eq("late delivery")
            status_duration_mismatches = int((duration_delayed[check_mask] != status_delayed[check_mask]).sum())

    st.write({
        "Project Root": str(PROJECT_ROOT),
        "Primary Dataset": str(DATA_FILE),
        "Dataset Exists": DATA_FILE.exists(),
        "Dataset Rows": len(data),
        "Dataset Columns": len(data.columns),
        "Filtered Rows": len(filtered_df),
        "Detected Order Date Column": ORDER_DATE_COL,
        "Detected Shipping Mode Column": SHIPPING_MODE_COL,
        "Actual Delay Flag Source Priority": "Is_Delayed > actual-vs-scheduled duration > recognized Delivery Status",
        "Records with Known Actual Outcome": actual_delay_valid_count,
        "Records with Unknown Actual Outcome": actual_delay_unknown_count,
        "Status-vs-Duration Mismatches": status_duration_mismatches,
        "Master KPI File Exists": MASTER_KPI_FILE.exists(),
        "Master KPI Rows": len(master_kpis),
        "Dashboard Inventory Exists": DASHBOARD_INVENTORY_FILE.exists(),
        "Dashboard Inventory Rows": len(dashboard_inventory),
    })
    st.caption("Unknown actual outcomes are excluded from delay-rate denominators rather than counted as non-delayed.")

st.markdown(
    """
    <div class="dashboard-footer">
        APL Logistics Analytics Dashboard
        <br>
        Delivery Performance | Delay Risk | Logistics Efficiency
        <br>
        Developed as part of the Logistics Analytics Project
    </div>
    """,
    unsafe_allow_html=True
)