from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import logging

app = FastAPI(title="FastAPI Translator")

# --- Логирование ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("translator")

# --- CORS для браузера ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Статика (интерфейс) ---
@app.get("/")
def index():
    return FileResponse("static/index.html")


# --- Проверка работоспособности ---
@app.get("/health")
def health():
    return {"status": "ok"}

# --- Основной endpoint перевода ---
@app.get("/translate")
def translate(
    text: str = Query(..., description="Текст для перевода"),
    target_lang: str = Query("en", description="Язык перевода"),
    source_lang: str = Query("auto", description="Исходный язык"),
    provider: str = Query("mymemory", description="API переводчика"),
):
    logger.info(f"📩 Translate request: {text=} {source_lang=} {target_lang=} {provider=}")

    if source_lang == "auto":
        source_lang = "ru"


    try:
        if provider == "mymemory":
            url = "https://api.mymemory.translated.net/get"
            params = {"q": text, "langpair": f"{source_lang}|{target_lang}"}
            headers = {"User-Agent": "Mozilla/5.0 (compatible; FastAPI-Translator/1.0)"}
            r = requests.get(url, params=params, headers=headers, timeout=10)
            data = r.json()
            translated = data.get("responseData", {}).get("translatedText", "")
            if not translated:
                logger.warning(f"MyMemory response: {data}")
                return JSONResponse({"error": "Empty translation", "raw": data}, status_code=200)
            return {"provider": "mymemory", "original": text, "translated": translated}

        else:
            return JSONResponse({"error": f"Unknown provider '{provider}'"}, status_code=400)

    except Exception as e:
        logger.exception("Translation error:")
        return JSONResponse({"error": str(e)}, status_code=500)
