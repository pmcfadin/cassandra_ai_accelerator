from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import os
from openai import OpenAI
import yaml
import logging
import logging
import os
import datetime

#initalize logging
def initialize_logging(log_level="INFO"):
    # Create the log directory if it doesn't exist
    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)

    # Set up the logging configuration
    log_file = os.path.join(log_dir, f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
    logging.basicConfig(filename=log_file, level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # Log a message to indicate that logging has been initialized
    logging.info("Logging initialized")


# Function to fetch and generate CREATE TABLE statements
def generate_create_table_statements(session, keyspace):
    create_table_statements = []
    
    tables = session.execute(f"SELECT * FROM system_schema.tables WHERE keyspace_name = '{keyspace}'")
    
    for table in tables:
        table_name = table.table_name
        create_stmt = f"CREATE TABLE {keyspace}.{table_name} ("
        
        columns = session.execute(f"SELECT * FROM system_schema.columns WHERE keyspace_name = '{keyspace}' AND table_name = '{table_name}'")
        pk = []
        ck = []
        for column in columns:
            create_stmt += f"\n  {column.column_name} {column.type},"
            if column.kind == 'partition_key':
                pk.append(column.column_name)
            elif column.kind == 'clustering':
                ck.append(column.column_name)
        
        if pk:
            create_stmt += f"\n  PRIMARY KEY ({'(' + ', '.join(pk) + ')' if len(pk) > 1 else pk[0]}"
            if ck:
                create_stmt += f", {' '.join(ck)}"
            create_stmt += ")"
        
        create_stmt += "\n);"
        create_table_statements.append(create_stmt)
    
    return create_table_statements

def ask_gpt_about_schema(schema_statements, question):
    client = OpenAI()


    with open("helper_docs/cassandra_vector.txt", 'r') as f:
        helper_text = f.read()

    print(helper_text)
    question += helper_text

    print(f"\n\nPrompting GPT-4 with the following question: {question}")

    # Combine schema statements into a single prompt
    prompt = f"Given the schema: \n{' '.join(schema_statements)}\n\n{question}"
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are an Apache Cassandra expert at data modeling and Generative AI strategy."},
            {"role": "user", "content": prompt},
        ]   
    )
  
    response_content = response.choices[0].message.content
    #print(response['choices'][0]['message']['content'])
    # Write the response content to a file
    with open('response.md', 'w') as f:
        f.write(response_content)


def load_config():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config

def main():
    # Call the initialize_logging function to set up the logging mechanism
    initialize_logging("INFO")

    # Load the configuration from config.yaml
    config = load_config()

    # Set the environment variables
    client_id = config['client_id']
    client_secret = config['client_secret']
    secure_connect_bundle_path = config['secure_connect_bundle_path']
    keyspace = config['keyspace']
    openai_api_key = config['openai_api_key']

    # Set the OpenAI API key
    os.environ['OPENAI_API_KEY'] = openai_api_key

    # Configure the connection
    auth_provider = PlainTextAuthProvider(client_id, client_secret)
    cloud_config= {
            'secure_connect_bundle': secure_connect_bundle_path
    }

    # Establish the connection
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()

    try:
        print(f"Generating CREATE TABLE statements for keyspace: {keyspace}")
        statements = generate_create_table_statements(session, keyspace)

        print(f"Generated {len(statements)} CREATE TABLE statements")
        print(f"\n\n{statements}")

        question = "Evaluate this Cassandra Query Language (CQL) schema. Categorize the use case or use cases. Provide a synopsis of what type of application this schema supports. What type of generative AI features could be added to this data model? Include the use of Cassandra Vector Data support. Suggest data model changes for each Generative AI suggestion with suggested queries using this guide: "
        ask_gpt_about_schema(statements, question)

    finally:
        cluster.shutdown()

if __name__ == "__main__":
    main()

