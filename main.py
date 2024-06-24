from fastapi import FastAPI, UploadFile, File
from helpers import *
from vcf_to_csvs import *
from spark_helpers import *
from fastapi import HTTPException
from fastparquet import write
app = FastAPI()

# set these
semi_processed_parquet = "../spark-warehouse/genepowerx.db/semi_processed.parquet"
processed_parquet = "../spark-warehouse/genepowerx.db/processed.parquet"
script_version  = 1
vcf_to_csv_func = process #this is for script changes, the function definition is below

# the function takes path to vcf, where to write the semi_processed, where to write processed
# example function: def process(filepath,semi_output_dir,output_dir):
#             # Process the VCF file  
#             #Process the VCF file
#             return path_to_semi_processed_csv, path_to_processed_csv
# it should return the path to the semi processed csv and the processed csv

#queries are returned as pandas dataframes, which are converted to json using the to_json() method to send through api, can be decoded using pd.read_json()

@app.get("/sql")
async def execute_sql(sql_command:str):
    result = sparkQ(sql_command)
    return {result.to_json()}

@app.get("/patient_analyzed")
async def execute_sql(patient_id:int):
    result = sparkQ("SELECT (*) FROM model1 WHERE patient_id LIKE " + str(patient_id)) 
    print(result.head())
    return result.to_json()  

@app.post("/upload_vcf")
async def upload_vcf(patient_id:int, file:UploadFile):
    print(patient_id)
    if not file.filename.endswith('.vcf'):
        raise HTTPException(status_code=400, detail="Wrong format, please upload a .vcf file")
    with open(f'../recieved/{file.filename}', 'wb') as buffer:
        contents = await file.read()  # async read
        buffer.write(contents)
    print("File received: "+file.filename)
    
    semi_proc_path, proc_path = vcf_to_csv_func(f'../recieved/{file.filename}', '../temp_semi_processed','../temp_processed')
    
    semi_proc_df = pd.read_csv(semi_proc_path)
    semi_proc_df["patient_id"] = patient_id
    semi_proc_df["version"] = script_version
    if os.path.exists(semi_processed_parquet):
        write(semi_processed_parquet,semi_proc_df,append = True)
    else:
        write(semi_processed_parquet,semi_proc_df,append = False)
    

    proc_df = pd.read_csv(proc_path)
    proc_df["patient_id"] = patient_id
    proc_df["version"] = script_version
    if os.path.exists(processed_parquet):
        write(processed_parquet,proc_df,append = True)
    else:
        write(processed_parquet,proc_df,append = False)
    
    #delete_files(f'../recieved/{file.filename}', semi_proc_path, proc_path) removes vcf, semi_proc.csv and processed.csv files
    
    return {"filename":file.filename,"patient_id":patient_id}
