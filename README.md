# DuckDB Data Evaluator

A CLI tool that evaluates DuckDB query results against binary questions using TypeSafe's AI-powered judgments.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Set your TypeSafe API key (in `.env` or exported):
```bash
export TYPESAFE_API_KEY="your-api-key-here"
```

## Usage

### Basic Example

Evaluate if revenue targets were hit:

```bash
uv run evaluate_data.py \
  --query "SELECT * FROM sales WHERE date > '2026-01-01'" \
  --question "Did we hit revenue target?" \
  --question "Are there anomalies in the data?"
```

### Command Options

- `--query` (required): DuckDB SQL query to execute
- `--question` (required, repeatable): Binary questions to evaluate. Use multiple times for multiple questions.
- `--db` (optional): Path to DuckDB database file. Default: `:memory:` (in-memory database)
- `--output` (optional): Output file for JSON results. Default: stdout

### With Local Database

```bash
uv run evaluate_data.py \
  --db "/path/to/your/database.duckdb" \
  --query "SELECT product, revenue, profit FROM monthly_sales" \
  --question "Did profit increase month-over-month?" \
  --question "Are any products underperforming?"
```

### Output Format

The CLI returns JSON with confidence scores and probabilities:

```json
{
  "query": "SELECT * FROM sales WHERE date > '2026-01-01'",
  "total_rows": 150,
  "evaluations": [
    {
      "question": "Did we hit revenue target?",
      "answer": "yes",
      "confidence": 0.92,
      "probability_yes": 0.95,
      "probability_no": 0.05
    },
    {
      "question": "Are there anomalies in the data?",
      "answer": "no",
      "confidence": 0.87,
      "probability_yes": 0.10,
      "probability_no": 0.90
    }
  ]
}
```

## Chain Evaluation

For evaluating LLM chain outputs and multi-step reasoning, see `chain_evaluation.py`:

```bash
uv run chain_evaluation.py
```

This module provides examples of evaluating Jev-based chains with configurable metrics and test scenarios.

## Architecture

1. **Query Execution**: Runs the DuckDB query and extracts results
2. **Schema Extraction**: Captures column names and types
3. **TypeSafe Evaluation**: Uses TypeSafe's `Noul` primitive (binary yes/no judgments) to evaluate each question
4. **Results**: Returns structured JSON with answers and confidence probabilities

## TypeSafe Integration

The tool uses TypeSafe's System One model (Jev) to evaluate whether specific conditions are present in the data. Each question is treated as an independent binary judgment with:

- `answer`: "yes" or "no"
- `confidence`: How certain the model is (0.0 - 1.0)
- `probability_yes`: Probability the answer is yes
- `probability_no`: Probability the answer is no

## Error Handling

- Missing TypeSafe API key: Error message and exit
- Empty query results: Error message and exit
- Invalid DuckDB query: Error message and exit
- API errors: Error message and exit

## Example Workflow

```bash
# Create a sample database and table
duckdb :memory: << EOF
CREATE TABLE sales AS
SELECT 
  date::DATE as date,
  revenue::DECIMAL(10,2) as revenue,
  units::INTEGER as units
FROM (
  SELECT '2026-01-01' as date, 5000 as revenue, 100 as units
  UNION ALL
  SELECT '2026-01-02', 5500, 110
  UNION ALL
  SELECT '2026-01-03', 4800, 95
);
EOF

# Run evaluation
uv run evaluate_data.py \
  --query "SELECT * FROM sales" \
  --question "Is revenue trending upward?" \
  --question "Are sales volumes consistent?"
```
