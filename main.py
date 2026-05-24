@app.post("/ask")
@app.get("/ask")
def ask_ciq(prompt: str, llms: str = "claude,gpt"):
    with httpx.Client(headers=HEADERS, base_url=BASE, timeout=180.0) as c:
        threads = c.get("/get_threads").json()["threads"]
        thread_id = threads[0] if threads else "default"

        r = c.post(
            "/process_message",
            data={
                "prompt": prompt,
                "thread_id": thread_id,
                "selected_llms": llms,
                "generate_combined": "true",
            },
        )
        run_id = r.json().get("combined_run_id")

        full_response = ""
        with httpx.stream("GET", f"{BASE}/sse", headers=HEADERS, timeout=None) as s:
            for line in s.iter_lines():
                if line.startswith("data: "):
                    content = line[6:].strip()
                    if content == "[DONE]":
                        break
                    if content:
                        full_response += content

        return {"response": full_response.strip() or "No response received."}
