#!/ibpc/telesto/hardiagon/anaconda3/bin/python

import matplotlib.pyplot as plt
import pandas as pd
import argparse
from argparse import RawTextHelpFormatter
import os
import sys

def list2str(l):
    """
    Transform list to string with whitespace.
    """
    return ' '.join(map(str, l))

def load_data(csv_file, time_offset):
    """
    Load data from the CSV file and filter based on the time offset.
    """
    try:
        data = pd.read_csv(csv_file, sep='\s+', header=0, skipinitialspace=True)
        filtered_data = data[data["time(ns)"] > time_offset]
        return filtered_data
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' does not exist.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{csv_file}' is empty or not a valid CSV file.")
        sys.exit(1)

def process_data(data):
    """
    Process the data by sorting and adding cumulative permeation counts.
    """
    sorted_data = data.sort_values(by='time(ns)')
    sorted_data['permeations_tot'] = [i + 1 for i in range(len(sorted_data))]
    return sorted_data

def generate_plot(data, flag, time_offset, dirname):
    """
    Generate and save the plot in PNG and PDF formats.
    """
    plt.figure()
    plt.step(data['time(ns)'], data['permeations_tot'], '-', where='post')
    plt.title(f'Cumulated Total number of Permeations \n in {flag}', fontsize=18)
    plt.xlabel('time(ns)', fontsize=16)
    plt.ylabel('# permeations', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.xlim(time_offset,)
    plt.ylim(0,)
    
    png_path = f'{dirname}/permeation_cumul_{flag}.png'
    pdf_path = f'{dirname}/permeation_cumul_{flag}.pdf'
    print(f'Saving plot as PNG: {png_path}')
    plt.savefig(png_path)
    print(f'Saving plot as PDF: {pdf_path}')
    plt.savefig(pdf_path)

def save_xvg(data, flag, dirname):
    """
    Save the processed data in XVG format.
    """
    xvg_path = f"{dirname}/permeation_cumul_{flag}.xvg"
    with open(xvg_path, "w") as fxvg:
        for t, perm in zip(data['time(ns)'], data['permeations_tot']):
            fxvg.write(f"{t:6.2f} {perm:6.2f}\n")
    print(f'Saving XVG data: {xvg_path}')

def save_sel(data, flag, dirname):
    """
    Save the selection of water molecules that have permeated in SEL format.
    """
    sel_path = f"{dirname}/permeation_selec_{flag}.sel"
    with open(sel_path, "w") as fsel:
        sel = f"resname SOL TIP3 and resid {list2str(data['resid'].tolist())}"
        fsel.write(sel)
    print(f'Saving SEL file: {sel_path}')

def handle_args():
    """
    Handle command-line arguments and return parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description='''
Analyze data from a CSV file generated by the perm_lip.py program.

This script processes simulation data to generate visualizations and data files that help analyze permeation events.

Outputs:
    - PNG file: A plot of cumulated total permeation events over time.
    - PDF file: A PDF version of the same plot.
    - XVG file: Data in XVG format containing time and cumulative permeations.
    - SEL file: Selection file for visualizing the permeated water molecules in VMD.

Examples:
    1. Basic usage without time offset:
       python plot_perm_tot.py data.csv <simulation_flag>

    2. Usage with a time offset:
       python plot_perm_tot.py data.csv <simulation_flag> --time_offset 10.0

This will generate the same output files as above but will filter the data to only include permeations occurring after 10 nanoseconds.
The script generates visualizations and data files to analyze and present the simulation results.''',
    formatter_class=RawTextHelpFormatter
    )
    parser.add_argument('csv_file', type=str, help='Path to the CSV file containing the simulation data.')
    parser.add_argument('flag', type=str, help='Identifier for the output files.')
    parser.add_argument('-t','--time-offset', type=float, default=0, help='Time offset (in nanoseconds) to filter the data for water molecule selection. Default is 0.')
    parser.add_argument('-o','--output-dir', type=str, default="", help='Output directory.')
    args = parser.parse_args()

    # Validate the inputs
    if not os.path.isfile(args.csv_file):
        print(f"Error: The file '{args.csv_file}' does not exist.")
        parser.print_help()
        sys.exit(1)

    if not args.flag:
        print("Error: The 'flag' argument is required.")
        parser.print_help()
        sys.exit(1)

    return args

def main():
    args = handle_args()
    dirname = args.output_dir
    if dirname == "":
        dirname = "."

    # Load and process data
    data = load_data(args.csv_file, args.time_offset)
    processed_data = process_data(data)

    # Generate and save outputs
    generate_plot(processed_data, args.flag, args.time_offset, dirname)
    save_xvg(processed_data, args.flag, dirname)
    save_sel(processed_data, args.flag, dirname)

if __name__ == "__main__":
    main()
