# ELL A/B test script

This project is a proof of concept for A/B testing prompts with the help of the amazing Ell package. The sample it contains uses 2 different prompts and models for summarizing a news article. It then uses coseine similarity and additional llm calls to evaluate the quality of the summary. 
It finally stores these evaluations in the same database as the invocations, in order to incrementally create the best possible prompt. 
For an in depth explanation see my [blog post](https://janwillemaltink.eu/blog/blogartikelen/agentframeworks-deel-2-hoe-je-het-ell-framework-kunt-gebruiken-voor-het-ab-testen-van-prompts)

## Features

- Fetch news articles from an RSS feed
- Summarize news articles using two different prompting strategies
- Evaluate summaries using vector embeddings and cosine similarity
- Evaluate summaries using other LLM calls
- Store evaluation results in a SQLite database
- Utilities for database initialization and structure analysis
- Create report on stored evaluations

## Installation

To install ELL Boilerplate as a package, follow these steps:

1. Clone the repository:

   ```
   git clone https://github.com/your-username/ell-boilerplate.git
   cd ell-boilerplate
   ```

2. Install the package:
   ```
   pip install -e .
   ```

## Usage

After installation, follow these steps to set up and run the project:

1. First, check the current database structure:

   ```
   ell_dbstructure
   ```

   This will generate a Markdown file describing the current database structure.

2. Initialize the evaluation table in the SQLite database:

   ```
   ell_initialize_db
   ```

   This step is crucial and must be done before running the main script.

3. Verify that the "evaluation" table has been created:

   ```
   ell_dbstructure
   ```

   Check the output to confirm that the new "evaluation" table is now present.

4. Run the main script to fetch news, generate summaries, and evaluate them:
   ```
   ell_boilerplate
   ```

You can run `ell_dbstructure` at any time to check the current state of the database structure.

5. Run the evaluation utility to create a markdown summary of the score of each of the tested prompts.
   ```
   ell_eval
   ```

## Configuration

- Create a `.env` file based on the `.env.example` and add your API keys and other configuration options. Note that ell relies on these environment variables so make sure they are set before using ell functionality, including ell studio and autocommit.

## Project Structure

```
ell-boilerplate/
├── src/
│   └── ell_boilerplate/
│       ├── main.py
│       └── utils/
│           ├── datastructure.py
│           └── evaluations_table.py
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml
```

## Dependencies

This project relies on several Python libraries, including:

- ell-ai
- anthropic
- pydantic
- openai
- feedparser
- voyageai
- scikit-learn
- numpy
- matplotlib

These dependencies are automatically installed when you install the package.
