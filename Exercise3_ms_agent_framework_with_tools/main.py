import asyncio
import os
from agent_framework import ChatMessage, ai_function, ChatAgent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv
import psycopg2
import matplotlib.pyplot as plt

load_dotenv()

@ai_function(
    name="generate_chart",
    description="Generate chart from time series data provided as a dictionary"
)
def generate_chart(data: dict) -> str:
    print(f'Calling chart tool with data: {data}')
    plt.plot(data.keys(), data.values())
    plt.savefig("chart.png")
    return "chart.png"

@ai_function(
    name="read_transactions",
    description="Get financial transactions from a database, query provided. Columns: id, txn_date, description, amount, category.",
)
def read_transactions(query: str) -> str:
    print(f'Calling database tool with query: {query}')
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="personal_finances",
        user="ivanp",
        password=os.environ['POSTGRES_DB_PASSWORD']
    )

    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return str(rows)

async def main():
    model = OpenAIChatClient(
        model_id="gpt-5-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # agent
    agent = ChatAgent(
        chat_client=model,
        instructions="You are a helpful assistant that can retrieve financial statements from the database and provide charts using tools.",
        tools=[read_transactions, generate_chart],
    )

    query = "What was my total spending by category in year 2025? Give me a summary and generate a chart"
    response = await agent.run(query)

    print(response)



if __name__ == "__main__":
    asyncio.run(main())
