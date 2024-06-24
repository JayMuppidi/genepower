from helpers import *
from genepowerx.postgres.postgres_helpers import *
queries = [
    "SELECT COUNT(*) FROM model1 AS m1, model1 AS m2 WHERE m1.\"Zygosity\" = m2.\"Zygosity\"",
    "SELECT COUNT(*) FROM model1 WHERE \"Zygosity\" = 'Homozygous'",
    "SELECT COUNT(*) FROM model1 WHERE \"Zygosity\" = 'Heterozygous' AND \"Gene\" LIKE 'PADI4'",
    "SELECT COUNT(*) FROM model1 WHERE \"Gene\" LIKE 'PADI4'",
]
for query in queries:
    print(query)
    result, timeTaken = runQ(query,postgresQ)
    print(result)
    print("Time for this query was: ", timeTaken*1000, "ms")