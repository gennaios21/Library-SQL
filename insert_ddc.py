import sqlite3

conn=sqlite3.connect("library.db")

###############################

# 000  Computer science, information and general works
# 100  Philosophy and psychology
# 200  Religion
# 300  Social sciences
# 400  Language
# 500  Pure Science
# 600  Technology
# 700  Arts and recreation
# 800  Literature
# 900  History and geography

categories = ["Γενικά θέματα", "Φιλοσοφία και ψυχολογία","Θρησκεία","Κοινωνικές επιστήμες","Γλώσσα",
                "Φυσικές επιστήμες και μαθηματικά","Τεχνολογία ","Τέχνες και διασκέδαση","Λογοτεχνία","Ιστορία και γεωγραφία"]
id_category = 1
n = '0'
ddc = n + '00'

def add_category(id_category):
    conn.execute("""INSERT INTO TOPIC VALUES(?,?);""",(ddc,categories[id_category-1]))
    conn.commit()

for i in range(len(categories)):
    add_category(id_category)
    id_category+=1
    n=int(n)
    n+=1
    n=str(n)
    ddc = n + '00'

conn.commit()
conn.close()