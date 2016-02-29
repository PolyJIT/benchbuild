from pprof.settings import CFG

CFG['db'] = {
    "host": {
        "desc": "host name of our db.",
        "default": "localhost"
    },
    "port": {
        "desc": "port to connect to the database",
        "default": 5432
    },
    "name": {
        "desc": "The name of the PostgreSQL database that will be used.",
        "default": "pprof"
    },
    "user": {
        "desc":
        "The name of the PostgreSQL user to connect to the database with.",
        "default": "pprof"
    },
    "pass": {
        "desc":
        "The password for the PostgreSQL user used to connect to the database with.",
        "default": "pprof"
    },
    "rollback": {
        "desc": "Rollback all operations after pprof completes.",
        "default": False
    }
}
