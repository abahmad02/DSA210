import pandas as pd
import glob
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt

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

# Visualization of daily message count
# Combine both datasets with a Sender column
# Group by week (starting on Sunday by default) and Sender to count messages per week
your_messages['Week'] = your_messages['Timestamp'].dt.to_period('W').dt.start_time
friend_messages['Week'] = friend_messages['Timestamp'].dt.to_period('W').dt.start_time

your_messages['Sender'] = 'You'
friend_messages['Sender'] = 'Friend'

# Combine both datasets
all_messages = pd.concat([your_messages, friend_messages], ignore_index=True)

# Group by 'Week' and 'Sender' to count messages per week
weekly_counts = all_messages.groupby(['Week', 'Sender']).size().unstack(fill_value=0)

# Plot weekly message counts
def plot_weekly_message_counts(weekly_counts):
    plt.figure(figsize=(12, 6))
    weekly_counts.plot(kind='bar', stacked=True, figsize=(12, 6), alpha=0.8)
    plt.title('Weekly Message Count by Sender')
    plt.xlabel('Week')
    plt.ylabel('Message Count')
    plt.legend(title='Sender')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

# Uncomment the line below to generate the plot
plot_weekly_message_counts(weekly_counts)

