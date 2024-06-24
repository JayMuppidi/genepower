from pyspark.sql import SparkSession# to interact with db

spark = SparkSession.builder \
    .appName("Connect to Database") \
    .config("spark.sql.catalogImplementation",) \
    .config("spark.driver.memory", "25g") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sql("CREATE DATABASE IF NOT EXISTS genepowerx")
spark.sql("USE genepowerx")


def sparkQ(query):
    result = spark.sql(query)
    result.show()
    return result.toPandas()
def stop():
    spark.stop()