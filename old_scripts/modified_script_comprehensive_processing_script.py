##################################### IMPORTING THE REQUIRED LIBRARIES ##########################################################
import numpy as np
import pandas as pd
import polars as pl
import sys
import re
import os
pd.set_option('display.max_columns',None)
import warnings
import xlsxwriter
warnings.filterwarnings("ignore")
print("Loading the Librabies completed")

######################################### GETTING THE COVERED POSITIONS FROM THE MOTHER VCF FILE FROM THE BED COORDINATES ####

def read_bed_file(bed_file):
    bed_positions = set()
    with open(bed_file, 'r') as f:
        for line in f:
            if line.startswith('#'):  # Skip header lines if present
                continue
            fields = line.strip().split('\t')
            if len(fields) >= 3:
                chrom = fields[0]
                try:
                    start = int(fields[1])
                    end = int(fields[2])
                except ValueError:
                    continue  # Skip this line if start or end position is not an integer
                for pos in range(start, end + 1):
                    bed_positions.add((chrom, pos))
    return bed_positions


def filter_vcf_file(vcf_file, bed_positions):
    filtered_vcf_records = []
    with open(vcf_file, 'r') as f:
        for line in f:
            if line.startswith('#'):  # Preserve header lines in the output
                filtered_vcf_records.append(line)
                continue
            fields = line.strip().split('\t')
            if len(fields) >= 2:
                raw_chrom = fields[0]
                chrom =  raw_chrom.split('_')[0]
                try:
                    pos = int(fields[1])
                except ValueError:
                    continue  # Skip this line if 'POS' is not an integer
                if (chrom, pos) in bed_positions:
                    filtered_vcf_records.append(line)
    return filtered_vcf_records

def write_filtered_vcf(filtered_vcf_records, output_file):
    with open(output_file, 'w') as f:
        for record in filtered_vcf_records:
            f.write(record)

def main():
    bed_file = r'C:/Users/GenepoweRx_Madhu/Downloads/BED_files/srinivas_sir_covered.bed'
    vcf_file = r'C:/Users/GenepoweRx_Madhu/Downloads/vcf_files_all/KHGLBS649_final.vcf'
    output_file = r'C:/Users/GenepoweRx_Madhu/Downloads/COVERED_VCF_FILES_BED/KHGLBS649_final.vcf'

    bed_positions = read_bed_file(bed_file)
    filtered_vcf_records = filter_vcf_file(vcf_file, bed_positions)
    write_filtered_vcf(filtered_vcf_records, output_file)

if __name__ == "__main__":
    main()

print("Covered/Not_Covered completed")

########################################### IMPORTING THE VCF DATA AND EXPANDING THE DEPTH COLUMNS ##########################

vcf = pd.read_csv(r'C:/Users/GenepoweRx_Madhu/Downloads/COVERED_VCF_FILES_BED/KHGLBS649_final.vcf', comment= '#', sep = '\t', header=None, low_memory=False)
vcf.columns = ['CHROM', 'POS', 'rsID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT', 'SAMPLE']

sample_cols = vcf['SAMPLE'].str.split(':', expand=True)
sample_cols.columns = ['GT', 'GQ', 'SDP', 'DP', 'RD', 'AD', 'FREQ', 'PVAL', 'RBQ', 'ABQ', 'RDF', 'RDR', 'ADF', 'ADR']

# Assign the values to the newly created columns
vcf = pd.concat([vcf, sample_cols], axis=1)
vcf = vcf[['CHROM', 'POS', 'rsID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'GT', 'GQ', 'SDP', 'DP', 'RD', 'AD', 'FREQ', 'PVAL','RDF', 'RDR', 'ADF', 'ADR']]

print('Data Loading completed and Depth columns splitted')

######################################### EXTRACTING THE ZYGOSITY FROM THE INFO COLUMN OF THE EACH VARIANT ##############

vcf['HET'] = vcf['INFO'].str.extract(r'HET=(\d)')
vcf['HOM'] = vcf['INFO'].str.extract(r'HOM=(\d)')

# Create a new column 'Zygosity' based on conditions
vcf['Zygosity'] = ''

vcf.loc[vcf['HOM'] == '1', 'Zygosity'] = 'Homozygous'
vcf.loc[vcf['HET'] == '1', 'Zygosity'] = 'Heterozygous'
vcf['GT'] = vcf['GT'].astype(str)

print('Zygosity extraction completed')

######################################## EXTRACTING THE GENEINFO FROM THE INFO COLUMN ####################################

vcf["Gene_Name"] = vcf["INFO"].str.extract('GENEINFO=(?P<GENEINFO>.+?);')
vcf['Gene Name'] = vcf['Gene_Name'].apply(lambda x: ','.join([segment.split(':')[0] for segment in x.split('|')]) if pd.notnull(x) else '')

print('Gene extraction completed')

####################################### SPLITTING AND EXPLODING THE CSQ COLUMN FOR THE REQUIRED PARAMETERS ##############

vcf['CSQ'] = vcf['INFO'].str.extract(r'CSQ=(.*)')
vcf['csq'] = vcf['CSQ'].str.split(',')
vcf = vcf.explode('csq')

print('CSQ splitting completed')

###################################### EXTRACTION OF THE REQUIRED KEY-VALUE PAIRS FROM THE CSQ ##########################

vcf['ClinVar_CLNDN'] = vcf['csq'].str.split('|').str[82]
vcf['CLIN_SIG'] = vcf['csq'].str.split('|').str[70]
vcf['ClinVar_CLNREVSTAT'] = vcf['csq'].str.split('|').str[81]
vcf['ClinVar_CLNSIG'] = vcf['csq'].str.split('|').str[80]
vcf['ClinVar'] = vcf['csq'].str.split('|').str[79]
vcf['HGVSC'] = vcf['csq'].str.split('|').str[10]
vcf['HGVSP'] = vcf['csq'].str.split('|').str[11]
vcf['PolyPhen'] = vcf['csq'].str.split('|').str[38]
vcf['BIOTYPE'] = vcf['csq'].str.split('|').str[7]
vcf['EXON'] = vcf['csq'].str.split('|').str[8]
vcf['INTRON'] = vcf['csq'].str.split('|').str[9]
vcf['Protein_position'] = vcf['csq'].str.split('|').str[14]
vcf['Amino_acids'] = vcf['csq'].str.split('|').str[15]
vcf['Codons'] = vcf['csq'].str.split('|').str[16]
vcf['STRAND'] = vcf['csq'].str.split('|').str[19]
vcf['PUBMED'] = vcf['csq'].str.split('|').str[73]
vcf['Consequence'] = vcf['csq'].str.split('|').str[1]
vcf['IMPACT'] = vcf['csq'].str.split('|').str[2]
vcf['SIFT'] = vcf['csq'].str.split('|').str[37]
vcf['AF'] = vcf['csq'].str.split('|').str[42]
vcf['AFR_AF'] = vcf['csq'].str.split('|').str[43]
vcf['AMR_AF'] = vcf['csq'].str.split('|').str[44]
vcf['EAS_AF'] = vcf['csq'].str.split('|').str[45]
vcf['EUR_AF'] = vcf['csq'].str.split('|').str[46]
vcf['SAS_AF'] = vcf['csq'].str.split('|').str[47]
vcf['gnomADe_AF'] = vcf['csq'].str.split('|').str[48]
vcf['gnomADe_AFR_AF'] = vcf['csq'].str.split('|').str[49]
vcf['gnomADe_AMR_AF'] = vcf['csq'].str.split('|').str[50]
vcf['gnomADe_ASJ_AF'] = vcf['csq'].str.split('|').str[51]
vcf['gnomADe_EAS_AF'] = vcf['csq'].str.split('|').str[52]
vcf['gnomADe_FIN_AF'] = vcf['csq'].str.split('|').str[53]
vcf['gnomADe_NFE_AF'] = vcf['csq'].str.split('|').str[54]
vcf['gnomADe_OTH_AF'] = vcf['csq'].str.split('|').str[55]
vcf['gnomADe_SAS_AF'] = vcf['csq'].str.split('|').str[56]
vcf['gnomADg_AF'] = vcf['csq'].str.split('|').str[57]
vcf['gnomADg_AFR_AF'] = vcf['csq'].str.split('|').str[58]
vcf['gnomADg_AMI_AF'] = vcf['csq'].str.split('|').str[59]
vcf['gnomADg_AMR_AF'] = vcf['csq'].str.split('|').str[60]
vcf['gnomADg_ASJ_AF'] = vcf['csq'].str.split('|').str[61]
vcf['gnomADg_EAS_AF'] = vcf['csq'].str.split('|').str[62]
vcf['gnomADg_FIN_AF'] = vcf['csq'].str.split('|').str[63]
vcf['gnomADg_MID_AF'] = vcf['csq'].str.split('|').str[64]
vcf['gnomADg_NFE_AF'] = vcf['csq'].str.split('|').str[65]
vcf['gnomADg_OTH_AF'] = vcf['csq'].str.split('|').str[66]
vcf['gnomADg_SAS_AF'] = vcf['csq'].str.split('|').str[67]
vcf['MAX_AF'] = vcf['csq'].str.split('|').str[68]
vcf['MAX_AF_POPS'] = vcf['csq'].str.split('|').str[69]

print('Required columns extraction completed')

############################################### Protein Position and Amino Acid Change ##################################

vcf['Protein Position and Amino Acid'] = vcf['Amino_acids'].str[0] + vcf['Protein_position'] + np.where(vcf['Amino_acids'].str[-1] == vcf['Amino_acids'].str[0], '', vcf['Amino_acids'].str[-1])

############################################### HGVSc AND HGVSp TRANSCRIPTS EXTRACTION ###################################

vcf[['HGVSc', 'HGVSc (Transcript)']] = vcf['HGVSC'].str.split(':', 1, expand=True)
vcf[['HGVSp', 'HGVSp (Transcript)']] = vcf['HGVSP'].str.split(':', 1, expand=True)
vcf_final = vcf.copy()

print('Protein_HGVSc_HGVSp_extraction completed')


################################################ REMOVING THE UNNESESSERY CHARACTERS FROM THE COLUMNS ###################

vcf_final = vcf_final.astype(str).applymap(lambda x: x.replace('&', ',').replace('_', ' '))

############################################ CONSEQUENCE SCORES AND IMPACT SCORES MAPPING ###################################

vcf_final['consequence'] = vcf_final['Consequence'].str.split(',').str[0]

df_1 = pd.read_excel(r'C:/Users/GenepoweRx_Madhu/Downloads/Madhu_folder_04_07_2023/kidney_health_final.vcf/consequence.xlsx')

merged_1 = pd.merge(vcf_final, df_1, on='consequence', how='left', sort=False)

df_2 = pd.read_excel(r'C:/Users/GenepoweRx_Madhu/Downloads/Madhu_folder_04_07_2023/kidney_health_final.vcf/IMPACT.xlsx')

merged_2 = pd.merge(merged_1, df_2, on = 'IMPACT', how='left', sort=False)

print('Scores added')


############ Here we can save the merged_2 valriable File for our analytics #################################################
merged_2 ######### save this variable ################################


#merged_2.to_excel(r'C:/Users/GenepoweRx_Madhu/Downloads/Processed_vcf_files/Backup_files/KHCDPRGPTTL116_final.xlsx', index=False)

############################################# CONDITION GENES MAPPING TO THE MAIN VCF ######################################

df_gene = pd.read_excel(r'C:/Users/GenepoweRx_Madhu/Downloads/condition_specific/Condition_specific_all_lit_genes/Final_lit/last_conditions/genes/Conditions_final_genes.xlsx')

merged_2['Gene Match'] = 'No'
merged_2['Matched_Gene'] = ''
    
# Iterate through each gene in vcf['Gene']
for index, genes in merged_2['Gene Name'].iteritems():
    if isinstance(genes, str):
        gene_list = genes.split(',')
        for gene in gene_list:
            if gene in df_gene['Gene Name'].values:
                merged_2.at[index, 'Gene Match'] = 'Yes'
                merged_2.at[index, 'Matched_Gene'] = gene
                break
    
df_gene = df_gene.rename({'Gene Name':'Matched_Gene'}, axis=1)

#merged_2 = merged_2.drop(columns=['Gene Match'], axis=1)

merged_2 = pd.merge(merged_2, df_gene, on= 'Matched_Gene', how = 'left', sort = False)
merged_2['Condition'] = merged_2['Condition'].fillna('No')
merged_2['Headings'] = merged_2['Headings'].fillna('No')
merged_2['21_Conditions_list'] = merged_2['21_Conditions_list'].fillna('No')
merged_2['Gene_Score'] = merged_2['Gene_Score'].fillna('No')

print("Specific Genes Mapped")

df_3 = pd.read_excel(r'C:/Users/GenepoweRx_Madhu/Downloads/condition_specific/Condition_specific_all_lit_genes/Final_lit/last_conditions/new_final_output_concatenated.xlsx')

merged_2['POS'] = merged_2['POS'].astype('int64')
df_3['POS'] = df_3['POS'].astype('int64')

merged_2 = merged_2.rename({'Matched_Gene':'Gene'}, axis=1)

merged_3 = pd.merge(merged_2, df_3, on=['CHROM', 'POS', 'REF', 'ALT'], how='left', sort=False)
merged_3['Literature'] = merged_3['Literature'].fillna('No')

print("Lit Variants Mapped")

merged_3 = merged_3[['Gene Name','Gene', 'Gene_Score', 'Condition', 'Headings', '21_Conditions_list', 'rsID', 'Literature', 'CHROM', 'POS', 'REF', 'ALT', 'Zygosity',
       'Consequence', 'Consequence_score', 'IMPACT', 'IMPACT_score',
       'ClinVar_CLNDN', 'CLIN_SIG', 'ClinVar_CLNREVSTAT','ClinVar_CLNSIG', 'ClinVar', 'HGVSc',
       'HGVSc (Transcript)', 'HGVSp', 'HGVSp (Transcript)', 'GT', 'GQ', 'SDP',
       'DP', 'RD', 'AD', 'FREQ', 'PVAL', 'RDF', 'RDR', 'ADF', 'ADR', 'SIFT',
       'PolyPhen', 'AF', 'AFR_AF', 'AMR_AF', 'EAS_AF', 'EUR_AF', 'SAS_AF',
       'gnomADe_AF', 'gnomADe_AFR_AF', 'gnomADe_AMR_AF', 'gnomADe_ASJ_AF',
       'gnomADe_EAS_AF', 'gnomADe_FIN_AF', 'gnomADe_NFE_AF', 'gnomADe_OTH_AF',
       'gnomADe_SAS_AF', 'gnomADg_AF', 'gnomADg_AFR_AF', 'gnomADg_AMI_AF',
       'gnomADg_AMR_AF', 'gnomADg_ASJ_AF', 'gnomADg_EAS_AF', 'gnomADg_FIN_AF',
       'gnomADg_MID_AF', 'gnomADg_NFE_AF', 'gnomADg_OTH_AF', 'gnomADg_SAS_AF',
       'MAX_AF', 'MAX_AF_POPS', 'BIOTYPE', 'EXON', 'INTRON',
       'Protein Position and Amino Acid', 'Codons', 'STRAND', 'PUBMED']]

print("Exporting to excel")


#merged_2.to_excel(r'C:/Users/GenepoweRx_Madhu/Documents/Processed_vcf_files/Gene_scores_KHAIGHGPTTL265_depth_vcf_processed.xlsx', index=False)

print('VCF processing Completed and Saved as Excel File')

print('Filter portion started')

condition_filter = merged_3[merged_3['21_Conditions_list'] != 'No']

consequence_filter = condition_filter[condition_filter['Consequence_score'].apply(lambda x: eval(x) >= 6/10)]

consequence_filter['DP'] = consequence_filter['DP'].astype('int64')

dp_filter = consequence_filter[consequence_filter['DP'] >= 15]

dp_filter['gnomADe_AF'] = dp_filter['gnomADe_AF'].replace('', '0').astype(float)

gnomADe_AF_filter = dp_filter[dp_filter['gnomADe_AF'] <= 0.6]

gnomADe_AF_filter['gnomADe_SAS_AF'] = gnomADe_AF_filter['gnomADe_SAS_AF'].replace('', '0').astype(float)

gnomADe_SAS_AF_filter = gnomADe_AF_filter[gnomADe_AF_filter['gnomADe_SAS_AF'] <= 0.6]

result_df = gnomADe_SAS_AF_filter.copy()

print('Exon and Intron Filtering started')

#########################################################################################################################

result_df['EXON'].replace('', '0/0', inplace=True)
result_df['INTRON'].replace('', '0/0', inplace=True)

# Custom function to filter rows based on conditions
def filter_rows(group):
    if all(group['EXON'] == '0/0'):
        highest_deno_index = group['INTRON'].str.split('/').str[-1].astype(int).idxmax()
    else:
        highest_deno_index = group['EXON'].str.split('/').str[-1].astype(int).idxmax()
    return group.loc[[highest_deno_index]]

# Grouping by 'rsID' and applying the custom function
result_df = result_df.groupby('rsID').apply(filter_rows)

# Dropping duplicates based on 'rsID'
result_df = result_df.drop_duplicates('rsID')

# Resetting index
result_df.reset_index(drop=True, inplace=True)

                                  
########################################################################################################################

drop_duplicates_filter = result_df.copy()

drop_duplicates_filter = drop_duplicates_filter.set_index(['Gene Name', 'Gene', 'Gene_Score', 'rsID', 'Literature', 'CHROM', 'POS', 'REF',
       'ALT', 'Zygosity', 'Consequence', 'Consequence_score', 'IMPACT',
       'IMPACT_score', 'ClinVar_CLNDN', 'CLIN_SIG', 'ClinVar_CLNREVSTAT','ClinVar_CLNSIG',
       'ClinVar', 'HGVSc', 'HGVSc (Transcript)', 'HGVSp', 'HGVSp (Transcript)',
       'GT', 'GQ', 'SDP', 'DP', 'RD', 'AD', 'FREQ', 'PVAL', 'RDF', 'RDR',
       'ADF', 'ADR', 'SIFT', 'PolyPhen', 'AF', 'AFR_AF', 'AMR_AF', 'EAS_AF',
       'EUR_AF', 'SAS_AF', 'gnomADe_AF', 'gnomADe_AFR_AF', 'gnomADe_AMR_AF',
       'gnomADe_ASJ_AF', 'gnomADe_EAS_AF', 'gnomADe_FIN_AF', 'gnomADe_NFE_AF',
       'gnomADe_OTH_AF', 'gnomADe_SAS_AF', 'gnomADg_AF', 'gnomADg_AFR_AF',
       'gnomADg_AMI_AF', 'gnomADg_AMR_AF', 'gnomADg_ASJ_AF', 'gnomADg_EAS_AF',
       'gnomADg_FIN_AF', 'gnomADg_MID_AF', 'gnomADg_NFE_AF', 'gnomADg_OTH_AF',
       'gnomADg_SAS_AF', 'MAX_AF', 'MAX_AF_POPS', 'BIOTYPE', 'EXON', 'INTRON',
       'Protein Position and Amino Acid', 'Codons', 'STRAND', 'PUBMED']).apply(lambda x: x.str.split('; ').explode()).reset_index()
# Specify the column names to move to the beginning
columns_to_move = ['Condition', 'Headings', '21_Conditions_list']

# Reorder the DataFrame to move specified columns to the beginning
drop_duplicates_filter = drop_duplicates_filter[columns_to_move + [col for col in drop_duplicates_filter.columns if col not in columns_to_move]]

print('filtering completed')
#######################################################################################################################################

# Sample list of condition names
conditions_list = [
    'Diabetes',
    'High_Blood_Pressure',
    'Cardiac_Health',
    'Cholesterol_Disorders',
    'Thyroid_Disorders',
    'Parkinsons',
    'Dementia',
    'Headaches',
    'Allergies',
    'Anemia',
    'Fatty_Liver',
    'Gall_stones',
    'Pancreatic_Disorders',
    'Gut_Health',
    'Gastritis',
    'Glomerular_Diseases',
    'Interstitial_Nephritis',
    'Renal_stones',
    'Skin_Health',
    'Osteoporosis',
    'Arthritis_Degenerative_Joint',
    'Muscular_Dystrophy',
    'Fatigue',
    'Mood_Disorders',
    'Obesity',
    'Seizures',
    'Bone_Joint_health',
    'Muscular_health' 
]

######################################################################################################################

# Create an Excel writer object
excel_writer = pd.ExcelWriter(r'C:/Users/GenepoweRx_Madhu/OneDrive/Documents/Processed_vcf_files/KHGLBS649_final_output.xlsx', engine='xlsxwriter')

# Define a workbook
workbook = excel_writer.book


# Define the green and pink cell formats
green_format = workbook.add_format({'bg_color': '#00FF00'})  # Green color
pink_format = workbook.add_format({'bg_color': '#FF00FF'})   # Pink color

# A flag to keep track of whether at least one group was found
found_at_least_one_group = False

# Iterate through each condition and save it as a separate sheet
for condition in conditions_list:
    group = drop_duplicates_filter[drop_duplicates_filter['21_Conditions_list'] == condition]
    if not group.empty:
        found_at_least_one_group = True
        # Modify the name to make it fit within the Excel sheet name limit (31 characters)
        sheet_name = re.sub(r'[\/:*?"<>|]', '_', condition)[:31]

        # Sort the group first by the "Condition" column and then by the "Literature" column
        group_sorted = group.sort_values(by=['Condition', 'Literature'], ascending=[True, False])

        # Delete the '21_Conditions_list' column
        group_sorted = group_sorted.drop(columns=['21_Conditions_list', 'Gene Name'])

        columns_to_keep = ['Condition', 'Headings', 'Gene', 'Gene_Score', 'Zygosity', 'ClinVar_CLNSIG','Consequence', 'Consequence_score', 'IMPACT', 'IMPACT_score', 'CHROM', 'POS','rsID','Literature', 'REF', 'ALT']

        # Select only the desired columns
        group_sorted = group_sorted[columns_to_keep]

        # Write each group to a separate sheet with the modified sheet name
        group_sorted.to_excel(excel_writer, sheet_name=sheet_name, index=False)

        # Access the worksheet to apply conditional formatting
        worksheet = excel_writer.sheets[sheet_name]

        # Apply conditional formatting based on 'Literature' column values
        for i, value in enumerate(group_sorted['Literature']):
            if value == 'Yes':
                worksheet.write(i + 1, columns_to_keep.index('Literature'), value, green_format)
            elif value == 'No':
                worksheet.write(i + 1, columns_to_keep.index('Literature'), value, pink_format)

# If no groups were found, create a sheet named "Condition not found" and write the message in cell A1
for condition in conditions_list:
    if condition not in excel_writer.sheets:
        # Modify the name to make it fit within the Excel sheet name limit (31 characters)
        sheet_name = re.sub(r'[\/:*?"<>|]', '_', condition)[:31]
        worksheet = excel_writer.book.add_worksheet(sheet_name)
        worksheet.write(0, 0, "Variants not found")


# Save the Excel file
excel_writer.save()

print('Sheets saved: Got the final output')