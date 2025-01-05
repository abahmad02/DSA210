# Project Proposal: Analysis of Instagram Message Data - Abdullah Ahmad DSA 210

## **Objective:**
The goal of this project is to analyze my Instagram usage, specifically the messages exchanged with a particular friend over time. The data for this analysis is obtained from Instagram's data export feature, which provides message records in HTML format. I aim to parse this data, conduct several hypothesis tests, and visualize the findings to determine trends, patterns, and differences in message activity.

---

## **Methodology:**

## 1. **Data Collection:**
- The raw message data is exported from Instagram in HTML format via Instagram's data request feature.
- Using Python's **BeautifulSoup** library, the HTML data is parsed to extract relevant details such as the sender, message content, and timestamp.

## 2. **Data Parsing:**
- After extracting the necessary data, I save it in CSV format for easier processing and further analysis. 
- **Pandas** is used to create and manipulate DataFrames, which allows for efficient data cleaning, organization, and aggregation.

## 3. **Data Analysis:**
- The parsed data is loaded into Pandas DataFrames for analysis.
- I first separate messages sent by me (Abdullah Ahmad) and my friend into distinct datasets.
- Using statistical tests, we compare the overall number of messages sent, reel-sharing behavior, and hashtag trends.

## 4. **Hypotheses:**
1. Overall Message Activity
   - **Null Hypothesis (H₀):** I and my friend send an equal proportion of messages.
   - **Alternative Hypothesis (H₁):** I send more messages than my friend.
2. Reel-Sharing Activity
   - **Null Hypothesis (H₀):** There is no difference in reel-sharing activity between weekdays and weekends.
   - **Alternative Hypothesis (H₁):** Reel-sharing activity differs significantly between weekdays and weekends.
3. Reel Activity by Day Type
   - **Null Hypothesis (H₀):** There is no significant difference in mine or my friend's reel-sharing activity between weekdays and weekends
   - **Alternative Hypothesis (H₁):** There is a significant difference in my mine or my friend's reel-sharing activity between weekdays and weekends.

## 5. **Statistical Tests:**
- The **t-test** and **z-test** are used to determine the results of the hypothesese above. 
- The results of the tests, including the T and Z statistics and P-values, are used to decide whether to reject or fail to reject the null hypotheses for the above claims.

## 6. **Visualization:**
### **Monthly Message Count Bar Charts**

Purpose: Displays the monthly message counts for each year, categorized by sender.
Visualization Method: Stacked bar charts, plotted for each year using matplotlib.

### **Heatmaps of Message Activity**

Purpose: Visualizes the distribution of message activity across days of the week and hours of the day for both users.
Visualization Method: Heatmaps created using seaborn.

### **Pie Charts of Message and Reel Proportions**

Purpose: Shows the proportion of regular messages versus reels for each sender.
Visualization Method: Pie charts, plotted separately for each sender using matplotlib.

### **Bar Charts for Message and Reel Counts**

Purpose: Provides a breakdown of the counts for regular messages and reels for each sender.
Visualization Method: Side-by-side bar charts using matplotlib.

### **Hourly and Daily Message Counts**

Purpose: Displays the frequency of messages sent by hour of the day and by day of the week.
Visualization Method: Bar charts using matplotlib.

### **T-Distribution vs Normal Distribution Plot**

Purpose: Compares the t-distribution to a normal distribution for hypothesis testing results.
Visualization Method: Line plots of distributions, with t-statistic markers using matplotlib.

### **Top Hashtags Bar Charts**

Purpose: Highlights the top 10 hashtags used by each sender.
Visualization Method: Horizontal bar charts created using seaborn.

### **Hashtag Usage Over Time**

Purpose: Shows trends in hashtag usage over time (grouped by month and year).
Visualization Method: Line charts with markers using matplotlib.
---

## **Libraries and Tools Used:**
- **BeautifulSoup**: To parse the HTML data obtained from Instagram.
- **Pandas**: For data manipulation and cleaning, including converting the parsed data into DataFrames and performing aggregations.
- **Scipy**: For conducting statistical tests such as the t-test to validate the hypothesis.
- **Matplotlib**: For visualizing the message data, specifically creating bar charts for daily or weekly counts.

---

## **Results:**
- Total Messages Sent by You: 18,845
- Total Messages Sent by Your Friend: 13,730
- T-statistic: 13.048
- P-value: 8.91e-38
- Since the P-value is extremely small, we reject the null hypothesis, meaning that I do indeed send more messages than my friend.

## **Conclusion:**
- Based on the results of the t-test and the visualizations, the hypothesis that I send more messages than my friend is supported by the data. The statistical evidence shows that I have sent significantly more messages overall and on a weekly basis. This analysis --   demonstrates how Instagram message data can be used to analyze personal communication patterns.

- ![Monthly Message Count Chart](Project_Fig_1_Messages_Spread.png)

The chart above visualizes the number of messages exchanged on a weekly basis.
