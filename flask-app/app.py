from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "flexo.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS plate_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_number TEXT NOT NULL,
            job_name TEXT NOT NULL,
            department TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def dashboard():
    conn = get_db_connection()

    jobs = conn.execute(
        "SELECT * FROM plate_requests ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template("dashboard.html", jobs=jobs)


@app.route("/new-request", methods=["GET", "POST"])
def new_request():

    if request.method == "POST":

        job_number = request.form["job_number"]
        job_name = request.form["job_name"]
        department = request.form["department"]
        quantity = request.form["quantity"]
        priority = request.form["priority"]

        status = "Requested"

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO plate_requests
            (job_number, job_name, department,
             quantity, priority, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            job_number,
            job_name,
            department,
            quantity,
            priority,
            status
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("new_request.html")

@app.route("/job/<int:job_id>", methods=["GET", "POST"])
def job_details(job_id):

    conn = get_db_connection()

    job = conn.execute(
        "SELECT * FROM plate_requests WHERE id = ?",
        (job_id,)
    ).fetchone()

    if job is None:
        conn.close()
        return "Job not found", 404

    if request.method == "POST":

        new_status = request.form["status"]

        conn.execute(
            "UPDATE plate_requests SET status = ? WHERE id = ?",
            (new_status, job_id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    conn.close()

    return render_template(
        "job_details.html",
        job=job
    )

@app.route("/inventory")
def inventory():
    return render_template("inventory.html")

if __name__ == "__main__":
    create_database()
    app.run(debug=True)