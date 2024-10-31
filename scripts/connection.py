import pyodbc


def connect_database():
    conn_str = (
        "DRIVER={SQL Anywhere 16};"
        "UID=consulta;"
        "PWD=1234;"
        "ENG=srvContabil;"
        "DBN=contabil;"
        "LINKS=tcpip(host=192.168.1.10)"
    )

    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as error:
        print(f"Error connecting to the database: {str(error)}")
        return None