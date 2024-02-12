# Astra Turtle
![Turtles all the way down image](image.png)
Using GenAI to make more GenAI. Turtles all the way down...

This project is a Python application that interacts with  DataStax Astra to generate CREATE TABLE statements for a given keyspace and uses them to create recommended use cases for Generative AI.

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

- `mode`: Operating mode. ASTRA is the only current choice
- `log_level`: The logging level. Default is 
- `model_system_role`: Role info to model. The default is probably fine
- `openai_model`: GPT model. Default included

For sensative data, rename the `example.settings.toml` file into `.settings.toml` and change the following
- `client_id`: Your Astra DB client ID.
- `client_secret`: Your Astra DB client secret.
- `secure_connect_bundle_path`: The path to your Astra DB secure connect bundle.
- `keyspace`: The keyspace to generate CREATE TABLE statements for.
- `openai_api_key`: Single use key from OpenAI

### Usage

To run the application, execute the `turtle_dive.py` script:

```sh
python turtle_dive.py
```

### Todo List
 - Allow for Local LLM usage. Privacy concerns
 - Fine-tune an LLM for this specific task (Better answers)
 - Make the use case exploration interactive for more specific use cases
 - Allow for either Astra or Cassandra targets (Shouldn't be hard. Just change the connect type)
 - Add more types of reports. SAI conversion. Schema optimization
 - Analyze data and suggest how data could be vectorized
 - (Stretch) Create sample code for LangChain or LlamaIndex or ...
---
### Sample report output

# Evaluation of the CQL schema and Generative AI Opportunities

## CQL Schema Overview

The provided schema supports a video sharing and social interaction platform named "KillrVideo." This platform allows users to upload videos, comment on videos, rate videos, and receive video recommendations. The schema accommodates user management, video metadata storage, tagging, playback statistics, and user interaction (comments, ratings) with videos.

### Use Cases

1. Video Content Management: Users can upload videos with descriptions, tags, and preview images.
2. Social Engagement: Users can comment on videos, rate them, and receive recommendations.
3. Analytics: The platform tracks video views and ratings for analytical purposes.
4. Personalization: Users receive recommendations based on their interactions.
5. Community Features: Videos and comments can be tagged for easier discovery.

### Application Synopsis

The application facilitated by this schema seems to be a comprehensive video-sharing platform with a strong emphasis on community engagement and content discoverability.

## Generative AI Features and Data Model Enhancements

### 1. Video Content Summarization

Generative AI can automatically generate summaries for videos based on the video description, comments, and tags.

**Data Model Changes:**

- Alter the `videos` table to include a `summary` text column.
  ```sql
  ALTER TABLE killrvideo.videos ADD summary text;
  ```
- For storing and searching through summaries by similarity, create a new table with vector support for the summary text.
  ```sql
  CREATE TABLE killrvideo.video_summaries_vs (
    videoid uuid,
    summary text,
    summary_vector VECTOR<FLOAT, 128>,  -- Assuming a 128-dimensional embedding
    PRIMARY KEY (videoid)
  )
  WITH CLUSTERING ORDER BY (videoid ASC);
  ```

### 2. Advanced Video Recommendations

Improve recommendation systems by incorporating vector-based similarity search on user preferences, video descriptions, and user interactions.

**Data Model Changes:**

- Incorporate vector columns in relevant tables such as `video_recommendations` or create a new dedicated table for vector-based recommendations.
  ```sql
  ALTER TABLE killrvideo.video_recommendations ADD recommendation_vector VECTOR<FLOAT, 128>;
  ```
  or, for a dedicated approach,
  ```sql
  CREATE TABLE killrvideo.video_recommendations_vs (
    userid uuid,
    videoid uuid,
    recommendation_vector VECTOR<FLOAT, 128>,
    PRIMARY KEY (userid, videoid)
  )
  WITH CLUSTERING ORDER BY (userid ASC);
  ```

### 3. Comment Sentiment Analysis

By analyzing the sentiment of the comments, the platform can better understand user engagement and filter or highlight comments based on positivity.

**Data Model Changes:**

- Add a `sentiment_score` column to the `comments_by_video` and `comments_by_user` tables.
  ```sql
  ALTER TABLE killrvideo.comments_by_video ADD sentiment_score float;
  ALTER TABLE killrvideo.comments_by_user ADD sentiment_score float;
  ```
- Create a vector table for sentiment analysis on comments.
  ```sql
  CREATE TABLE killrvideo.comments_sentiment_vs (
    commentid timeuuid,
    comment text,
    sentiment_vector VECTOR<FLOAT, 5>,  -- Example dimension for sentiment
    PRIMARY KEY (commentid)
  );
  ```

### 4. Tag Generation for Videos

Automatically generate and suggest tags for new videos based on video descriptions and names using Natural Language Processing (NLP).

**Data Model Changes:**

- Implementing AI to suggest tags doesn't require changes to the existing schema but integrating an AI model to process video uploads and updating the `tags` set in the `videos` table accordingly.

### Vector Search Integration

To support AI-driven features like summarization, recommendation, sentiment analysis, and tag generation, vector search capabilities have been introduced into the data model. These capabilities enable similarity-based operations, leveraging the semantic understanding of content.

**Example Usage with Generative AI:**

1. **Recommendation Enhancements:**
   - After generating embeddings for video content and user preferences, use vector search to find the closest matches for personalized recommendations.

2. **Sentiment Analysis on Comments:**
   - Use vector search to find comments with similar sentiments, enabling features like filtering comments by positivity or negativity.

### Conclusion

Enhancing the KillrVideo schema with Generative AI and vector search capabilities can significantly improve user experience through personalized content, better engagement through sentiment analysis, and efficient management of content through summarization and tagging. The vector search functionality in Cassandra adds a powerful tool for leveraging semantic similarities within the data, paving the way for advanced AI-driven features in applications.
