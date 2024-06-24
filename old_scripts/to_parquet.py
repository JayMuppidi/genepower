from fastparquet import write
import os
import pandas as pd
import tqdm
print("The current working directory is:", os.getcwd())
def process_semi(csv_file_path, num_duplicates,write_dest):
    count = 0
    for filename in os.listdir(csv_file_path):
        if filename.endswith('.csv'):
            # Read the CSV file into a dataframe
            file_path = os.path.join(csv_file_path, filename)
            og_df = pd.read_csv(file_path)
            og_df['patient_id'] = count
            count+=1
            for _ in tqdm.tqdm(range(num_duplicates)):
                if count >15:
                    break
                duplicate_df = og_df.copy()
                duplicate_df['patient_id'] =count
                if count == 1:
                    write(write_dest, duplicate_df,append = False)
                else:
                    write(write_dest, duplicate_df, append=True)
                count+=1

process_semi('../semi_processed2',30,'spark-warehouse/genepowerx.db/semi_processed.parquet')
# import fastparquet

# # Read the Parquet file
# df = fastparquet.ParquetFile('spark-warehouse/genepowerx.db/semi_processed.parquet').to_pandas()

# # Drop the column you want to remove
# df.drop(columns=['consequence','csq','hgvsc','hgvsp'], inplace=True)

# # Write the modified DataFrame back to a new Parquet file
# fastparquet.write('spark-warehouse/genepowerx.db/semi_processed.parquet', df)