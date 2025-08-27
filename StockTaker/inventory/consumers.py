from channels.generic.http import AsyncHttpConsumer
import asyncio
import redis
from partial_json_parser import loads, ensure_json
import json
from decouple import config


class ServerSentEventsConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        await self.send_headers(headers=[
            (b"Cache-Control", b"no-cache"),
            (
                b"Content-Type",
                b"text/event-stream",
            ),  # Indicates that the response is of type SSE
            (
                b"Transfer-Encoding",
                b"chunked",
            ),  # Indicates that data is to be sent in a series of chunks, and total size is unknown
            (b"Connection", b"keep-alive"),
        ])
        r = redis.Redis(host=config('REDIS_HOST'),
                        port=6379, decode_responses=True)
        while True:
            try:
                job_id = self.scope['url_route']['kwargs']['pk']
                data = r.get(f"recipes:{str(job_id)}")
                print(data)
                pyObj = json.loads(data)
                data = json.dumps(pyObj, separators=(',', ':'))
                data = ensure_json(data)
                print(data)
                payload = f"data: {data} \n\n"
                await self.send_body(payload.encode("utf-8"), more_body=True)

                if r.get(f"recipes:{str(job_id)}:done") == "True":
                    await self.send_body(b'event: close\ndata: end\n\n', more_body=False)
                    break
            except KeyError:
                payload = f"data: Error {job_id} stream does not exist \n\n"
                await self.send_body(payload.encode("utf-8"), more_body=False)
                break

            await asyncio.sleep(1)
