#!/usr/bin/env python3
import json
import sys
from typing import Any
import click
import duckdb
from typesafe_sdk import TypeSafeClient, Noul
import os
from dotenv import load_dotenv

load_dotenv()


@click.command()
@click.option(
    "--query",
    required=True,
    help="DuckDB SQL query to execute",
)
@click.option(
    "--question",
    multiple=True,
    required=True,
    help="Binary question to evaluate (can be used multiple times)",
)
@click.option(
    "--db",
    default=":memory:",
    help="Path to DuckDB database file (default: :memory:)",
)
@click.option(
    "--output",
    type=click.File("w"),
    default="-",
    help="Output file for JSON results (default: stdout)",
)
def evaluate(query: str, question: tuple, db: str, output: Any) -> None:
    """
    Evaluate DuckDB query results against binary questions using TypeSafe.

    Example:
        python evaluate_data.py \\
            --query "SELECT * FROM sales WHERE date > '2026-01-01'" \\
            --question "Did we hit revenue target?" \\
            --question "Are there anomalies?"
    """
    try:
        # Initialize TypeSafe client
        api_key = os.getenv("TYPESAFE_API_KEY")
        if not api_key:
            click.echo(
                "Error: TYPESAFE_API_KEY environment variable not set",
                err=True,
            )
            sys.exit(1)

        # Execute DuckDB query
        click.echo(f"Executing query on {db}...", err=True)
        conn = duckdb.connect(db)
        cursor = conn.execute(query)
        result = cursor.fetchall()

        if not result:
            click.echo("Query returned no results", err=True)
            sys.exit(1)

        # Get column descriptions for schema
        schema = {desc[0]: str(desc[1]) for desc in cursor.description}

        # Format results as readable text for TypeSafe
        click.echo(f"Got {len(result)} rows", err=True)

        # Convert results to dict format for better readability
        result_dicts = [dict(zip(schema.keys(), row)) for row in result]
        result_text = json.dumps(result_dicts, indent=2, default=str)

        # Prepare state with query results and schema
        state = {
            "query": query,
            "schema": schema,
            "result_rows": len(result),
            "data": result_text,
        }

        # Create questions for TypeSafe evaluation
        click.echo(f"Evaluating {len(question)} questions with TypeSafe...", err=True)

        question_names = [f"q{i}" for i in range(len(question))]
        questions_map = {
            name: Noul(instructions=q) for name, q in zip(question_names, question)
        }

        # Call TypeSafe API
        with TypeSafeClient(api_key=api_key) as client:
            response = client.system_one(state=state, questions=questions_map)

        # Build results
        results = {
            "query": query,
            "total_rows": len(result),
            "evaluations": [],
        }

        # Process each answer
        for name, q_text in zip(question_names, question):
            probability_yes = response.nouls[name].noul
            evaluation = {
                "question": q_text,
                "answer": "yes" if probability_yes >= 0.5 else "no",
                "probability_yes": probability_yes,
                "probability_no": 1 - probability_yes,
                "confidence": abs(probability_yes - 0.5) * 2,
            }
            results["evaluations"].append(evaluation)

        # Output JSON results
        json.dump(results, output, indent=2)
        output.write("\n")
        click.echo("Evaluation complete", err=True)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    evaluate()
