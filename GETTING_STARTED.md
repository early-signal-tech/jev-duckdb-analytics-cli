# Getting Started with DuckDB Data Evaluator

This guide walks you through setting up and using the data evaluator CLI.

## Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/)
- A TypeSafe API key (free at https://typesafe.ai)

## Step 1: Install Dependencies

```bash
uv sync
```

## Step 2: Set Up Your TypeSafe API Key

Create a `.env` file in this directory (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your TypeSafe API key:

```
TYPESAFE_API_KEY=your-actual-api-key-here
```

## Step 3: Try the Examples

Run the example script to see the tool in action:

```bash
uv run example.py
```

This will:
1. Create a sample DuckDB database with sales data
2. Run two example evaluations
3. Show you the JSON output format

Expected output (showing evaluation results with confidence scores).

## Step 4: Use with Your Own Data

### Option A: Query an Existing Database

```bash
uv run evaluate_data.py \
  --db "/path/to/your/database.duckdb" \
  --query "SELECT * FROM your_table WHERE conditions" \
  --question "Is condition X true in the data?" \
  --question "Does pattern Y exist?"
```

### Option B: Use an In-Memory Database

```bash
uv run evaluate_data.py \
  --query "SELECT 1 as id, 'test' as value" \
  --question "Does the data contain expected fields?"
```

## Understanding the Output

Each evaluation returns:

```json
{
  "query": "your SQL query",
  "total_rows": 100,
  "evaluations": [
    {
      "question": "Is revenue trending upward?",
      "answer": "yes",
      "confidence": 0.92,
      "probability_yes": 0.95,
      "probability_no": 0.05
    }
  ]
}
```

- **answer**: The model's judgment ("yes" or "no")
- **confidence**: How certain the model is (0-1, higher is more confident)
- **probability_yes**: Probability the answer is yes (0-1)
- **probability_no**: Probability the answer is no (0-1)

## Tips

1. **Multiple Questions**: You can ask multiple independent questions in one evaluation:
   ```bash
   uv run evaluate_data.py \
     --query "SELECT * FROM sales" \
     --question "Question 1?" \
     --question "Question 2?" \
     --question "Question 3?"
   ```

2. **Be Specific**: The better your question and the more relevant your query results, the better the evaluation.

3. **Check Confidence**: Look at the confidence scores. Higher confidence means the model is more certain about its answer.

4. **Parse Output**: The JSON output is easy to parse in scripts:
   ```bash
   uv run evaluate_data.py ... | jq '.evaluations[0].answer'
   ```

## Troubleshooting

**Error: TYPESAFE_API_KEY environment variable not set**
- Make sure you have a `.env` file with your API key
- Or set it in your shell: `export TYPESAFE_API_KEY=your-key`

**Error: Query returned no results**
- Your query didn't return any rows
- Check your WHERE clause and table names

**Error: Invalid DuckDB query**
- Check your SQL syntax
- Use valid DuckDB SQL

## Next Steps

- Try different types of questions on your data
- Integrate the JSON output into your monitoring/alerting systems
- Use confidence scores to set thresholds for actions

## Resources

- [TypeSafe Documentation](https://docs.typesafe.ai)
- [DuckDB Documentation](https://duckdb.org/docs)
- [Click CLI Framework](https://click.palletsprojects.com)
