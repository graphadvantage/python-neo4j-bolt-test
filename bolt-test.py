#!pip install neo4j-driver
# note: always consume the BOLT result set to avoid memory overflows eg summary = result.consume()

import time

from neo4j import GraphDatabase, basic_auth, TRUST_ON_FIRST_USE, CypherError

driver = GraphDatabase.driver("bolt://localhost",
                              auth=basic_auth("neo4j", "test"),
                              encrypted=False,
                              trust=TRUST_ON_FIRST_USE)

session = driver.session()

query1 = '''
CALL db.labels();
'''

query2 = '''
CALL db.relationshipTypes();
'''

## full pattern, using explicit transactions (recommended)
try:
    session = driver.session()
    t0 = time.time()

    with session.begin_transaction() as tx:
        result = tx.run(query1)
        tx.success = True;

        for record in result:
            print(record)

        summary = result.consume()
        counters = summary.counters
        print("nodes: " , counters.nodes_created)
        print("rels:" , counters.relationships_created)
        print(round((time.time() - t0)*1000,1), " ms elapsed time")

except Exception as e:
    print('*** Got exception',e)
    if not isinstance(e, CypherError):
        print('*** Rolling back')
        session.rollback()
    else:
        print('*** Not rolling back')

finally:
    session.close()
    print('-----------------')

## short pattern, using implicit transaction (quick and dirty)
session = driver.session()
t0 = time.time()
print("processing...")
result = session.run(query2)

for record in result:
    print(record)

summary = result.consume()
counters = summary.counters
print(summary)
print(counters)
print(round((time.time() - t0)*1000,1), " ms elapsed time")
print('-----------------')
session.close()

## short pattern as a function
def run_bolt_query(q):
    session = driver.session()
    t0 = time.time()
    print("processing..." + q)
    result = session.run(q)
    summary = result.consume()
    counters = summary.counters
    print(summary)
    print(counters)
    print(round((time.time() - t0)*1000,1), " ms elapsed time")
    print('-----------------')
    session.close()

run_bolt_query(query1)
run_bolt_query(query2)
