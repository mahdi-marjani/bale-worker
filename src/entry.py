from workers import WorkerEntrypoint, Response
import json
import requests

BALE_TOKEN = None
SEND_MSG_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"


def _json_resp(obj, status=200):
    return Response(
        body=json.dumps(obj, ensure_ascii=False),
        status=status,
        headers={"Content-Type": "application/json"}
    )


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        try:
            # Health check
            if request.method == "GET":
                return _json_resp({"status": "alive", "BALE_TOKEN_set": bool(BALE_TOKEN)})

            data = await request.json()
            msg = data.get("message")

            response_summary = {"handled": False, "payload_sent": None, "error": None}

            if msg:
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")

                if text == "/start":
                    payload = {"chat_id": chat_id, "text": "hi 👋"}
                    response_summary["handled"] = True
                    response_summary["payload_sent"] = payload

                    try:
                        r = requests.post(SEND_MSG_URL, json=payload)
                        response_summary["status_code"] = r.status_code
                        response_summary["response_body"] = r.text
                    except Exception as e:
                        response_summary["error"] = str(e)

                else:
                    # echo for any other message
                    payload = {"chat_id": chat_id, "text": f"you said: {text}"}
                    response_summary["handled"] = True
                    response_summary["payload_sent"] = payload
                    try:
                        r = requests.post(SEND_MSG_URL, json=payload)
                        response_summary["status_code"] = r.status_code
                        response_summary["response_body"] = r.text
                    except Exception as e:
                        response_summary["error"] = str(e)

            return _json_resp({"received": data, "summary": response_summary})

        except Exception as e:
            return Response(f"error: {e}", status=500)
