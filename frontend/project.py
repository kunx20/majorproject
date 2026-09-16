import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv('/Dataset .csv')
# Shape of the dataset
print("Shape:", df.shape)           # (rows, columns)
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# Preview the data
df.head()                            # First 5 rows
# Total missing values per column
print(df.isnull().sum())

# Percentage of missing values
print((df.isnull().sum() / len(df)) * 100)

# Visual heatmap of missing values
sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
plt.title("Missing Values Heatmap")
plt.show()
# Option A: Drop rows with missing values
df.dropna(inplace=True)

# Option B: Fill with mean (numerical columns) - REMOVED: 'column_name' is a placeholder and not an actual column
# df['column_name'].fillna(df['column_name'].mean(), inplace=True)

# Option C: Fill with mode (categorical columns) - REMOVED: 'column_name' is a placeholder and not an actual column
# df['column_name'].fillna(df['column_name'].mode()[0], inplace=True)
# Check data types
print(df.dtypes)

# Check column info
df.info()
# Convert to numeric - REMOVED: 'column_name' is a placeholder and not an actual column
# df['column_name'] = pd.to_numeric(df['column_name'], errors='coerce')

# Convert to category - REMOVED: 'column_name' is a placeholder and not an actual column
# df['column_name'] = df['column_name'].astype('category')

# Convert to datetime - REMOVED: 'date_column' is a placeholder and not an actual column
# df['date_column'] = pd.to_datetime(df['date_column'])
df['Aggregate rating'] = df['Aggregate rating'].astype(float)
# Value counts
print(df['Aggregate rating'].value_counts())

# Distribution plot
plt.figure(figsize=(10, 5))
sns.countplot(x='Aggregate rating', data=df, palette='Set2')
plt.title("Distribution of Aggregate Rating")
plt.xlabel("Rating")
plt.ylabel("Count")      
plt.xticks(rotation=45)
plt.show()
# Percentage of each class
print(df['Aggregate rating'].value_counts(normalize=True) * 100)