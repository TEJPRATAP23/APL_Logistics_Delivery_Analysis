# ============================================================
# APL LOGISTICS ANALYTICS DASHBOARD
# Complete Application
# ============================================================

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# 1. PROJECT PATHS AND PAGE CONFIGURATION
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

st.set_page_config(
    page_title="APL Logistics Analytics Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. THEME-ADAPTIVE STYLING
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: var(--background-color);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: var(--background-color);
    }

    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
    }

    .dashboard-title {
        font-size: 2rem;
        font-weight: 750;
        color: var(--text-color);
        margin-bottom: .15rem;
    }

    .dashboard-subtitle {
        color: var(--text-color);
        opacity: .75;
        margin-bottom: 1rem;
    }

    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, .25);
        border-radius: 12px;
        padding: 14px;
    }

    .dashboard-footer {
        text-align: center;
        opacity: .7;
        font-size: .85rem;
        padding-top: 24px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. DATA LOADING
# ============================================================

@st.cache_data(show_spinner="Loading logistics data...")
def load_csv(path_string, modified_time, primary=False):
    """Load a CSV safely without modifying the original file."""

    path = Path(path_string)

    if not path.exists():
        return pd.DataFrame()

    encodings = (
        ["cp1252", "utf-8-sig", "utf-8"]
        if primary
        else ["utf-8-sig", "cp1252", "utf-8"]
    )

    for encoding in encodings:
        try:
            frame = pd.read_csv(
                path,
                encoding=encoding,
                low_memory=False,
            )
            frame.columns = frame.columns.astype(str).str.strip()
            return frame

        except (UnicodeDecodeError, UnicodeError):
            continue

        except Exception:
            continue

    return pd.DataFrame()


data = load_csv(
    str(DATA_FILE),
    DATA_FILE.stat().st_mtime if DATA_FILE.exists() else 0,
    primary=True,
)

master_kpis = load_csv(
    str(MASTER_KPI_FILE),
    MASTER_KPI_FILE.stat().st_mtime if MASTER_KPI_FILE.exists() else 0,
)

dashboard_inventory = load_csv(
    str(DASHBOARD_INVENTORY_FILE),
    DASHBOARD_INVENTORY_FILE.stat().st_mtime
    if DASHBOARD_INVENTORY_FILE.exists()
    else 0,
)


st.markdown(
    '<div class="dashboard-title">'
    '🚚 APL Logistics Analytics Dashboard</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Delivery Performance | Delay Risk | Logistics Efficiency'
    '</div>',
    unsafe_allow_html=True,
)

if data.empty:
    st.error(
        "The primary dataset could not be loaded. Confirm that "
        "`data/feature_data/APL_Day3_Feature_Engineered.csv` exists."
    )
    st.stop()


# ============================================================
# 4. COLUMN DETECTION AND DATA PREPARATION
# ============================================================

def find_column(frame, candidates):
    """Find a column without depending on capitalization."""

    if frame is None or frame.empty:
        return None

    lookup = {
        str(column).strip().lower(): column
        for column in frame.columns
    }

    for candidate in candidates:
        key = candidate.strip().lower()

        if key in lookup:
            return lookup[key]

    return None


def numeric_series(frame, column):
    """Return a numeric series or an aligned NaN series."""

    if column is None or column not in frame.columns:
        return pd.Series(np.nan, index=frame.index, dtype=float)

    return pd.to_numeric(frame[column], errors="coerce")


SHIPPING_MODE_COL = find_column(
    data,
    ["Shipping Mode", "Shipping_Mode"],
)

REGION_COL = find_column(
    data,
    ["Order Region", "Order_Region"],
)

MARKET_COL = find_column(
    data,
    ["Market"],
)

SEGMENT_COL = find_column(
    data,
    ["Customer Segment", "Customer_Segment"],
)

COUNTRY_COL = find_column(
    data,
    ["Order Country", "Order_Country"],
)

STATE_COL = find_column(
    data,
    ["Order State", "Order_State", "State"],
)

DELIVERY_STATUS_COL = find_column(
    data,
    ["Delivery Status", "Delivery_Status"],
)

ORDER_DATE_COL = find_column(
    data,
    [
        "order date (DateOrders)",
        "Order Date",
        "Order_Date",
        "OrderDate",
        "order_date",
    ],
)

SHIPMENT_DELAY_COL = find_column(
    data,
    ["Shipping_Delay_Days", "Shipping Delay Days"],
)

REAL_SHIPPING_DAYS_COL = find_column(
    data,
    [
        "Days for shipping (real)",
        "Days_for_shipping_real",
        "Actual Shipping Days",
    ],
)

SCHEDULED_SHIPPING_DAYS_COL = find_column(
    data,
    [
        "Days for shipment (scheduled)",
        "Days_for_shipment_scheduled",
        "Scheduled Shipping Days",
    ],
)

IS_DELAYED_COL = find_column(
    data,
    ["Is_Delayed", "Is Delayed"],
)

LATE_RISK_COL = find_column(
    data,
    ["Late_delivery_risk", "Late Delivery Risk"],
)

DELAY_SEVERITY_COL = find_column(
    data,
    ["Delay_Severity", "Delay Severity"],
)

SALES_COL = find_column(
    data,
    ["Sales", "Sales Amount"],
)

PROFIT_COL = find_column(
    data,
    ["Order Profit Per Order", "Order_Profit_Per_Order", "Profit"],
)

QUANTITY_COL = find_column(
    data,
    ["Order Item Quantity", "Quantity"],
)

ORDER_ID_COL = find_column(
    data,
    ["Order Id", "Order ID", "Order_Id"],
)

CUSTOMER_ID_COL = find_column(
    data,
    ["Customer Id", "Customer ID", "CustomerId", "Customer_Id"],
)

CATEGORY_COL = find_column(
    data,
    ["Category Name", "Category", "Category_Name"],
)

PRODUCT_COL = find_column(
    data,
    ["Product Name", "Product", "Product_Name"],
)


df = data.copy()

if ORDER_DATE_COL is not None:
    df[ORDER_DATE_COL] = pd.to_datetime(
        df[ORDER_DATE_COL],
        errors="coerce",
    )


# Create delay duration only when it does not already exist.
if (
    SHIPMENT_DELAY_COL is None
    and REAL_SHIPPING_DAYS_COL is not None
    and SCHEDULED_SHIPPING_DAYS_COL is not None
):
    df["Shipping_Delay_Days"] = (
        numeric_series(df, REAL_SHIPPING_DAYS_COL)
        - numeric_series(df, SCHEDULED_SHIPPING_DAYS_COL)
    )

    SHIPMENT_DELAY_COL = "Shipping_Delay_Days"


def actual_delay_flag(frame):
    """
    Determine actual delay using this priority:
    1. Valid engineered Is_Delayed flag.
    2. Actual versus scheduled shipping durations.
    3. Recognized delivery status.
    """

    result = pd.Series(
        np.nan,
        index=frame.index,
        dtype=float,
    )

    engineered = find_column(
        frame,
        ["Is_Delayed", "Is Delayed"],
    )

    if engineered is not None:
        values = numeric_series(frame, engineered)
        valid = values.isin([0, 1])
        result.loc[valid] = values.loc[valid]

    actual = find_column(
        frame,
        [
            "Days for shipping (real)",
            "Days_for_shipping_real",
            "Actual Shipping Days",
        ],
    )

    scheduled = find_column(
        frame,
        [
            "Days for shipment (scheduled)",
            "Days_for_shipment_scheduled",
            "Scheduled Shipping Days",
        ],
    )

    if actual is not None and scheduled is not None:
        actual_values = numeric_series(frame, actual)
        scheduled_values = numeric_series(frame, scheduled)

        valid = (
            actual_values.notna()
            & scheduled_values.notna()
            & actual_values.ge(0)
            & scheduled_values.ge(0)
        )

        fallback = result.isna() & valid

        result.loc[fallback] = (
            actual_values.loc[fallback]
            > scheduled_values.loc[fallback]
        ).astype(float)

    status_col = find_column(
        frame,
        ["Delivery Status", "Delivery_Status"],
    )

    if status_col is not None:
        status = (
            frame[status_col]
            .astype("string")
            .str.strip()
            .str.lower()
        )

        mapping = {
            "late delivery": 1.0,
            "advance shipping": 0.0,
            "shipping on time": 0.0,
            "on time": 0.0,
            "on-time": 0.0,
            "early": 0.0,
            "delivered early": 0.0,
        }

        mapped = status.map(mapping)
        fallback = result.isna() & mapped.notna()

        result.loc[fallback] = mapped.loc[fallback]

    return result


# Calculate analytical fields on the full in-memory dataset.
# The source CSV is never modified.

df["_Actual_Delay_Flag"] = actual_delay_flag(df)

df["_On_Time_Flag"] = (
    1 - df["_Actual_Delay_Flag"]
).where(
    df["_Actual_Delay_Flag"].isin([0, 1]),
    np.nan,
)

df["_DASH_Sales"] = numeric_series(df, SALES_COL)
df["_DASH_Profit"] = numeric_series(df, PROFIT_COL)
df["_DASH_Quantity"] = numeric_series(df, QUANTITY_COL)

df["_DASH_Actual_Days"] = numeric_series(
    df,
    REAL_SHIPPING_DAYS_COL,
)

df["_DASH_Scheduled_Days"] = numeric_series(
    df,
    SCHEDULED_SHIPPING_DAYS_COL,
)

if SHIPMENT_DELAY_COL is not None:
    df["_DASH_Delay_Days"] = numeric_series(
        df,
        SHIPMENT_DELAY_COL,
    )
else:
    df["_DASH_Delay_Days"] = (
        df["_DASH_Actual_Days"]
        - df["_DASH_Scheduled_Days"]
    )

df["_DASH_Late_Risk"] = numeric_series(df, LATE_RISK_COL)


# ============================================================
# 5. SIDEBAR NAVIGATION AND GLOBAL FILTERS
# ============================================================

PAGES = [
    "Overview",
    "Delivery Performance",
    "Delay Risk",
    "Shipping Efficiency",
    "Financial Performance",
    "Regional Analysis",
    "Market Analysis",
    "Country Analysis",
    "Customer Segments",
    "Product & Category",
    "Relationship Analysis",
]


with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:8px 0 18px">
            <div style="font-size:2.7rem">🚚</div>
            <div style="font-size:1.25rem;font-weight:750">
                APL LOGISTICS
            </div>
            <div style="font-size:.85rem;opacity:.7">
                Analytics & Intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_page = st.radio(
        "Select Dashboard",
        PAGES,
        index=0,
        key="dashboard_page",
    )

    st.divider()
    st.markdown("### Integrated Filters")

    st.caption(
        "All filters are selected by default. Select at least one "
        "value in every available filter. If any filter is empty, "
        "the analytical outputs will remain empty."
    )

    selected_date_range = None

    # The full available date range is selected by default.
    if ORDER_DATE_COL is not None:
        valid_dates = df[ORDER_DATE_COL].dropna()

        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            selected_date_range = st.date_input(
                "Order Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="filter_order_date",
            )

    filter_dict = {}

    filter_columns = [
        (
            "Shipping Mode",
            SHIPPING_MODE_COL,
            "filter_shipping_mode",
        ),
        (
            "Order Region",
            REGION_COL,
            "filter_order_region",
        ),
        (
            "Market",
            MARKET_COL,
            "filter_market",
        ),
        (
            "Customer Segment",
            SEGMENT_COL,
            "filter_customer_segment",
        ),
    ]

    for label, column, key in filter_columns:
        if column is None:
            continue

        options = sorted(
            df[column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        # Select every available value on the first launch.
        # Streamlit preserves subsequent user selections using key.
        selected_values = st.multiselect(
            label,
            options=options,
            default=options,
            key=key,
            help=(
                "Select one or more values. Clearing this filter "
                "will temporarily empty the analytical outputs."
            ),
        )

        filter_dict[column] = selected_values

    st.divider()

    st.caption(
        "Delivery Performance, Delay Risk, and Logistics Efficiency"
    )

    st.caption("Project data: APL Logistics")


# ============================================================
# 6. APPLY GLOBAL FILTERS
# ============================================================

# A filter is required only if its corresponding dataset column exists.
empty_filters = [
    label
    for label, column, key in filter_columns
    if column is not None
    and len(filter_dict.get(column, [])) == 0
]

filtered_df = df.copy()


# An empty selection in ANY available filter means no records.
if empty_filters:
    filtered_df = df.iloc[0:0].copy()

else:
    # Apply the date filter when a date column is available.
    if (
        selected_date_range is not None
        and isinstance(selected_date_range, (tuple, list))
        and len(selected_date_range) == 2
        and ORDER_DATE_COL is not None
    ):
        start_date, end_date = selected_date_range

        if start_date is not None and end_date is not None:
            date_values = filtered_df[ORDER_DATE_COL].dt.date

            date_mask = (
                date_values.notna()
                & date_values.ge(start_date)
                & date_values.le(end_date)
            )

            filtered_df = filtered_df.loc[date_mask]

    # Apply categorical filters.
    for column, selected_values in filter_dict.items():
        filtered_df = filtered_df.loc[
            filtered_df[column].astype(str).isin(selected_values)
        ]


# Preserve the same analytical fields in the filtered dataset.
filtered_df = filtered_df.copy()

filtered_df["_Actual_Delay_Flag"] = actual_delay_flag(
    filtered_df
)

filtered_df["_On_Time_Flag"] = (
    1 - filtered_df["_Actual_Delay_Flag"]
).where(
    filtered_df["_Actual_Delay_Flag"].isin([0, 1]),
    np.nan,
)

filtered_df["_DASH_Sales"] = numeric_series(
    filtered_df,
    SALES_COL,
)

filtered_df["_DASH_Profit"] = numeric_series(
    filtered_df,
    PROFIT_COL,
)

filtered_df["_DASH_Quantity"] = numeric_series(
    filtered_df,
    QUANTITY_COL,
)

filtered_df["_DASH_Actual_Days"] = numeric_series(
    filtered_df,
    REAL_SHIPPING_DAYS_COL,
)

filtered_df["_DASH_Scheduled_Days"] = numeric_series(
    filtered_df,
    SCHEDULED_SHIPPING_DAYS_COL,
)

if SHIPMENT_DELAY_COL is not None:
    filtered_df["_DASH_Delay_Days"] = numeric_series(
        filtered_df,
        SHIPMENT_DELAY_COL,
    )
else:
    filtered_df["_DASH_Delay_Days"] = (
        filtered_df["_DASH_Actual_Days"]
        - filtered_df["_DASH_Scheduled_Days"]
    )

filtered_df["_DASH_Late_Risk"] = numeric_series(
    filtered_df,
    LATE_RISK_COL,
)

st.divider()


# ============================================================
# 7. SHARED DASHBOARD HELPERS
# ============================================================

def money(value):
    """Format a numeric amount as currency."""

    return f"${value:,.2f}" if pd.notna(value) else "N/A"


def chart_layout(fig, height=420):
    """Apply consistent transparent chart styling."""

    fig.update_layout(
        height=height,
        margin=dict(l=15, r=15, t=50, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def unavailable(message):
    st.info(message)


def safe_bar(
    frame,
    x,
    y,
    title,
    horizontal=False,
    color=None,
    height=420,
):
    """Render a bar chart only when its inputs are available."""

    if (
        frame.empty
        or x not in frame.columns
        or y not in frame.columns
    ):
        unavailable(f"Not enough data to display: {title}.")
        return

    if horizontal:
        fig = px.bar(
            frame,
            x=y,
            y=x,
            orientation="h",
            color=color,
            title=title,
        )
    else:
        fig = px.bar(
            frame,
            x=x,
            y=y,
            color=color,
            title=title,
        )

    st.plotly_chart(
        chart_layout(fig, height),
        use_container_width=True,
    )


def grouped_summary(frame, group_col, metrics):
    """Build a safe grouped summary."""

    if (
        group_col is None
        or group_col not in frame.columns
        or frame.empty
    ):
        return pd.DataFrame()

    aggregations = {}

    for output, source, operation in metrics:
        if source in frame.columns:
            aggregations[output] = (source, operation)

    if not aggregations:
        return (
            frame.groupby(group_col, dropna=False)
            .size()
            .reset_index(name="Shipments")
        )

    return (
        frame.groupby(group_col, dropna=False)
        .agg(**aggregations)
        .reset_index()
    )


# ============================================================
# 8. MODULE ROUTING
# ============================================================

if empty_filters:
    st.warning(
        "Dashboard outputs are currently empty. Select at least "
        "one value in each available filter: "
        f"{', '.join(empty_filters)}. "
        "Charts, KPIs, tables, and analytical results will appear "
        "after every required filter has a selection."
    )

elif filtered_df.empty:
    st.warning(
        "No shipment records match the selected filters. "
        "Please adjust the selections."
    )

else:
    f = filtered_df

    st.caption(
        f"Showing {len(f):,} shipment records "
        "after applying the global filters."
    )

    # ========================================================
    # MODULE 1: OVERVIEW
    # ========================================================

    if selected_page == "Overview":
        st.subheader("Executive Overview")

        valid_delay = f["_Actual_Delay_Flag"].dropna()
        valid_ontime = f["_On_Time_Flag"].dropna()

        positive_delays = f.loc[
            f["_DASH_Delay_Days"] > 0,
            "_DASH_Delay_Days",
        ]

        kpis = st.columns(5)

        kpis[0].metric(
            "📦 Total Shipment Records",
            f"{len(f):,}",
        )

        kpis[1].metric(
            "✅ On-Time / Early Rate",
            (
                f"{valid_ontime.mean() * 100:.2f}%"
                if len(valid_ontime)
                else "N/A"
            ),
        )

        kpis[2].metric(
            "⚠️ Actual Late Delivery Rate",
            (
                f"{valid_delay.mean() * 100:.2f}%"
                if len(valid_delay)
                else "N/A"
            ),
        )

        kpis[3].metric(
            "🕒 Avg Delay Among Late Records",
            (
                f"{positive_delays.mean():.2f} days"
                if len(positive_delays)
                else "N/A"
            ),
        )

        kpis[4].metric(
            "💰 Total Sales",
            (
                money(f["_DASH_Sales"].sum())
                if f["_DASH_Sales"].notna().any()
                else "N/A"
            ),
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Shipment Volume by Shipping Mode")

            if SHIPPING_MODE_COL:
                summary = (
                    f.groupby(SHIPPING_MODE_COL, dropna=False)
                    .size()
                    .reset_index(name="Shipments")
                )

                safe_bar(
                    summary,
                    SHIPPING_MODE_COL,
                    "Shipments",
                    "Shipment Volume by Mode",
                )
            else:
                unavailable("Shipping Mode column is unavailable.")

        with col2:
            st.subheader("Delivery Status Distribution")

            if DELIVERY_STATUS_COL:
                summary = (
                    f[DELIVERY_STATUS_COL]
                    .fillna("Unknown")
                    .astype(str)
                    .value_counts()
                    .rename_axis("Status")
                    .reset_index(name="Shipments")
                )

                fig = px.pie(
                    summary,
                    names="Status",
                    values="Shipments",
                    hole=0.5,
                    title="Delivery Status",
                )

                st.plotly_chart(
                    chart_layout(fig),
                    use_container_width=True,
                )
            else:
                unavailable("Delivery Status column is unavailable.")

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Shipment Volume by Region")

            if REGION_COL:
                summary = (
                    f.groupby(REGION_COL, dropna=False)
                    .size()
                    .reset_index(name="Shipments")
                    .sort_values("Shipments", ascending=False)
                )

                safe_bar(
                    summary,
                    REGION_COL,
                    "Shipments",
                    "Shipments by Region",
                    horizontal=True,
                )
            else:
                unavailable("Order Region column is unavailable.")

        with col4:
            st.subheader("Sales by Market")

            if MARKET_COL and f["_DASH_Sales"].notna().any():
                summary = (
                    f.groupby(MARKET_COL, dropna=False)["_DASH_Sales"]
                    .sum()
                    .reset_index()
                )

                safe_bar(
                    summary,
                    MARKET_COL,
                    "_DASH_Sales",
                    "Total Sales by Market",
                )
            else:
                unavailable("Market or Sales data is unavailable.")

        st.subheader("Sample Shipment Records")

        preferred = [
            ORDER_ID_COL,
            ORDER_DATE_COL,
            SHIPPING_MODE_COL,
            REGION_COL,
            MARKET_COL,
            COUNTRY_COL,
            DELIVERY_STATUS_COL,
            SHIPMENT_DELAY_COL,
            SALES_COL,
        ]

        display = [
            column
            for column in preferred
            if column is not None and column in f.columns
        ]

        st.dataframe(
            f[display].head(20) if display else f.head(20),
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # MODULE 2: DELIVERY PERFORMANCE
    # ========================================================

    elif selected_page == "Delivery Performance":
        st.subheader("Delivery Performance Analysis")

        known = f["_Actual_Delay_Flag"].dropna()
        delayed = int(known.eq(1).sum())

        cols = st.columns(4)

        cols[0].metric("Shipment Records", f"{len(f):,}")
        cols[1].metric("Known Delivery Outcomes", f"{len(known):,}")
        cols[2].metric("Actual Delayed Shipments", f"{delayed:,}")

        cols[3].metric(
            "Actual Delay Rate",
            (
                f"{known.mean() * 100:.2f}%"
                if len(known)
                else "N/A"
            ),
        )

        c1, c2 = st.columns(2)

        with c1:
            if DELIVERY_STATUS_COL:
                summary = (
                    f[DELIVERY_STATUS_COL]
                    .fillna("Unknown")
                    .astype(str)
                    .value_counts()
                    .rename_axis("Status")
                    .reset_index(name="Shipments")
                )

                fig = px.pie(
                    summary,
                    names="Status",
                    values="Shipments",
                    hole=0.45,
                    title="Delivery Status Breakdown",
                )

                st.plotly_chart(
                    chart_layout(fig),
                    use_container_width=True,
                )
            else:
                unavailable("Delivery Status column is unavailable.")

        with c2:
            values = f["_DASH_Delay_Days"].dropna()

            if not values.empty:
                fig = px.histogram(
                    pd.DataFrame({"Delay Days": values}),
                    x="Delay Days",
                    nbins=30,
                    title="Shipping Delay Distribution",
                )

                st.plotly_chart(
                    chart_layout(fig),
                    use_container_width=True,
                )
            else:
                unavailable("Shipping-delay data is unavailable.")

        if SHIPPING_MODE_COL:
            summary = (
                f.groupby(SHIPPING_MODE_COL, dropna=False)
                .agg(
                    Shipments=("_Actual_Delay_Flag", "size"),
                    Delay_Rate=("_Actual_Delay_Flag", "mean"),
                )
                .reset_index()
            )

            summary["Delay Rate (%)"] = summary["Delay_Rate"] * 100

            safe_bar(
                summary,
                SHIPPING_MODE_COL,
                "Delay Rate (%)",
                "Actual Delay Rate by Shipping Mode",
            )

            st.dataframe(
                summary.round(2),
                use_container_width=True,
                hide_index=True,
            )

    # ========================================================
    # MODULE 3: DELAY RISK
    # ========================================================

    elif selected_page == "Delay Risk":
        st.subheader("Delay Risk Dashboard")

        st.caption(
            "Late_delivery_risk is the dataset risk label. Actual delay "
            "is calculated from a valid Is_Delayed flag, actual-versus-"
            "scheduled shipping durations, or recognized delivery "
            "statuses. This descriptive comparison is not an "
            "independent model-performance evaluation."
        )

        if LATE_RISK_COL:
            risk = numeric_series(f, LATE_RISK_COL)

            valid_mask = risk.isin([0, 1])
            risk_df = f.loc[valid_mask].copy()
            risk_df["_Risk_Value"] = risk.loc[valid_mask]

            high = int(risk_df["_Risk_Value"].eq(1).sum())
            low = int(risk_df["_Risk_Value"].eq(0).sum())

            k = st.columns(4)

            k[0].metric("Valid Risk Records", f"{len(risk_df):,}")
            k[1].metric("High-Risk Records", f"{high:,}")
            k[2].metric("Lower-Risk Records", f"{low:,}")

            k[3].metric(
                "High-Risk Percentage",
                (
                    f"{high / len(risk_df) * 100:.2f}%"
                    if len(risk_df)
                    else "N/A"
                ),
            )

            if not risk_df.empty:
                risk_df["_Risk_Label"] = (
                    risk_df["_Risk_Value"]
                    .map({0: "Lower Risk", 1: "Higher Risk"})
                )

                c1, c2 = st.columns(2)

                with c1:
                    counts = (
                        risk_df["_Risk_Label"]
                        .value_counts()
                        .rename_axis("Risk Category")
                        .reset_index(name="Records")
                    )

                    fig = px.pie(
                        counts,
                        names="Risk Category",
                        values="Records",
                        hole=0.5,
                        title="Risk Classification Distribution",
                    )

                    st.plotly_chart(
                        chart_layout(fig),
                        use_container_width=True,
                    )

                with c2:
                    if SHIPPING_MODE_COL:
                        summary = (
                            risk_df.groupby(
                                SHIPPING_MODE_COL,
                                dropna=False,
                            )
                            .agg(
                                Total_Records=("_Risk_Value", "size"),
                                High_Risk_Records=(
                                    "_Risk_Value",
                                    lambda values: int(values.eq(1).sum()),
                                ),
                            )
                            .reset_index()
                        )

                        summary["High-Risk %"] = (
                            summary["High_Risk_Records"]
                            / summary["Total_Records"]
                            * 100
                        )

                        safe_bar(
                            summary,
                            SHIPPING_MODE_COL,
                            "High_Risk_Records",
                            "High-Risk Records by Shipping Mode",
                        )

                        st.dataframe(
                            summary.round(2),
                            use_container_width=True,
                            hide_index=True,
                        )

                if REGION_COL:
                    summary = (
                        risk_df.groupby(REGION_COL, dropna=False)
                        .agg(
                            Total_Records=("_Risk_Value", "size"),
                            High_Risk_Records=(
                                "_Risk_Value",
                                lambda values: int(values.eq(1).sum()),
                            ),
                        )
                        .reset_index()
                    )

                    summary["High-Risk %"] = (
                        summary["High_Risk_Records"]
                        / summary["Total_Records"]
                        * 100
                    )

                    safe_bar(
                        summary.sort_values("High-Risk %"),
                        REGION_COL,
                        "High-Risk %",
                        "High-Risk Percentage by Region",
                        horizontal=True,
                    )

                if COUNTRY_COL:
                    summary = (
                        risk_df.groupby(COUNTRY_COL, dropna=False)
                        .agg(
                            Total_Records=("_Risk_Value", "size"),
                            High_Risk_Records=(
                                "_Risk_Value",
                                lambda values: int(values.eq(1).sum()),
                            ),
                        )
                        .reset_index()
                        .sort_values(
                            "High_Risk_Records",
                            ascending=False,
                        )
                        .head(10)
                    )

                    safe_bar(
                        summary,
                        COUNTRY_COL,
                        "High_Risk_Records",
                        "Top 10 Countries by High-Risk Records",
                        horizontal=True,
                    )

                st.subheader("High-Risk Shipment Records")

                high_records = risk_df[
                    risk_df["_Risk_Value"].eq(1)
                ]

                preferred = [
                    ORDER_ID_COL,
                    SHIPPING_MODE_COL,
                    REGION_COL,
                    MARKET_COL,
                    COUNTRY_COL,
                    DELIVERY_STATUS_COL,
                    SHIPMENT_DELAY_COL,
                    REAL_SHIPPING_DAYS_COL,
                    SCHEDULED_SHIPPING_DAYS_COL,
                    LATE_RISK_COL,
                ]

                display = [
                    column
                    for column in preferred
                    if column is not None and column in high_records.columns
                ]

                st.dataframe(
                    (
                        high_records[display].head(100)
                        if display
                        else high_records.head(100)
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    label="Download High-Risk Records CSV",
                    data=high_records.to_csv(
                        index=False
                    ).encode("utf-8-sig"),
                    file_name="APL_High_Risk_Records.csv",
                    mime="text/csv",
                )

            else:
                unavailable(
                    "No valid 0/1 risk labels are present "
                    "in the filtered records."
                )

        else:
            unavailable("The Late_delivery_risk column is unavailable.")

    # ========================================================
    # MODULE 4: SHIPPING EFFICIENCY
    # ========================================================

    elif selected_page == "Shipping Efficiency":
        st.subheader("Shipping Efficiency Dashboard")

        if REAL_SHIPPING_DAYS_COL and SCHEDULED_SHIPPING_DAYS_COL:
            actual = numeric_series(f, REAL_SHIPPING_DAYS_COL)
            scheduled = numeric_series(f, SCHEDULED_SHIPPING_DAYS_COL)

            valid = (
                actual.notna()
                & scheduled.notna()
                & actual.ge(0)
                & scheduled.ge(0)
            )

            eff = f.loc[valid].copy()
            eff["_Actual"] = actual.loc[valid]
            eff["_Scheduled"] = scheduled.loc[valid]

            if not eff.empty:
                avg_actual = eff["_Actual"].mean()
                avg_scheduled = eff["_Scheduled"].mean()

                k = st.columns(5)

                k[0].metric(
                    "Valid Duration Records",
                    f"{len(eff):,}",
                )

                k[1].metric(
                    "Average Actual Days",
                    f"{avg_actual:.2f}",
                )

                k[2].metric(
                    "Average Scheduled Days",
                    f"{avg_scheduled:.2f}",
                )

                k[3].metric(
                    "Average Variation",
                    f"{avg_actual - avg_scheduled:+.2f} days",
                    delta_color="inverse",
                )

                k[4].metric(
                    "On-Schedule Rate",
                    f"{(eff['_Actual'] <= eff['_Scheduled']).mean() * 100:.2f}%",
                )

                c1, c2 = st.columns(2)

                with c1:
                    sample = eff.sample(
                        n=min(2000, len(eff)),
                        random_state=42,
                    )

                    fig = px.scatter(
                        sample,
                        x="_Scheduled",
                        y="_Actual",
                        title="Actual vs Scheduled Shipping Days",
                        opacity=0.55,
                    )

                    max_days = max(
                        1,
                        float(eff["_Scheduled"].max()),
                        float(eff["_Actual"].max()),
                    )

                    fig.add_shape(
                        type="line",
                        x0=0,
                        y0=0,
                        x1=max_days,
                        y1=max_days,
                        line=dict(dash="dash"),
                    )

                    st.plotly_chart(
                        chart_layout(fig),
                        use_container_width=True,
                    )

                with c2:
                    if SHIPPING_MODE_COL:
                        fig = px.box(
                            eff,
                            x=SHIPPING_MODE_COL,
                            y="_Actual",
                            color=SHIPPING_MODE_COL,
                            points=False,
                            title="Actual Shipping Days by Mode",
                        )

                        fig.update_layout(showlegend=False)

                        st.plotly_chart(
                            chart_layout(fig),
                            use_container_width=True,
                        )
                    else:
                        unavailable("Shipping Mode column is unavailable.")

                if SHIPPING_MODE_COL:
                    mode_summary = (
                        eff.groupby(
                            SHIPPING_MODE_COL,
                            dropna=False,
                        )
                        .agg(
                            Records=("_Actual", "size"),
                            Average_Actual_Days=("_Actual", "mean"),
                            Average_Scheduled_Days=("_Scheduled", "mean"),
                        )
                        .round(2)
                        .reset_index()
                    )

                    st.dataframe(
                        mode_summary,
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.dataframe(
                        eff[["_Actual", "_Scheduled"]]
                        .describe()
                        .round(2),
                        use_container_width=True,
                    )

            else:
                unavailable(
                    "No valid non-negative actual and scheduled "
                    "shipping durations are available."
                )

        else:
            unavailable(
                "Actual or scheduled shipping-duration columns "
                "are unavailable."
            )

    # ========================================================
    # MODULE 5: FINANCIAL PERFORMANCE
    # ========================================================

    elif selected_page == "Financial Performance":
        st.subheader("Financial Performance Analysis")

        sales = f["_DASH_Sales"].dropna()
        profit = f["_DASH_Profit"].dropna()

        paired = f[
            ["_DASH_Sales", "_DASH_Profit"]
        ].dropna()

        k = st.columns(4)

        k[0].metric(
            "Total Sales",
            money(sales.sum()) if len(sales) else "N/A",
        )

        k[1].metric(
            "Total Recorded Profit",
            money(profit.sum()) if len(profit) else "N/A",
        )

        ratio = np.nan

        if (
            not paired.empty
            and paired["_DASH_Sales"].sum() != 0
        ):
            ratio = (
                paired["_DASH_Profit"].sum()
                / paired["_DASH_Sales"].sum()
                * 100
            )

        k[2].metric(
            "Recorded Profit-to-Sales Ratio",
            f"{ratio:.2f}%" if pd.notna(ratio) else "N/A",
        )

        k[3].metric(
            "Paired Sales & Profit Records",
            f"{len(paired):,}",
        )

        st.caption(
            "Profit-to-sales is a descriptive ratio of recorded "
            "fields, not necessarily an accounting profit margin."
        )

        c1, c2 = st.columns(2)

        with c1:
            if MARKET_COL:
                summary = (
                    f.groupby(MARKET_COL, dropna=False)
                    .agg(
                        Sales=("_DASH_Sales", "sum"),
                        Profit=("_DASH_Profit", "sum"),
                    )
                    .reset_index()
                )

                long = summary.melt(
                    id_vars=[MARKET_COL],
                    value_vars=["Sales", "Profit"],
                    var_name="Metric",
                    value_name="Amount",
                )

                fig = px.bar(
                    long,
                    x=MARKET_COL,
                    y="Amount",
                    color="Metric",
                    barmode="group",
                    title="Sales and Profit by Market",
                )

                st.plotly_chart(
                    chart_layout(fig),
                    use_container_width=True,
                )
            else:
                unavailable("Market column is unavailable.")

        with c2:
            if not paired.empty:
                sample = paired.sample(
                    n=min(3000, len(paired)),
                    random_state=42,
                )

                fig = px.scatter(
                    sample,
                    x="_DASH_Sales",
                    y="_DASH_Profit",
                    opacity=0.6,
                    title="Sales vs Recorded Profit",
                )

                st.plotly_chart(
                    chart_layout(fig),
                    use_container_width=True,
                )
            else:
                unavailable(
                    "Sales and profit are not jointly available."
                )

        if PRODUCT_COL:
            product_summary = (
                f.groupby(PRODUCT_COL, dropna=False)
                .agg(
                    Sales=("_DASH_Sales", "sum"),
                    Profit=("_DASH_Profit", "sum"),
                )
                .reset_index()
            )

            product_summary = product_summary.nlargest(15, "Sales")

            safe_bar(
                product_summary.sort_values("Sales"),
                PRODUCT_COL,
                "Sales",
                "Top 15 Products by Sales",
                horizontal=True,
                height=550,
            )
        else:
            unavailable("Product name column is unavailable.")

    # ========================================================
    # MODULE 6: REGIONAL ANALYSIS
    # ========================================================

    elif selected_page == "Regional Analysis":
        st.subheader("Regional Analysis")

        if REGION_COL:
            summary = (
                f.groupby(REGION_COL, dropna=False)
                .agg(
                    Shipments=(REGION_COL, "size"),
                    Delay_Rate=("_Actual_Delay_Flag", "mean"),
                    Average_Delay_Days=("_DASH_Delay_Days", "mean"),
                    Total_Sales=("_DASH_Sales", "sum"),
                    Total_Profit=("_DASH_Profit", "sum"),
                )
                .reset_index()
            )

            summary["Delay Rate (%)"] = (
                summary["Delay_Rate"] * 100
            )

            k = st.columns(3)

            k[0].metric(
                "Regions Represented",
                f"{summary[REGION_COL].nunique(dropna=True):,}",
            )

            k[1].metric("Total Shipments", f"{len(f):,}")

            known = f["_Actual_Delay_Flag"].dropna()

            k[2].metric(
                "Actual Delay Rate",
                f"{known.mean() * 100:.2f}%" if len(known) else "N/A",
            )

            c1, c2 = st.columns(2)

            with c1:
                safe_bar(
                    summary.sort_values("Shipments"),
                    REGION_COL,
                    "Shipments",
                    "Shipment Volume by Region",
                    horizontal=True,
                    height=500,
                )

            with c2:
                safe_bar(
                    summary.dropna(subset=["Delay Rate (%)"]).sort_values(
                        "Delay Rate (%)"
                    ),
                    REGION_COL,
                    "Delay Rate (%)",
                    "Actual Delay Rate by Region",
                    horizontal=True,
                    height=500,
                )

            st.dataframe(
                summary.round(2),
                use_container_width=True,
                hide_index=True,
            )

        else:
            unavailable("Order Region column is unavailable.")

        if STATE_COL:
            state_summary = (
                f.groupby(STATE_COL, dropna=False)
                .size()
                .reset_index(name="Shipments")
                .nlargest(15, "Shipments")
            )

            safe_bar(
                state_summary.sort_values("Shipments"),
                STATE_COL,
                "Shipments",
                "Top 15 States by Shipment Volume",
                horizontal=True,
                height=500,
            )

    # ========================================================
    # MODULE 7: MARKET ANALYSIS
    # ========================================================

    elif selected_page == "Market Analysis":
        st.subheader("Market Analysis")

        if MARKET_COL:
            summary = (
                f.groupby(MARKET_COL, dropna=False)
                .agg(
                    Shipments=(MARKET_COL, "size"),
                    Delay_Rate=("_Actual_Delay_Flag", "mean"),
                    Average_Delay=("_DASH_Delay_Days", "mean"),
                    Sales=("_DASH_Sales", "sum"),
                    Profit=("_DASH_Profit", "sum"),
                )
                .reset_index()
            )

            summary["Delay Rate (%)"] = (
                summary["Delay_Rate"] * 100
            )

            k = st.columns(3)

            k[0].metric(
                "Markets Represented",
                f"{summary[MARKET_COL].nunique(dropna=True):,}",
            )

            k[1].metric("Total Shipments", f"{len(f):,}")

            k[2].metric(
                "Total Sales",
                money(f["_DASH_Sales"].sum()),
            )

            c1, c2 = st.columns(2)

            with c1:
                fig = px.pie(
                    summary,
                    names=MARKET_COL,
                    values="Shipments",
                    hole=0.45,
                    title="Shipment Distribution by Market",
                )

                st.plotly_chart(
                    chart_layout(fig),
                    use_container_width=True,
                )

            with c2:
                safe_bar(
                    summary,
                    MARKET_COL,
                    "Delay Rate (%)",
                    "Actual Delay Rate by Market",
                )

            long = summary.melt(
                id_vars=[MARKET_COL],
                value_vars=["Sales", "Profit"],
                var_name="Metric",
                value_name="Amount",
            )

            fig = px.bar(
                long,
                x=MARKET_COL,
                y="Amount",
                color="Metric",
                barmode="group",
                title="Sales and Profit by Market",
            )

            st.plotly_chart(
                chart_layout(fig),
                use_container_width=True,
            )

            st.dataframe(
                summary.round(2),
                use_container_width=True,
                hide_index=True,
            )

        else:
            unavailable("Market column is unavailable.")

    # ========================================================
    # MODULE 8: COUNTRY ANALYSIS
    # ========================================================

    elif selected_page == "Country Analysis":
        st.subheader("Country-Level Operations Analysis")

        if COUNTRY_COL:
            summary = (
                f.groupby(COUNTRY_COL, dropna=False)
                .agg(
                    Shipments=(COUNTRY_COL, "size"),
                    Delay_Rate=("_Actual_Delay_Flag", "mean"),
                    Average_Delay=("_DASH_Delay_Days", "mean"),
                    Sales=("_DASH_Sales", "sum"),
                    Profit=("_DASH_Profit", "sum"),
                )
                .reset_index()
            )

            summary["Delay Rate (%)"] = (
                summary["Delay_Rate"] * 100
            )

            k = st.columns(3)

            k[0].metric(
                "Countries Represented",
                f"{summary[COUNTRY_COL].nunique(dropna=True):,}",
            )

            k[1].metric("Total Shipments", f"{len(f):,}")

            k[2].metric(
                "Total Sales",
                money(f["_DASH_Sales"].sum()),
            )

            top = summary.nlargest(15, "Shipments")

            c1, c2 = st.columns(2)

            with c1:
                safe_bar(
                    top.sort_values("Shipments"),
                    COUNTRY_COL,
                    "Shipments",
                    "Top 15 Countries by Shipment Volume",
                    horizontal=True,
                    height=550,
                )

            with c2:
                safe_bar(
                    top.dropna(subset=["Delay Rate (%)"]).sort_values(
                        "Delay Rate (%)"
                    ),
                    COUNTRY_COL,
                    "Delay Rate (%)",
                    "Actual Delay Rate — Top Countries",
                    horizontal=True,
                    height=550,
                )

            st.subheader("Country-Level Financial Performance")

            safe_bar(
                summary.nlargest(15, "Sales").sort_values("Sales"),
                COUNTRY_COL,
                "Sales",
                "Top Countries by Sales",
                horizontal=True,
                height=550,
            )

            st.dataframe(
                summary.sort_values(
                    "Shipments",
                    ascending=False,
                ).round(2),
                use_container_width=True,
                hide_index=True,
            )

        else:
            unavailable("Order Country column is unavailable.")

    # ========================================================
    # MODULE 9: CUSTOMER SEGMENTS
    # ========================================================

    elif selected_page == "Customer Segments":
        st.subheader("Customer Segment Analysis")

        if SEGMENT_COL:
            summary = (
                f.groupby(SEGMENT_COL, dropna=False)
                .agg(
                    Shipment_Records=(SEGMENT_COL, "size"),
                    Sales=("_DASH_Sales", "sum"),
                    Profit=("_DASH_Profit", "sum"),
                    Average_Quantity=("_DASH_Quantity", "mean"),
                )
                .reset_index()
            )

            if CUSTOMER_ID_COL:
                customers = (
                    f.groupby(SEGMENT_COL, dropna=False)[CUSTOMER_ID_COL]
                    .nunique()
                    .reset_index(name="Unique Customers")
                )

                summary = summary.merge(
                    customers,
                    on=SEGMENT_COL,
                    how="left",
                )

            k = st.columns(3)

            k[0].metric(
                "Segment Categories",
                f"{summary[SEGMENT_COL].nunique(dropna=True):,}",
            )

            k[1].metric("Shipment Records", f"{len(f):,}")

            k[2].metric(
                "Unique Customers",
                (
                    f"{f[CUSTOMER_ID_COL].nunique(dropna=True):,}"
                    if CUSTOMER_ID_COL
                    else "Unavailable"
                ),
            )

            c1, c2 = st.columns(2)

            with c1:
                fig = px.pie(
                    summary,
                    names=SEGMENT_COL,
                    values="Shipment_Records",
                    hole=0.45,
                    title="Shipment Distribution by Segment",
                )

                st.plotly_chart(
                    chart_layout(fig),
                    use_container_width=True,
                )

            with c2:
                safe_bar(
                    summary,
                    SEGMENT_COL,
                    "Sales",
                    "Sales by Customer Segment",
                )

            safe_bar(
                summary,
                SEGMENT_COL,
                "Profit",
                "Profit by Customer Segment",
            )

            st.dataframe(
                summary.round(2),
                use_container_width=True,
                hide_index=True,
            )

        else:
            unavailable(
                "No dedicated customer-segment column was detected "
                "in the dataset."
            )

    # ========================================================
    # MODULE 10: PRODUCT AND CATEGORY
    # ========================================================

    elif selected_page == "Product & Category":
        st.subheader("Product & Category Analysis")

        if CATEGORY_COL:
            summary = (
                f.groupby(CATEGORY_COL, dropna=False)
                .agg(
                    Shipments=(CATEGORY_COL, "size"),
                    Quantity=("_DASH_Quantity", "sum"),
                    Sales=("_DASH_Sales", "sum"),
                    Profit=("_DASH_Profit", "sum"),
                )
                .reset_index()
            )

            k = st.columns(3)

            k[0].metric(
                "Categories Represented",
                f"{summary[CATEGORY_COL].nunique(dropna=True):,}",
            )

            k[1].metric(
                "Total Quantity",
                f"{f['_DASH_Quantity'].sum(skipna=True):,.0f}",
            )

            k[2].metric(
                "Total Sales",
                money(f["_DASH_Sales"].sum()),
            )

            safe_bar(
                summary.nlargest(20, "Shipments").sort_values("Shipments"),
                CATEGORY_COL,
                "Shipments",
                "Top Categories by Shipment Volume",
                horizontal=True,
                height=600,
            )

            safe_bar(
                summary.nlargest(20, "Sales").sort_values("Sales"),
                CATEGORY_COL,
                "Sales",
                "Sales by Category",
                horizontal=True,
                height=600,
            )

            safe_bar(
                summary.nlargest(20, "Profit").sort_values("Profit"),
                CATEGORY_COL,
                "Profit",
                "Top Categories by Profit",
                horizontal=True,
                height=500,
            )

            st.dataframe(
                summary.round(2),
                use_container_width=True,
                hide_index=True,
            )

        else:
            unavailable("Category Name column is unavailable.")

        if PRODUCT_COL:
            product_summary = (
                f.groupby(PRODUCT_COL, dropna=False)
                .agg(
                    Shipments=(PRODUCT_COL, "size"),
                    Quantity=("_DASH_Quantity", "sum"),
                    Sales=("_DASH_Sales", "sum"),
                    Profit=("_DASH_Profit", "sum"),
                )
                .reset_index()
                .nlargest(20, "Sales")
            )

            safe_bar(
                product_summary.sort_values("Sales"),
                PRODUCT_COL,
                "Sales",
                "Top Products by Sales",
                horizontal=True,
                height=600,
            )

            st.dataframe(
                product_summary.round(2),
                use_container_width=True,
                hide_index=True,
            )

        else:
            unavailable("Product name column is unavailable.")

    # ========================================================
    # MODULE 11: RELATIONSHIP ANALYSIS
    # ========================================================

    elif selected_page == "Relationship Analysis":
        st.subheader("Multivariate Relationship Analysis")

        numeric_df = f[
            [
                "_DASH_Sales",
                "_DASH_Profit",
                "_DASH_Quantity",
                "_DASH_Actual_Days",
                "_DASH_Scheduled_Days",
                "_DASH_Delay_Days",
            ]
        ].copy()

        numeric_df.columns = [
            "Sales",
            "Recorded Profit",
            "Order Quantity",
            "Actual Shipping Days",
            "Scheduled Shipping Days",
            "Shipping Delay Days",
        ]

        usable = [
            column
            for column in numeric_df.columns
            if (
                numeric_df[column].notna().sum() >= 2
                and numeric_df[column].nunique(dropna=True) > 1
            )
        ]

        if len(usable) >= 2:
            corr = numeric_df[usable].corr(method="pearson")

            fig = px.imshow(
                corr,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1,
                title="Numerical Correlation Heatmap",
            )

            st.plotly_chart(
                chart_layout(fig, 600),
                use_container_width=True,
            )

            st.caption(
                "Pearson correlation measures linear association; "
                "correlation does not establish causation."
            )

            c1, c2 = st.columns(2)

            with c1:
                pair = numeric_df.dropna(
                    subset=["Sales", "Recorded Profit"]
                )

                if not pair.empty:
                    pair = pair.sample(
                        n=min(3000, len(pair)),
                        random_state=42,
                    )

                    fig = px.scatter(
                        pair,
                        x="Sales",
                        y="Recorded Profit",
                        opacity=0.6,
                        title="Sales vs Recorded Profit",
                    )

                    st.plotly_chart(
                        chart_layout(fig),
                        use_container_width=True,
                    )

                else:
                    unavailable(
                        "Sales and recorded profit are not jointly available."
                    )

            with c2:
                pair = numeric_df.dropna(
                    subset=[
                        "Actual Shipping Days",
                        "Shipping Delay Days",
                    ]
                )

                if not pair.empty:
                    pair = pair.sample(
                        n=min(3000, len(pair)),
                        random_state=42,
                    )

                    fig = px.scatter(
                        pair,
                        x="Actual Shipping Days",
                        y="Shipping Delay Days",
                        title="Actual Shipping Days vs Delay Days",
                    )

                    st.plotly_chart(
                        chart_layout(fig),
                        use_container_width=True,
                    )

                else:
                    unavailable(
                        "Shipping duration and delay fields are unavailable."
                    )

            st.subheader("Correlation Matrix")

            st.dataframe(
                corr.round(3),
                use_container_width=True,
            )

        else:
            unavailable(
                "At least two varying numerical metrics are required "
                "for correlation analysis."
            )


# ============================================================
# 9. DIAGNOSTICS AND FOOTER
# ============================================================

with st.expander("Dashboard Inventory", expanded=False):
    if not dashboard_inventory.empty:
        st.dataframe(
            dashboard_inventory,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("The dashboard inventory file was not found.")


with st.expander("Application Data Information", expanded=False):
    known_count = int(df["_Actual_Delay_Flag"].notna().sum())
    unknown_count = int(df["_Actual_Delay_Flag"].isna().sum())

    st.write(
        {
            "Project Root": str(PROJECT_ROOT),
            "Primary Dataset": str(DATA_FILE),
            "Dataset Exists": DATA_FILE.exists(),
            "Dataset Rows": len(data),
            "Dataset Columns": len(data.columns),
            "Filtered Rows": len(filtered_df),
            "Detected Order Date Column": ORDER_DATE_COL,
            "Detected Shipping Mode Column": SHIPPING_MODE_COL,
            "Detected Region Column": REGION_COL,
            "Detected Market Column": MARKET_COL,
            "Detected Customer Segment Column": SEGMENT_COL,
            "Filters Requiring Selection": empty_filters,
            "Records with Known Actual Outcome": known_count,
            "Records with Unknown Actual Outcome": unknown_count,
            "Master KPI File Exists": MASTER_KPI_FILE.exists(),
            "Master KPI Rows": len(master_kpis),
            "Dashboard Inventory Exists": DASHBOARD_INVENTORY_FILE.exists(),
            "Dashboard Inventory Rows": len(dashboard_inventory),
        }
    )

    st.caption(
        "Unknown actual outcomes are excluded from delay-rate "
        "denominators rather than counted as non-delayed."
    )


st.markdown(
    """
    <div class="dashboard-footer">
        APL Logistics Analytics Dashboard<br>
        Delivery Performance | Delay Risk | Logistics Efficiency<br>
        Developed as part of the Logistics Analytics Project
    </div>
    """,
    unsafe_allow_html=True,
)
