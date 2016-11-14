from flask import Flask, render_template

from db import init, Session
import mappings


app = Flask(__name__)
app.db = init()


@app.route("/")
def home():
    projects = Session.query(mappings.Project)
    return render_template('home.html', projects=projects)


if __name__ == "__main__":
    app.run()
