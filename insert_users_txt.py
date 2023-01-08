import sqlite3
from datetime import datetime

conn=sqlite3.connect("library.db")
members = []
employees = []

with open("library_data/members.txt", encoding="utf-8",) as f:
    lines = f.read().split('\n')

with open("library_data/employees.txt", encoding="utf-8",) as f:
    lines2 = f.read().split('\n')

################# προσθηκη μελων
mem_id=1000
for line in lines:
    line = line.split(",")
    line.insert(0, mem_id)
    member_ID = line[0]
    mem_name = line[1]
    mem_last_name = line[2]
    email = line[3]
    library_ID = line[4]
    line.pop()
    line.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    subscr_date = line[5]
    # στοιχεια μελους
    member = [member_ID,mem_name, mem_last_name, email, library_ID,subscr_date]
    members.append(member)
    mem_id+=1

for member in members:
    try:
        conn.execute('INSERT INTO MEMBER VALUES (?,?,?,?,?,?)'
        ,(member[0],member[1],member[2],member[3],member[4],member[5]))
        conn.commit()
    except:
        print("error member")

#################### προσθηκη 10 υπαλληλων
lib=1
id=101
for line in lines2:
    line = line.split(",")
    line.insert(0, id)
    employee_ID = line[0]
    emp_name = line[1]
    emp_last_name = line[2]
    emp_email = line[3]
    line.insert(4, lib)
    library_ID = line[4]
    salary = line[5]
 
    # στοιχεια υπαλληλου
    employee = [employee_ID,emp_name, emp_last_name, emp_email, library_ID,salary]
    employees.append(employee)
    lib+=1
    id+=1

for employee in employees:
    try:
        conn.execute('INSERT INTO EMPLOYEE VALUES (?,?,?,?,?,?)'
        ,(employee[0],employee[1],employee[2],employee[3],employee[4],employee[5]))
        conn.commit()
    except:
        print("error employee")


###############################
conn.commit()
conn.close()
