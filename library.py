import PySimpleGUI as sg
import sqlite3
from datetime import datetime, timedelta
import random
from starting_data import (headings as headings, headings_employee as headings_employee, headings_employee2 as headings_employee2, 
headings_antitypa as headings_antitypa, headings_myrequests as headings_myrequests, headings_mylends as headings_mylends, headings_apps as headings_apps,
headings_members as headings_members, headings_loan as headings_loan, headings_interloan as headings_interloan, search_users as search_users,
search_params as search_params, search_params2 as search_params2, depts_names as depts_names, depts as depts, distances as distances)


################ db connection
conn=sqlite3.connect("library.db")
c=conn.cursor()

################ starting parameters
data_query=[]
data_values=[]
data_user_values=[]
data_antitypa=[]
data_interloan=[]
list_of_applications=[]
data_expired=[]
account = 'none'
delta = timedelta(days=14)    # προθεσμια δανεισμου 
loan_limit = 3                # οριο δανεισμου

################ request number και interloan number
try:
    request = c.execute('SELECT max(req_number) FROM REQUESTS')
    request = int(c.fetchall()[0][0])
except:
    request = 1
try:
    interloan_number = c.execute('SELECT max(interloan_number) FROM INTERLOAN')
    interloan_number = int(c.fetchall()[0][0])
except:
    interloan_number = 1


################ headings


################ fonts, colors etc.
text_font = "Courier"
text_size = 16
exit_color = "red"
search_color = "black on yellow"
cancel_color = "blue"
mybooks_color = "green"
add_color = "purple"
row_height = 30


##################### συναρτηση ευρεσης βελτιστου αντιτυπου διαδανεισμου βαση αποστασης, διαθεσιμοτητας και αιτησεων

def find_score(elem):
    return elem[3]


def best_available_copy(bookISBN, library_ID):
    depts_copy = depts          # αντιγραφα των λιστων γιατι κανουμε add/remove
    distances_copy = distances

    dept_name=c.execute("""SELECT dep_name FROM LIBRARY WHERE library_id=?""",
                    (library_ID,)).fetchall()[0][0]
    
    for i in range(len(depts_copy)):
        num_of_copies=c.execute("""SELECT COUNT(copy_number)
            FROM COPY
            WHERE library_ID=? AND copy_ISBN=? and availability = 1""",(depts_copy[i][1], bookISBN,)).fetchall()[0][0]
        depts_copy[i].append(num_of_copies)

    x=[]
    for i in range(len(depts_copy)):
        if dept_name in depts_copy[i]:
            x=depts_copy[i]

    depts_copy.remove(x)

    distances_from_dept=[]
    for i in range(len(distances_copy)):
        if dept_name in distances_copy[i]:
            distances_from_dept.append(distances_copy[i])

    for i in range(len(distances_from_dept)):
        distances_from_dept[i].remove(dept_name)

    for i in range(len(depts_copy)):
        depts_copy[i].append(distances_from_dept[i][1])


    #for i in range(len(depts_copy)):
        #αν δεν έχει αντίτυπα η πόλη, υψηλό σκορ
    #    if depts_copy[i][2]==0:
    #        depts_copy[i].append(10000)
    #    else:
    #        depts_copy[i].append(depts_copy[i][2]*0.9+depts_copy[i][3]*0.1)

    for i in range(len(depts_copy)):
        depts[i].append(c.execute("""SELECT COUNT(req_number)
                                    FROM REQUESTS, MEMBER
                                    WHERE ISBN=? AND memberID=member_ID and ongoing = 1
                                    AND library_ID=?""" 
                                    ,(bookISBN,depts_copy[i][1],)).fetchall()[0][0])

    #sort κατά αύξουσα σειρά σκορ
    depts_copy.sort(key=find_score)

    best_copy=[]
    for i in range(len(depts_copy)):
        print("-----------", depts_copy[i])
        if depts_copy[i][2]>depts_copy[i][4]:
            best_copy=depts_copy[i]
            break
    print(best_copy)
    #Το best_copy είναι λίστα [πόλη, id, αρ_αντιτύπων, απόσταση, αρ_αιτήσεων]

    #επιστρέφει αριθμό αντιτύπου και πόλη στην οποία είναι το αντίτυπο
    return [c.execute("""SELECT MIN(copy_number)
                    FROM COPY
                    WHERE copy_ISBN=?
                    AND library_ID=? and availability = 1 """,(bookISBN,best_copy[1],)).fetchall()[0][0],
            best_copy[1]]

    #Το πρώτο στοιχείο του depts_copy είναι λίστα
    #['Πόλη', id, αρ αντιτύπων, απόσταση, σκορ]
    #return [c.execute("""SELECT MIN(copy_number)
    #            FROM COPY
    #            WHERE copy_ISBN=?
    #            AND library_ID=? """,(bookISBN,depts_copy[0][1],)).fetchall()[0][0],depts_copy[0][1]]
    

################################## queries αναζήτησης εντυπων/μελων απο μελος και υπαλληλο

# αναζητηση εντυπου απο μελος
def search_by_title(title, topic):
    c.execute("""SELECT title, author, ISBN, sum(availability='1'), BOOK.DDC, Category, IIF(collection_number="","-",collection_name)
                    FROM BOOK, COPY, TOPIC, COLLECTION
                    WHERE title LIKE ? and (collection_number = collection_ID or collection_number = "") 
                    and (SELECT cast(IIF((substr(BOOK.DDC,1,1)*100)=0 ,"000",(substr(BOOK.DDC,1,1)*100)) as text) as dewey)=TOPIC.DDC 
                    and Category LIKE ? AND ISBN=copy_ISBN AND availability='1' 
                    GROUP BY copy_ISBN ORDER BY title""",(title,topic,))

def search_by_author(author, topic):
    c.execute("""SELECT title, author, ISBN, sum(availability='1'), BOOK.DDC, Category, IIF(collection_number="","-",collection_name)
                    FROM BOOK, COPY, TOPIC, COLLECTION
                    WHERE author LIKE ? and (collection_number = collection_ID or collection_number = "") 
                    and (SELECT cast(IIF((substr(BOOK.DDC,1,1)*100)=0 ,"000",(substr(BOOK.DDC,1,1)*100)) as text) as dewey)=TOPIC.DDC 
                    and Category LIKE ? AND ISBN=copy_ISBN AND availability='1' 
                    GROUP BY copy_ISBN ORDER BY author""",(author,topic,))

def search_by_ISBN(isbn, topic):
    c.execute("""SELECT title, author, ISBN, sum(availability='1'), BOOK.DDC, Category, IIF(collection_number="","-",collection_name)
                    FROM BOOK, COPY, TOPIC, COLLECTION
                    WHERE Title LIKE ? and (collection_number = collection_ID or collection_number = "") 
                    and (SELECT cast(IIF((substr(BOOK.DDC,1,1)*100)=0 ,"000",(substr(BOOK.DDC,1,1)*100)) as text) as dewey)=TOPIC.DDC 
                    and Category LIKE ? AND ISBN=copy_ISBN AND availability='1' 
                    GROUP BY copy_ISBN ORDER BY ISBN""",(isbn,topic,))

def search_by_year(year, topic):
    c.execute("""SELECT title, author, ISBN, sum(availability='1'), BOOK.DDC, Category, IIF(collection_number="","-",collection_name)
                    FROM BOOK, COPY, TOPIC , COLLECTION
                    WHERE publ_year LIKE ? and (collection_number = collection_ID or collection_number = "") 
                    and (SELECT cast(IIF((substr(BOOK.DDC,1,1)*100)=0 ,"000",(substr(BOOK.DDC,1,1)*100)) as text) as dewey)=TOPIC.DDC 
                    and Category LIKE ? AND ISBN=copy_ISBN AND availability='1' 
                    GROUP BY copy_ISBN  ORDER BY publ_year""",(year,topic,))

def search_by_DDC(ddc, topic):
    c.execute("""SELECT title, author, ISBN, sum(availability='1'), BOOK.DDC, Category, IIF(collection_number="","-",collection_name)
                    FROM BOOK, COPY, TOPIC, COLLECTION
                        WHERE BOOK.DDC > ? AND BOOK.DDC < ?
                        and (collection_number = collection_ID or collection_number = "") 
                        and (SELECT cast(IIF((substr(BOOK.DDC,1,1)*100)=0 ,"000",(substr(BOOK.DDC,1,1)*100)) as text) as dewey)=TOPIC.DDC 
                        and Category LIKE ? AND ISBN=copy_ISBN AND availability='1' 
                        GROUP BY copy_ISBN  ORDER BY BOOK.DDC""",(float(ddc),float(float(ddc)+100-float(ddc[1:])),topic))

def search_by_collection(coll_name, topic):
    c.execute("""SELECT title, author, ISBN, sum(availability='1'), BOOK.DDC, Category, IIF(collection_number="","-",collection_name)
                FROM BOOK, COPY, TOPIC, COLLECTION
                WHERE ISBN=copy_ISBN 
                and collection_name LIKE ? and Category like ? and (collection_number = collection_ID or collection_number = "") 
                and (SELECT cast(IIF((substr(BOOK.DDC,1,1)*100)=0 ,"000",(substr(BOOK.DDC,1,1)*100)) as text) as dewey)=TOPIC.DDC 
                GROUP BY copy_ISBN ORDER BY collection_name, title""",(coll_name,topic,))

########### αναζητηση εντυπου απο υπαλληλο

def employee_search_title(title, library_ID):
    c.execute("""SELECT title, author, ISBN, count(copy_ISBN), sum(availability), BOOK.DDC, Category
                        FROM BOOK, COPY, TOPIC
                        WHERE title  LIKE ? AND library_ID=? 
                        and (SELECT cast(IIF((substr(BOOK.DDC,1,1)*100)=0 ,"000",(substr(BOOK.DDC,1,1)*100)) as text) as dewey)=TOPIC.DDC 
                        AND ISBN=copy_ISBN GROUP BY copy_ISBN ORDER BY title""",(title, library_ID,))
    
def employee_search_author(author, library_ID):
    c.execute("""SELECT title, author, ISBN, count(copy_ISBN), sum(availability), BOOK.DDC, Category
                        FROM BOOK, COPY, TOPIC
                        WHERE author  LIKE ? AND library_ID=?
                        and (SELECT cast(IIF((substr(BOOK.DDC,1,1)*100)=0 ,"000",(substr(BOOK.DDC,1,1)*100)) as text) as dewey)=TOPIC.DDC 
                        AND ISBN=copy_ISBN GROUP BY copy_ISBN ORDER BY author""",(author, library_ID,))

def employee_search_ISBN(isbn, library_ID):
    c.execute("""SELECT title, author, ISBN, count(copy_ISBN), sum(availability), BOOK.DDC, Category
                        FROM BOOK, COPY, TOPIC
                        WHERE isbn LIKE ? AND library_ID=?
                        and (SELECT cast(IIF((substr(BOOK.DDC,1,1)*100)=0 ,"000",(substr(BOOK.DDC,1,1)*100)) as text) as dewey)=TOPIC.DDC 
                        AND ISBN=copy_ISBN GROUP BY copy_ISBN ORDER BY isbn""",(isbn, library_ID,))


def employee_search_year(year, library_ID):
    c.execute("""SELECT title, author, ISBN, count(copy_ISBN), sum(availability), BOOK.DDC, Category
                        FROM BOOK, COPY, TOPIC
                        WHERE publ_year LIKE ? AND library_ID=?
                        and (SELECT cast(IIF((substr(BOOK.DDC,1,1)*100)=0 ,"000",(substr(BOOK.DDC,1,1)*100)) as text) as dewey)=TOPIC.DDC 
                        AND ISBN=copy_ISBN GROUP BY copy_ISBN ORDER BY publ_year""",(year, library_ID,))

def employee_search_DDC(ddc, library_ID):
    c.execute("""SELECT title, author, ISBN, count(copy_ISBN), sum(availability), BOOK.DDC, Category
                    FROM BOOK, COPY, TOPIC
                    WHERE BOOK.DDC > ? AND BOOK.DDC < ?
                    and (SELECT cast(IIF((substr(BOOK.DDC,1,1)*100)=0 ,"000",(substr(BOOK.DDC,1,1)*100)) as text) as dewey)=TOPIC.DDC 
                    AND ISBN=copy_ISBN AND library_ID=? 
                    GROUP BY copy_ISBN ORDER BY BOOK.DDC""",(float(ddc),float(float(ddc)+100-float(ddc[1:])),library_ID,))

############ αναζητηση χρηστη απο υπαλληλο
def employee_search_name(name, library_ID):
    c.execute("""SELECT DISTINCT mem_name, mem_last_name, member_ID, email, subscr_date
                        FROM MEMBER, LIBRARY
                        WHERE mem_name  LIKE ? AND MEMBER.library_ID=?
                        ORDER BY mem_name""",(name, library_ID,))

def employee_search_surname(surname, library_ID):
    c.execute("""SELECT DISTINCT mem_name, mem_last_name, member_ID, email, subscr_date
                        FROM MEMBER, LIBRARY
                        WHERE mem_last_name  LIKE ? AND MEMBER.library_ID=?
                        ORDER BY mem_name""",(surname, library_ID,))

def employee_search_userid(userid, library_ID):
    c.execute("""SELECT DISTINCT mem_name, mem_last_name, member_ID, email, subscr_date
                        FROM MEMBER, LIBRARY
                        WHERE member_ID  LIKE ? AND MEMBER.library_ID=?
                        ORDER BY member_ID""",(userid, library_ID,))

def employee_search_email(email, library_ID):
    c.execute("""SELECT DISTINCT mem_name, mem_last_name, member_ID, email, subscr_date
                        FROM MEMBER, LIBRARY
                        WHERE email  LIKE ? AND MEMBER.library_ID=?
                        ORDER BY member_ID""",(email, library_ID,))

############################################ LAYOUTS SIGN-IN, ΜΕΛΟΥΣ, ΥΠΑΛΛΗΛΟΥ ############################################

# Αρχικη σελιδα sign in μελους/υπαλληλου
layout_signin = [  
    [sg.VPush()],
    [sg.Text('ID χρήστη (μέλους/υπαλλήλου):',font=(text_font,text_size+4))],
    [sg.InputText('',font=(text_font,text_size))],
    [sg.Button("Είσοδος στην εφαρμογή",key="Είσοδος",font=(text_font,text_size))],
    [sg.Button("Εγγραφή",key="Εγγραφή",font=(text_font,text_size))],
    [sg.Button('Έξοδος',font=(text_font,text_size),button_color = (exit_color))],	
    [sg.VPush()]
    ]

# Σελίδα αναζήτησης εντύπων μελους
layout_search = [  
    [sg.Text('Αναζήτηση εντύπου: ',font=(text_font,text_size)), sg.Combo(search_params,default_value='Τίτλος',key='board',size=(20,10),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))],
    [sg.Text('Φίλτρο κατηγορίας: ',font=(text_font,text_size)), sg.Combo(search_params2,default_value='',key='topic',size=(35,10),font=(text_font,text_size))],
    [sg.Button('Αναζήτηση',	font=(text_font,text_size),button_color = (search_color))],
    [sg.Table(values=data_values, headings=headings,
        enable_events=True,
        auto_size_columns=False,
        col_widths=list(map(lambda i:len(i)+15, headings)),
        row_height=row_height,
        justification='center',
        key='-TABLE-',font=(text_font,text_size),vertical_scroll_only=False)],
    [sg.Button('Επιλογή εντύπου για δανεισμό',key='-REQUEST-',	font=(text_font,text_size))],
    [sg.Button('Οι δανεισμοί μου',key='-LEND-',font=(text_font,text_size),button_color = (mybooks_color))],
    [sg.Button('Οι αιτήσεις μου',key='-ACTIVE-',font=(text_font,text_size),button_color = (mybooks_color)), sg.Push(),sg.Button('Έξοδος',font=(text_font,text_size),button_color = (exit_color))],
    ]

# Σελίδα αναζήτησης εντύπων υπαλληλου
layout_employee = [  
    [sg.Text('Αναζήτηση εντύπου με: ',font=(text_font,text_size)), sg.Combo(search_params,default_value='Τίτλος',key='board',size=(20,10),font=(text_font,text_size)), 
        sg.InputText(font=(text_font,text_size)),sg.Push(),sg.Button('Αναζήτηση',key="-SEARCH_BOOK-",	font=(text_font,text_size),button_color = (search_color))],
    [sg.Table(values=data_values, headings=headings_employee,
        enable_events=True,
        auto_size_columns=False,
        col_widths=list(map(lambda i:len(i)+15, headings)),
        row_height=row_height,
        justification='center',
        key='-TABLE-',font=(text_font,text_size),vertical_scroll_only=False)],
    [sg.Button('Προβολή αιτήσεων εντύπου',key='-APPLICATIONS-',	font=(text_font,text_size),button_color = (mybooks_color)),sg.Push(),
     sg.Button('Προβολή αιτήσεων για διαδανεισμό',key='-INTERLOAN_REQUESTS-',	font=(text_font,text_size),button_color = (mybooks_color)),sg.Push(),
     sg.Button('Εισαγωγή χρήστη',key='-ADD_USER-', font=(text_font,text_size),button_color = (add_color))],
    #[sg.Button('Προβολή λίστας προτεραιότητας',key='-PRIORITY-',	font=(text_font,text_size))],
    [sg.Button('Προβολή ενεργών δανεισμών', key='-LOANS-',font=(text_font,text_size),button_color = (mybooks_color)),sg.Push(),sg.Button('Αυτόματη ανάθεση αντιτύπων',key='-ASSIGN-',font=(text_font,text_size)),sg.Push(),
    sg.Button('Εισαγωγή εντύπου',key='-ADD_BOOK-', font=(text_font,text_size),button_color = (add_color))],
    [sg.Text('Αναζήτηση χρήστη με: ',font=(text_font,text_size)), sg.Combo(search_users,default_value='Όνομα',key='members',size=(20,10),font=(text_font,text_size)), 
        sg.InputText(font=(text_font,text_size)),sg.Push(),sg.Button('Αναζήτηση',key="-SEARCH_USER-",	font=(text_font,text_size),button_color = (search_color))],
    [sg.Table(values=data_user_values, headings=headings_employee2,
        enable_events=True,
        auto_size_columns=False,
        col_widths=list(map(lambda i:len(i)+15, headings)),
        row_height=row_height,
        justification='center',
        key='-TABLE2-',font=(text_font,text_size),vertical_scroll_only=False)],
    [sg.Button('Προβολή αιτήσεων χρήστη',key='-USER_REQUESTS-',	font=(text_font,text_size),button_color = (mybooks_color)),sg.Push(),
    sg.Button('Προβολή δανεισμών χρήστη',key='-USER_LOANS-',	font=(text_font,text_size),button_color = (mybooks_color)),sg.Push(),
     sg.Button('Προβολή καθυστερήσεων',key='-EXPIRED-',	font=(text_font,text_size),button_color = (mybooks_color))],
    [sg.Button("Εκτέλεση custom query",key="-QUERY_SEARCH-",font=(text_font,text_size),button_color = (search_color)), sg.Push(),sg.Button('Έξοδος',font=(text_font,text_size),button_color = (exit_color))],	

    ]
############################################## εκκινηση της εφαρμογης με το sign in 

window_sign=sg.Window('Δίκτυο Δανειστικών Βιβλιοθηκών ΗΜΤΥ',layout_signin ,size=(500,300),element_justification='c',resizable=True)

while True:
    event,values=window_sign.read()
    if event==sg.WIN_CLOSED or event=='Έξοδος':
        window_sign.close()
        break
    # εγγραφη νεου μελους (κανονικα οι νεοι υπαλληλοι εγγραφονται απο αλλον υπαλληλο μεσα στην εφαρμογη, αλλα χαριν ευκολιας μπορει να εγγραφει και νεος υπαλληλος)
    if event == 'Εγγραφή':
        departments = ["Αθήνα", "Πάτρα","Θεσσαλονίκη","Ιωάννινα","Ηράκλειο","Βόλος","Χανιά","Λάρισα","Τρίκαλα","Ξάνθη"]
        users=["Μέλος","Υπάλληλος"]

        layout_adduser = [	
            [sg.Text('Εισάγετε στοιχεία χρήστη: ', font=(text_font,text_size))], [sg.VPush()],	
            [sg.Text('Όνομα',size=(15,1),font=(text_font,text_size)),sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
            [sg.Text('Επώνυμο',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
            [sg.Text('Email',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
            [sg.Text('Βιβλιοθήκη:',size=(15,1),font=(text_font,text_size)),sg.Combo(departments,default_value='Πάτρα',key='depts',size=(20,10),font=("Courier",18))],[sg.VPush()],
            [sg.Text('Τύπος χρήστη:',size=(15,1),font=(text_font,text_size)),sg.Combo(users,default_value='Μέλος',key='users',size=(20,10),font=("Courier",18))],[sg.VPush()],
            
            [sg.Button("Εισαγωγή",key="Εισαγωγή",font=(text_font,text_size)),sg.VPush(),sg.Button('Έξοδος',font=(text_font,text_size),button_color = (exit_color))],	
        ]	
        window_adduser = sg.Window("Εισαγωγή νέου χρήστη", layout_adduser, size=(500,500),modal=True,resizable=True)

        while True:
            event, values = window_adduser.read()	
            if event=="Έξοδος"or event==sg.WIN_CLOSED:
                window_adduser.close()
                break

            if	event == "Εισαγωγή" and values['depts'] in departments and values['users'] in users and values[0]!="" and values[1]!="" and values[2]!="":	
                
                if(values["users"]=="Μέλος"):
                    try:
                        userID = c.execute('SELECT max(member_ID) FROM MEMBER')
                        userID = int(c.fetchall()[0][0])
                    except:
                        userID = 999
                    userID+=1
                    conn.execute('''INSERT	INTO	MEMBER	VALUES	(?,	?,	?,	?, ?,?);''',	
                    (userID,	values[0],	values[1],	values[2], departments.index(values['depts'])+1,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")));
                    conn.commit()
                    cursor = conn.cursor()	
                    cursor.execute("SELECT * FROM MEMBER  WHERE member_ID = ?",(userID,))
                    data = cursor.fetchall()
                    print("USER: ", data)	
                    window_adduser.close()
                    sg.Popup(f"Your member ID is: {userID}",font=(text_font,text_size))

                elif(values["users"]=="Υπάλληλος" ):
                    try:
                        userID = c.execute('SELECT max(employee_ID) FROM EMPLOYEE')
                        userID = int(c.fetchall()[0][0])
                        print(userID)
                    except:
                        userID = 100
                    userID+=1
                    conn.execute('''INSERT	INTO	EMPLOYEE	VALUES	(?,	?,	?,	?, ?,?);''',	
                    (userID,	values[0],	values[1],	values[2], departments.index(values['depts'])+1,random.randint(10000,20000)));
                    conn.commit()
                    cursor = conn.cursor()	
                    cursor.execute("SELECT * FROM EMPLOYEE  WHERE employee_ID = ?",(userID,))
                    data = cursor.fetchall()
                    print("EMPLOYEE: ", data)	
                    window_adduser.close()
                    sg.Popup(f"Your member ID is: {userID}",font=(text_font,text_size))
                    
                else:
                    sg.Popup("Error: input the correct user fields",font=(text_font,text_size))
                    continue
    # εισοδος χρηστη
    if event=='Είσοδος':
        try:
            c.execute("""SELECT * FROM MEMBER WHERE member_ID LIKE ?""",(f'{values[0]}',))
            user=c.fetchall()
            memberID=int(user[0][0])

        except:
            print("no user found")

        try:
            c.execute("""SELECT * FROM EMPLOYEE WHERE employee_ID LIKE ?""",(f'{values[0]}',)) 
            employee=c.fetchall()
            employeeID=int(employee[0][0])
            
        except:
            print("no employee found")
        if(len(user)==1):
            window_sign.close()
            # print("user, memberID: ", user, memberID)
            account = "user"

        elif(len(employee)==1):
            window_sign.close()
            # print("employee, employeeID: ", employee, employeeID)
            account = "employee"
        else:
            sg.Popup('Warning: input a correct id',font=(text_font,text_size)) 


############################################################################################## αν γινει sign in, κομματι μελους

if(account=="user"):
    c.execute('''SELECT dep_name FROM MEMBER as M, LIBRARY as L WHERE M.library_ID = L.library_ID AND
    M.member_ID = ?''',(memberID,))
    library_dept = c.fetchall()[0][0]
    c.execute('''SELECT M.library_ID FROM MEMBER as M, LIBRARY as L WHERE M.library_ID = L.library_ID AND
    M.member_ID = ?''',(memberID,))
    library_ID = c.fetchall()[0][0]

    c.execute('''SELECT mem_name || ' ' || mem_last_name FROM MEMBER as M WHERE M.member_ID = ?''',(memberID,))
    member_name = c.fetchall()[0][0]

    layout_member=[sg.Push(),sg.Text("ΜΕΛΟΣ: "+ member_name + ", "+ library_dept, font=(text_font,text_size)),sg.Push()]
    layout_search[0].insert(0,layout_member)
    window=sg.Window('Δίκτυο Δανειστικών Βιβλιοθηκών ΗΜΤΥ',layout_search ,size=(1400,650),resizable=True)

    while True:
        event,values=window.read()
        if event==sg.WIN_CLOSED or event=='Έξοδος':
            break
        # αναζητηση με εντυπο (τιτλος, συγγραφεας κλπ)
        if event=='Αναζήτηση':
            if values['board']=='Τίτλος':
                search_by_title(f'%{values[0]}%',f'%{values["topic"]}%')
            if values['board']=='Συγγραφέας':
                search_by_author(f'%{values[0]}%',f'%{values["topic"]}%')

            if values['board']=='ISBN':
                search_by_ISBN(f'%{values[0]}%',f'%{values["topic"]}%')

            if values['board']=='Έτος έκδοσης':
                search_by_year(f'%{values[0]}%',f'%{values["topic"]}%')
                
            if values['board']=='DDC':
                try:
                    search_by_DDC(f'{values[0]}',f'%{values["topic"]}%')
                except:
                    sg.Popup("Input a correct DDC number",font=(text_font,text_size))
            if values['board']=='Συλλογές':
                search_by_collection(f'%{values[0]}%',f'%{values["topic"]}%')
            data=c.fetchall()

            #c.execute("""SELECT κωδ_εντύπου, αρ_αντιτύπου
            #    FROM ΕΝΤΥΠΟ, ΑΝΤΙΤΥΠΟ
            #    WHERE Τίτλος  LIKE ?
            #    AND ISBN=κωδ_εντύπου AND διαθεσιμότητα='1'""",(f'%{values[0]}%',))
            data2=c.fetchall()
            
            data_values=data
            #data_antitypa = data2
            window['-TABLE-'].update(values=data_values)

        # επιλογη εντυπου απο τον πινακα αποτελεσματων αναζητησης
        if event=='-TABLE-':
            selected_row=values['-TABLE-'][0]
            #print("To antitypo: ",  data_antitypa[selected_row])
        # οι αιτησεις μου
        if event == '-ACTIVE-':
            c.execute("""SELECT title, REQUESTS.ISBN, REQUESTS.req_date, req_number, IIF(ongoing=1,"ΝΑΙ","ΟΧΙ")
                    FROM REQUESTS, BOOK
                    WHERE memberID = ? AND REQUESTS.ISBN=BOOK.ISBN
                    GROUP BY req_date
                    UNION
                    SELECT title, INTERLOAN.bookISBN, INTERLOAN.req_date, interloan_number, IIF(status='pending',"ΝΑΙ","ΟΧΙ")
                    FROM INTERLOAN, BOOK
                    WHERE INTERLOAN.member_ID = ? AND INTERLOAN.bookISBN=BOOK.ISBN
                    GROUP BY req_date
                    ORDER BY title """, (memberID,memberID,))
            data_requests=c.fetchall()
            

            layout_myrequests = [ 
                [sg.Table(values=data_requests, headings=headings_myrequests,
                    enable_events=True,
                    auto_size_columns=False,
                    col_widths=list(map(lambda i:len(i)+20, headings)),
                    row_height = row_height,
                    justification='center',
                    key='-TABLE_REQUESTS-',font=(text_font,text_size),vertical_scroll_only=False)],
                [sg.Button('Ακύρωση αίτησης',key='-CANCEL-',font=(text_font,text_size),button_color = (cancel_color))],
                [sg.Button('Κλείσιμο',key='-CLOSE-',font=(text_font,text_size),button_color = (exit_color))],
                ]

            window_myrequests=sg.Window("Οι αιτήσεις μου", layout_myrequests, modal=True,resizable=True)
            
            while True:
                event,values=window_myrequests.read()
                if event=='-CLOSE-' or event==sg.WIN_CLOSED:
                    window_myrequests.close()
                    break
                # ακυρωση αιτησης
                if event=='-CANCEL-':
                    try:
                        selected_row=values['-TABLE_REQUESTS-'][0]
                        print("You have selected request: ", data_requests[selected_row])
                        bookISBN = data_requests[selected_row][1]
                        requestNum = data_requests[selected_row][3]
                        active = data_requests[selected_row][4] # ongoing/pending ΟΧΙ ή ΝΑΙ
                        if(active=="ΟΧΙ"):
                            sg.Popup("You can't cancel an old request",font=(text_font,text_size))
                        elif(active=="ΝΑΙ"):
                            try:
                                c.execute('''DELETE FROM REQUESTS where ISBN=? AND req_number = ?''',(bookISBN,requestNum,))
                                conn.commit()
                                window_myrequests.close()
                            except:
                                print()
                            try:
                                c.execute('''DELETE FROM INTERLOAN where bookISBN=? AND interloan_number = ?''',(bookISBN,requestNum,))
                                conn.commit()
                                window_myrequests.close()
                            except:
                                print()
                            
                    except:
                        sg.Popup("Choose a request to cancel it",font=(text_font,text_size))

        # οι δανεισμοι μου
        if event == '-LEND-':
            c.execute("""SELECT title, borrowed_ISBN, borrow_date, deadline_date, IIF(loan_ongoing=1,"ΝΑΙ","ΟΧΙ")
                    FROM BORROW, BOOK
                    WHERE member_ID = ? AND borrowed_ISBN=ISBN 
                   UNION
                   SELECT title, bookISBN, loan_date, deadline_date, IIF(status="approved","ΝΑΙ","ΟΧΙ")
                   FROM INTERLOAN, BOOK
                   WHERE member_ID=? AND bookISBN=ISBN""", (memberID,memberID))

            #c.execute("""SELECT title, borrowed_ISBN, BORROW.borrow_date, deadline_date
            #    FROM BORROW, BOOK
            #    WHERE BORROW.member_ID=? AND borrowed_ISBN=ISBN
            #    AND (borrowed_ISBN, BORROW.borrow_date, deadline_date) IN(
            #    SELECT borrowed_ISBN, BORROW.borrow_date, deadline_date
            #    FROM BORROW
            #    WHERE BORROW.member_ID=?
            #    EXCEPT
            #    SELECT borrowed_ISBN, BORROW.borrow_date, deadline_date
            #    FROM BORROW, RETURN
            #    WHERE BORROW.member_ID=? AND borrowed_ISBN=book_ISBN
            #    AND BORROW.borrow_date=RETURN.borrow_date
            #    AND borrowed_copy=copy_number) """, (memberID, memberID, memberID,))
            data_lend=c.fetchall()

            layout_mylend = [ 
                [sg.Table(values=data_lend, headings=headings_mylends,
                    enable_events=True,
                    auto_size_columns=False,
                    col_widths=list(map(lambda i:len(i)+20, headings)),
                    row_height = row_height,
                    justification='center',
                    key='-TABLE_LEND-',font=(text_font,text_size),vertical_scroll_only=False)],
                [sg.Button('Κλείσιμο',key='-CLOSE-',font=(text_font,text_size),button_color = (exit_color))],
                ]

            window_mylend=sg.Window("Οι δανεισμοί μου", layout_mylend, modal=True,resizable=True)
            
            while True:
                event,values=window_mylend.read()
                if event=='-CLOSE-' or event==sg.WIN_CLOSED:
                    window_mylend.close()
                    break
        
        # αιτηση αντιτυπου
        if event=='-REQUEST-':
            try:
                bookISBN=data_values[selected_row][2]
                #Παράθυρο προβολής κατάστασης αντιτύπων
                print("ISBN: ", bookISBN)
                c.execute("""SELECT dep_name, Address, copy_number
                        FROM COPY, LIBRARY
                        WHERE copy_ISBN=? 
                        AND availability='1' AND COPY.library_ID = LIBRARY.library_ID 
                        ORDER BY dep_name""", (bookISBN,))      # να δειχνει πρωτα τα αντιτυπα του παραρτηματος του, και μετα των υπολοιπων
                data_antitypa=c.fetchall()
                print("Ta antitypa:\n", data_antitypa)
                print("Epilogh aithshs: ", data_values[selected_row])

                layout_antitypa = [
                    [sg.Text(data_values[selected_row][0]+", "+data_values[selected_row][1],font=(text_font,text_size))], 
                    [sg.Table(values=data_antitypa, headings=headings_antitypa,
                        enable_events=True,
                        auto_size_columns=False,
                        col_widths=list(map(lambda i:len(i)+20, headings)),
                        row_height = row_height,
                        justification='center',
                        key='-TABLE_ANTITYPA-',font=(text_font,text_size),vertical_scroll_only=False)],
                    [sg.Button('Αίτηση δανεισμού',key='-APPLY-',	font=(text_font,text_size))],
                    [sg.Button('Κλείσιμο',key='-CLOSE-',	font=(text_font,text_size),button_color = (exit_color))],
                    ]

                window_aithsh=sg.Window("Αίτηση δανεισμού", layout_antitypa, modal=True,resizable=True)
                
                
                while True:
                    event,values=window_aithsh.read()
                    if event=='-CLOSE-' or event==sg.WIN_CLOSED:
                        window_aithsh.close()
                        break

                    if event=='-APPLY-':
                            # ελεγχος για οριο δανεισμων
                            c.execute("""SELECT title, borrowed_ISBN, borrow_date, BORROW.loan_ongoing
                                        FROM BORROW, BOOK
                                        WHERE member_ID = ? AND borrowed_ISBN=ISBN  and BORROW.loan_ongoing = 1
                                    UNION
                                    SELECT title, bookISBN, loan_date, INTERLOAN.status
                                    FROM INTERLOAN, BOOK
                                    WHERE member_ID=? AND bookISBN=ISBN and INTERLOAN.status IN ("pending","approved")  """, 
                                    (memberID,memberID,))

                            data_user_loans=c.fetchall()
                            if len(data_user_loans)>=loan_limit:
                                sg.Popup("You have exceeded the maximum of 3 active loans and/or interloans",font=(text_font,text_size))
                            # αν μπορει να κανει αιτηση:
                            else:
                                # ελεγχος αν κανει αιτηση ξανα το ιδιο εντυπο
                                c.execute('''SELECT borrowed_ISBN, BORROW.loan_ongoing
                                            FROM BORROW, BOOK
                                            WHERE member_ID = ? AND borrowed_ISBN=ISBN  and BORROW.loan_ongoing = 1
                                            UNION
                                            SELECT bookISBN,  INTERLOAN.status
                                            FROM INTERLOAN, BOOK
                                            WHERE member_ID=? AND bookISBN=ISBN and INTERLOAN.status IN ("pending","approved")
                                            UNION
                                            SELECT REQUESTS.ISBN,  REQUESTS.ongoing
                                            FROM REQUESTS, BOOK
                                            WHERE memberID=? AND REQUESTS.ISBN=BOOK.ISBN and REQUESTS.ongoing = 1 '''
                                            ,(memberID,memberID,memberID,))
                                data_prev_isbn = c.fetchall()
                                if(len(data_prev_isbn)>0 and data_prev_isbn[0][0] == bookISBN):
                                    sg.Popup("You already have an active request or loan of this book",font=(text_font,text_size))

                                else:
                                    c.execute('''SELECT min(copy_number)
                                                FROM COPY
                                                WHERE library_ID=? AND copy_ISBN=?''',(library_ID,bookISBN,))
                                    data_libID=c.fetchall()

                                    if(data_libID[0][0])!=None:
                                        request+=1
                                        # print("Antitypo selected: ",data_antitypa[selected_row])   

                                        c.execute("""INSERT INTO REQUESTS VALUES(?,?,?,?,?)"""
                                        ,(bookISBN, memberID, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request,1,))

                                        ################## αλλαγη διαθεσιμοτητας στην αιτηση
                                        
                                        # c.execute('''UPDATE ΑΝΤΙΤΥΠΟ set διαθεσιμότητα='0' where κωδ_εντύπου=? AND αρ_αντιτύπου= 
                                        # (SELECT min(αρ_αντιτύπου) FROM ΑΝΤΙΤΥΠΟ WHERE κωδ_εντύπου=? AND διαθεσιμότητα='1')''',(bookISBN,bookISBN,))
                                        conn.commit()
                                        window_aithsh.close()
                                    else:
                                        interloan_number+=1
                                        #c.execute('''SELECT min(copy_number),library_ID
                                        #        FROM COPY
                                        #        WHERE copy_ISBN=?''',(bookISBN,))
                                        copy_data=best_available_copy(bookISBN, library_ID)
                                        print(copy_data)
                                        #copy_data=c.fetchall()[0]
                                        copy_num=copy_data[0]
                                        copy_libID=copy_data[1]

                                        print("copy_data interloan line 622: ",copy_num, copy_libID)
                                        status = 'pending'

                                        c.execute("""INSERT INTO INTERLOAN VALUES(?,?,?,?,?,?,?,?,?,?)"""
                                        ,(memberID,bookISBN,copy_num, copy_libID,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"","","",status,interloan_number))
                                        c.execute("""UPDATE COPY SET availability='0' WHERE copy_number=? AND copy_ISBN=? """,(copy_num, bookISBN,))
                                        # απευθειας δεσμευση ελευθερου αντιτυπου για να γινει ο διαδανεισμος πιο γρηγορα
                                        conn.commit()
                                        print("success interloan")
                                        window_aithsh.close()
            except:
               sg.Popup("Choose a book to make a request",font=(text_font,text_size))    
            
                
            #window.close()
            
            #c.execute('''UPDATE ΑΝΤΙΤΥΠΟ set διαθεσιμότητα='0' where κωδ_εντύπου = ? AND αρ_αντιτύπου=?''',(data_values[selected_row][2], data_antitypa[selected_row][1],))
            #conn.commit()
            #c.execute("""SELECT Τίτλος, Συγγραφέας, ISBN, sum(διαθεσιμότητα='1')
            #    FROM ΕΝΤΥΠΟ, ΑΝΤΙΤΥΠΟ
            #    WHERE Τίτλος  LIKE ?
            #    AND ISBN=κωδ_εντύπου AND διαθεσιμότητα='1' GROUP BY κωδ_εντύπου""",(f'%{values[0]}%',))
            #new_values=c.fetchall()
            #window['-TABLE-'].update(values=new_values)    
        # elif event=='-LEND-':
        #     print("You did not select any book!")
        



############################################################################################## αν γινει sign in, κομματι υπαλληλου

if(account=="employee"):
    c.execute('''SELECT dep_name FROM EMPLOYEE as E, LIBRARY as L WHERE E.library_ID = L.library_ID AND
    E.employee_ID = ?''',(employeeID,))
    library_dept = c.fetchall()[0][0]
 
    c.execute('''SELECT E.library_ID FROM EMPLOYEE as E, LIBRARY as L WHERE E.library_ID = L.library_ID AND
    E.employee_ID = ?''',(employeeID,))
    library_ID = c.fetchall()[0][0]

    c.execute('''SELECT emp_name || ' ' || emp_last_name FROM EMPLOYEE as E WHERE E.employee_ID = ?''',(employeeID,))
    emp_name = c.fetchall()[0][0]

    layout_dept=[sg.Push(),sg.Text("ΥΠΑΛΛΗΛΟΣ: "+ emp_name + ", "+ library_dept, font=(text_font,text_size)),sg.Push()]

    layout_employee[0].insert(0,layout_dept)
    window=sg.Window('Δίκτυο Δανειστικών Βιβλιοθηκών ΗΜΤΥ - Παράρτημα: '+library_dept,layout_employee ,size=(1400,1050),resizable=True)

    while True:
        event,values=window.read()
        if event==sg.WIN_CLOSED or event=='Έξοδος':
            break
        if event=='-SEARCH_BOOK-':

            # 1) για αναζητηση εντυπου
            if values['board']=='Τίτλος':
                employee_search_title(f'%{values[0]}%',library_ID)

            if values['board']=='Συγγραφέας':
                employee_search_author(f'%{values[0]}%',library_ID)

            if values['board']=='ISBN':
                employee_search_ISBN(f'%{values[0]}%',library_ID)

            if values['board']=='Έτος έκδοσης':
                employee_search_year(f'%{values[0]}%',library_ID)

            if values['board']=='DDC':
                try:
                    employee_search_DDC(f'%{values[0]}%',library_ID)
                except:
                    sg.Popup("Input a correct DDC number",font=(text_font,text_size))
            data=c.fetchall()
            # data.insert(0, headings_employee2) 
            data_values=data
            window['-TABLE-'].update(values=data_values)
        if event=='-SEARCH_USER-':
            # 2) για αναζητηση χρηστη
            if values['members']=='Όνομα':
                employee_search_name(f'%{values[1]}%',library_ID)

            if values['members']=='Επώνυμο':
                employee_search_surname(f'%{values[1]}%',library_ID)

            if values['members']=='ID μέλους':
                employee_search_userid(f'%{values[1]}%',library_ID)

            if values['members']=='Email':
                employee_search_email(f'%{values[1]}%',library_ID)

            data2=c.fetchall()
            # data.insert(0, headings_employee2) 
            # columns = list(map(lambda x: x[0], c.description))
            # data.insert(0, columns)
            data_user_values=data2
            window['-TABLE2-'].update(values=data_user_values)

        if event=='-TABLE-':
            selected_row=values['-TABLE-'][0]
            print("You have selected: ", data_values[selected_row])

        if event=='-TABLE2-':
            users_row=values['-TABLE2-'][0]
            print("You have selected: ", data_user_values[users_row])
            
        # ολες οι αιτησεις του παραρτηματος για επιλεγμενο εντυπο (τωρα δειχνει για ολα τα παραρτηματα)
        if event=='-APPLICATIONS-':
            try:
                bookISBN=data_values[selected_row][2]

                c.execute("""SELECT ISBN, memberID, req_date, req_number
                    FROM REQUESTS, MEMBER 
                    WHERE memberID=member_ID
                    AND ISBN=? AND ongoing=1 AND library_ID=?
                    ORDER BY library_ID, req_number""",(bookISBN, library_ID,))
                list_of_applications=c.fetchall()
                data_apps=list_of_applications
                print(list_of_applications)

                #οι αριθμοί των διαθέσιμων αντιτύπων
                copy_data=c.execute("""SELECT copy_number FROM COPY WHERE copy_ISBN=? 
                AND library_ID=? AND availability='1'""",(bookISBN, library_ID,)).fetchall()
                print(copy_data)
                copy_params=[]
                        
                for i in range(0,len(copy_data)):
                    copy_params.append(copy_data[i][0])

                #Οι χρήστες που έχουν κάνει αίτηση για αυτό το έντυπο
                user_id=[]
                for j in range(0,len(list_of_applications)):
                    user_id.append(list_of_applications[j][1])

                print(user_id)
                
                layout_apps= [
                    [sg.Text(data_values[selected_row][0]+", "+data_values[selected_row][1],font=(text_font,text_size))], 
                    [sg.Table(values=data_apps, headings=headings_apps,
                        enable_events=True,
                        auto_size_columns=False,
                        col_widths=list(map(lambda i:len(i)+20, headings)),
                        row_height = row_height,
                        justification='center',
                        key='-TABLE_REQUESTS-',font=(text_font,text_size),vertical_scroll_only=False)],
                    [sg.Text("Επιλέξτε το αντίτυπο που θέλετε να δανείσετε", font=(text_font, text_size))],
                    [sg.Combo(copy_params, default_value=copy_params[0],key='copy_number',size=(20,10),font=(text_font,text_size))],
                    [sg.Text("Επιλέξτε τον χρήστη στον οποίο θέλετε να το δανείσετε", font=(text_font, text_size))],
                    [sg.Combo(user_id, default_value=user_id[0],key='user_id',size=(20,10),font=(text_font,text_size))],
                    [sg.Button('Ανάθεση αντιτύπου',key='-COPY-',font=(text_font,text_size))],
                    [sg.Button('Κλείσιμο',key='-CLOSE-',font=(text_font,text_size),button_color = (exit_color))],
                    #[sg.Button('Αίτηση δανεισμού',key='-APPLY-',	font=(text_font,text_size))]
                    ]
                
                windowApps=sg.Window("Αιτήσεις εντύπου", layout_apps, modal=True,resizable=True)
                
                while True:
                    event,values=windowApps.read()
                    if event=='-CLOSE-' or event==sg.WIN_CLOSED:
                        windowApps.close()
                        break

                    if event=='-COPY-':
                        print(values['user_id'], bookISBN, values['copy_number'])
                        c.execute("""INSERT INTO BORROW VALUES(?,?,?,?,?,?)"""
                        , (values['user_id'], bookISBN, values['copy_number'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        , (datetime.now()+delta).strftime("%Y-%m-%d %H:%M:%S"),1,)) 
                        conn.commit()
                        c.execute("""UPDATE COPY SET availability='0' WHERE copy_ISBN=? AND copy_number=?""",(bookISBN, values['copy_number']))
                        conn.commit()
                        c.execute("""UPDATE REQUESTS SET ongoing=0 WHERE ISBN=? AND memberID=?""",(bookISBN, values['user_id']))
                        conn.commit()
                        #windowApps['-TABLE_REQUESTS-'].update(list_of_applications)
                        windowApps.close()
                        #windowApps.Refresh()

                        
            except:
                sg.Popup("Choose a book first to see its requests",font=(text_font,text_size))

        if event=='-USER_REQUESTS-':

            try:    
                member_ID=data_user_values[users_row][2]
                c.execute("""SELECT title, REQUESTS.ISBN, req_date, req_number, IIF(ongoing=1,"ΝΑΙ","ΟΧΙ")
                    FROM REQUESTS, BOOK
                    WHERE REQUESTS.memberID = ? AND REQUESTS.ISBN=BOOK.ISBN
                    GROUP BY req_date
                    ORDER BY ongoing DESC, req_date DESC """,(member_ID,))

                list_of_user_applications=c.fetchall()
                print(list_of_user_applications)

                layout_user_requests = [
                    [sg.Text("Αιτήσεις του χρήστη: "+data_user_values[users_row][0]+" "+data_user_values[users_row][1], font=(text_font,text_size))],
                    [sg.Table(values=list_of_user_applications, headings=headings_myrequests,
                    enable_events=True,
                    auto_size_columns=False,
                    col_widths=list(map(lambda i:len(i)+20, headings)),
                    row_height = row_height,
                    justification='center',
                    key='-TABLE_REQUESTS-',font=(text_font,text_size),vertical_scroll_only=False)],
                    [sg.Button('Κλείσιμο',key='-CLOSE-',font=(text_font,text_size),button_color = (exit_color))],
                    ]

                windowUserReq=sg.Window("Αιτήσεις του χρήστη: "+data_user_values[users_row][0]+data_user_values[users_row][1],layout_user_requests,modal=True, resizable=True)

                while True:
                    event,values=windowUserReq.read()
                    if event=='-CLOSE-' or event==sg.WIN_CLOSED:
                        windowUserReq.close()
                        break
                    #windowUserReq.close()    
            except:
                sg.Popup("Select a user first to see their requests",font=(text_font,text_size))

        if event=='-USER_LOANS-':

            try:
                member_ID=data_user_values[users_row][2]
                c.execute("""SELECT title, borrowed_ISBN, borrow_date, deadline_date
                        FROM BORROW, BOOK
                        WHERE member_ID = ? AND borrowed_ISBN=ISBN 
                        ORDER BY borrow_date DESC, borrowed_ISBN""", (member_ID,))

                #c.execute("""SELECT title, borrowed_ISBN, BORROW.borrow_date, deadline_date
                #FROM BORROW, BOOK
                #WHERE BORROW.member_ID=? AND borrowed_ISBN=ISBN
                #AND (borrowed_ISBN, BORROW.borrow_date, deadline_date) IN(
                #SELECT borrowed_ISBN, BORROW.borrow_date, deadline_date
                #FROM BORROW
                #WHERE BORROW.member_ID=?
                #EXCEPT
                #SELECT borrowed_ISBN, BORROW.borrow_date, deadline_date
                #FROM BORROW, RETURN
                #WHERE BORROW.member_ID=? AND borrowed_ISBN=book_ISBN
                #AND BORROW.borrow_date=RETURN.borrow_date
                #AND borrowed_copy=copy_number) """, (member_ID, member_ID, member_ID,))
                data_user_lend=c.fetchall()

                layout_user_lend = [ 
                    [sg.Text("Δανεισμοί του χρήστη: "+data_user_values[users_row][0]+" "+data_user_values[users_row][1], font=(text_font,text_size))],
                    [sg.Table(values=data_user_lend, headings=headings_mylends,
                        enable_events=True,
                        auto_size_columns=False,
                        col_widths=list(map(lambda i:len(i)+20, headings)),
                        row_height = row_height,
                        justification='center',
                        key='-TABLE_LEND-',font=(text_font,text_size),vertical_scroll_only=False)],
                    [sg.Button('Κλείσιμο',key='-CLOSE-',font=(text_font,text_size),button_color = (exit_color))],
                    ]

                window_user_lend=sg.Window("Δανεισμοί του χρήστη: "+data_user_values[users_row][0]+data_user_values[users_row][1], layout_user_lend, modal=True,resizable=True)
                
                while True:
                    event,values=window_user_lend.read()
                    if event=='-CLOSE-' or event==sg.WIN_CLOSED:
                        window_user_lend.close()
                        break
            except:
                sg.Popup("Select a user first to see their loans",font=(text_font,text_size))
            
        #Προβολή και έγκριση αιτημάτων διαδανεισμού από άλλα παραρτήματα
        if event=='-INTERLOAN_REQUESTS-':

            c.execute("""SELECT I.bookISBN, I.member_ID, mem_name, mem_last_name, req_date, dep_name, status
                FROM INTERLOAN as I, MEMBER as M, LIBRARY as L
                WHERE  M.member_ID=I.member_ID AND M.library_ID=L.library_ID and I.library_ID = ?""",(library_ID,))
            data_interloan=c.fetchall()

            # Για τη σελίδα προβολής αιτημάτων διαδανεισμού
            layout_interloan = [
                [sg.Text("Αιτήσεις για διαδανεισμό από χρήστες αλλων παραρτημάτων", font=(text_font, text_size))],
                [sg.Table(values=data_interloan, headings=headings_interloan,
                        enable_events=True,
                        auto_size_columns=False,
                        col_widths=list(map(lambda i:len(i)+20, headings)),
                        row_height = row_height,
                        justification='center',
                        key='-TABLE_INTERLOAN-',font=(text_font,text_size),vertical_scroll_only=False)],
                [sg.Button('Έγκριση αιτήματος',key='-VERIFY-',font=(text_font,text_size),button_color = (cancel_color)),sg.Push(),
                sg.Button('Κλείσιμο',key='-CLOSE-',font=(text_font,text_size),button_color = (exit_color))],
                ]

            window_interloan=sg.Window("Αιτήσεις για διαδανεισμό",layout_interloan, modal=True, resizable=True,size=(1400,500))
            while True:
                event,values=window_interloan.read()
                if event=='-CLOSE-' or event==sg.WIN_CLOSED:
                    window_interloan.close()
                    break
                if event=='-TABLE_INTERLOAN-':
                    interloan_row=values['-TABLE_INTERLOAN-'][0]
                # έγκριση αιτήματος
                if event=='-VERIFY-':
                    try:
                        print("You have selected interloan: ", data_interloan[interloan_row])
                        status = data_interloan[interloan_row][6]
                        if(status!="pending"):
                            sg.Popup("You can't approve an approved or completed interloan",font=(text_font,text_size))
                        else:
                            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            return_time=(datetime.now()+delta).strftime("%Y-%m-%d %H:%M:%S")
                            # c.execute(""" UPDATE COPY SET availability=0 WHERE copy_num=? AND bookISBN=?""",(min_avail_copy, data_interloan[interloan_row][0],))
                            c.execute('''UPDATE INTERLOAN SET loan_date = ?, deadline_date =?, status="approved" ''',(now_time, return_time))
                            conn.commit()
                            window_interloan.close()
                    except:
                        sg.Popup("If there are interloan requests, choose one first to approve it",font=(text_font,text_size))
                    
        
        # Οι τρέχοντες δανεισμοί των μελων του τρεχοντος παραρτηματος
        if event=='-LOANS-':

            #c.execute("""SELECT mem_name, mem_last_name, BORROW.member_ID, title, BOOK.ISBN, 
            #    borrowed_copy, borrow_date, deadline_date
            #    FROM BORROW, MEMBER, BOOK
            #    WHERE BORROW.member_ID=MEMBER.member_ID 
            #    AND ISBN=borrowed_ISBN AND  MEMBER.library_ID=?""",(library_ID,))
            c.execute("""SELECT mem_name, mem_last_name, BORROW.member_ID, title, borrowed_ISBN,
                borrowed_copy, borrow_date, deadline_date
                FROM MEMBER, BOOK, BORROW
                WHERE BORROW.member_ID=MEMBER.member_ID
                AND ISBN=BORROW.borrowed_ISBN AND MEMBER.library_ID=?
                AND (BORROW.member_ID, borrowed_ISBN, borrowed_copy,
                borrow_date) IN(
                SELECT BORROW.member_ID, borrowed_ISBN,
                borrowed_copy, borrow_date
                FROM BORROW
                EXCEPT
                SELECT BORROW.member_ID, borrowed_ISBN, borrowed_copy, BORROW.borrow_date
                FROM BORROW JOIN RETURN ON BORROW.member_ID=RETURN.member_ID
                AND borrowed_ISBN=book_ISBN AND borrowed_copy=copy_number 
                AND BORROW.borrow_date=RETURN.borrow_date) """,(library_ID,))

            list_of_loans=c.fetchall()
            loan_values=list_of_loans
            print(loan_values)
            
            layout_loans=[
                [sg.Text("Οι δανεισμοί για το παράρτημα "+library_dept,font=(text_font,text_size))],
                [sg.Table(values=loan_values, headings=headings_loan,
                          enable_events=True,
                        auto_size_columns=False,
                        col_widths=list(map(lambda i:len(i)+20, headings)),
                        row_height = row_height,
                        justification='center',
                        key='-TABLE_CURRENT_LOANS-',font=(text_font,text_size),vertical_scroll_only=False)],
                [sg.Button("Επιστροφή αντιτύπου",key='-RETURN_COPY-',font=(text_font,text_size),button_color = (cancel_color))],
                [sg.Button("Κλείσιμο",key='-CLOSE-',font=(text_font,text_size),button_color = (exit_color))]
                ]

            windowLoans=sg.Window("Δανεισμοί-"+library_dept, layout_loans, modal=True, resizable=True,size=(1800,500))

            while True:
                event,values=windowLoans.read()
                if event=='-CLOSE-' or event==sg.WIN_CLOSED:
                    windowLoans.close()
                    break

                if event=='-TABLE_CURRENT_LOANS-':
                    loan_row=values['-TABLE_CURRENT_LOANS-'][0]
                    loan_memberID = loan_values[loan_row][2]

                if event=='-RETURN_COPY-':
                    try:
                        c.execute("""UPDATE BORROW SET loan_ongoing=0 WHERE member_ID=? AND borrowed_copy=? AND borrowed_ISBN=?"""
                                ,(loan_values[loan_row][2], loan_values[loan_row][5], loan_values[loan_row][4],))
                        
                        c.execute("""UPDATE COPY SET availability='1' WHERE copy_ISBN=? AND copy_number=?""",(loan_values[loan_row][4], loan_values[loan_row][5],))
                        conn.commit()

                        c.execute("""INSERT INTO RETURN VALUES(?,?,?,?,?)""",(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), loan_values[loan_row][2], loan_values[loan_row][4],
                                                                                 loan_values[loan_row][5],loan_values[loan_row][6],))
                        conn.commit()
                        windowLoans.close()

                    except:
                        sg.Popup("Choose the copy you want to return",font=(text_font,text_size))

                    
            
        #if event=='-PRIORITY-':

        #    bookISBN=data_values[selected_row][2]

        # αυτοματη αναθεση αντιτυπων στις αιτησεις (δανεισμος)
        if event=='-ASSIGN-':
            allISBN=[]
            listISBN=c.execute("""SELECT DISTINCT REQUESTS.ISBN
            FROM REQUESTS, MEMBER
            WHERE REQUESTS.memberID=MEMBER.member_ID
            AND MEMBER.library_ID=? AND ongoing=1""",(library_ID,)).fetchall()

            for i in range(len(listISBN)):
                allISBN.append(listISBN[i][0])

            print(allISBN)

            starting_copy=0
            current_copy=0
            for i in range(len(listISBN)):
                starting_copy=c.execute("""SELECT MIN(copy_number)
                            FROM COPY
                            WHERE copy_ISBN=? AND library_ID=?
                            AND availability=1""",
                            (allISBN[i],library_ID,)).fetchall()[0][0]
    #fin_copy=c.execute("""SELECT MAX(copy_number)
    #                FROM COPY
    #                WHERE copy_ISBN=? AND library_ID=2
    #                AND availability=1""",
    #                   (listISBN[i],)).fetchall()[0][0]
                current_copy=starting_copy
                while current_copy!=None:
                    try:
                        priority_member=c.execute("""SELECT REQUESTS.memberID
                                FROM REQUESTS JOIN MEMBER ON REQUESTS.memberID=MEMBER.member_ID
                                WHERE ISBN=? AND ongoing=1 AND library_ID=?
                                ORDER BY req_date
                                LIMIT 1""",(allISBN[i],library_ID,)).fetchall()[0][0]
        
                        print("Priority member: ",priority_member)

                        c.execute("""UPDATE COPY SET availability='0' WHERE
                        copy_ISBN=? AND copy_number=?""",
                        (allISBN[i], current_copy,))
                        conn.commit()
                        c.execute("""UPDATE REQUESTS SET ongoing=0 WHERE ISBN=?
                        AND memberID=?""",(allISBN[i], priority_member,))
                        conn.commit()

                        return_time=(datetime.now()+delta).strftime("%Y-%m-%d %H:%M:%S")
                        c.execute("""INSERT INTO BORROW VALUES(?,?,?,?,?,1)""",(priority_member,
                            allISBN[i], current_copy, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            return_time,))
                        conn.commit()

                        print("INSERT: ", priority_member, current_copy, allISBN[i])

                        current_copy=c.execute("""SELECT MIN(copy_number)
                            FROM COPY
                            WHERE copy_ISBN=? AND library_ID=?
                            AND availability=1""",
                            (allISBN[i],library_ID,)).fetchall()[0][0]

                    except IndexError:
                        break

        if event=='-EXPIRED-':
            data_expired=c.execute("""SELECT BORROW.member_ID, mem_name, mem_last_name, borrowed_ISBN,
                borrow_date, deadline_date
                FROM BORROW, MEMBER
                WHERE BORROW.member_ID=MEMBER.member_ID AND 
                deadline_date<datetime('now') AND loan_ongoing=1 AND library_ID=?""",(library_ID,)).fetchall()

            headings_expired=['ID μέλους', 'Όνομα', 'Επώνυμο', 'ISBN', 'Ημ δανεισμού', 'Ημ λήξης']

            layout_expired=[
                [sg.Text("Οι καθυστερήσεις για το παράρτημα", font=(text_font,text_size))],
                [sg.Table(values=data_expired, headings=headings_expired,
                          enable_events=True,
                        auto_size_columns=False,
                        col_widths=list(map(lambda i:len(i)+20, headings)),
                        row_height = row_height,
                        justification='center',
                        key='-TABLE_EXPIRED-',font=(text_font,text_size),vertical_scroll_only=False)],
                [sg.Button("Κλείσιμο",key='-CLOSE-',font=(text_font,text_size),button_color = (exit_color))]
                
                ]
            windowExpired=sg.Window("Καθυστερήσεις", layout_expired, modal=True, resizable=True, size=(1400,500))

            while True:
                event,values=windowExpired.read()
                if event=='-CLOSE-' or event==sg.WIN_CLOSED:
                    windowExpired.close()
                    break
            

        # προσθηκη χρηστη στην βαση       
        if event == '-ADD_USER-':
            departments = ["Αθήνα", "Πάτρα","Θεσσαλονίκη","Ιωάννινα","Ηράκλειο","Βόλος","Χανιά","Λάρισα","Τρίκαλα","Ξάνθη"]
            users=["Μέλος", "Υπάλληλος"]

            layout_adduser = [	
                [sg.Text('Εισάγετε στοιχεία χρήστη: ', font=(text_font,text_size))], [sg.VPush()],	
                [sg.Text('Όνομα',size=(15,1),font=(text_font,text_size)),sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                [sg.Text('Επώνυμο',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                [sg.Text('Email',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                [sg.Text('Βιβλιοθήκη:',size=(15,1),font=(text_font,text_size)),sg.Combo(departments,default_value='Πάτρα',key='depts',size=(20,10),font=("Courier",18))],[sg.VPush()],
                [sg.Text('Τύπος χρήστη:',size=(15,1),font=(text_font,text_size)),sg.Combo(users,default_value='Μέλος',key='users',size=(20,10),font=("Courier",18))],[sg.VPush()],
                
                [sg.Button("Εισαγωγή",key="Εισαγωγή",font=(text_font,text_size)),sg.VPush(),sg.Button('Έξοδος',font=(text_font,text_size),button_color = (exit_color))],	
            ]	
            window_adduser = sg.Window("Εισαγωγή δανειζόμενου", layout_adduser, size=(500,500),modal=True,resizable=True)

            while True:
                event, values = window_adduser.read()	
                if event=="Έξοδος"or event==sg.WIN_CLOSED:
                    window_adduser.close()
                    break

                if	event == "Εισαγωγή" and values['depts'] in departments and values['users'] in users and values[0]!="" and values[1]!="" and values[2]!="":	
                    
                    if(values["users"]=="Μέλος"):
                        try:
                            userID = c.execute('SELECT max(member_ID) FROM MEMBER')
                            userID = int(c.fetchall()[0][0])
                        except:
                            userID = 999
                        userID+=1
                        conn.execute('''INSERT	INTO	MEMBER	VALUES	(?,	?,	?,	?, ?,?);''',	
                        (userID,	values[0],	values[1],	values[2], departments.index(values['depts'])+1,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")));
                        conn.commit()
                        cursor = conn.cursor()	
                        cursor.execute("SELECT * FROM MEMBER  WHERE member_ID = ?",(userID,))
                        data = cursor.fetchall()
                        print("USER: ", data)	
                        window_adduser.close()
                        sg.Popup(f"Your member ID is: {userID}",font=(text_font,text_size))

                    elif(values["users"]=="Υπάλληλος" ):
                        try:
                            userID = c.execute('SELECT max(employee_ID) FROM EMPLOYEE')
                            userID = int(c.fetchall()[0][0])
                            print(userID)
                        except:
                            userID = 100
                        userID+=1
                        conn.execute('''INSERT	INTO	EMPLOYEE	VALUES	(?,	?,	?,	?, ?,?);''',	
                        (userID,	values[0],	values[1],	values[2], departments.index(values['depts'])+1,random.randint(10000,20000)));
                        conn.commit()
                        cursor = conn.cursor()	
                        cursor.execute("SELECT * FROM EMPLOYEE  WHERE employee_ID = ?",(userID,))
                        data = cursor.fetchall()
                        print("EMPLOYEE: ", data)	
                        window_adduser.close()
                        sg.Popup(f"Your member ID is: {userID}",font=(text_font,text_size))
                    
                else:
                    sg.Popup("Error: input the correct user fields",font=(text_font,text_size))
                    continue

        # προσθηκη εντύπου στην βαση, μαζι με τα τυχαια αντιτυπα του    
        if event == '-ADD_BOOK-':
            collections = ["Αποθετήριο βιβλιοθήκης","Magazines - Calendars", "Rare literature books","Poems","Rules and laws","Historic"]
            layout_addbook = [	
                    [sg.Text('Εισάγετε στοιχεία εντύπου: ', font=(text_font,text_size))], [sg.VPush()],	
                    [sg.Text('ISBN', font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                    [sg.Text('Τίτλος',size=(15,1),font=(text_font,text_size)),sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                    [sg.Text('Συγγραφέας',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                    [sg.Text('Αρ. Σελιδών',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                    [sg.Text('DDC',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                    [sg.Text('Έκδοση',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                    [sg.Text('Έτος έκδοσης',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                    [sg.Text('Εκδότης',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                    [sg.Text('Γλώσσα',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                    [sg.Text('Μεταφραστής',size=(15,1),font=(text_font,text_size)), sg.InputText(font=(text_font,text_size))], [sg.VPush()],	
                    [sg.Text('Συλλογή:',size=(15,1),font=(text_font,text_size)),sg.Combo(collections,default_value='Αποθετήριο βιβλιοθήκης',key='collections',size=(40,10),font=("Courier",18))],[sg.VPush()],
                    [sg.Button("Εισαγωγή",key="Εισαγωγή",font=(text_font,text_size)),sg.VPush(),sg.Button('Έξοδος',font=(text_font,text_size),button_color = (exit_color))],	
            ]
                
            window_addbook = sg.Window("Εισαγωγή εντύπου", layout_addbook, size=(600,550),modal=True,resizable=True)
            while True:
                event, values = window_addbook.read()	
                if event=="Έξοδος"or event==sg.WIN_CLOSED:
                    window_addbook.close()
                    break

                if	event == "Εισαγωγή" and values[0]!="" and values[1]!="" and values[2]!="" and values[3]!="" and values[4]!="" and values[5]!="" and values[6]!="" and values[7]!="" and values[8]!="":	
                    cursor = conn.cursor()	
                    conn.execute("""INSERT INTO BOOK VALUES(?,?,?,?,?,?,?,?,?,?,?)"""
                    ,(values[0],values[1],values[2],int(values[3]),values[4],values[5],values[6],values[7],values[8],values[9],collections.index(values["collections"]),))
                    conn.commit()
                    for i in range(random.randint(1,9)):
                        conn.execute("""INSERT INTO COPY VALUES(?,?,?,?)""",(i, values[0], random.randint(1,10), '1'))
                        conn.commit()
                    cursor.execute("SELECT * FROM BOOK  WHERE ISBN = ?",(values[0],))
                    data = cursor.fetchall()
                    print("BOOK: ", data)	
                    window_addbook.close()
                    break
                else:
                    sg.Popup("Error: input the correct book fields",font=(text_font,text_size))
                    continue

        # custom εκτελεση query
        if event == '-QUERY_SEARCH-':
                layout_query_first = [
                    [sg.Text('Εισάγετε το query σας: ',font=(text_font,text_size))],
                    [sg.Multiline(font=(text_font,text_size),size=(200,10),key="-TABLE_QUERY-", right_click_menu=[[''], ['Paste']]),sg.VPush()],
                    [sg.Button("Εκτέλεση query",key="-QUERY_SEARCH2-",font=(text_font,text_size),button_color = (search_color)), sg.Push(),sg.Button('Κλείσιμο',key="-CLOSE1-",font=(text_font,text_size),button_color = (exit_color))],	
                ]

                window_query_first=sg.Window("Εκτέλεση query", layout_query_first, size=(1400,400),modal=True,resizable=True)
    
                while True:
                    event, values = window_query_first.read()	
                    if event=='-CLOSE1-' or event==sg.WIN_CLOSED:
                        window_query_first.close()
                        break
                    if event == '-QUERY_SEARCH2-':
                        try:
                            c.execute(f'''{values["-TABLE_QUERY-"]}''')
                            conn.commit()
                            data = c.fetchall()
                            columns = list(map(lambda x: x[0], c.description))
                            headings_query=columns
                            data_query=data
                            # for line in data_query:
                            #     print(line)
                            layout_query_second = [
                                [sg.Table(values=data_query, headings=headings_query,
                                    enable_events=True,
                                    auto_size_columns=False,
                                    col_widths = list(map(lambda x:len(x)+20, headings)),
                                    row_height = 25,
                                    justification='center',
                                    key='-TABLE_QUERY2-',font=(text_font,text_size),
                                    vertical_scroll_only=False, 
                                    right_click_menu=[[''], ['Paste']])],
                                [sg.Button('Κλείσιμο',key='-CLOSE2-',font=(text_font,text_size),button_color = (exit_color))],
                                ]

                            window_query_second=sg.Window("SQL QUERY", layout_query_second, size=(1400,400),modal=True,resizable=True,finalize=True)
                
                            while True:
                                event, values = window_query_second.read()	
                                if event=='-CLOSE2-' or event==sg.WIN_CLOSED:
                                    window_query_second.close()
                                    break
                                if event == 'Paste':
                                    window_query_first['-TABLE_QUERY2-'].update(sg.clipboard_get(), paste=True)
                        except:
                            sg.Popup("Error: input a correct sqlite query",font=(text_font,text_size))                
                    
        
###################### close db and app
conn.commit()
conn.close()
window.close() #window = το παραθυρο του μελους ή του υπαλληλου
