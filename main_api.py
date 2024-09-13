import io
import numpy as np
import uvicorn
import sys
import os

now_dir = os.getcwd()
sys.path.append(now_dir)
sys.path.append(now_dir + "/../")
sys.path.append(now_dir + "/../../")
sys.path.append("%s/GPT_SoVITS" % (now_dir))
from fastapi import FastAPI, Request, HTTPException
from tools.i18n.i18n import I18nAuto, scan_language_list
from GPT_SoVITS.inference import get_tts_wav, change_sovits_weights, change_gpt_weights

# from GPT_SoVITS.inference_webui import get_tts_wav

from config import ref_wav_menu
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

language = os.environ.get("language", "Auto")
language = sys.argv[-1] if sys.argv[-1] in scan_language_list() else language
i18n = I18nAuto(language=language)
app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key="some-random-string")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，也可以指定具体源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# process_session = SessionCookie(
#     secret_key="process",
#     scheme_name="process Cookies",
#     auto_error=False
# )


@app.get("/test")
async def get_wav(request: Request):
    return JSONResponse({"code": 200, "message": "test"}, status_code=200)


# @app.post("/getTTS")
# async def get_wav(request: Request):
#     json_post_raw = await request.json()
#     raw = ref_wav_menu[json_post_raw["role"]]
#     path = ttime()
#     wav_stream = get_tts_wav(
#         now_dir + "\\wav\\" + raw["field"] + ".wav",
#         raw["field"],
#         "中文",
#         json_post_raw["text"] or "",
#         "中文",
#         "凑四句一切",
#         5,
#         1,
#         1,
#         False,
#         str(path) + ".wav",
#     )
#     return StreamingResponse(wav_stream, media_type="audio/" + "wav")


@app.post("/getTTS")
@app.get("/getTTS")
async def get_wav(role, text, top_k=5, top_p=1, temperature=1, language="中文"):
    raw = ref_wav_menu[int(role)]
    path = os.getenv("sovits_model", "")
    # path = ttime()
    change_sovits_weights(path + raw["sovits_weights"])
    change_gpt_weights(path + raw["gpt_weights"])
    wav_generator = get_tts_wav(
        ref_wav_path=now_dir + "/wav/" + raw["field"] + ".wav",
        prompt_text=raw["field"],
        prompt_language="中文",
        text=text or "",
        text_language=language,
        how_to_cut=i18n("凑四句一切"),
    )
    # 获取采样率和音频数据
    sample_rate, audio_data = next(wav_generator)
    audio_bytes = io.BytesIO()
    # 将音频数据写入字节流
    import wave
    with wave.open(audio_bytes, 'wb') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16位音频
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    # 将指针移到流的开始
    audio_bytes.seek(0)

    # 返回StreamingResponse
    return StreamingResponse(audio_bytes, media_type="audio/wav")

@app.get("/getRefMenu")
async def get_wav():
    return JSONResponse({"code": 200, "data": ref_wav_menu}, status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=19999, workers=1)
