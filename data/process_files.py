import json
import pandas as pd

# Load questions.json and create DataFrame without input, expected, and requirements
with open('data/questions.json', 'r') as f:
    questions_data = json.load(f)

# Create DataFrame with only function_id
df_questions = pd.DataFrame([{
    'function_id': record['function_id']
} for record in questions_data])

# Drop duplicates based on function_id
df_questions = df_questions.drop_duplicates(subset=['function_id'])

# Extract class_day and exercise_number from function_id
df_questions['class_day'] = df_questions['function_id'].str.extract(r'(A\d+)')
df_questions['exercise_number'] = df_questions['function_id'].str.extract(r'E(\d+)')

# Merge the DataFrames on class_day
function_counts = df_questions.groupby('class_day').size().sort_values(ascending=False)

function_counts.to_csv('data/merged_data.csv')
# Display first few rows of the merged DataFrame
print(function_counts)