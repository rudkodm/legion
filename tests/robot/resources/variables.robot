*** Variables ***
@{SUBDOMAINS}                       jenkins  nexus
@{ENCLAVE_SUBDOMAINS}               edi  edge  airflow  flower
@{TEST_DAGS}                        example_python_work  s3_connection_test
${MODEL_WITH_PROPS}                 Test-Summation
${MODEL_WITH_PROPS_ENDPOINT}        sum_and_pow
${MODEL_WITH_PROPS_PROP}            number.pow_of_ten
${TEST_MODEL_ID}                    demo-abc-model
${TEST_MODEL_1_VERSION}             1.0
${TEST_MODEL_2_VERSION}             1.1
# TODO: Two next lines should be removed when closing LEGION #499, #313, #316
${SERVICE_ACCOUNT}                  admin
${SERVICE_PASSWORD}                 admin