{\rtf1\ansi\ansicpg1252\cocoartf2709
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from fastapi import FastAPI\
import httpx\
import os\
\
app = FastAPI(title="CIQ for Siri")\
\
API_KEY = os.getenv("CIQ_API_KEY", "ciq_test_a91vaF9tvaviYbw8Hsjqsf2CHjoua9sEM2UnsQadJkhR")\
BASE = "https://api.staging.collectiviq.ai"\
HEADERS = \{"Authorization": f"Bearer \{API_KEY\}"\}\
\
@app.post("/ask")\
async def ask_ciq(prompt: str, llms: str = "claude,gpt"):\
    """Simple endpoint for Siri Shortcuts"""\
    async with httpx.AsyncClient(headers=HEADERS, base_url=BASE, timeout=180.0) as c:\
        threads = (await c.get("/get_threads")).json()["threads"]\
        thread_id = threads[0] if threads else "default"\
\
        r = await c.post(\
            "/process_message",\
            data=\{\
                "prompt": prompt,\
                "thread_id": thread_id,\
                "selected_llms": llms,\
                "generate_combined": "true",\
            \},\
        )\
        run_id = r.json().get("combined_run_id")\
\
        full_response = ""\
        async with c.stream("GET", f"\{BASE\}/sse") as s:\
            async for line in s.aiter_lines():\
                if line.startswith("data: "):\
                    content = line[6:].strip()\
                    if content == "[DONE]":\
                        break\
                    if content:\
                        full_response += content\
\
        return \{"response": full_response.strip() or "No response received."\}\
\
@app.get("/")\
def health():\
    return \{"status": "ok", "service": "CIQ for Siri"\}}