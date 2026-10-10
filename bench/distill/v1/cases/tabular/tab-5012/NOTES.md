## Traps
- TR-MULTISRC: the dispatched quantities sit in order_lines_2026-08.csv and the prices in product_costs.csv.
  Reading the line log alone leaves quantities rather than a value; the Bellhaven units on their own are 4894.
- TR-DUPROW: four lines were written twice by the export, so adding up every line gives 153105.38.

## Reference solution
1. List the workspace: the August line log and the product cost list.
2. Read product_costs.csv and note the unit cost of each product code.
3. Read order_lines_2026-08.csv, keep the Bellhaven lines and one line per line_id, and match each product code
   to its unit cost.
4. Multiply units by unit cost on each line and add: 129529.08.

## Why the answer is unique
Every dispatched value needs both files: the line log holds units and warehouse, while the cost list holds the only
price for each product code, so neither file alone yields the figure. The reprinted lines repeat their line_id and
every other field, so they are one dispatch each. With the warehouse scope fixed and the two sources joined on
product code, the total is 129529.08.
