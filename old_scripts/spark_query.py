from helpers import *
from spark_helpers import *


queries = [
    "USE genepowerx",
    "SELECT COUNT (*) FROM model1 A, model1 B WHERE A.zygosity = B.zygosity",
    "SELECT COUNT(*) FROM model1 WHERE zygosity = 'Homozygous'",
    "SELECT COUNT(*) FROM model1 WHERE gene LIKE 'PADI4' AND zygosity = 'Heterozygous'",
    "SELECT COUNT(*) FROM model1 WHERE gene LIKE 'PADI4'"
]
for query in queries:
    print(query)
    result, timeTaken = runQ(query,sparkQ)
    print("Time for this query was: ", timeTaken*1000, "ms\n")