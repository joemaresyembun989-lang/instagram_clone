from flask import Flask, render_template, request, redirect, session
import mysql.connector, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret_ig_clone"

UPLOAD_POSTS = "static/uploads/posts"
UPLOAD_PROFILE = "static/uploads/profile"
os.makedirs(UPLOAD_POSTS, exist_ok=True)
os.makedirs(UPLOAD_PROFILE, exist_ok=True)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="instagram_clone"
)
cursor = db.cursor(dictionary=True)

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (request.form["username"], request.form["password"])
        )
        user = cursor.fetchone()
        if user:
            session["user"] = user
            return redirect("/home")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        cursor.execute(
            "INSERT INTO users (username,password) VALUES (%s,%s)",
            (request.form["username"], request.form["password"])
        )
        db.commit()
        return redirect("/")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")

    cursor.execute("""
        SELECT posts.*, users.username, users.photo
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """)
    posts = cursor.fetchall()

    for p in posts:
        cursor.execute(
            "SELECT COUNT(*) c FROM post_likes WHERE post_id=%s",
            (p["id"],)
        )
        p["likes"] = cursor.fetchone()["c"]

        cursor.execute("""
            SELECT comments.*, users.username
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id=%s
            ORDER BY comments.created_at
        """,(p["id"],))
        comments = cursor.fetchall()

        for c in comments:
            cursor.execute(
                "SELECT COUNT(*) c FROM comment_likes WHERE comment_id=%s",
                (c["id"],)
            )
            c["like_count"] = cursor.fetchone()["c"]

            cursor.execute(
                "SELECT 1 FROM comment_likes WHERE comment_id=%s AND user_id=%s",
                (c["id"], session["user"]["id"])
            )
            c["liked"] = cursor.fetchone() is not None

        p["comments"] = comments

    return render_template("home.html", posts=posts)

@app.route("/add", methods=["GET","POST"])
def add():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        image = request.files["image"]
        caption = request.form["caption"]

        filename = secure_filename(image.filename)
        path = os.path.join(UPLOAD_POSTS, filename)
        image.save(path)

        cursor.execute(
            "INSERT INTO posts (user_id,image,caption) VALUES (%s,%s,%s)",
            (session["user"]["id"], "/"+path, caption)
        )
        db.commit()
        return redirect("/home")

    return render_template("post.html")

@app.route("/like/<int:post_id>")
def like(post_id):
    try:
        cursor.execute(
            "INSERT INTO post_likes (post_id,user_id) VALUES (%s,%s)",
            (post_id, session["user"]["id"])
        )
        db.commit()
    except:
        cursor.execute(
            "DELETE FROM post_likes WHERE post_id=%s AND user_id=%s",
            (post_id, session["user"]["id"])
        )
        db.commit()
    return redirect("/home")

@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    cursor.execute(
        "INSERT INTO comments (post_id,user_id,comment) VALUES (%s,%s,%s)",
        (post_id, session["user"]["id"], request.form["comment"])
    )
    db.commit()
    return redirect("/home")

@app.route("/chat/<int:user_id>", methods=["GET","POST"])
def chat(user_id):
    if request.method == "POST":
        cursor.execute(
            "INSERT INTO chats (sender_id,receiver_id,message) VALUES (%s,%s,%s)",
            (session["user"]["id"], user_id, request.form["message"])
        )
        db.commit()

    cursor.execute("""
        SELECT * FROM chats
        WHERE (sender_id=%s AND receiver_id=%s)
        OR (sender_id=%s AND receiver_id=%s)
        ORDER BY created_at
    """,(session["user"]["id"], user_id, user_id, session["user"]["id"]))

    messages = cursor.fetchall()
    return render_template("chat.html", messages=messages, user_id=user_id)

@app.route("/profile/<int:user_id>")
def profile(user_id):
    if "user" not in session:
        return redirect("/")

    cursor.execute("SELECT * FROM users WHERE id=%s",(user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM posts WHERE user_id=%s",(user_id,))
    posts = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) c FROM posts WHERE user_id=%s",(user_id,))
    post_count = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(*) c FROM follows WHERE following_id=%s",(user_id,))
    followers = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(*) c FROM follows WHERE follower_id=%s",(user_id,))
    following = cursor.fetchone()["c"]

    return render_template(
        "profile.html",
        user=user,
        posts=posts,
        post_count=post_count,
        followers=followers,
        following=following
    )

@app.route("/edit_profile", methods=["POST"])
def edit_profile():
    bio = request.form["bio"]
    photo = request.files["photo"]

    filename = session["user"]["photo"]
    if photo:
        fname = secure_filename(photo.filename)
        photo.save(os.path.join(UPLOAD_PROFILE, fname))
        filename = "/static/uploads/profile/"+fname

    cursor.execute(
        "UPDATE users SET bio=%s, photo=%s WHERE id=%s",
        (bio, filename, session["user"]["id"])
    )
    db.commit()
    return redirect("/profile/"+str(session["user"]["id"]))

@app.route("/like_comment/<int:comment_id>")
def like_comment(comment_id):
    if "user" not in session:
        return redirect("/")

    try:
        cursor.execute(
            "INSERT INTO comment_likes (comment_id, user_id) VALUES (%s, %s)",
            (comment_id, session["user"]["id"])
        )
        db.commit()
    except:
        cursor.execute(
            "DELETE FROM comment_likes WHERE comment_id=%s AND user_id=%s",
            (comment_id, session["user"]["id"])
        )
        db.commit()

    return redirect(request.referrer)


if __name__ == "__main__":
    app.run(debug=True)
