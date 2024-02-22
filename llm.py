from litellm import completion
import os
from conf.config import settings
from loguru import logger
from openai import OpenAI

def get_completeion(prompt):

    logger.info(f"Getting completion from LLM provider: {settings.llm_provider}")

    if settings.llm_provider == "OPENAI":
        response = _openai_completion(prompt)
    elif settings.llm_provider == "BEDROCK":
        response = _bedrock_completion(prompt)
    elif settings.llm_provider == "VERTEXAI":
        response = _vertexai_completion(prompt)
    elif settings.llm_provider == "OLLAMA":
        response = _ollama_compleation(prompt)
    elif settings.llm_provider == "AZUREGPT":
        response = _azuregpt_completion(prompt)
    else:
        response = None
        logger.error(f"LLM provider {settings.llm_provider} is not supported")

    return response

def _openai_completion(prompt):
    # Set the OpenAI API key
    os.environ['OPENAI_API_KEY'] = settings.openai_api_key

    client = OpenAI()
    
    logger.info("Asking OpenAI about the schema")

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": settings.openai_model_system_role},
            {"role": "user", "content": prompt},
        ]   
    )
    logger.info(f"Received response from OpenAI:")

    return response

def _bedrock_completion(prompt):
    os.environ["AWS_ACCESS_KEY_ID"] = settings.aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = settings.aws_secret_access_key
    os.environ["AWS_REGION_NAME"] = settings.aws_region_name

    response = completion(
        model=settings.aws_bedrock_model_name,
        max_tokens=settings.aws_bedrock_max_tokens,
        temperature=settings.aws_bedrock_temperature,
        messages=[
            {"role": "system", "content": settings.openai_model_system_role},
            {"role": "user", "content": prompt},
        ]
    )

    return response

def _vertexai_completion(prompt):
    pass

def _ollama_compleation(prompt):
    pass

def _azuregpt_completion(prompt):
    pass
