from bs4 import BeautifulSoup
import pandas as pd

# Load the HTML file
with open("message_1.html", "r", encoding="utf-8") as file:
    html_data = file.read()

# Parse the data with BeautifulSoup
soup = BeautifulSoup(html_data, 'html.parser')
messages = []

# Extract messages
for message_div in soup.find_all("div", class_="pam _3-95 _2ph- _a6-g uiBoxWhite noborder"):
    sender_div = message_div.find("div", class_="_3-95 _2pim _a6-h _a6-i")
    content_div = message_div.find("div", class_="_3-95 _a6-p") 
    timestamp_div = message_div.find("div", class_="_3-94 _a6-o")

    # Extract sender, content, and timestamp with fallback for missing elements
    sender = sender_div.text.strip() if sender_div else "Unknown"
    content = content_div.get_text(" ", strip=True) if content_div else "No content"
    timestamp = timestamp_div.text.strip() if timestamp_div else "No timestamp"

    messages.append({"Sender": sender, "Content": content, "Timestamp": timestamp})

# Convert to DataFrame
df = pd.DataFrame(messages)
# Split the Timestamp into Date and Time columns
df[['Date', 'Time']] = df['Timestamp'].str.extract(r'(\w+ \d{1,2}, \d{4}) (.+)')

# Separate messages
user_messages = df[df['Sender'] == "Abdullah Ahmad"]
friend_messages = df[df['Sender'] == "##NAME_REDACTED##"]

# Save results to CSV files for further analysis
user_messages.to_csv("your_messages_1.csv", index=False)
friend_messages.to_csv("friend_messages_1.csv", index=False)

# Display summary
print("Your Messages:\n", user_messages.head())
print("\nFriend's Messages:\n", friend_messages.head())
