# ELL Boilerplate

ELL Boilerplate is a Python package that demonstrates a method for prompt A/B testing using the Ell framework. This project provides an approach to compare different prompting strategies and evaluate their effectiveness using cosine similarity metrics.

## Features

- Fetch news articles from an RSS feed
- Summarize news articles using two different prompting strategies
- Evaluate summaries using vector embeddings and cosine similarity
- Store evaluation results in a SQLite database
- Utilities for database initialization and structure analysis

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

## Configuration

- Create a `.env` file based on the `.env.example` and add your API keys and other configuration options.

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

These dependencies are automatically installed when you install the package.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [LICENSE](LICENSE) file in the repository.
