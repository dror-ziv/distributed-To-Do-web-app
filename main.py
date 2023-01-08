from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from ServerToServer import Server_to_server
import threading
import logging

# global vars #
IP = "0.0.0.0"
S2C_PORT = 8000
S2S_PORT = 8001
OTHER_SERVERS = ( ("127.0.0.1", 8002), )
TITLE_LEN_MAX = 50
DESC_LEN_MAX = 200



# init #


#magic number 99 is calculated from size of other fields in json
#such as: date added, id number.. allowing up to 6 digits in id field (999,999 items in db)
MAX_JSON_LEN = TITLE_LEN_MAX + DESC_LEN_MAX + 99 

#calculating db dir
project_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_dir, "todo.db")
database_file = "sqlite:///{}".format(db_path)

#logs
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(project_dir, "logfile"), filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

#init app , db, and server to server
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)
server = Server_to_server((IP, S2S_PORT), db_path, MAX_JSON_LEN)



# DB class, basic CRUD oprations #
class Note(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    task_title = db.Column(db.Text)
    task_description = db.Column(db.TEXT)
    dateadded = db.Column(db.DateTime)

def create_note(title, desc):
    note = Note(task_title = title, task_description = desc, dateadded = datetime.now())
    db.session.add(note)
    db.session.commit()
    db.session.refresh(note)
    return note

def read_notes():
    return db.session.query(Note).all()

def delete_note(note_id):
    db.session.query(Note).filter_by(id=note_id).delete()
    db.session.commit()

def __str__(self):
    return 'id: {}, title: {}, desc: {}, date added: {}'.format(self.id, self.task_title, self.task_description, self.dateadded)





# server to server communication #

def send_to_servers_del(id):
    new_socket = Server_to_server()
    for address in OTHER_SERVERS:
        if not new_socket.send_delete(address, id):
            logging.error("error at other instance...")


def send_to_servers_create(task):
    new_socket = Server_to_server()
    for address in OTHER_SERVERS:
        if not new_socket.send_new_note(address, task):
            logging.error("error at other instance... reversing changes..\ndumping new column at logs..")
            logging.error("title: {}\n description: {}".format(task.task_title, task.task_description))
            with app.app_context():
                delete_note(task.id)
            


# client request handeling #

@app.route('/', methods=["POST", "GET"])
def view_index():
    if request.method == "POST":
        new_note = create_note(request.form['task_title'], request.form['task_description'])
        threading.Thread(target=send_to_servers_create, args=(new_note,)).start()
    return render_template("index.html", notes = read_notes(), max_title=TITLE_LEN_MAX, max_desc = DESC_LEN_MAX)

@app.route("/delete/<note_id>")
def handle_delete(note_id):
    delete_note(note_id)
    threading.Thread(target=send_to_servers_del, args=(note_id,)).start()
    return redirect("/", code=302)



# setting up different threads for S2C and S2S #

def start_http_app():
    with app.app_context():
        db.create_all()
    app.run(host = IP, port=S2C_PORT)

def start_tcp_server():
    while True:
        server.listen_for_commands()


# starting threads #
def main():
    
    http_app_thread = threading.Thread(target=start_http_app)
    tcp_server_thread = threading.Thread(target=start_tcp_server)
    http_app_thread.start()
    tcp_server_thread.start()
    

if __name__ == "__main__":
    main()
