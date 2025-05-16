import os
import sys
import webbrowser

def open_dashboard():
    """Open the dashboard in the default browser."""
    dashboard_path = os.path.join('dashboard', 'index.html')
    
    if not os.path.exists(dashboard_path):
        print(f"Dashboard not found at {dashboard_path}")
        return False
    
    try:
        # Get absolute path
        abs_path = os.path.abspath(dashboard_path)
        print(f"Opening dashboard at: {abs_path}")
        
        # Use a single method to open the browser
        webbrowser.open(f'file:///{abs_path}')
        return True
    except Exception as e:
        print(f"Error opening dashboard: {str(e)}")
        return False

if __name__ == "__main__":
    # First, copy any files from figures directory to dashboard/assets if needed
    try:
        import shutil
        
        # Ensure the assets directory exists
        os.makedirs(os.path.join('dashboard', 'assets'), exist_ok=True)
        
        # Copy key visualization files
        if os.path.exists('figures/keyword_price_correlation.png'):
            shutil.copy('figures/keyword_price_correlation.png', 'dashboard/assets/')
        
        # Removed reference to trends overview visualization
            
        # Copy individual keyword visualizations
        if os.path.exists('data/keyword_trends.csv'):
            import pandas as pd
            import re
            
            trends_df = pd.read_csv('data/keyword_trends.csv')
            top_keywords = trends_df.nlargest(5, 'frequency')['keyword'].tolist()
            
            for keyword in top_keywords:
                # Sanitize the keyword for filename
                safe_name = re.sub(r'[<>:"\\|?*]', '_', keyword).strip('. ').replace(' ', '_')
                
                if os.path.exists(f'figures/{safe_name}_vs_price.png'):
                    shutil.copy(f'figures/{safe_name}_vs_price.png', 'dashboard/assets/')
        
        print("Successfully copied visualization files to dashboard assets.")
    except Exception as e:
        print(f"Warning: Could not copy visualization files: {str(e)}")
    
    # Open the dashboard
    open_dashboard() 