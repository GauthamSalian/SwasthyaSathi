import os
from pydantic import BaseModel
from typing import List
from fastapi import APIRouter
from openai import AzureOpenAI
from dotenv import load_dotenv

router = APIRouter()

#extracting environment variables
load_dotenv()

#defining the formats of request and response bodies
class UserInput(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    response: str

#loading the model
client = AzureOpenAI(
    api_version = "2024-12-01-preview",
    azure_endpoint = os.getenv("AZURE_ENDPOINT"),
    api_key = os.getenv("GPT_KEY")
)

#defining the funtion to generate response from the model
def generate_response(user_input: str) -> str:
    response =client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {
                "role": "system",
                "content": """You are a medically informed assistant with deep knowledge of symptoms and the diseases they may indicate. Your role is to help users from rural India understand their health concerns in a clear, respectful, and emotionally mature way.
                            Most users may describe symptoms vaguely or in everyday language. If the input is unclear or incomplete, ask simple follow-up questions using familiar terms, avoiding medical jargon. Be patient and kind.
                            When symptoms suggest a serious or potentially life-threatening condition, calmly advise the user to seek medical care immediately. Do not downplay the urgency—but do not create panic. Use relatable examples to explain the concern.
                            Always respond with empathy, clarity, and caution. Avoid diagnosing. Instead, suggest possible conditions and explain why they might be relevant. If symptoms are mild or unclear, reassure the user and guide them toward better symptom description.
                            When appropriate, offer safe, culturally familiar home remedies based on official AYUSH guidelines. These should be clearly explained, easy to prepare, and framed as supportive care—not substitutes for medical treatment.
                            Your tone should be supportive, informative, and grounded—like a trusted village health worker who knows both medicine and the emotional needs of the people.""",
            },
            {
                "role": "user",
                "content": user_input,
            }
        ],
        max_tokens = 1024,
        temperature = 0.3,
        top_p = 0.9,
    )
    return response.choices[0].message.content

@router.post('/chat', response_model = ChatResponse)
async def chat_endpoint(user_input: UserInput):
    return ChatResponse(
        response = generate_response(user_input.user_input)
    )