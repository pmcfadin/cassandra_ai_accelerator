# Astra Turtle
![Turtles all the way down image](image.png)
Using GenAI to make more GenAI. Turtles all the way down...

This project is a Python application that interacts with  DataStax Astra to generate CREATE TABLE statements for a given keyspace and uses them to create recomedended use cases for Generative AI.

The output is a Markdown formatted report you can find in `report_output` It will describe the use case(s) for your schema and suggest any GenAI use cases you could add. It will then give you the exact table changes needed to implement the idea you want!

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.6 or higher
- pip
- A DataStax Astra instance
- An OpenAI API key

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/your-repo-name.git
    ```
2. Navigate to the project directory:
    ```sh
    cd your-repo-name
    ```
3. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

### Configuration

Before running the application, you need to set up your configuration in the `example-config.yaml` file:

- `client_id`: Your Astra DB client ID.
- `client_secret`: Your Astra DB client secret.
- `secure_connect_bundle_path`: The path to your Astra DB secure connect bundle.
- `keyspace`: The keyspace to generate CREATE TABLE statements for.
- `logging`: The logging level.
- `openai_api_key`: Single use key from OpenAI
- `openai_model`: GPT model. Default included 
- `model_system_role`: Role info to model. Default is probably fine

### Usage

To run the application, execute the `turtle_dive.py` script:

```sh
python turtle_dive.py# astra_turtle

