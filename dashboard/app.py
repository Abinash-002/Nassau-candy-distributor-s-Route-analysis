"""
Main Streamlit Dashboard - Nassau Candy Distributor Route Analysis
Interactive web application for logistics analytics and optimization
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from utils import (
    load_dataframe, OUTPUT_DIR, get_geojson_url, format_currency,
    format_percentage, logger
)

# Page configuration
st.set_page_config(
    page_title="Nassau Candy Route Analysis",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_all_data():
    """Load all processed data files"""
    try:
        data = {
            'route_metrics': load_dataframe("route_metrics.csv", data_type='output'),
            'regional_metrics': load_dataframe("regional_metrics.csv", data_type='output'),
            'shipmode_metrics': load_dataframe("shipmode_metrics.csv", data_type='output'),
            'state_performance': load_dataframe("state_performance.csv", data_type='output'),
            'bottlenecks': load_dataframe("bottleneck_analysis.csv", data_type='output'),
            'factory_matrix': load_dataframe("factory_route_matrix.csv", data_type='output'),
            'top_routes': load_dataframe("top_10_routes.csv", data_type='output'),
            'bottom_routes': load_dataframe("bottom_10_routes.csv", data_type='output'),
        }
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def display_kpi_cards(route_metrics, regional_metrics, shipmode_metrics):
    """Display KPI metric cards"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_lead_time = route_metrics['Avg_Lead_Time'].mean()
        st.metric(
            "Avg Lead Time",
            f"{avg_lead_time:.1f} days",
            delta=None,
            delta_color="inverse"
        )

    with col2:
        total_routes = len(route_metrics)
        st.metric("Total Routes", f"{total_routes}", delta=None)

    with col3:
        excellent_routes = (route_metrics['Efficiency_Class'] == 'Excellent').sum()
        excellent_pct = (excellent_routes / len(route_metrics) * 100)
        st.metric("Excellent Routes", f"{excellent_pct:.1f}%", delta=None)

    with col4:
        regions = len(regional_metrics)
        st.metric("Active Regions", f"{regions}", delta=None)


def page_overview():
    """Route Efficiency Overview page"""
    st.header("📊 Route Efficiency Overview")

    data = load_all_data()
    if data is None:
        st.error("Unable to load data")
        return

    # KPI Cards
    display_kpi_cards(data['route_metrics'], data['regional_metrics'], data['shipmode_metrics'])

    st.divider()

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        efficiency_filter = st.selectbox(
            "Filter by Efficiency",
            ["All", "Excellent", "Good", "Poor"]
        )
    with col2:
        volume_filter = st.selectbox(
            "Filter by Volume",
            ["All", "Low", "Medium", "High"]
        )

    # Apply filters
    filtered_routes = data['route_metrics'].copy()
    if efficiency_filter != "All":
        filtered_routes = filtered_routes[filtered_routes['Efficiency_Class'] == efficiency_filter]
    if volume_filter != "All":
        filtered_routes = filtered_routes[filtered_routes['Volume_Class'] == volume_filter]

    # Route Leaderboard
    st.subheader("🏆 Route Performance Leaderboard")
    display_cols = ['Route_ID', 'Total_Shipments', 'Avg_Lead_Time', 'On_Time_Rate', 'Efficiency_Score', 'Efficiency_Class']
    st.dataframe(
        filtered_routes[display_cols].head(20),
        use_container_width=True,
        hide_index=True
    )

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Efficiency Score Distribution
        fig = px.histogram(
            data['route_metrics'],
            x='Efficiency_Score',
            nbins=20,
            title="Distribution of Route Efficiency Scores",
            labels={'Efficiency_Score': 'Efficiency Score', 'count': 'Number of Routes'},
            color_discrete_sequence=['#636EFA']
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Efficiency Class Breakdown
        efficiency_counts = data['route_metrics']['Efficiency_Class'].value_counts()
        fig = px.pie(
            values=efficiency_counts.values,
            names=efficiency_counts.index,
            title="Routes by Efficiency Class",
            color_discrete_sequence=['#00CC96', '#AB63FA', '#FFA15A']
        )
        st.plotly_chart(fig, use_container_width=True)

    # Lead Time vs Shipment Volume
    st.subheader("Lead Time vs Shipment Volume")
    fig = px.scatter(
        data['route_metrics'],
        x='Total_Shipments',
        y='Avg_Lead_Time',
        size='Total_Sales',
        color='Efficiency_Score',
        hover_data=['Route_ID', 'On_Time_Rate'],
        title="Route Scatter: Volume vs Lead Time (Size = Sales)",
        labels={'Total_Shipments': 'Total Shipments', 'Avg_Lead_Time': 'Average Lead Time (days)'},
        color_continuous_scale='RdYlGn_r'
    )
    st.plotly_chart(fig, use_container_width=True)


def page_geographic():
    """Geographic Analysis page"""
    st.header("🗺️ Geographic Shipping Analysis")

    data = load_all_data()
    if data is None:
        st.error("Unable to load data")
        return

    # Regional Performance
    st.subheader("Regional Performance Metrics")
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            data['regional_metrics'],
            x='Region_Mapped',
            y='Avg_Lead_Time',
            color='Efficiency_Score',
            title="Average Lead Time by Region",
            labels={'Region_Mapped': 'Region', 'Avg_Lead_Time': 'Avg Lead Time (days)'},
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            data['regional_metrics'],
            x='Region_Mapped',
            y='Delay_Rate',
            color='Delay_Rate',
            title="Delay Rate by Region",
            labels={'Region_Mapped': 'Region', 'Delay_Rate': 'Delay Rate (%)'},
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # State Performance Heatmap
    st.subheader("State-Level Performance Heatmap")
    fig = px.choropleth(
        data['state_performance'],
        locations='State_Code',
        locationmode='USA-states',
        color='Efficiency_Score',
        hover_name='State_Code',
        hover_data={'Avg_Lead_Time': ':.1f', 'Total_Shipments': ':,'},
        color_continuous_scale='RdYlGn_r',
        scope='usa',
        title="Shipping Efficiency Across US States"
    )
    fig.update_layout(
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(243, 243, 243)'
        ),
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Bottleneck Analysis
    st.subheader("🚨 Geographic Bottlenecks")
    bottleneck_display = data['bottlenecks'][['State/Province', 'Shipment_Volume', 'Avg_Lead_Time', 'Delay_Rate', 'Bottleneck_Level']].head(15)
    st.dataframe(bottleneck_display, use_container_width=True, hide_index=True)


def page_shipmode():
    """Ship Mode Comparison page"""
    st.header("📦 Ship Mode Performance Comparison")

    data = load_all_data()
    if data is None:
        st.error("Unable to load data")
        return

    # Ship Mode Metrics Table
    st.subheader("Ship Mode Metrics")
    st.dataframe(data['shipmode_metrics'], use_container_width=True, hide_index=True)

    st.divider()

    # Comparisons
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            data['shipmode_metrics'],
            x='Ship Mode',
            y='Avg_Lead_Time',
            title="Average Lead Time by Ship Mode",
            color='Avg_Lead_Time',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            data['shipmode_metrics'],
            x='Ship Mode',
            y='Delay_Rate',
            title="Delay Rate by Ship Mode",
            color='Delay_Rate',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Cost vs Speed Analysis
    st.subheader("Cost-Speed Tradeoff Analysis")
    fig = px.scatter(
        data['shipmode_metrics'],
        x='Avg_Lead_Time',
        y='Avg_Sales_Per_Shipment',
        size='Total_Shipments',
        text='Ship Mode',
        title="Ship Mode: Speed vs Average Order Value",
        labels={'Avg_Lead_Time': 'Avg Lead Time (days)', 'Avg_Sales_Per_Shipment': 'Avg Sales per Shipment ($)'}
    )
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)


def page_drill_down():
    """Drill-Down Analysis page"""
    st.header("🔍 Detailed Drill-Down Analysis")

    data = load_all_data()
    if data is None:
        st.error("Unable to load data")
        return

    # Top and Bottom Routes
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🥇 Top 10 Most Efficient Routes")
        top_display = data['top_routes'][['Route_ID', 'Total_Shipments', 'Avg_Lead_Time', 'Efficiency_Score']].head(10)
        st.dataframe(top_display, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("🔴 Bottom 10 Least Efficient Routes")
        bottom_display = data['bottom_routes'][['Route_ID', 'Total_Shipments', 'Avg_Lead_Time', 'Efficiency_Score']].tail(10)
        st.dataframe(bottom_display, use_container_width=True, hide_index=True)

    st.divider()

    # Factory Performance
    st.subheader("🏭 Factory Performance Comparison")
    try:
        factory_perf = load_dataframe("factory_performance.csv", data_type='output')
        st.dataframe(factory_perf, use_container_width=True, hide_index=True)

        # Factory comparison charts
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                factory_perf,
                x='Origin_Factory',
                y='Avg_Lead_Time',
                title="Average Lead Time by Factory",
                color='Avg_Lead_Time',
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                factory_perf,
                x='Origin_Factory',
                y='Delay_Rate',
                title="Delay Rate by Factory",
                color='Delay_Rate',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning(f"Factory performance data not available: {e}")

    st.divider()

    # Critical Bottlenecks
    st.subheader("🚨 Critical Bottlenecks")
    if len(data['bottlenecks']) > 0:
        critical = data['bottlenecks'][data['bottlenecks']['Bottleneck_Level'] == 'Critical']
        if len(critical) > 0:
            st.dataframe(critical.head(10), use_container_width=True, hide_index=True)
        else:
            st.info("No critical bottlenecks identified")
    else:
        st.info("Bottleneck analysis not available")


def page_insights():
    """Insights and Recommendations page"""
    st.header("💡 Insights & Recommendations")

    try:
        with open(OUTPUT_DIR / "executive_summary.txt", 'r') as f:
            summary = f.read()
        st.text(summary)
    except FileNotFoundError:
        st.info("Executive summary not available. Please run the analysis pipeline first.")


def main():
    """Main application"""
    # Sidebar navigation
    st.sidebar.title("🍬 Nassau Candy Distributor")
    st.sidebar.markdown("Route Analysis & Optimization")

    page = st.sidebar.radio(
        "Select Page",
        ["Overview", "Geographic Analysis", "Ship Mode Comparison", "Drill-Down", "Insights"]
    )

    st.sidebar.divider()

    # Help section
    st.sidebar.markdown("### 📖 Help")
    st.sidebar.markdown("""
    - **Overview**: View route efficiency metrics and performance
    - **Geographic**: Analyze regional and state-level performance
    - **Ship Mode**: Compare shipping methods performance
    - **Drill-Down**: Detailed analysis of top/bottom routes
    - **Insights**: Executive summary and recommendations
    """)

    # Route to correct page
    if page == "Overview":
        page_overview()
    elif page == "Geographic Analysis":
        page_geographic()
    elif page == "Ship Mode Comparison":
        page_shipmode()
    elif page == "Drill-Down":
        page_drill_down()
    elif page == "Insights":
        page_insights()

    # Footer
    st.sidebar.divider()
    st.sidebar.markdown("---")
    st.sidebar.markdown("*Last updated: June 2026*")
    st.sidebar.markdown("*Powered by Streamlit & Plotly*")


if __name__ == "__main__":
    main()
