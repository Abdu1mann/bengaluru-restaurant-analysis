# Bengaluru Restaurant Market Analysis

**Goal:** Find which areas, cuisines and price ranges look most promising for a new restaurant in Bengaluru, and which are oversaturated.

![Dashboard](dashboard.png)

## Dataset
Zomato Bangalore Restaurants (Kaggle), about 51,700 rows, reduced to 12,480 unique restaurants.

## Tools
Python (pandas), SQL (SQLite), Power BI

## What I did
- Cleaned the data: converted ratings and costs to numbers, removed duplicates, handled missing values
- Built a one-row-per-restaurant table and a separate cuisine table
- Wrote SQL queries using joins, CTEs and window functions
- Built an interactive Power BI dashboard with slicers

## Key decisions
- Kept unrated ("NEW") restaurants and left their rating empty
- Checked the highest-cost rows: all are luxury hotel restaurants, so no outliers were removed
- Ignored cuisines with fewer than 100 restaurants when ranking ratings, so tiny samples don't skew results

## Findings
- Whitefield has the most restaurants, followed by Electronic City, BTM and HSR
- About half of all restaurants (6,032 of 12,480) are in the Rs 300-599 price band
- Among cuisines with 100+ restaurants, European (4.16) and Asian (4.09) are rated highest

## Files
- `bengaluru_restaurants.pbix`: Power BI dashboard
- `bengaluru_restaurants.ipynb`: cleaning and SQL analysis
- `restaurants_model.csv`, `restaurant_cuisines.csv`: cleaned data

## Next
Add a text-to-SQL AI agent on top of the data.
