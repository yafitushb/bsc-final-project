import os
import glob
from datetime import datetime

def generate_full_report(output_folder):
    """
    Generates an HTML report by aggregating all PNG graphs found in the
    output/graphs directory.
    
    Args:
        output_folder (str): The path to the main output directory.
    """
    print(f"[*] Generating HTML report in: {output_folder}")
    
    # Define the graphs directory path
    graphs_dir = os.path.join(output_folder, "graphs")
    
    # Find all PNG files in the graphs directory
    graph_files = glob.glob(os.path.join(graphs_dir, "*.png"))
    
    if not graph_files:
        print("[!] No graphs found to include in the report.")
        return

    # Start building the HTML content with embedded CSS
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Security Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }}
            h1 {{ color: #333; text-align: center; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            .graph-container {{ margin-bottom: 40px; text-align: center; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
            img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; padding: 5px; }}
            .timestamp {{ text-align: center; color: #888; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Authentication Security Analysis</h1>
            <p class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
    """

    # Iterate through sorted graph files and add them to the report
    for graph_path in sorted(graph_files):
        filename = os.path.basename(graph_path)
        # Create a relative path for the HTML src attribute
        relative_path = f"graphs/{filename}"
        
        # Format the filename to create a readable title 
        display_name = filename.replace(".png", "").replace("_", " ").title()
        
        html_content += f"""
            <div class="graph-container">
                <h2>{display_name}</h2>
                <img src="{relative_path}" alt="{display_name}">
            </div>
        """

    # Close HTML tags
    html_content += """
        </div>
    </body>
    </html>
    """

    # Save the HTML file to the output directory
    report_path = os.path.join(output_folder, "analysis_report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"[+] Report generated successfully: {report_path}")