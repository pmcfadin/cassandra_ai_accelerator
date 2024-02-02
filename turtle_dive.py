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
    
def create_prompt(schema_statements):

    with open("helper_docs/prompt_question.txt", 'r') as f:
        question = f.read()

    prompt = f"Given the schema: \n{' '.join(schema_statements)}\n\nAnswer the following questions:\n\n{question}"

    logging.info(f"Prompt created: {prompt}")
    return prompt

def ask_gpt_about_schema(prompt, config):
    client = OpenAI()
    
    logging.info("Asking OpenAI about the schema")

    response = client.chat.completions.create(
        model=config['openai_model'],
        messages=[
            {"role": "system", "content": config['model_system_role']},
            {"role": "user", "content": prompt},
        ]   
    )
    logging.info(f"Received response from OpenAI:")

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

    # Set the OpenAI API key
    os.environ['OPENAI_API_KEY'] = config['openai_api_key']

    # Connect to the Astra database
    session = cassandra_utils.connect_to_astra(config)

    logging.info(f"Generating CREATE TABLE statements for keyspace: {config['keyspace']}")
    statements = cassandra_utils.generate_create_table_statements(session, config)

    logging.info(f"Generated {len(statements)} CREATE TABLE statements")

    prompt = create_prompt(statements)

    response = ask_gpt_about_schema(prompt, config)

    create_report(response, config['keyspace'])

if __name__ == "__main__":
    main()

