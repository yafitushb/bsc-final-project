import os
import sys
from logic import run_analysis

def main():

    # Define directories: where your *.log files should be
    input_folder = 'logs'
    # output: where the report & graphs will be saved
    output_folder = 'output'

    # Ensure output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output directory: {output_folder}")

    # Check if input directory exists
    if not os.path.exists(input_folder):
        print(f"Error: Input directory '{input_folder}' not found.")
        print("Please create a 'logs' folder and place your .log files inside.")
        return

    # Run the analysis
    print("--- Starting Auth Analysis Automation ---")
    try:
        run_analysis(input_folder, output_folder)
        print("--- Process Completed Successfully ---")
        print(f"Check the '{output_folder}' directory for your report.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()