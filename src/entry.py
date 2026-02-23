from workers import WorkerEntrypoint, Response
import requests

BALE_TOKEN = "bale bot token"
SEND_MSG_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
SEND_DOC_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendDocument"


SUBSCRIPTIONS = [
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/refs/heads/master/Eternity.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/refs/heads/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/All_Configs_Sub.txt",
    "https://openproxylist.com/v2ray/rawlist/text"
    # add more here for /sub5 /sub6 ...
]

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "GET":
            return Response("ok", status=200)

        data = await request.json()
        msg = data.get("message")
        if not msg:
            return Response("ok", status=200)

        chat_id = msg["chat"]["id"]
        text = msg.get("text", "").strip()

        if text == "/sublist":
            msg_text = "Sub List:\n"
            for i in range(len(SUBSCRIPTIONS)):
                msg_text += f"sub{i+1} : {SUBSCRIPTIONS[i]}\n"
            requests.post(SEND_MSG_URL, json={"chat_id": chat_id, "text": msg_text})
            return Response("ok", status=200)

        if text.startswith("/sub") and text[4:].isdigit():
            n = int(text[4:])
            if 1 <= n <= len(SUBSCRIPTIONS):
                url = SUBSCRIPTIONS[n-1]
                content = requests.get(url).text
                files = {'document': (f"sub{n}.txt", content)}
                requests.post(SEND_DOC_URL, data={'chat_id': chat_id}, files=files)
            return Response("ok", status=200)

        if text.startswith("/search "):
            query = text[8:].strip()
            if query:
                try:
                    r = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1", timeout=10)
                    dd = r.json()
                    results = "Search Results:\n\n"
                    if dd.get("AbstractURL"):
                        results += f"url: {dd.get('AbstractURL')}\n"
                        results += f"title: {dd.get('Heading')}\n"
                        results += f"description: {dd.get('Abstract')}\n\n"
                    for topic in dd.get("RelatedTopics", [])[:10]:
                        if topic.get("FirstURL"):
                            results += f"url: {topic.get('FirstURL')}\n"
                            results += f"title: {topic.get('Text')}\n"
                            results += f"description: {topic.get('Text')}\n\n"
                    requests.post(SEND_MSG_URL, json={"chat_id": chat_id, "text": results})
                except:
                    requests.post(SEND_MSG_URL, json={"chat_id": chat_id, "text": "Search error."})
            return Response("ok", status=200)

        if text.startswith("/html "):
            url = text[6:].strip()
            if url.startswith("http"):
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    r = requests.get(url, timeout=15, headers=headers)
                    content = r.text
                    files = {'document': ("page.html", content, "text/html")}
                    requests.post(SEND_DOC_URL, data={'chat_id': chat_id}, files=files)
                except:
                    requests.post(SEND_MSG_URL, json={"chat_id": chat_id, "text": "Failed to fetch page."})
            return Response("ok", status=200)

        if text == "/start":
            requests.post(SEND_MSG_URL, json={"chat_id": chat_id, "text": "Hi\n/sub1\n/sublist\n/search python\n/html https://example.com"})

        return Response("ok", status=200)