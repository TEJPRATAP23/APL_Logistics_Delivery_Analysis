# Delivery Performance, Delay Risk, and Logistics Efficiency Analysis in Global Supply Chain Operations

## Project Overview

This project analyzes logistics and supply chain shipment records to evaluate delivery performance, delivery delays, shipping efficiency, profitability, regional variation, customer segments, and product/category performance.

The project uses data analysis, feature engineering, KPI development, interactive visualizations, and a Streamlit dashboard to support operational insights and logistics decision-making.

## Objectives

- Analyze actual versus scheduled shipping duration.
- Evaluate delivery delays and delay-risk patterns.
- Compare shipping modes and delivery performance.
- Examine regional, market, and country-level performance.
- Investigate financial performance and recorded profitability.
- Analyze customer segments and product/category patterns.
- Build an interactive dashboard for exploring logistics KPIs.
- Document the analytical workflow and findings.

## Technology Stack

- Python
- pandas
- NumPy
- Plotly
- Streamlit
- Jupyter Notebook
- Git and GitHub

## Dashboard Modules

1. Executive Overview
2. Delivery Performance
3. Shipping Efficiency
4. Financial Performance
5. Regional Analysis
6. Market Analysis
7. Country Analysis
8. Customer Segments
9. Product and Category Analysis
10. Relationship Analysis

## Project Structure

    .
    ├── app/
    │   └── app.py
    ├── data/
    │   ├── raw/
    │   ├── cleaned/
    │   ├── feature_data/
    │   └── analysis_data/
    ├── notebooks/
    ├── reports/
    ├── requirements.txt
    ├── .gitignore
    └── README.md

## Dataset

The project uses shipment-level logistics data containing shipping durations, delivery status, shipping modes, geographical information, customer segments, products, sales, and profitability.

The original dataset is maintained separately from cleaned and feature-engineered data and should not be overwritten.

## Key Analytical Areas

### 1. Delivery Performance
- Compare actual and scheduled shipping durations.
- Analyze delivery status and shipment delays.
- Examine delayed and non-delayed shipments.

### 2. Shipping Efficiency
- Compare shipping modes.
- Evaluate actual versus scheduled shipping durations.
- Identify potential shipping efficiency issues.

### 3. Financial Performance
- Analyze sales and recorded profitability.
- Investigate financial patterns across delay categories.
- Examine relationships between delivery delays and financial outcomes.

### 4. Regional and Market Analysis
- Compare shipment performance across regions and markets.
- Analyze country-level delivery patterns.
- Identify potential geographical bottlenecks.

### 5. Customer and Product Analysis
- Analyze customer segments.
- Examine product and category performance.
- Explore relationships between shipment characteristics, sales, and profitability.

## Dashboard Features

- Interactive KPI cards.
- Delivery performance visualizations.
- Shipping efficiency comparisons.
- Financial performance charts.
- Regional, market, and country analysis.
- Customer segment comparisons.
- Product and category analysis.
- Relationship analysis.
- Interactive dashboard navigation.

## Installation and Setup

### 1. Create a Virtual Environment

    python -m venv .venv

### 2. Activate the Virtual Environment

    .\.venv\Scripts\Activate.ps1

### 3. Install Dependencies

    python -m pip install --upgrade pip
    pip install -r requirements.txt

### 4. Run the Streamlit Dashboard

    python -m streamlit run app/app.py

Open the local URL displayed in the terminal to access the dashboard.

## Data Management

- Keep the original dataset unchanged.
- Store feature-engineered data in `data/feature_data/`.
- Store analytical outputs in `data/analysis_data/`.
- Maintain dashboard code in `app/app.py`.
- Maintain dependencies in `requirements.txt`.
- Do not commit credentials or sensitive information to GitHub.

## Limitations

- Analysis depends on the quality and availability of the source data.
- Historical patterns do not guarantee future logistics performance.
- Relationships between delivery delays and profitability do not necessarily establish causation.
- Findings should be validated before operational or financial decisions are made.

## Expected Outcomes

- Structured analysis of shipment and delivery performance.
- Identification of delay patterns and potential operational bottlenecks.
- Comparisons of shipping efficiency across shipment groups.
- Insights into regional, customer, product, and financial performance.
- An interactive Streamlit dashboard.
- Documentation suitable for technical review and project presentation.

## Author

TEJ PRATAP

## Project Status

The project covers data preparation, exploratory analysis, feature engineering, KPI development, and Streamlit dashboard development.

Refer to the latest project files and testing results for the final implementation status.
