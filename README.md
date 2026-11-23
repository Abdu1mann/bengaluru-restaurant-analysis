# Bengaluru Restaurant Market Analysis

**Goal:** Find which areas, cuisines and price ranges look most promising for a new restaurant in Bengaluru, and which are oversaturated.

## Dataset
Zomato Bangalore Restaurants (Kaggle), about 51,700 rows.

## Progress
- [x] Data cleaning (Python, pandas)
- [ ] SQL analysis
- [ ] Dashboard
- [ ] Insights and recommendations
- [ ] AI text-to-SQL agent

## Key decisions
- Removed exact duplicate rows, then built a one-row-per-restaurant table (same name and address).
- Kept unrated ("NEW") restaurants and left their rating empty.
- Checked the highest-cost rows: all are luxury hotel restaurants, so no outliers were removed.
