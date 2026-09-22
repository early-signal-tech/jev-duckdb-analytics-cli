#!/usr/bin/env python3
"""
Example of chaining JEV probability decisions.
Each question's result influences which question gets asked next.
"""

import json
import os
from typing import Any
import duckdb
from typesafe_sdk import TypeSafeClient, Noul
from dotenv import load_dotenv

load_dotenv()


def chain_evaluation_example(db_path: str = "sample.duckdb") -> None:
    """
    Demonstrate chaining decisions through multiple questions.
    The output of one evaluation determines the next question to ask.
    """

    api_key = os.getenv("TYPESAFE_API_KEY")
    if not api_key:
        print("Error: TYPESAFE_API_KEY environment variable not set")
        return

    # Initialize database
    conn = duckdb.connect(db_path)

    print("="*70)
    print("CHAINED DECISION EXAMPLE: Revenue Analysis")
    print("="*70)

    # STEP 1: Initial assessment
    print("\n[STEP 1] Assessing overall revenue health...")
    print("-" * 70)

    query_step1 = "SELECT * FROM sales"
    result_step1 = conn.execute(query_step1).fetchall()
    schema_step1 = {desc[0]: str(desc[1]) for desc in conn.execute(query_step1).description}

    result_dicts_step1 = [
        dict(zip(schema_step1.keys(), row)) for row in result_step1
    ]
    result_text_step1 = json.dumps(result_dicts_step1, indent=2, default=str)

    state_step1 = {
        "query": query_step1,
        "schema": schema_step1,
        "result_rows": len(result_step1),
        "data": result_text_step1,
    }

    # Ask initial question
    with TypeSafeClient(api_key=api_key) as client:
        response_step1 = client.system_one(
            state=state_step1,
            questions={"q1": Noul(instructions="Is revenue trending downward across all regions?")}
        )

    prob_revenue_down = response_step1.nouls["q1"].noul
    is_revenue_down = prob_revenue_down >= 0.5

    print(f"Question: Is revenue trending downward across all regions?")
    print(f"Probability YES: {prob_revenue_down:.2%}")
    print(f"Probability NO: {1 - prob_revenue_down:.2%}")
    print(f"Decision: {'YES - Revenue is declining' if is_revenue_down else 'NO - Revenue is stable/growing'}")

    # STEP 2: Branching decision based on Step 1
    print("\n[STEP 2] Following up based on Step 1 result...")
    print("-" * 70)

    if is_revenue_down:
        # Branch A: If revenue is down, analyze by region
        print("→ Revenue is declining, analyzing which regions are affected...")

        query_step2 = """
            SELECT
                region,
                COUNT(*) as transaction_count,
                AVG(revenue) as avg_revenue,
                MIN(revenue) as min_revenue,
                MAX(revenue) as max_revenue
            FROM sales
            GROUP BY region
        """

        result_step2 = conn.execute(query_step2).fetchall()
        schema_step2 = {desc[0]: str(desc[1]) for desc in conn.execute(query_step2).description}

        result_dicts_step2 = [
            dict(zip(schema_step2.keys(), row)) for row in result_step2
        ]
        result_text_step2 = json.dumps(result_dicts_step2, indent=2, default=str)

        state_step2 = {
            "query": query_step2,
            "schema": schema_step2,
            "result_rows": len(result_step2),
            "data": result_text_step2,
        }

        with TypeSafeClient(api_key=api_key) as client:
            response_step2 = client.system_one(
                state=state_step2,
                questions={
                    "q1": Noul(instructions="Is the North region significantly underperforming compared to other regions?"),
                    "q2": Noul(instructions="Are there regional revenue disparities that need attention?")
                }
            )

        north_underperforming = response_step2.nouls["q1"].noul
        regional_disparity = response_step2.nouls["q2"].noul

        print(f"\nQuestion A: Is North region underperforming?")
        print(f"Probability YES: {north_underperforming:.2%}")

        print(f"\nQuestion B: Are there regional revenue disparities?")
        print(f"Probability YES: {regional_disparity:.2%}")

        # STEP 3A: If North is underperforming, dig deeper
        if north_underperforming >= 0.5:
            print("\n[STEP 3A] North region issue detected, analyzing further...")
            print("-" * 70)

            query_step3 = "SELECT * FROM sales WHERE region = 'North'"
            result_step3 = conn.execute(query_step3).fetchall()
            schema_step3 = {desc[0]: str(desc[1]) for desc in conn.execute(query_step3).description}

            result_dicts_step3 = [
                dict(zip(schema_step3.keys(), row)) for row in result_step3
            ]
            result_text_step3 = json.dumps(result_dicts_step3, indent=2, default=str)

            state_step3 = {
                "query": query_step3,
                "schema": schema_step3,
                "result_rows": len(result_step3),
                "data": result_text_step3,
            }

            with TypeSafeClient(api_key=api_key) as client:
                response_step3 = client.system_one(
                    state=state_step3,
                    questions={
                        "q1": Noul(instructions="Are profit margins in North region healthy despite lower revenue?")
                    }
                )

            north_margins_healthy = response_step3.nouls["q1"].noul
            print(f"Question: Are North region profit margins healthy?")
            print(f"Probability YES: {north_margins_healthy:.2%}")
            print(f"Insight: {'Margins are good, focus on volume growth' if north_margins_healthy >= 0.5 else 'Both revenue AND margins are weak, urgent action needed'}")

    else:
        # Branch B: If revenue is stable, look for optimization opportunities
        print("→ Revenue is stable/growing, looking for optimization opportunities...")

        query_step2 = """
            SELECT
                region,
                AVG(profit) as avg_profit,
                AVG(revenue) as avg_revenue,
                (AVG(profit) / AVG(revenue)) as profit_margin
            FROM sales
            GROUP BY region
        """

        result_step2 = conn.execute(query_step2).fetchall()
        schema_step2 = {desc[0]: str(desc[1]) for desc in conn.execute(query_step2).description}

        result_dicts_step2 = [
            dict(zip(schema_step2.keys(), row)) for row in result_step2
        ]
        result_text_step2 = json.dumps(result_dicts_step2, indent=2, default=str)

        state_step2 = {
            "query": query_step2,
            "schema": schema_step2,
            "result_rows": len(result_step2),
            "data": result_text_step2,
        }

        with TypeSafeClient(api_key=api_key) as client:
            response_step2 = client.system_one(
                state=state_step2,
                questions={
                    "q1": Noul(instructions="Are profit margins consistent across all regions?"),
                    "q2": Noul(instructions="Is the East region significantly outperforming other regions?")
                }
            )

        margins_consistent = response_step2.nouls["q1"].noul
        east_outperforming = response_step2.nouls["q2"].noul

        print(f"\nQuestion A: Are profit margins consistent?")
        print(f"Probability YES: {margins_consistent:.2%}")

        print(f"\nQuestion B: Is East region outperforming?")
        print(f"Probability YES: {east_outperforming:.2%}")

        if east_outperforming >= 0.5:
            print("\n[STEP 3B] East is outperforming, analyzing best practices...")
            print("-" * 70)

            query_step3 = "SELECT * FROM sales WHERE region = 'East'"
            result_step3 = conn.execute(query_step3).fetchall()
            schema_step3 = {desc[0]: str(desc[1]) for desc in conn.execute(query_step3).description}

            result_dicts_step3 = [
                dict(zip(schema_step3.keys(), row)) for row in result_step3
            ]
            result_text_step3 = json.dumps(result_dicts_step3, indent=2, default=str)

            state_step3 = {
                "query": query_step3,
                "schema": schema_step3,
                "result_rows": len(result_step3),
                "data": result_text_step3,
            }

            with TypeSafeClient(api_key=api_key) as client:
                response_step3 = client.system_one(
                    state=state_step3,
                    questions={
                        "q1": Noul(instructions="Can East region's success strategy be replicated in other regions?")
                    }
                )

            replicable = response_step3.nouls["q1"].noul
            print(f"Question: Can East's success be replicated?")
            print(f"Probability YES: {replicable:.2%}")
            print(f"Action: {'Develop scaling playbook' if replicable >= 0.5 else 'Investigate unique East market factors'}")

    conn.close()
    print("\n" + "="*70)
    print("Chained evaluation complete!")
    print("="*70)


if __name__ == "__main__":
    chain_evaluation_example("sample.duckdb")
