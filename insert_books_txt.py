import sqlite3
import random
import string    


conn=sqlite3.connect("library.db")
departments_number = 10
books=[]
publishers = ["Simon & Schuster","HarperCollins","Macmillan Publishers","Penguin Random House","Hachette Livre"]
languages = ["English","Swedish","English","German","English","Greek","Latin"]
translators = ["Morgan Giles","Aaron Robertson","Tiffany Tsao","Julia Sanches","Pavlos Zannas","Fotini MEgaloudi"]
collections = [0,1,2,3,4,5]

with open("library_data/books.txt", encoding="utf-8",) as f:
    lines = f.read().split('\n')

def version_creator():
    version=random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase) + "-" + str(random.randint(10,99))+"-"+str(random.randint(1000,9999))
    return version

for line in lines:
    line = line.split(",")
    version = version_creator()
    isbn = line[0]
    title = line[1]
    author = line[2]
    pages = line[3]
    ddc = line[4]
    if len(ddc)!=6:
        if len(ddc)==4:
            ddc=str(ddc)
            ddc = '00' + ddc
        if len(ddc)==5:
            ddc=str(ddc)
            ddc = '0' + ddc

    line.insert(5, version)
    version = line[5]
    year = line[6]
    line.append(random.choice(publishers))
    publisher = line[7]
    line.append(random.choice(languages))
    language = line[8]
    line.append(random.choice(translators))
    translator = line[9]
    line.append(random.choice(collections))
    collection = line[10]
    # στοιχεια εντυπου
    book = [isbn,title, author, pages, ddc,version, year, publisher, language, translator, collection]
    books.append(book)

for book in books:
    try:
        conn.execute(f'''INSERT INTO BOOK VALUES (?,?,?,?,?,?,?,?,?,?,?)'''
        ,(book[0],book[1],book[2],book[3],book[4],book[5],book[6],book[7],book[8],book[9],book[10]))
        conn.commit()
        for i in range(random.randint(1,9)):
            conn.execute("""INSERT INTO COPY VALUES(?,?,?,?)"""
            ,(i+1, book[0], random.randint(1,departments_number), '1'))
        conn.commit()

    except:
        print("error book")

###############################
conn.commit()
conn.close()
