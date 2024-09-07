#https://chatgpt.com/g/g-cKXjWStaE-python/c/0ae5e862-a914-42fa-9626-c67aada2d5ca

import pandas as pd
import matplotlib.pyplot as plt

# Data format: List of dictionaries
data = [
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 5000, "Unit Price": 5000},
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 7500, "Unit Price": 7500},
    {"Item": "Blood Aspect Core", "Quantity": 2, "Total Price": 15500, "Unit Price": 7750},
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 7900},
    {"Item": "Blood Aspect Core", "Quantity": 2, "Total Price": 15500, "Unit Price": 7750},
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 8900},
    {"Item": "Blood Aspect Core", "Quantity": 2, "Total Price": 15500, "Unit Price": 8750},
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 8900},
    {"Item": "Blood Aspect Core", "Quantity": 2, "Total Price": 15500, "Unit Price": 7750},
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 7900},
    {"Item": "Blood Aspect Core", "Quantity": 2, "Total Price": 15500, "Unit Price": 7750},
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 9900},
    {"Item": "Blood Aspect Core", "Quantity": 2, "Total Price": 15500, "Unit Price": 7750},
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 7900},
    {"Item": "Blood Aspect Core", "Quantity": 2, "Total Price": 15500, "Unit Price": 7750},
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 7900},
    {"Item": "Blood Aspect Core", "Quantity": 2, "Total Price": 15500, "Unit Price": 7750},
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 9900},
    {"Item": "Blood Aspect Core", "Quantity": 2, "Total Price": 15500, "Unit Price": 7750},
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 7900},
    {"Item": "Blood Aspect Core", "Quantity": 2, "Total Price": 15500, "Unit Price": 7750},
    {"Item": "Blood Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 7900},
    {"Item": "Blood Aspect Core", "Quantity": 2, "Total Price": 15500, "Unit Price": 7750},
    {"Item": "Artisan Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 7900},
    {"Item": "Artisan Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 7900},
    {"Item": "Artisan Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 7900},
    {"Item": "Artisan Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 7900},
    {"Item": "Artisan Aspect Core", "Quantity": 1, "Total Price": 7900, "Unit Price": 7900},
    {"Item": "Artisan Aspect Core", "Quantity": 1, "Total Price": 80000, "Unit Price": 80000},
    # Add more rows as needed...
]

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(data)

# Function to analyze the data
def analyze_data(df):
    # Categorize by price ranges
    price_bins = [0, 5000, 10000, 15000, 20000, float('inf')]
    price_labels = ['<=5k', '5k-10k', '10k-15k', '15k-20k', '>20k']
    df['Price Category'] = pd.cut(df['Unit Price'], bins=price_bins, labels=price_labels)

    # Frequency distribution
    freq_dist = df['Price Category'].value_counts().sort_index()

    # Statistical summaries
    summaries = df.groupby('Price Category').agg(
        Count=('Unit Price', 'size'),
        Median=('Unit Price', 'median'),
        Mode=('Unit Price', lambda x: x.mode().iloc[0] if not x.mode().empty else None),
        Std_Dev=('Unit Price', 'std')
    ).reset_index()

    return freq_dist, summaries

# Function to visualize the data
def visualize_data(freq_dist, summaries):
    # Bar Chart for Frequency Distribution
    plt.figure(figsize=(10, 6))
    freq_dist.plot(kind='bar')
    plt.title('Frequency Distribution of Price Categories')
    plt.xlabel('Price Category')
    plt.ylabel('Frequency')
    plt.show()

    # Box Plot for Unit Prices per Category
    plt.figure(figsize=(10, 6))
    summaries.boxplot(column='Median', by='Price Category')
    plt.title('Box Plot of Unit Prices per Category')
    plt.xlabel('Price Category')
    plt.ylabel('Unit Price')
    plt.show()

# Main program interface
def main(df):
    # Analyze the data
    freq_dist, summaries = analyze_data(df)

    # Print the analysis results
    print("\nFrequency Distribution:\n", freq_dist)
    print("\nStatistical Summaries:\n", summaries)

    # Visualize the data
    visualize_data(freq_dist, summaries)

# Interface with the main function
if __name__ == "__main__":
    main(df)
