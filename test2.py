from fastapi import FastAPI
import httpx
import uvicorn
app = FastAPI()

# 定义代理接口
@app.get("/proxy/{path:path}")
async def proxy_request(path: str):
    # 发起代理请求
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://127.0.0.1:8000/{path}")
    #     except httpx.RequestError:
    #         raise HTTPException(status_code=500, detail="Failed to proxy the request")
    #
    # if response.status_code!= 200:
    #     raise HTTPException(status_code=response.status_code, detail="Failed to proxy the request")

    content_type = response.headers.get("Content-Type", "").lower()
    return response.content

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=19999, workers=1)
