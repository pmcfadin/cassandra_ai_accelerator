import cassandra_utils
import os
from openai import OpenAI
import yaml
import logging
import os
import datetime
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

def create_report(response, keyspace):
    # Create a report name with keyspace name and current date and time
    report_name = f"report_output/genai-usecases-{keyspace}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"

    response_content = response.choices[0].message.content
    
    # Create a report from the response
    with open(report_name, 'w') as f:
        f.write(response_content)

    # Log details about the report
    logging.info(f"Report created: {report_name}")


    # Log details of model usage
    usage = response.usage
    logging.info(f"Model usage - Prompt tokens: {usage.prompt_tokens}, Completion tokens: {usage.completion_tokens}, Total tokens: {usage.total_tokens}")
    

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
  
    return response


def load_config():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config

def main():
    # Call the initialize_logging function to set up the logging mechanism
    initialize_logging("INFO")

    # Load the configuration from config.yaml
    config = load_config()
    config["logging"] = logging

    # Set the environment variables

    openai_api_key = config['openai_api_key']

    # Set the OpenAI API key
    os.environ['OPENAI_API_KEY'] = openai_api_key


    # Connect to the Astra database
    session = cassandra_utils.connect_to_astra(config)

    logging.info(f"Generating CREATE TABLE statements for keyspace: {config['keyspace']}")
    statements = cassandra_utils.generate_create_table_statements(session, config)

    logging.info(f"Generated {len(statements)} CREATE TABLE statements")
    logging.info(f"\n\n{statements}")

    question = "Evaluate this Cassandra Query Language (CQL) schema. Categorize the use case or use cases. Provide a synopsis of what type of application this schema supports. What type of generative AI features could be added to this data model? Include the use of Cassandra Vector Data support. Suggest data model changes for each Generative AI suggestion with suggested queries using this guide: "
    response = ask_gpt_about_schema(statements, question)

    create_report(response, config['keyspace'])

if __name__ == "__main__":
    main()

