from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel
import uvicorn
from datetime import datetime, timedelta
import httpx
from fastapi.responses import FileResponse
import os

# FastAPIルート: http://127.0.0.1:8000/openapi.json
# FastAPI 実行: uvicorn main:app --reload



#### ==== 初期化 ==== ####

# 認証用設定
SECRET_KEY = "your-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# アプリ初期化
app = FastAPI()


# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



#### ==== 関数定義 ==== ####

# 認証トークン（JWT）を検証する依存関数
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# 天気情報を取得する関数
async def get_weather(city_code):
    url = f"https://weather.tsukumijima.net/api/forecast?city={city_code}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    # 今日の天気情報を取得
    for forecast in data["forecasts"]:
        if forecast["dateLabel"] == "今日":
            return forecast["telop"]
    return "天気情報が見つかりませんでした。"


# 季節を取得する関数
def get_season(month: int) -> str:
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"
    raise ValueError("Invalid month")



#### ==== モデル ==== ####

# ユーザーモデル
class User(BaseModel):
    id: Optional[int] = None
    username: str
    hashed_password: Optional[str] = None
    model_config = {"from_attributes": True}


# ユーザーデータベース（ダミー）
fake_users_db = {
    "alice": {
        "username": "alice",
        "password": "wonderland",
    }
}


# リクエストモデル
class MoodRequest(BaseModel):
    mood: str = None



#### ==== エンドポイント ==== ####

# APIヘルスチェック
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


# トークン発行エンドポイント
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = jwt.encode(
        {"sub": user["username"], "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer"}


# ユーザー情報取得
@app.get("/users/me", summary="現在のユーザ情報を取得")
def read_users_me(username: str = Depends(get_current_user)):
    return {"username": username}


# レコメンド機能 (URLを返す)
@app.get("/recommend", summary="おすすめ曲を取得")
# def recommend_music(req: MoodRequest, username: str = Depends(get_current_user)):
async def recommend_music():
    """
    # 受け取ったデータを確認
    print(f"IN /recommend !! req.mood: {req.mood}")
    if not req.mood:
        print("Mood が ねえ！")
        # raise HTTPException(status_code=400, detail="Mood is required")
        """
    
    # ---- レコメンドロジック ---- #
    # 今日の日付を取得
    today = datetime.today().date()
    print(f"Today's date: {today}")
    
    # 日付から季節を取得
    month = today.month
    current_season = get_season(month)
    print(f"Current season: {current_season}")
    
    # 現在の天気を取得
    city_code = "230010" # 名古屋市の地域コード
    weather = await get_weather(city_code)
    print(f"今日の天気（名古屋市）: {weather}")
    
    # 例: ダミー曲を返す
    """
    return {
        "request": req,
        "recommendations": [
            {
                "title": "Rainy Mood",
                "artist": "Lo-Fi Beats",
                "spotify_url": "https://open.spotify.com/track/xxx"
            }
        ]
    }
    """
    return {
        "recommendations": [
            {
                "title": "Rainy Mood",
                "artist": "Lo-Fi Beats",
                "spotify_url": "https://open.spotify.com/track/xxx"
            }
        ]
    }


# レコメンド機能 (音楽ファイルパスを返す)
@app.get("/music")
def get_music():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    music_path = os.path.join(current_dir, "musics/test.mp3")
    if not os.path.exists(music_path):
        print(music_path)
        return {"error": "Music file not found"}, 404
    return FileResponse(music_path, media_type="audio/mpeg")



#### ==== 実行ブロック ==== ####
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)