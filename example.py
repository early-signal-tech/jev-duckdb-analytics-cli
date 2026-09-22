#!/usr/bin/env python3
"""
Example script showing how to use the data evaluator.
This creates sample data and demonstrates the evaluation.
"""

import duckdb
import json
import subprocess
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def setup_sample_data(db_path: str = "sample.duckdb") -> None:
    """Create a sample DuckDB database with test data."""
    print(f"Creating sample database at {db_path}...")

    conn = duckdb.connect(db_path)

    # Create sales table (drop if exists to allow re-running)
    conn.execute("DROP TABLE IF EXISTS sales;")

    conn.execute("""
        CREATE TABLE sales AS
        SELECT
            date::DATE as date,
            region::VARCHAR as region,
            revenue::DECIMAL(10,2) as revenue,
            units::INTEGER as units,
            profit::DECIMAL(10,2) as profit
        FROM (
            SELECT '2026-01-01' as date, 'North' as region, 5000.00 as revenue, 100 as units, 1000.00 as profit
            UNION ALL
            SELECT '2026-01-02', 'North', 5500.00, 110, 1100.00
            UNION ALL
            SELECT '2026-01-03', 'North', 4800.00, 95, 900.00
            UNION ALL
            SELECT '2026-01-01', 'South', 4200.00, 85, 800.00
            UNION ALL
            SELECT '2026-01-02', 'South', 4500.00, 92, 900.00
            UNION ALL
            SELECT '2026-01-03', 'South', 5200.00, 105, 1050.00
            UNION ALL
            SELECT '2026-01-01', 'East', 6000.00, 120, 1200.00
            UNION ALL
            SELECT '2026-01-02', 'East', 6500.00, 130, 1300.00
            UNION ALL
            SELECT '2026-01-03', 'East', 6200.00, 125, 1240.00
        );
    """)

    # Verify data was created
    result = conn.execute("SELECT COUNT(*) as count FROM sales;").fetchone()
    print(f"✓ Created sales table with {result[0]} rows")

    # Show sample data
    print("\nSample data:")
    sample = conn.execute(
        "SELECT * FROM sales LIMIT 3;"
    ).fetchall()
    for row in sample:
        print(f"  {row}")

    conn.close()


def run_evaluation(db_path: str = "sample.duckdb") -> None:
    """Run the data evaluator with sample queries."""

    if not os.getenv("TYPESAFE_API_KEY"):
        print("\n⚠️  TYPESAFE_API_KEY not set!")
        print("Set it with: export TYPESAFE_API_KEY='your-key-here'")
        print("Get your key from: https://typesafe.ai")
        return

    print(f"\n{'='*60}")
    print("Running Data Evaluations")
    print(f"{'='*60}\n")

    # Example 1: Overall revenue trends
    print("Example 1: Evaluating overall revenue trends")
    print("-" * 60)

    cmd = [
        "uv",
        "run",
        "evaluate_data.py",
        "--db",
        db_path,
        "--query",
        "SELECT * FROM sales WHERE date = '2026-01-03';",
        "--question",
        "Did revenue increase from 2026-01-01 to 2026-01-03?",
        "--question",
        "Are all regions profitable?",
    ]

    print(f"Running: {' '.join(cmd)}\n")
    env = os.environ.copy()
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    if result.returncode == 0:
        output = json.loads(result.stdout)
        print(json.dumps(output, indent=2))
    else:
        print(f"Error: {result.stderr}")

    # Example 2: Region analysis
    print("\n" + "=" * 60)
    print("Example 2: Evaluating regional performance")
    print("-" * 60)

    cmd = [
        "uv",
        "run",
        "evaluate_data.py",
        "--db",
        db_path,
        "--query",
        "SELECT region, AVG(revenue) as avg_revenue, AVG(profit) as avg_profit FROM sales GROUP BY region;",
        "--question",
        "Is the East region outperforming other regions?",
        "--question",
        "Are profit margins consistent across regions?",
    ]

    print(f"Running: {' '.join(cmd)}\n")
    env = os.environ.copy()
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    if result.returncode == 0:
        output = json.loads(result.stdout)
        print(json.dumps(output, indent=2))
    else:
        print(f"Error: {result.stderr}")


if __name__ == "__main__":
    import sys

    # Create sample database
    db_path = "sample.duckdb"
    setup_sample_data(db_path)

    # Run evaluations
    run_evaluation(db_path)

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print(
        "\nTo use with your own data:\n"
        "  python evaluate_data.py --db your-database.duckdb \\\n"
        "    --query 'SELECT ...' \\\n"
        "    --question 'Your question here?' \\\n"
        "    --question 'Another question?'\n"
    )
