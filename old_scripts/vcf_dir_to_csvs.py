from vcf_to_csvs import *
input_dir = '../vcfFiles'
output_dir = '../processedFinal2'
semi_output_dir = '../semi_processed2'
# Get the list of VCF files in the input directory
vcf_files = [file for file in os.listdir(input_dir) if file.endswith('.vcf')]
semi_processed = os.listdir(semi_output_dir)
processed = os.listdir(output_dir)


# Process each VCF file
count =0 
for file in tqdm.tqdm(vcf_files):
    filename = os.path.splitext(file)[0]+'.csv'
    if(filename in processed and filename in semi_processed): #skips if the file has already been processed
        continue
    file_path = os.path.join(input_dir, file)
    process(file_path, semi_output_dir,output_dir)