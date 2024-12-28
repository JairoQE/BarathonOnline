import pyodbc

try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=Jairo;'
        'DATABASE=Barathon;'
        'Trusted_Connection=yes;'
    )
    print("Conexión exitosa!")
except Exception as e:
    print("Error de conexión:", e)
