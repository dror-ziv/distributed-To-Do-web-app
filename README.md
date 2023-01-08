# distributed-To-Do-web-app

A distributed todo-list service that is able to support multiple instances such that:

- Every instance can provide access to a shared To-Do list
- Latency is not dependent on the distance between the two instances

## Access

The service allows users to:

* Create new tasks
* Delete existing tasks
* View all tasks

## Build Instructions

To install the necessary dependencies:
```sh
pip install Flask
pip install SQLAlchemy
```

## Insert Constants at Each Instance

To run the app, you will need to insert the following constants at each instance:

- `ip` - Host IP
- `S2c_port` - Client-facing port
- `S2S_port` - Server-facing port
- `other_servers` - A list of other instances of this service, in the format of `[(ip, port), (ip2, port2)]`
- `title_len_max` - Maximum length of a task title
- `desc_len_max` - Maximum length of a task description

## Run

To start the app:
```sh
python3 main.py
```

## Technical Choices

I chose to use the following technologies for this project:

* Python - I am very experienced with this language.
* Flask and SQLAlchemy - I chose these tools for their ease of use in setting up a web server and ORM, respectively.
* SQLite3 - I chose this database for its ease of use in building and performing CRUD operations.
* Socket communication - I chose this method for its simplicity and reliability.

## How Does It Work?

The app sets up two threads: one to listen for client HTTP requests, and the other for socket connections.

### Client-Facing

When a request comes in, the app:

1. Parses the request
2. Starts another thread to synchronize with other servers
3. Performs the CRUD operation
4. Returns the updated index page

### Server-Facing

The app listens for requests and, when one is received, it:

1. Parses the request
2. Executes the appropriate function (CRUD operation)

## Tradeoffs and Known Flaws and Vulnerabilities

### Event-Based Synchronization

I chose event-based synchronization to keep the two instances of the database in sync. If I expected the instances to handle more traffic, I would have implemented fixed-time synchronization.

### Database Queries

To retrieve information from the database, I chose to query the database each time. If I expected the instance to handle more traffic, I would have used some kind of caching mechanism.

### Flaws

- If two people upload at the exact same time to different instances, the operation will fail, return an error, and reverse itself back.
- If using more than two instances and multiple people upload at the exact same time, the database may become unsynced.
- The app currently does not save `\r\n` characters.

### Vulnerabilities

The app is vulnerable to the following attacks:

- SQL injection
- XSS

There is also no authentication or input validation in place.

## Future Improvements

If I had more resources, I would add the following features:

- Search and sort by task name/team
- Ability to edit existing tasks
- A more reactive, aesthetically pleasing front end
- Authentication, encryption, and input validation
- Backups
- Thorough testing
- A better logging mechanism

## Featured Project

If you liked this project, I encourage you to check out my "elf loader" project, which demonstrates a deep understanding of the Linux OS: [elf loader](https://github.com/dror-ziv/elf-loader)

You are also welcome to check out my resume: [Resume](https://drive.google.com/file/d/1_LtGfMli7Du-kTcUYqtq_JsZV3E-ttZA/view?usp=sharing)


