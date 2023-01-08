import socket
import sqlite3
import json

class Server_to_server:

    #init S2S: either binding to known ports or initiating as "clients"
    def __init__(self, address=None, db_path=None, JSON_SIZE_MAX = None):
        if address or db_path:
            self.address = address
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(address)
            self.server.listen()
            self.db_conn = sqlite3.connect(db_path, check_same_thread=False)
            self.JSON_SIZE_MAX = JSON_SIZE_MAX
        else:
            self.server = socket.socket()
    

    # basic socket operations
    def accept_connection(self):
        self.connection, self.client_address = self.server.accept()

    def send_message(self, message):
        self.connection.sendall(message.encode())
    
    def receive_nessage(self, size):
        recived_data = self.connection.recv(size)
        recived_data = recived_data.decode()
        return recived_data
    

    # parsing messages and directing to func
    def listen_for_commands(self):
        self.accept_connection()
        command = self.receive_nessage(6)

        if command == "delete":
            id = self.receive_nessage(1024)
            try:
                self.del_from_db(id)
                self.send_message("OK")
            except Exception as e:
                    self.send_message("ER")
                    print(e)
        elif command == "create":
            json_of_query = self.receive_nessage(self.JSON_SIZE_MAX)
            try:
                self.add_to_db(json_of_query)
                self.send_message("OK")
            except Exception as e:
                self.send_message("ER")
                print(e)

        else:
            print("error.. command '{}' not known".format(command))
            self.send_message("ER")
        self.connection.close()
    

    #handeling sending messages
    def send_delete(self, address, id):
        try:
            self.server.connect(address)
        except:
            return 0
        data = "delete{}".format(id)
        self.server.send(data.encode())
        response = self.server.recv(2).decode()
        self.server.close()
        if response == "OK":
            return 1
        elif response == "ER": #ER = ERROR
            return 0

        
    
    def send_new_note(self, address, new_task_object):
        json_task = note_to_json(new_task_object)
        try:
            self.server.connect(address)
        except:
            return 0
        data = "create"
        self.server.send(data.encode())
        self.server.send(json_task.encode())
        response = self.server.recv(2).decode()
        self.server.close()
        if response == "OK":
            return 1
        elif response == "ER": #ER = ERROR
            return 0


    #handeling db changes
    def add_to_db(self, json_object):
        sql_note = json_to_sql_format(json_object)
        sql = '''INSERT INTO note(id, task_title, task_description, dateadded) VALUES (?, ?, ?, ?)'''
        cur = self.db_conn.cursor()
        cur.execute(sql, sql_note)
        self.db_conn.commit()


    def del_from_db(self, id):
        sql = "DELETE FROM note WHERE id=?"
        cur = self.db_conn.cursor()
        cur.execute(sql, (id,))
        self.db_conn.commit()


#json to and from different formats
def json_to_sql_format(json_object):
    buf = json.loads(json_object)
    id = buf["id"]
    title = buf["task_title"]
    desc = buf["task_description"]
    date = buf["dateadded"]
    return (id, title, desc, date)

def note_to_json(note):
    note_dict = {}
    note_dict["id"] = note.id
    note_dict["task_title"] = note.task_title
    note_dict["task_description"] = note.task_description
    note_dict["dateadded"] = str(note.dateadded)
    note_json = json.dumps(note_dict)
    return note_json
         

def main():
    print("this is not supposed to happen :)")


if __name__ == "__main__":
    main()
