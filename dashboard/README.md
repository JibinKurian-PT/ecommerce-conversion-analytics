# E-Commerce Conversion Analytics dashboard

Open `index.html` in a browser. No server or build step is needed.

## Updating the data
1. Replace the CSVs in `data/` (names `sql_current_project_Q1.csv` to `Q23.csv`, same columns).
2. Run `python3 tools/build_data.py`. This regenerates `js/data.js`.
3. Reload the page.

## Structure
- `js/data.js`   generated data layer (Q1 to Q23), never edited by hand
- `js/calc.js`   formatting, date filtering, joining Q10/Q11/Q12 by date
- `js/charts.js` interactive line chart (hover tooltips, resizes with its container)
- `js/app.js`    pages, tables, filters, routing. Each card shows the Q tag it is drawn from
- `css/styles.css`
