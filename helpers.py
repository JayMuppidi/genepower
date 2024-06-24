import time 
import os
import pandas as pd
import tqdm 
from fastparquet import write

def runQ(query,function):
    start = time.time()
    result = function(query)
    end = time.time()
    return result, end - start

def delete_files(vcf_path, semi_proc_path, proc_path):
    os.remove(vcf_path)
    os.remove(semi_proc_path)
    os.remove(proc_path)
    


def create_duplicates(df, num_duplicates,count):
    duplicates = []
    df['patient_id'] = count
    count+=1
    for _ in tqdm.tqdm(range(num_duplicates)):
        duplicate_df = df.copy()
        duplicate_df['patient_id'] =count
        duplicates.append(duplicate_df)
        count+=1
    duplicates.append(df)
    return duplicates
def process_data(csv_file_path, num_duplicates):
    
    all_dataframes = []
    
    for filename in os.listdir(csv_file_path):
        if filename.endswith('.csv'):
            # Read the CSV file into a dataframe
            file_path = os.path.join(csv_file_path, filename)
            df = pd.read_csv(file_path,low_memory=False)
            # Skip headers for dataframes after the first one
            if len(all_dataframes) > 0:
                df = df.iloc[1:]
            # Append the dataframe to the list
            all_dataframes.append(df)
    
    # Iterate through each dataframe in all_dataframes and create duplicates
    new_dataframes = []
    count = 0
    for original_df in all_dataframes:
        duplicates = create_duplicates(original_df, num_duplicates, count)
        count += duplicates[0].shape[0]
        new_dataframes.extend(duplicates)
    
    return new_dataframes
