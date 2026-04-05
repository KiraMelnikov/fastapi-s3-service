import asyncio

from app.clients.self_client import ApiHttpClient

DEFAULT_BASE_URL = "http://localhost:8000"
TEST_COUNT = 1


async def main() -> None:
    client = ApiHttpClient(DEFAULT_BASE_URL, "admin", "admin")

    try:
        for i in range(TEST_COUNT):
            body = {
                "content": {
                    "count": 10,
                    "type": "issues",
                    "issues": [{"id": j, "title": f"test{j}"} for j in range(1, 11)],
                }
            }
            response = await client.add_event_vulnerabilities(body=body)
            keys = response.get("keys", [])
            print(f"{i}:add {len(keys)} files")
            for key in keys:
                response = await client.get_vulnerability(key=key)
                print(f"--get file: {response.get('key')}")
                del_response = await client.delete_vulnerability(key=key)
                print(f"delete file: {del_response.get('key')}, {del_response.get('deleted')}")

        for mode in ["append", "overwrite", "fake"]:
            body = {"meta": {"writeModePerDay": mode}, "content": {"key": "value"}}
            response = await client.add_batch_vulnerabilities(body=body)
            print(f"batch upload with writeModePerDay={mode}")
            key = response.get("key")
            del_response = await client.delete_vulnerability(key=key)
            print(f"delete file: {del_response.get('key')}, {del_response.get('deleted')}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
