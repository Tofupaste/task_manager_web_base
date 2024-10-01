from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "Response_Pwebprak"

mysql = MySQL(app)

app.secret_key = "Ini-sangat-rahasia"

@app.route("/")
def home():
    if 'is_logged_in' in session:
        user_id = session.get('user_id')

        cur = mysql.connection.cursor()

        # Ambil data tugas yang akan datang
        cur.execute("SELECT task_name, deadline, status FROM tasks WHERE user_id = %s AND deadline > NOW()", (user_id,))
        upcoming_tasks = cur.fetchall()

        # Hitung statistik tugas
        cur.execute("SELECT COUNT(*) FROM tasks WHERE user_id = %s", (user_id,))
        total_tasks = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM tasks WHERE user_id = %s AND status = 'completed'", (user_id,))
        completed_tasks = cur.fetchone()[0]

        # Menghitung tugas yang masih pending
        pending_tasks = total_tasks - completed_tasks

        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

        # Pesan sambutan
        welcome_message = "Start managing your tasks efficiently with our Task Manager app."

        # Ambil tugas yang baru ditambahkan
        cur.execute("SELECT task_name, created_at FROM tasks WHERE user_id = %s ORDER BY created_at DESC LIMIT 5", (user_id,))
        new_tasks = cur.fetchall()

        cur.close()

        return render_template("home.html", upcoming_tasks=upcoming_tasks,
                               total_tasks=total_tasks, completed_tasks=completed_tasks,
                               pending_tasks=pending_tasks, completion_rate=completion_rate,
                               welcome_message=welcome_message, new_tasks=new_tasks)
    else:
        return redirect(url_for('login'))
        

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["inpNama"]
        email = request.form["inpEmail"]
        password = request.form["inpPass"]

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, email, password) VALUES(%s, %s, %s)", (name, email, password))

        # Ambil id pengguna yang baru dibuat
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_id_result = cur.fetchone()

        if user_id_result:
            user_id = user_id_result[0]

            # cur.execute("INSERT INTO tasks(user_id, task_name) VALUES(%s, %s)", (user_id, 'Welcome Task'))

            mysql.connection.commit()

            cur.close()

            return redirect( url_for("login"))

        cur.close()
    
    return render_template("register.html")



@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # Get form data
        email = request.form["inpEmail"]
        password = request.form["inpPass"]

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))

        # Get user
        user = cur.fetchone()

        # Close connection
        cur.close()
        if user:
            # Add user information to the session
            session["is_logged_in"] = True
            session["username"] = user[1]
            session["user_id"] = user[0]  # Add user_id to session

            # Redirect to home page
            return redirect(url_for("home"))
        else:
            # If user not found, show error message
            error = "Invalid email or password"
            return render_template("login.html", msg=error)
    else:
        # If it's a GET request, render the login page
        return render_template("login.html")
    
@app.route("/task_manager")
def task_manager():
    if 'is_logged_in' in session:
        user_id = session.get('user_id')

        cur = mysql.connection.cursor()

        # Ambil semua tugas pengguna dengan kolom id, task_name, dan status
        cur.execute("SELECT id, task_name, status FROM tasks WHERE user_id = %s", (user_id,))
        tasks = cur.fetchall()

        cur.close()

        return render_template("task_manager.html", tasks=tasks)
    else:
        return redirect(url_for('login'))
    
@app.route("/logout")
def logout():
    session.pop("is_logged_in", None)
    session.pop("username", None)

    return redirect(url_for("login"))

@app.route("/edit_task/<int:task_id>", methods=['GET', 'POST'])
def edit_task(task_id):
    if 'is_logged_in' in session:
        user_id = session.get('user_id')

        if request.method == 'POST':
            new_task_name = request.form.get('new_task_name')
            new_description = request.form.get('new_description')
            new_deadline = request.form.get('new_deadline')

            cur = mysql.connection.cursor()

            # Perbarui nama, deskripsi, dan deadline tugas
            cur.execute("UPDATE tasks SET task_name = %s, description = %s, deadline = %s WHERE id = %s AND user_id = %s",
                        (new_task_name, new_description, new_deadline, task_id, user_id))

            mysql.connection.commit()

            cur.close()

            return redirect(url_for('task_manager'))
        else:
            cur = mysql.connection.cursor()

            # Ambil detail tugas untuk ditampilkan pada halaman edit
            cur.execute("SELECT * FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
            task = cur.fetchone()

            cur.close()

            if task:
                return render_template('edit_task.html', task=task)
            else:
                flash("Task not found", "error")
                return redirect(url_for('task_manager'))
    else:
        return redirect(url_for('login'))

@app.route("/delete_task/<int:task_id>", methods=['POST'])
def delete_task(task_id):
    if 'is_logged_in' in session:
        user_id = session.get('user_id')

        cur = mysql.connection.cursor()

        # Hapus tugas dengan task_id tertentu untuk pengguna tertentu
        cur.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))

        mysql.connection.commit()

        cur.close()

        return redirect(url_for('task_manager'))
    else:
        return redirect(url_for('login'))

@app.route("/add_task", methods=['GET', 'POST'])
def add_new_task():  # Ganti endpoint ke add_new_task
    if 'is_logged_in' in session:
        user_id = session.get('user_id')
        if request.method == 'POST':
            task_name = request.form.get('task_name')
            description = request.form.get('description')
            deadline = request.form.get('deadline')

            # Perhatikan bahwa created_at diisi dengan waktu saat ini
            created_at = datetime.now()

            cur = mysql.connection.cursor()

            # Tambahkan tugas baru untuk pengguna
            cur.execute(
                "INSERT INTO tasks(user_id, task_name, description, deadline, created_at) VALUES(%s, %s, %s, %s, %s)",
                (user_id, task_name, description, deadline, created_at)
            )

            mysql.connection.commit()

            cur.close()

            return redirect(url_for('task_manager'))
        else:
            return render_template("add_task.html")
    else:
        return redirect(url_for('login'))

@app.route("/task/<int:task_id>")
def task_detail(task_id):
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, task_name, description, created_at, deadline, status "
        "FROM tasks "
        "WHERE id = %s AND user_id = %s",
        (task_id, user_id),
    )
    task = cur.fetchone()
    cur.close()

    print("Task ID:", task_id)
    print("Task Result:", task)  # Print the result

    # Check if task is not None and has the expected structure
    if task and isinstance(task, tuple) and len(task) == 6:
        task_dict = {
            'id': task[0],
            'task_name': task[1],
            'description': task[2],
            'created_at': task[3],
            'deadline': task[4],
            'status': task[5],
        }
        # Convert datetime to string for rendering
        task_dict['created_at'] = task_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S') if task_dict['created_at'] else 'N/A'
        task_dict['deadline'] = task_dict['deadline'].strftime('%Y-%m-%d %H:%M:%S') if task_dict['deadline'] else 'N/A'
        return render_template("task_detail.html", task=task_dict)
    else:
        return render_template("task_not_found.html")
    

@app.route("/complete_task/<int:task_id>", methods=['POST'])
def complete_task(task_id):
    if 'is_logged_in' in session:
        user_id = session.get('user_id')

        cur = mysql.connection.cursor()

        # Perbarui status tugas menjadi 'completed'
        cur.execute("UPDATE tasks SET status = 'completed' WHERE id = %s AND user_id = %s", (task_id, user_id))

        mysql.connection.commit()

        cur.close()

        flash("Task completed successfully", "success")

        return redirect(url_for('task_manager'))
    else:
        return redirect(url_for('login'))

@app.route("/cancel_task/<int:task_id>", methods=['POST'])
def cancel_task(task_id):
    if 'is_logged_in' in session:
        user_id = session.get('user_id')

        cur = mysql.connection.cursor()

        # Perbarui status tugas menjadi 'pending'
        cur.execute("UPDATE tasks SET status = 'pending' WHERE id = %s AND user_id = %s", (task_id, user_id))

        mysql.connection.commit()

        cur.close()

        flash("Task status changed to pending", "info")

        return redirect(url_for('task_manager'))
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
