import sqlite3
import random

conn=sqlite3.connect("library.db")

###############################
departments = ["Αθήνα", "Πάτρα","Θεσσαλονίκη","Ιωάννινα","Ηράκλειο","Βόλος","Χανιά","Λάρισα","Τρίκαλα","Ξάνθη"]
postcodes = [10123,26368,54234,44345,71456,38567,73678,41789,42890,67901]
id_department = 1

def add_department(id_department):
    conn.execute("""INSERT INTO LIBRARY VALUES(?,?,?,?,?);"""
    ,(id_department,departments[id_department-1],f"Street {id_department}",postcodes[id_department-1],random.randint(2610000000,2610999999)))
    conn.commit()



for i in range(len(departments)):
    add_department(id_department)
    id_department+=1

conn.commit()
conn.close()