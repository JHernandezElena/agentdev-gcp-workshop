#!/bin/bash

PROJECT_ID=$(gcloud config get-value project)

# Updated to the public source bucket
SOURCE_BUCKET="gs://sample-data-and-media/mcp_bakery_data"

echo "----------------------------------------------------------------"
echo "MCP Bakery Demo Setup"
echo "Project: $PROJECT_ID"
echo "Dataset: $BQ_DATASET_NAME"
echo "Source:  $SOURCE_BUCKET"
echo "----------------------------------------------------------------"

# 1. Create Dataset
echo "[1/6] Creating Dataset '$BQ_DATASET_NAME'..."
if bq show "$PROJECT_ID:$BQ_DATASET_NAME" >/dev/null 2>&1; then
    echo "      Dataset already exists. Skipping creation."
else    
    bq mk --location=$BQ_LOCATION --dataset \
        --description "$DATASET_DESCRIPTION" \
        "$PROJECT_ID:$BQ_DATASET_NAME"
    echo "      Dataset created."
fi

# 2. Create Demographics Table
echo "[2/6] Setting up Table: demographics..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$BQ_DATASET_NAME.demographics\` (
    zip_code STRING OPTIONS(description='5-digit US Zip Code'),
    city STRING OPTIONS(description='City name, e.g., Los Angeles'),
    neighborhood STRING OPTIONS(description='Common neighborhood name, e.g., Santa Monica, Silver Lake'),
    total_population INT64 OPTIONS(description='Total population count in the zip code'),
    median_age FLOAT64 OPTIONS(description='Median age of residents'),
    bachelors_degree_pct FLOAT64 OPTIONS(description='Percentage of population 25+ with a Bachelors degree or higher'),
    foot_traffic_index FLOAT64 OPTIONS(description='Index of estimated foot traffic based on commercial density and mobility data')
)
OPTIONS(
    description='Census data by zip code for various California cities.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --ignore_unknown_values=true --replace \
    "$PROJECT_ID:$BQ_DATASET_NAME.demographics" "$SOURCE_BUCKET/demographics.csv"

# 3. Create Bakery Prices Table
echo "[3/6] Setting up Table: bakery_prices..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$BQ_DATASET_NAME.bakery_prices\` (
    store_name STRING OPTIONS(description='Name of the competitor bakery'),
    product_type STRING OPTIONS(description='Type of baked good, e.g., Sourdough Loaf, Croissant'),
    price FLOAT64 OPTIONS(description='Price per unit in USD'),
    region STRING OPTIONS(description='Geographic region, e.g., Los Angeles Metro, SF Bay Area'),
    is_organic BOOL OPTIONS(description='Whether the product is certified organic')
)
OPTIONS(
    description='Competitor pricing and product details for common baked goods.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --replace \
    "$PROJECT_ID:$BQ_DATASET_NAME.bakery_prices" "$SOURCE_BUCKET/bakery_prices.csv"

# 4. Create Sales History Table
echo "[4/6] Setting up Table: sales_history_weekly..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$BQ_DATASET_NAME.sales_history_weekly\` (
    week_start_date DATE OPTIONS(description='The start date of the sales week (Monday)'),
    store_location STRING OPTIONS(description='Location of the bakery branch'),
    product_type STRING OPTIONS(description='Product category: Sourdough Loaf, Croissant, etc.'),
    quantity_sold INT64 OPTIONS(description='Total units sold this week'),
    total_revenue FLOAT64 OPTIONS(description='Total revenue in USD for this week')
)
OPTIONS(
    description='Weekly sales performance history by store and product.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --replace \
    "$PROJECT_ID:$BQ_DATASET_NAME.sales_history_weekly" "$SOURCE_BUCKET/sales_history_weekly.csv"

# 5. Create Foot Traffic Table
echo "[5/6] Setting up Table: foot_traffic..."
bq query --use_legacy_sql=false \
"CREATE OR REPLACE TABLE \`$PROJECT_ID.$BQ_DATASET_NAME.foot_traffic\` (
    zip_code STRING OPTIONS(description='5-digit US Zip Code'),
    time_of_day STRING OPTIONS(description='Time of day: morning, afternoon, evening'),
    foot_traffic_score FLOAT64 OPTIONS(description='Score of foot traffic (1-100)')
)
OPTIONS(
    description='Foot traffic scores by zip code and time of day.'
);"

bq load --source_format=CSV --skip_leading_rows=1 --replace \
    "$PROJECT_ID:$BQ_DATASET_NAME.foot_traffic" "$SOURCE_BUCKET/foot_traffic.csv"

echo "----------------------------------------------------------------"
echo "Setup Complete!"
echo "----------------------------------------------------------------"