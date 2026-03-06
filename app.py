# app.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/webhook/vapi")
async def vapi_webhook(req: Request):
    data = await req.json()

    msg = data.get("message", {})
    msg_type = msg.get("type")
    print("Vapi message type:", msg_type)

    # Tool calls come in as message.type == "tool-calls"
    if msg_type == "tool-calls":
        tool_calls = msg.get("toolCallList", [])
        results = []

        for call in tool_calls:
            name = call.get("name")
            args = call.get("arguments", {})

            if name == "lookup_order":
                order_id = args.get("order_id")
                results.append({
                    "toolCallId": call.get("id"),
                    "result": {"order_id": order_id, "status": "shipped"}
                })

            elif name == "create_ticket":
                issue = args.get("issue")
                results.append({
                    "toolCallId": call.get("id"),
                    "result": {"ticket_id": "TKT-123", "issue": issue}
                })

            else:
                results.append({
                    "toolCallId": call.get("id"),
                    "result": {"error": f"Unknown tool: {name}"}
                })

        # Vapi expects you to respond with tool results tied to toolCallId
        return JSONResponse({"toolCallResultList": results})

    # For other webhook events, just ack
    return {"received": True}