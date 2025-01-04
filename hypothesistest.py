import pandas as pd
import glob
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Function to load data from a list of files
def load_data(file_list):
    combined_data = pd.DataFrame()
    for file in file_list:
        df = pd.read_csv(file)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')  # Ensure Timestamp is datetime
        combined_data = pd.concat([combined_data, df], ignore_index=True)
    return combined_data

# File paths for your and your friend's messages
your_files = sorted(glob.glob("your_messages_*.csv"))
friend_files = sorted(glob.glob("friend_messages_*.csv"))

# Load data
your_messages = load_data(your_files)
friend_messages = load_data(friend_files)

# Count total messages
your_message_count = len(your_messages)
friend_message_count = len(friend_messages)

# Extract dates and group by date for message counts
your_daily_message_counts = your_messages.groupby(your_messages['Timestamp'].dt.date).size()
friend_daily_message_counts = friend_messages.groupby(friend_messages['Timestamp'].dt.date).size()

# Align daily message counts by date for proper comparison
aligned_counts = pd.concat([your_daily_message_counts, friend_daily_message_counts], axis=1, keys=['You', 'Friend']).fillna(0)

t_stat, p_value = ttest_ind(aligned_counts['You'], aligned_counts['Friend'], alternative='greater')

# Display results
print(f"Total Messages Sent by You: {your_message_count}")
print(f"Total Messages Sent by Your Friend: {friend_message_count}")
print(f"T-statistic: {t_stat}, P-value: {p_value}")

# Interpretation
if p_value < 0.05:
    print("Reject the null hypothesis: You send more messages than your friend.")
else:
    print("Fail to reject the null hypothesis: There is no significant evidence that you send more messages than your friend.")

# Add year and month columns
your_messages['Year'] = your_messages['Timestamp'].dt.year
your_messages['Month'] = your_messages['Timestamp'].dt.month
friend_messages['Year'] = friend_messages['Timestamp'].dt.year
friend_messages['Month'] = friend_messages['Timestamp'].dt.month

# Combine both datasets
your_messages['Sender'] = 'You'
friend_messages['Sender'] = 'Friend'
all_messages = pd.concat([your_messages, friend_messages], ignore_index=True)

# Group by Year, Month, and Sender to count messages per month
monthly_counts = all_messages.groupby(['Year', 'Month', 'Sender']).size().unstack(fill_value=0)

# Fill in missing months for each year
all_months = pd.MultiIndex.from_product([
    sorted(all_messages['Year'].unique()), range(1, 13)
], names=['Year', 'Month'])
monthly_counts = monthly_counts.reindex(all_months, fill_value=0)

# Drop rows with NaN years (if any)
monthly_counts = monthly_counts.dropna()

# Ensure all years are correctly captured from the dataset
all_years = sorted(all_messages['Year'].dropna().unique())

# Plot monthly message counts using a gridspec layout
def plot_monthly_message_counts(monthly_counts):
    num_years = len(all_years)
    rows = (num_years + 1) // 2  # Calculate rows for grid layout
    fig = plt.figure(figsize=(16, 6 * rows))
    spec = gridspec.GridSpec(rows, 2, figure=fig)
    axes = [fig.add_subplot(spec[i // 2, i % 2]) for i in range(num_years)]

    for i, year in enumerate(all_years):
        ax = axes[i]
        yearly_data = monthly_counts.loc[year]
        yearly_data.plot(kind='bar', stacked=True, ax=ax, alpha=0.8)
        ax.set_title(f'Monthly Message Count for {year}')
        ax.set_xlabel('Month')
        ax.set_ylabel('Message Count')
        ax.legend(title='Sender')
        ax.set_xticks(range(12))
        ax.set_xticklabels([
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ], rotation=45)

    plt.tight_layout()
    plt.show()

# Uncomment the line below to generate the plot
plot_monthly_message_counts(monthly_counts)
