import pandas as pd
import glob
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import numpy as np


# Function to load data from a list of files
def load_data(file_list):
    combined_data = pd.DataFrame()
    for file in file_list:
        df = pd.read_csv(file)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')  # Ensure Timestamp is datetime
        combined_data = pd.concat([combined_data, df], ignore_index=True)
    return combined_data

# Load message data
your_files = sorted(glob.glob("your_messages_*.csv"))
friend_files = sorted(glob.glob("friend_messages_*.csv"))
your_messages = load_data(your_files)
friend_messages = load_data(friend_files)

# Data preprocessing
your_messages['Hour'] = pd.to_datetime(your_messages['Time'], errors='coerce').dt.hour
your_messages['Day'] = pd.to_datetime(your_messages['Date'], errors='coerce').dt.day_name()
friend_messages['Hour'] = pd.to_datetime(friend_messages['Time'], errors='coerce').dt.hour
friend_messages['Day'] = pd.to_datetime(friend_messages['Date'], errors='coerce').dt.day_name()

# Count total messages
your_message_count = len(your_messages)
friend_message_count = len(friend_messages)

# Daily message counts for statistical comparison
your_daily_message_counts = your_messages.groupby(your_messages['Timestamp'].dt.date).size()
friend_daily_message_counts = friend_messages.groupby(friend_messages['Timestamp'].dt.date).size()

# Align counts for t-test
aligned_counts = pd.concat([your_daily_message_counts, friend_daily_message_counts], axis=1, keys=['You', 'Friend']).fillna(0)

# Perform t-test
t_stat, p_value = ttest_ind(aligned_counts['You'], aligned_counts['Friend'], alternative='greater')

# Results interpretation
print(f"Total Messages Sent by You: {your_message_count}")
print(f"Total Messages Sent by Your Friend: {friend_message_count}")
print(f"T-statistic: {t_stat}, P-value: {p_value}")
if p_value < 0.05:
    print("Reject the null hypothesis: You send more messages than your friend.")
else:
    print("Fail to reject the null hypothesis: There is no significant evidence that you send more messages than your friend.")

# Group messages by sender, year, and month
your_messages['Year'] = your_messages['Timestamp'].dt.year
your_messages['Month'] = your_messages['Timestamp'].dt.month
friend_messages['Year'] = friend_messages['Timestamp'].dt.year
friend_messages['Month'] = friend_messages['Timestamp'].dt.month
your_messages['Sender'] = 'You'
friend_messages['Sender'] = 'Friend'

all_messages = pd.concat([your_messages, friend_messages], ignore_index=True)

# Monthly message counts
monthly_counts = all_messages.groupby(['Year', 'Month', 'Sender']).size().unstack(fill_value=0)
all_months = pd.MultiIndex.from_product([sorted(all_messages['Year'].unique()), range(1, 13)], names=['Year', 'Month'])
monthly_counts = monthly_counts.reindex(all_months, fill_value=0)

# Heatmap data
your_heatmap_data = your_messages.groupby(['Day', 'Hour']).size().unstack(fill_value=0).T
friend_heatmap_data = friend_messages.groupby(['Day', 'Hour']).size().unstack(fill_value=0).T
ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
your_heatmap_data = your_heatmap_data.reindex(columns=ordered_days)
friend_heatmap_data = friend_heatmap_data.reindex(columns=ordered_days)

# Identify reels and categorize messages
def categorize_message(content, prefix):
    if isinstance(content, str) and content.startswith(prefix):
        return 'Reel'
    return 'Message'

your_messages['Type'] = your_messages['Content'].apply(lambda x: categorize_message(x, "You sent an attachment."))
friend_messages['Type'] = friend_messages['Content'].apply(lambda x: categorize_message(x, "Muhammad sent an attachment."))

# Combine and analyze type counts
all_messages = pd.concat([your_messages, friend_messages], ignore_index=True)
type_counts = all_messages.groupby(['Sender', 'Type']).size().unstack(fill_value=0)
type_counts['Proportion'] = type_counts['Reel'] / (type_counts['Reel'] + type_counts['Message'])
print(type_counts)
# Visualization functions
def plot_monthly_message_counts(monthly_counts):
    num_years = len(monthly_counts.index.levels[0])
    rows = (num_years + 1) // 2
    fig = plt.figure(figsize=(16, 6 * rows))
    spec = gridspec.GridSpec(rows, 2, figure=fig)
    axes = [fig.add_subplot(spec[i // 2, i % 2]) for i in range(num_years)]

    for i, year in enumerate(monthly_counts.index.levels[0]):
        ax = axes[i]
        yearly_data = monthly_counts.loc[year]
        yearly_data.plot(kind='bar', stacked=True, ax=ax, alpha=0.8)
        ax.set_title(f'Monthly Message Count for {year}')
        ax.set_xlabel('Month')
        ax.set_ylabel('Message Count')
        ax.set_xticks(range(12))
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)

    plt.tight_layout()
    plt.show()

def plot_heatmaps(your_data, friend_data):
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    sns.heatmap(your_data, ax=axes[0], cmap="YlGnBu", cbar=True)
    axes[0].set_title("Your Message Activity")
    axes[0].set_xlabel("Day of Week")
    axes[0].set_ylabel("Hour of Day")
    axes[0].invert_yaxis()

    sns.heatmap(friend_data, ax=axes[1], cmap="YlGnBu", cbar=True)
    axes[1].set_title("Friend's Message Activity")
    axes[1].set_xlabel("Day of Week")
    axes[1].set_ylabel("Hour of Day")
    axes[1].invert_yaxis()

    plt.tight_layout()
    plt.show()

import matplotlib.pyplot as plt

# Plot pie charts for message and reel proportions
def plot_message_reel_proportions_pie(type_counts):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Plot pie chart for your messages
    your_data = type_counts.loc['You', ['Message', 'Reel']]
    axes[0].pie(
        your_data, labels=your_data.index, autopct='%1.1f%%', startangle=90, colors=['skyblue', 'orange']
    )
    axes[0].set_title("Your Messages")

    # Plot pie chart for friend's messages
    friend_data = type_counts.loc['Friend', ['Message', 'Reel']]
    axes[1].pie(
        friend_data, labels=friend_data.index, autopct='%1.1f%%', startangle=90, colors=['skyblue', 'orange']
    )
    axes[1].set_title("Friend's Messages")

    plt.tight_layout()
    plt.show()

def plot_message_reel_proportions_bar(type_counts):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    your_data = type_counts.loc['You', ['Message', 'Reel']]
    your_data.plot(kind='bar', ax=axes[0], color=['skyblue', 'orange'])
    axes[0].set_title("Your Messages")
    axes[0].set_ylabel("Count")

    friend_data = type_counts.loc['Friend', ['Message', 'Reel']]
    friend_data.plot(kind='bar', ax=axes[1], color=['skyblue', 'orange'])
    axes[1].set_title("Friend's Messages")
    axes[1].set_ylabel("Count")

    plt.tight_layout()
    plt.show()

# Uncomment to plot
#plot_monthly_message_counts(monthly_counts)
#plot_heatmaps(your_heatmap_data, friend_heatmap_data)
#plot_message_reel_proportions_pie(type_counts)
#plot_message_reel_proportions_bar(type_counts)

# Classify messages into weekdays and weekends
def classify_day_type(day):
    if day in ['Saturday', 'Sunday']:
        return 'Weekend'
    return 'Weekday'

your_messages['DayType'] = your_messages['Day'].apply(classify_day_type)
friend_messages['DayType'] = friend_messages['Day'].apply(classify_day_type)

# Filter reels and group by DayType
your_reel_counts = your_messages[your_messages['Type'] == 'Reel'].groupby('DayType').size()
friend_reel_counts = friend_messages[friend_messages['Type'] == 'Reel'].groupby('DayType').size()

# Combine weekday and weekend counts
all_reel_counts = pd.concat([
    your_reel_counts.rename('You'),
    friend_reel_counts.rename('Friend')
], axis=1).fillna(0)

print("\nReel Counts by Day Type:")
print(all_reel_counts)

# Perform t-test for weekdays vs. weekends
your_weekday_counts = your_messages[(your_messages['Type'] == 'Reel') & (your_messages['DayType'] == 'Weekday')].groupby(your_messages['Timestamp'].dt.date).size()
your_weekend_counts = your_messages[(your_messages['Type'] == 'Reel') & (your_messages['DayType'] == 'Weekend')].groupby(your_messages['Timestamp'].dt.date).size()

friend_weekday_counts = friend_messages[(friend_messages['Type'] == 'Reel') & (friend_messages['DayType'] == 'Weekday')].groupby(friend_messages['Timestamp'].dt.date).size()
friend_weekend_counts = friend_messages[(friend_messages['Type'] == 'Reel') & (friend_messages['DayType'] == 'Weekend')].groupby(friend_messages['Timestamp'].dt.date).size()

# Perform t-tests
t_stat_your, p_value_your = ttest_ind(
    your_weekday_counts, your_weekend_counts, alternative='two-sided', nan_policy='omit'
)
t_stat_friend, p_value_friend = ttest_ind(
    friend_weekday_counts, friend_weekend_counts, alternative='two-sided', nan_policy='omit'
)

# Results
print("\nYour Reel Sharing T-Test Results:")
print(f"T-statistic: {t_stat_your}, P-value: {p_value_your}")
if p_value_your < 0.05:
    print("Significant difference in your reel-sharing activity between weekdays and weekends.")
else:
    print("No significant difference in your reel-sharing activity between weekdays and weekends.")

print("\nFriend's Reel Sharing T-Test Results:")
print(f"T-statistic: {t_stat_friend}, P-value: {p_value_friend}")
if p_value_friend < 0.05:
    print("Significant difference in your friend's reel-sharing activity between weekdays and weekends.")
else:
    print("No significant difference in your friend's reel-sharing activity between weekdays and weekends.")

