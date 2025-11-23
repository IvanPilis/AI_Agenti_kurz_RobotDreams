import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
WOLFRAM_APP_ID = os.environ["WOLFRAM_APP_ID"]  # Free Wolfram API ID available after registration (choose Simple API)


def solve_math_with_wolfram(query: str):
    url = "https://api.wolframalpha.com/v1/result"
    params = {
        "i": query,
        "appid": WOLFRAM_APP_ID
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return f"Error from WolframAlpha: {response.text}"

    return response.text


tools = [
    {
        "type": "function",
        "function": {
            "name": "solve_math_with_wolfram",
            "description": "Solve a math question using the WolframAlpha API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The math problem to solve."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

model = "gpt-4o"
provided_tools = {
    "solve_math_with_wolfram": solve_math_with_wolfram
}


def call_openai_api_using_tools(messages):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    if response_message.tool_calls:
        tool_call = response_message.tool_calls[0]

        # Extract tool name and arguments
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        tool_id = tool_call.id

        # Call the function
        function_to_call = provided_tools[function_name]
        function_response = function_to_call(**function_args)

        print(f'Tool {function_name} returned: {function_response}')
        messages.append({
            "role": "assistant",
            "tool_calls": [
                {
                    "id": tool_id,
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "arguments": json.dumps(function_args),
                    }
                }
            ]
        })
        messages.append({
            "role": "tool",
            "tool_call_id": tool_id,
            "name": function_name,
            "content": json.dumps(function_response),
        })
    # Second call to get final response based on function output

    second_response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    final_answer = second_response.choices[0].message

    print("AI response:", final_answer.content)
    return final_answer


# Run the example API call using tools

user_question = "What is the derivative of x^3 * ln(x)?"  # sample math problem
print(f'User question: {user_question}')

sample_messages = [
    {"role": "system",
     "content": "You are a helpful math expert using tools to solve math problems. Return the final answer in plain text, no LaTeX."},
    {"role": "user", "content": user_question},
]
call_openai_api_using_tools(sample_messages)

# Prints:
# User question: What is the derivative of x^3 * ln(x)?
# Tool solve_math_with_wolfram returned: x^2 (3 log(x) + 1)
# AI response: The derivative of x^3 * ln(x) is x^2 (3 ln(x) + 1).

# Note: It's important to tell the model to return the final answer in plain text, no LaTex, otherwise the answer is escaped:
# AI response: The derivative of \( x^3 \cdot \ln(x) \) is \( x^2 (3 \ln(x) + 1) \).

# Note: This is a useful tool, as generic AI models are not very good at math
