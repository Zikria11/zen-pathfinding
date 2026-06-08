#!/bin/bash
echo "Regenerating street maps..."
# Increase workers to max to speed this up
sed -i 's/workers = max(1, mp.cpu_count() - 2)/workers = mp.cpu_count()/g' run_street_maps.py
python3 run_street_maps.py

echo "Aggregating and plotting..."
python3 aggregate_and_plot.py
python3 plot_custom_pdfs.py

echo "Organizing street maps..."
mkdir -p street_data
mv csv_files street_data/csv_files
mv plots street_data/plots
mv results.csv street_data/street_results.csv
echo "Restore complete!"
