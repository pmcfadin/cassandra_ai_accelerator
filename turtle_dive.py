import os
from openai import OpenAI
import yaml
from loguru import logger
import os
import datetime
from conf.config import settings
from cassandra_utils import CassandraUtils

#initalize logging
def initialize_logging(log_level="INFO"):
    logger.remove()
    
    # Create the log directory if it doesn't exist
    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)

    logger.add(f"{log_dir}/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log", level=log_level)

    # Set up the logging configuration
    #log_file = os.path.join(log_dir, f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
    #logging.basicConfig(filename=log_file, level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # Log a message to indicate that logging has been initialized
    logger.info("Logging initialized")

def create_report(response, keyspace):
    # Create a report name with keyspace name and current date and time
    report_name = f"report_output/genai-usecases-{keyspace}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"

    response_content = response.choices[0].message.content
    
    # Create a report from the response
    with open(report_name, 'w') as f:
        f.write(response_content)

    # Log details about the report
    logger.info(f"Report created: {report_name}")


    # Log details of model usage
    usage = response.usage
    logger.info(f"Model usage - Prompt tokens: {usage.prompt_tokens}, Completion tokens: {usage.completion_tokens}, Total tokens: {usage.total_tokens}")
    
def create_prompt(schema_statements):

    with open("helper_docs/prompt_question.txt", 'r') as f:
        question = f.read()

    prompt = f"Given the schema: \n{' '.join(schema_statements)}\n\nAnswer the following questions:\n\n{question}"

    logger.info(f"Prompt created: {prompt}")
    return prompt

def ask_gpt_about_schema(prompt):
    client = OpenAI()
    
    logger.info("Asking OpenAI about the schema")

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": settings.model_system_role},
            {"role": "user", "content": prompt},
        ]   
    )
    logger.info(f"Received response from OpenAI:")

    return response

def main():
    # Call the initialize_logging function to set up the logging mechanism
    initialize_logging(settings.log_level)

    # Set the OpenAI API key
    os.environ['OPENAI_API_KEY'] = settings.openai_api_key

    # Connect to the Astra database
    cassandra_utils = CassandraUtils()

    logger.info(f"Generating CREATE TABLE statements for keyspace: {settings.keyspace}")
    statements = cassandra_utils.generate_create_table_statements()

    logger.info(f"Generated {len(statements)} CREATE TABLE statements")

    prompt = create_prompt(statements)

    response = ask_gpt_about_schema(prompt)

    create_report(response, settings.keyspace)

if __name__ == "__main__":
    main()
