from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Create SQLAlchemy instance but do NOT bind to app yet
db = SQLAlchemy()

# Application Factory
def create_app():
    app = Flask(__name__)

    # SQLite in /tmp (only writable place on Render free tier)
    db_path = os.path.join("/tmp", "test.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Bind database to app
    db.init_app(app)

    # Define Model inside factory scope
    class Todo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(200), nullable=False)
        date_created = db.Column(db.DateTime, default=datetime.utcnow)

        def __repr__(self):
            return f"<Task {self.id}>"

    # Create tables
    with app.app_context():
        db.create_all()

    # Routes
    @app.route("/", methods=["POST", "GET"])
    def index():
        if request.method == "POST":
            task_content = request.form["content"]
            new_task = Todo(content=task_content)

            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect("/")
            except:
                return "There was an issue adding your task"

        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template("index.html", tasks=tasks)

    @app.route("/delete/<int:id>")
    def delete(id):
        task_to_delete = Todo.query.get_or_404(id)

        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return redirect("/")
        except:
            return "There was a problem deleting that task"

    @app.route("/update/<int:id>", methods=["GET", "POST"])
    def update(id):
        task = Todo.query.get_or_404(id)

        if request.method == "POST":
            task.content = request.form["content"]

            try:
                db.session.commit()
                return redirect("/")
            except:
                return "There was an issue updating your task"

        return render_template("update.html", task=task)

    return app


# For Gunicorn (Render uses this)
app = create_app()


# For local development: python app.py
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)