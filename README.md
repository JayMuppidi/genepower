# GenePowerX: A Genomics Data Processing and API Application

**GenePowerX** is a genomics data processing project that leverages Apache Spark for large-scale analytics and FastAPI for creating a RESTful API. The project is designed to process and analyze patient genomic data, offering two key functionalities: large-scale analytics for research purposes and filtered, report-ready data for medical professionals.

## Project Structure

- **Apache Spark Database**:
  - Contains two tables:
    - **`Semi_processed`**: Stores raw genomic data for large-scale analytics.
    - **`Processed`**: Contains filtered and processed data from `Semi_processed` for generating patient reports.

- **FastAPI Application**:
  - Provides API endpoints to interact with the Spark database.
  - Key functions:
    - **`authenticate`**: Verifies user credentials.
    - **`execute_sql`**: Executes SQL commands on the Spark database.
    - **`patient_semi_processed`**: Retrieves data from the `Semi_processed` table based on a patient's barcode.
    - **`patient_processed`**: Retrieves data from the `Processed` table based on a patient's barcode.
    - **`upload_vcf`**: Handles VCF file uploads for processing.

- **Watcher Script**:
  - Located at `watcher.py`.
  - Monitors a directory for newly uploaded VCF files, processes them, and updates the Spark database.
  - Processes up to four files in parallel.

- **VCF Processing**:
  - Managed by `vcfs_to_csvs.py`.
  - Converts VCF files into CSV format, storing them in the appropriate directories (`semi_processed` and `processed`).

## How It Works

1. **Data Ingestion**:
   - VCF files are uploaded via the FastAPI application.
   - The watcher script detects these files, processes them, and appends the results to the appropriate tables in the Spark database.

2. **Data Processing**:
   - The `vcfs_to_csvs.py` script converts VCF files into CSV files, which are then stored in the `Semi_processed` and `Processed` tables.
   - Custom processing functions can be defined and plugged into the watcher script.

3. **Data Access**:
   - The FastAPI application provides endpoints to retrieve data from the `Semi_processed` and `Processed` tables.
   - SQL queries can also be executed directly on the Spark database through the API.

