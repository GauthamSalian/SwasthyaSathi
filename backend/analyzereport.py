from fastapi import APIRouter, UploadFile, File, Form
import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from dotenv import load_dotenv
import io
load_dotenv()

router = APIRouter()

client = AzureOpenAI(
    api_version = "2024-12-01-preview",
    azure_endpoint = os.getenv("AZURE_ENDPOINT"),
    api_key = os.getenv("GPT_KEY")
)

@router.post("/analyze_report")
async def analyze_report(
    file: UploadFile = File(...),
    preffered_language: str = Form(...)
):
   
   #initialize the Document Intelligence client
   document_intelligence_client = DocumentIntelligenceClient(
        endpoint = os.getenv("AZURE_DOCS_ENDPOINT"),
        credential = AzureKeyCredential(os.getenv("AZURE_DOCS_SUBSCRIPTION_KEY"))
   )
   
   #read the uploaded file
   contents = await file.read()
   
   #analyze the document
   poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout",
        io.BytesIO(contents),
        content_type="application/pdf"
    )
   
   #get the analysis result
   unformatted = poller.result()["content"]

   #send the result to azure gpt-4o for analysis and translation
   response = client.chat.completions.create(
      model = "gpt-4o",
      messages = [
         {
            "role": "system",
            "content": """You are a medically aware assistant designed to read and summarize diagnostic reports for users in a calm, clear, and emotionally supportive manner.
                        Your role is to:
                        - Focus only on medically relevant findings and interpretations.
                        - Avoid unnecessary metadata, personal identifiers, or lab logistics.
                        - Preserve all important clinical insights, reference ranges, and interpretations.
                        - Communicate in the user's preferred language (e.g., Kannada, Hindi, Bengali) using simple, culturally sensitive phrasing.
                        - Maintain a warm, reassuring tone—especially when findings may be abnormal or concerning.
                        - Avoid medical jargon unless essential, and explain terms gently if used.
                        - Never fabricate information. If something is unclear or missing, say so transparently.
                        Your goal is to help users understand their health status without fear or confusion. Speak as if you are guiding a family member through their report with care and clarity.
                        """,
         },
        {
            "role": "user",
            "content": f"Please summarize the following diagnostic report in {preffered_language}:\n\n{unformatted}",
         }
      ],
        max_tokens = 1024,
        temperature = 0.3,
        top_p = 0.9,
   )
   return response.choices[0].message.content

