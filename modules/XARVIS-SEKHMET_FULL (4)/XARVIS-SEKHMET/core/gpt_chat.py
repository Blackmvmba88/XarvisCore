#!/usr/bin/env python3
import openai
import os
import sys

openai.api_key = os.getenv("OPENAI_API_KEY")  # export OPENAI_API_KEY='tu_clave'

def preguntar_a_gpt(pregunta):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": pregunta}]
    )
    print("[XARVIS GPT]:", response.choices[0].message.content)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        preguntar_a_gpt(" ".join(sys.argv[1:]))
    else:
        print("Uso: ./gpt_chat.py [pregunta]")
