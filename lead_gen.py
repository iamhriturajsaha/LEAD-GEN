import requests
import pandas as pd
import schedule
import time
import urllib.parse
import re

def fetch_lead_data():
    """Fetches lead data from the local Dataset.csv."""
    print("Fetching data from Dataset.csv...")
    try:
        # Load the dataset
        df = pd.read_csv('Dataset.csv')
        
        # Filter for operating companies
        if 'status' in df.columns:
            df = df[df['status'] == 'operating']
        
        # Take a random sample of 100 rows
        if len(df) > 100:
            df = df.sample(n=100)
            
        leads = []
        for _, row in df.iterrows():
            name = str(row.get('name', 'Unknown'))
            website = str(row.get('homepage_url', ''))
            if website == 'nan': website = ''
            
            category = str(row.get('category_list', 'Unknown'))
            if category == 'nan': category = 'Unknown'
            # Clean up category (it has pipes like A|B|C)
            category = category.split('|')[0] if category else 'Unknown'
            
            funding = str(row.get('funding_total_usd', '0'))
            if funding == 'nan' or funding == '-': funding = '0'
            
            city = str(row.get('city', 'Unknown'))
            if city == 'nan': city = 'Unknown'
            
            country = str(row.get('country_code', ''))
            if country == 'nan': country = ''
            
            location = f"{city}, {country}".strip(", ")
            
            leads.append({
                'Company Name': name,
                'Contact Name': None, # To be added from API
                'Email': None, # To be generated in clean_data
                'Category': category,
                'Funding (USD)': funding,
                'Location': location,
                'Website': website
            })
            
        # API Integration: Fetch dummy users for Contact Names
        try:
            print("Fetching contact names from DummyJSON API...")
            api_res = requests.get('https://dummyjson.com/users?limit=100', timeout=10)
            api_users = api_res.json().get('users', [])
        except Exception as api_e:
            print(f"Error fetching API data: {api_e}")
            api_users = []
            
        for i, lead in enumerate(leads):
            if i < len(api_users):
                user = api_users[i]
                first = user.get('firstName', '')
                last = user.get('lastName', '')
                lead['Contact Name'] = f"{first} {last}".strip()
            else:
                lead['Contact Name'] = "Unknown Contact"
                
        return leads
    except Exception as e:
        print(f"Error reading dataset: {e}")
        return []

def extract_domain(url):
    if pd.isna(url) or str(url) == 'nan' or not str(url).strip():
        return None
    url_str = str(url).strip()
    try:
        if not url_str.startswith('http'):
            url_str = 'http://' + url_str
        parsed = urllib.parse.urlparse(url_str)
        domain = parsed.netloc
        # Remove www.
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return None

def clean_data(df):
    """Cleans the dataset by handling duplicates and missing values, and generating emails."""
    print("Cleaning data...")
    initial_count = len(df)
    
    # 1. Remove exact duplicate rows
    df = df.drop_duplicates()

    # 2. Remove duplicates based on Company Name (keep the first occurrence)
    df = df.drop_duplicates(subset=['Company Name'], keep='first')
    
    # 3. Handle missing values
    # Drop rows that don't have a valid Company Name (essential for leads)
    df = df[df['Company Name'].str.strip() != '']
    df = df[df['Company Name'].str.lower() != 'unknown']
    df = df[df['Company Name'].str.lower() != 'nan']

    # Drop rows missing Website or Funding info
    df = df[df['Website'].str.strip() != '']
    df = df[df['Website'].str.lower() != 'nan']
    df = df[df['Funding (USD)'] != '0']

    # Standardize missing/empty values in other columns
    df = df.fillna('')
    df = df.replace('nan', '')
    
    # Make placeholders more professional
    df.loc[df['Category'] == 'Unknown', 'Category'] = 'Uncategorized'
    df.loc[df['Location'] == 'Unknown', 'Location'] = 'Location Undisclosed'
    
    # Generate Email format based on Website and Contact Name
    def generate_email(row):
        domain = extract_domain(row['Website'])
        contact = str(row.get('Contact Name', ''))
        
        name_parts = contact.split()
        first = name_parts[0].lower() if len(name_parts) > 0 else 'contact'
        last = name_parts[1].lower() if len(name_parts) > 1 else ''
        
        if domain:
            if last:
                return f"{first}.{last}@{domain}"
            return f"{first}@{domain}"
        
        # Fallback if no website
        company_clean = re.sub(r'[^a-zA-Z0-9]', '', str(row['Company Name'])).lower()
        if company_clean:
            if last:
                return f"{first}.{last}@{company_clean}.com"
            return f"{first}@{company_clean}.com"
            
        return "no-email@example.com"
        
    df['Email'] = df.apply(generate_email, axis=1)
    
    final_count = len(df)
    print(f"Data cleaning complete. Removed {initial_count - final_count} duplicates/invalid rows.")
    return df

def save_to_excel(df, filename='leads_output.xlsx'):
    """Saves the DataFrame to an Excel file."""
    print(f"Saving data to {filename}...")
    try:
        df.to_excel(filename, index=False)
        print("Data saved successfully to Excel.")
    except Exception as e:
        print(f"Error saving to Excel: {e}")

def save_to_csv(df, filename='leads_output.csv'):
    """Saves the DataFrame to a CSV file (for Google Sheets compatibility)."""
    print(f"Saving data to {filename}...")
    try:
        df.to_csv(filename, index=False)
        print("Data saved successfully to CSV.")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def run_generation():
    """Main execution job. Returns the cleaned data as a list of dicts."""
    print("\n--- Starting Lead Generation Job ---")
    raw_leads = fetch_lead_data()
    if not raw_leads:
        print("No leads fetched. Exiting.")
        return []
        
    df = pd.DataFrame(raw_leads)
    
    cleaned_df = clean_data(df)
    save_to_excel(cleaned_df)
    save_to_csv(cleaned_df)
    print("--- Job Complete ---\n")
    
    # Convert DataFrame to list of dicts for JSON serialization
    return cleaned_df.fillna("").to_dict('records')

def job():
    run_generation()

if __name__ == "__main__":
    # Execute once immediately
    job()
    
    # Bonus: Basic automation trigger (Scheduled run)
    print("\nBonus feature: Scheduler activated.")
    print("The script is scheduled to run every day at 09:00 AM.")
    print("Press Ctrl+C to exit if running interactively.\n")
    
    schedule.every().day.at("09:00").do(job)
