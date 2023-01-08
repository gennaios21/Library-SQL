import sqlite3
import random

conn=sqlite3.connect("library.db")

###############################
collections = ["Αποθετήριο βιβλιοθήκης","Magazines - Calendars", "Rare literature books","Poems","Rules and laws","Historic"]
id_collection = 1

def add_collection(id_collection):
    conn.execute("""INSERT INTO COLLECTION VALUES(?,?)"""
    ,(id_collection,collections[id_collection-1],))
    conn.commit()



for i in range(len(collections)):
    add_collection(id_collection)
    id_collection+=1

conn.commit()
conn.close()