# The Cloud Functions for Firebase SDK to create Cloud Functions and set up triggers.
from firebase_functions import firestore_fn, https_fn
import psycopg2
# The Firebase Admin SDK to access Cloud Firestore.
from firebase_admin import initialize_app

app = initialize_app()

PGHOST='ep-withered-smoke-aowkgu5t-pooler.c-2.ap-southeast-1.aws.neon.tech'
PGDATABASE='neondb'
PGUSER='neondb_owner'
PGPASSWORD='npg_Bko6mP2yNGRc'
PGSSLMODE='require'
PGCHANNELBINDING='require'

@https_fn.on_request()
def addmessage(req: https_fn.Request) -> https_fn.Response:
    """Take the text parameter passed to this HTTP endpoint and insert it into
    a new document in the messages collection."""
    # Grab the text parameter.
    original = req.args.get("text")
    conn = psycopg2.connect(
        host=PGHOST,
        port=5432,
        user=PGUSER,
        password=PGPASSWORD,
        dbname=PGDATABASE
    )

    cur = conn.cursor()
    cur.execute("SELECT * from user_profiles")
    rows = cur.fetchall()

    cur.close()
    conn.close()
   
    if rows:
        response_text = "\n".join([str(row) for row in rows])
        return https_fn.Response(response_text)
    else:
        return https_fn.Response("No data found")

@https_fn.on_request()
def create_profile(req: https_fn.Request) -> https_fn.Response:
    """
    登録用API: 画面からPOSTされたプロフィール情報をPostgreSQLに登録します。
    """
    # CORS対応（フロントエンドからのリクエストを許可するため）
    if req.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type",
        }
        return https_fn.Response("", status=204, headers=headers)

    headers = {"Access-Control-Allow-Origin": "*"}

    if req.method != "POST":
        return https_fn.Response("Method Not Allowed", status=405, headers=headers)

    # リクエストボディからJSONデータを取得
    data = req.get_json(silent=True)
    if not data:
        return https_fn.Response("Invalid JSON data", status=400, headers=headers)

    PGHOST='ep-withered-smoke-aowkgu5t-pooler.c-2.ap-southeast-1.aws.neon.tech'
    PGDATABASE='neondb'
    PGUSER='neondb_owner'
    PGPASSWORD='npg_Bko6mP2yNGRc'
    PGSSLMODE='require'
    PGCHANNELBINDING='require'
    try:
        conn = psycopg2.connect(
            host=PGHOST,
            port=5432,
            user=PGUSER,
            password=PGPASSWORD,
            dbname=PGDATABASE
        )
        cur = conn.cursor()

        # INSERT文の実行
        # idはDB側での自動採番（SERIAL等）、created_at/updated_atはNOW()を使用することを想定しています
        sql = """
            INSERT INTO user_profiles (
                display_name, bio, profile_image_url, text_color, 
                background_type, background_color, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id;
        """
        params = (
            data.get("display_name"),
            data.get("bio"),
            data.get("profile_image_url"),
            data.get("text_color"),
            data.get("background_type"),
            data.get("background_color")
        )

        cur.execute(sql, params)
        new_id = cur.fetchone()[0]
        conn.commit()

        cur.close()
        conn.close()

        return https_fn.Response(f"Successfully registered. ID: {new_id}", status=201, headers=headers)

    except Exception as e:
        print(f"Error: {e}")
        return https_fn.Response(f"Internal Server Error: {str(e)}", status=500, headers=headers)