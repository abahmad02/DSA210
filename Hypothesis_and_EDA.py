import pandas as pd
import glob
from scipy.stats import ttest_ind, t, norm,ttest_ind_from_stats
from statsmodels.stats.proportion import proportions_ztest
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import numpy as np
import re
from collections import Counter
from textblob import TextBlob

# Function to load data from a list of files
def load_data(file_list):
    combined_data = pd.DataFrame()
    for file in file_list:
        df = pd.read_csv(file)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%b %d, %Y %I:%M %p', errors='coerce')  # Ensure Timestamp is datetime
        combined_data = pd.concat([combined_data, df], ignore_index=True)
    return combined_data

# Load message data
your_files = sorted(glob.glob("your_messages_*.csv"))
friend_files = sorted(glob.glob("friend_messages_*.csv"))
print("Your Files:", your_files)
print("Friend Files:", friend_files)
your_messages = load_data(your_files)
friend_messages = load_data(friend_files)

# Data preprocessing
your_messages['Hour'] = pd.to_datetime(your_messages['Time'], errors='coerce').dt.hour
your_messages['Day'] = pd.to_datetime(your_messages['Date'], errors='coerce').dt.day_name()
friend_messages['Hour'] = pd.to_datetime(friend_messages['Time'], errors='coerce').dt.hour
friend_messages['Day'] = pd.to_datetime(friend_messages['Date'], errors='coerce').dt.day_name()

your_hourly_counts = your_messages.groupby('Hour').size()
your_daily_counts = your_messages.groupby('Day').size()
friend_hourly_counts = friend_messages.groupby('Hour').size()
friend_daily_counts = friend_messages.groupby('Day').size()

print("Your messages count by hour:\n", your_hourly_counts)
print("Your messages count by day:\n", your_daily_counts)
print("Friend's messages count by hour:\n", friend_hourly_counts)
print("Friend's messages count by day:\n", friend_daily_counts)

your_messages['Timestamp'] = pd.to_datetime(
    your_messages['Timestamp'], format='%b %d, %Y %I:%M %p', errors='coerce'
)

friend_messages['Timestamp'] = pd.to_datetime(
    friend_messages['Timestamp'], format='%b %d, %Y %I:%M %p', errors='coerce'
)

print("Your Messages:" , your_messages['Day'])

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

# Hypothesis test
your_reels = type_counts.loc['You', 'Reel']
your_total = type_counts.loc['You', 'Reel'] + type_counts.loc['You', 'Message']
friend_reels = type_counts.loc['Friend', 'Reel']
friend_total = type_counts.loc['Friend', 'Reel'] + type_counts.loc['Friend', 'Message']

# Observed successes (reels sent) and total trials (messages sent)
counts = [your_reels, friend_reels]
nobs = [your_total, friend_total]

# Perform a one-sided z-test
z_stat, p_value = proportions_ztest(counts, nobs, alternative='larger')

print(f"Z-statistic: {z_stat:.3f}, P-value: {p_value:.3f}")
if p_value < 0.05:
    print("Reject the null hypothesis: You send more reels than your friend.")
else:
    print("Fail to reject the null hypothesis: There is no significant evidence that you send more reels than your friend.")
    
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

plot_monthly_message_counts(monthly_counts)

# Plotting the bar graphs
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(2, 2)

ax1 = fig.add_subplot(gs[0, 0])
ax1.bar(your_hourly_counts.index, your_hourly_counts.values)
ax1.set_title("Your Messages by Hour")
ax1.set_xlabel("Hour")
ax1.set_ylabel("Count")

ax2 = fig.add_subplot(gs[0, 1])
ax2.bar(your_daily_counts.index, your_daily_counts.values)
ax2.set_title("Your Messages by Day")
ax2.set_xlabel("Day")
ax2.set_ylabel("Count")

ax3 = fig.add_subplot(gs[1, 0])
ax3.bar(friend_hourly_counts.index, friend_hourly_counts.values)
ax3.set_title("Friend's Messages by Hour")
ax3.set_xlabel("Hour")
ax3.set_ylabel("Count")

ax4 = fig.add_subplot(gs[1, 1])
ax4.bar(friend_daily_counts.index, friend_daily_counts.values)
ax4.set_title("Friend's Messages by Day")
ax4.set_xlabel("Day")
ax4.set_ylabel("Count")

plt.tight_layout()
plt.show()

plot_heatmaps(your_heatmap_data, friend_heatmap_data)
plot_message_reel_proportions_pie(type_counts)
plot_message_reel_proportions_bar(type_counts)

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

def plot_t_and_normal_distribution(t_stat, df, title, color):
    """
    Plot a t-distribution with a normal distribution overlay, with the t-statistic marked.
    
    Parameters:
        t_stat (float): The t-statistic value.
        df (int): Degrees of freedom.
        title (str): Title for the plot.
        color (str): Color for the t-distribution plot.
    """
    # Generate x-axis values
    x = np.linspace(-4, 4, 1000)
    
    # Generate t-distribution and normal distribution values
    t_dist = t.pdf(x, df)
    normal_dist = norm.pdf(x)
    
    # Plot the distributions
    plt.figure(figsize=(10, 6))
    plt.plot(x, t_dist, color=color, label=f"t-distribution (df={df})", linewidth=2)
    plt.plot(x, normal_dist, color="orange", linestyle="--", label="Normal distribution", linewidth=2)
    
    # Mark the t-statistic
    plt.axvline(t_stat, color="red", linestyle="--", label=f"t-statistic: {t_stat:.2f}")
    plt.axvline(-t_stat, color="red", linestyle="--", alpha=0.5, label=f"Opposite t-stat: {-t_stat:.2f}")
    
    # Add labels, legend, and grid
    plt.title(title)
    plt.xlabel("t-value / z-value")
    plt.ylabel("Density")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

# Degrees of freedom calculation
your_df = len(your_weekday_counts) + len(your_weekend_counts) - 2
friend_df = len(friend_weekday_counts) + len(friend_weekend_counts) - 2

# Plot t- and normal distributions
plot_t_and_normal_distribution(t_stat_your, your_df, "Your Reel Sharing: T vs Normal Distribution", color="blue")
plot_t_and_normal_distribution(t_stat_friend, friend_df, "Friend's Reel Sharing: T vs Normal Distribution", color="green")

# Hashtag testing

# Function to extract hashtags from content
def extract_hashtags(content):
    if isinstance(content, str):
        return re.findall(r"#\w+", content)
    return []

# Extract hashtags from your and your friend's messages
your_messages['Hashtags'] = your_messages['Content'].apply(extract_hashtags)
friend_messages['Hashtags'] = friend_messages['Content'].apply(extract_hashtags)

# Flatten and count hashtag frequencies
your_hashtag_counts = Counter([hashtag for hashtags in your_messages['Hashtags'] for hashtag in hashtags])
friend_hashtag_counts = Counter([hashtag for hashtags in friend_messages['Hashtags'] for hashtag in hashtags])

# Convert to DataFrame for visualization
your_hashtag_df = pd.DataFrame(your_hashtag_counts.items(), columns=['Hashtag', 'Count']).sort_values(by='Count', ascending=False)
friend_hashtag_df = pd.DataFrame(friend_hashtag_counts.items(), columns=['Hashtag', 'Count']).sort_values(by='Count', ascending=False)

# Display top hashtags
print("Top Hashtags in Your Messages:")
print(your_hashtag_df.head(10))

print("\nTop Hashtags in Friend's Messages:")
print(friend_hashtag_df.head(10))

# Plot top hashtags for you and your friend
def plot_top_hashtags(hashtag_df, title):
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Count', y='Hashtag', data=hashtag_df.head(10), palette='viridis')
    plt.title(title)
    plt.xlabel('Count')
    plt.ylabel('Hashtag')
    plt.tight_layout()
    plt.show()

plot_top_hashtags(your_hashtag_df, "Top 10 Hashtags in Your Messages")
plot_top_hashtags(friend_hashtag_df, "Top 10 Hashtags in Friend's Messages")

# Find overlapping hashtags
your_hashtags_set = set(your_hashtag_counts.keys())
friend_hashtags_set = set(friend_hashtag_counts.keys())
common_hashtags = your_hashtags_set.intersection(friend_hashtags_set)

print(f"Number of common hashtags: {len(common_hashtags)}")
print(f"Common Hashtags: {list(common_hashtags)[:10]}")

# Add a column for number of hashtags in each message
your_messages['Num_Hashtags'] = your_messages['Hashtags'].apply(len)
friend_messages['Num_Hashtags'] = friend_messages['Hashtags'].apply(len)

# Group by month and year
your_hashtag_trends = your_messages.groupby(['Year', 'Month'])['Num_Hashtags'].sum()
friend_hashtag_trends = friend_messages.groupby(['Year', 'Month'])['Num_Hashtags'].sum()

# Plot trends
def plot_hashtag_trends(trends, title):
    trends.plot(kind='line', marker='o', figsize=(10, 6), title=title, xlabel="Time", ylabel="Number of Hashtags")
    plt.grid()
    plt.show()

plot_hashtag_trends(your_hashtag_trends, "Your Hashtag Usage Over Time")
plot_hashtag_trends(friend_hashtag_trends, "Friend's Hashtag Usage Over Time")

# Function to compute sentiment
def compute_sentiment(content):
    if isinstance(content, str):
        return TextBlob(content).sentiment.polarity
    return 0

# Add sentiment scores
your_messages['Sentiment'] = your_messages['Content'].apply(compute_sentiment)
friend_messages['Sentiment'] = friend_messages['Content'].apply(compute_sentiment)

# Analyze sentiment for messages containing hashtags
your_hashtag_sentiment = your_messages[your_messages['Num_Hashtags'] > 0]['Sentiment'].mean()
friend_hashtag_sentiment = friend_messages[friend_messages['Num_Hashtags'] > 0]['Sentiment'].mean()

print(f"Average Sentiment of Your Hashtag Messages: {your_hashtag_sentiment:.2f}")
print(f"Average Sentiment of Friend's Hashtag Messages: {friend_hashtag_sentiment:.2f}")

