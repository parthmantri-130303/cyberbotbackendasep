import openai
import os

# Set your OpenAI key (better via environment variable)
openai.api_key = os.getenv("OPENAI_API_KEY")

def chatgpt_reply(user_message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a cybersecurity assistant."},
            {"role": "user", "content": user_message}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content
