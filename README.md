# Google Map Timeline Search Demo App

## Setup

1. Download your GoogleMaps timeline data (Takeout) from <https://timeline.google.com/maps/timeline>
1. Extract downloaded `.zip` or `.gz` file into `./Takeout` directory
1. Make sure Location History data (`.json`) is contained on downloaded takeout.

### Postgres

- psql (PostgreSQL) 14.4
- create database tables

### Python Enviroment

- Python=3.10.4
- pip=21.2.4

```shell
pip install -r requirments.txt
```

create database from Takeout data

```shell
python db.py
```

then run Streamlit server

```shell
python run.py 127.0.0.1 8080
```
