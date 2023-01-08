headings=['Τίτλος','Συγγραφέας','ISBN','διαθ. αντίτυπα',"DDC","Κατηγορία","Συλλογή"]
headings_employee=['Τίτλος','Συγγραφέας','ISBN','Αρ. αντιτ. παραρτ.',"Αρ. διαθεσ. αντιτ.","DDC","Κατηγορία"]
headings_employee2=["Όνομα","Επώνυμο","ID μέλους","Email","Ημ/νια εγγραφής"]

headings_antitypa=['Παράρτημα',"Οδός παραρτήματος",'Αρ. αντιτύπου']
headings_myrequests=["Τίτλος", "ISBN","Ημ/νία αίτησης","Αρ. αίτησης","Τρέχουσα"] 
headings_mylends = ["Τίτλος", "ISBN","Ημ/νία δανεισμού","Καταληκτική ημ/νία επιστροφής","Τρέχων"]
headings_apps=['ISBN', 'ID μέλους', 'Ημ/νία αιτησης', 'Αριθμός αίτησης']
headings_members=["ID μέλους","Όνομα μέλους","Επίθετο μέλους","Email","Αρ. αιτήσεων"]
headings_loan=["Όνομα μέλους","Επίθετο μέλους","ID μέλους","Τίτλος εντύπου","ISBN","Αρ. αντιτύπου","Ημ. έναρξης δανεισμού", "Ημ. λήξης προθεσμίας"]
headings_interloan=['ISBN', 'ID μέλους', 'Όνομα', 'Επώνυμο', 'Ημ αίτησης', 'Παράρτημα', 'Status']

search_users=["Όνομα","Επώνυμο","ID μέλους","Email"]
search_params=["Τίτλος", "Συγγραφέας", "ISBN","Έτος έκδοσης","DDC","Συλλογές"]
search_params2= ["","Γενικά θέματα", "Φιλοσοφία και ψυχολογία","Θρησκεία","Κοινωνικές επιστήμες","Γλώσσα",
                "Φυσικές επιστήμες και μαθηματικά","Τεχνολογία ","Τέχνες και διασκέδαση","Λογοτεχνία","Ιστορία και γεωγραφία"]


depts_names=["Αθήνα",
    "Πάτρα",
    "Θεσσαλονίκη",
    "Ιωάννινα",
    "Ηράκλειο",
    "Βόλος",
    "Χανιά",
    "Λάρισα",
    "Τρίκαλα",
    "Ξάνθη"]

depts=[
    ["Αθήνα",1],
    ["Πάτρα",2],
    ["Θεσσαλονίκη",3],
    ["Ιωάννινα",4],
    ["Ηράκλειο",5],
    ["Βόλος",6],
    ["Χανιά",7],
    ["Λάρισα",8],
    ["Τρίκαλα",9],
    ["Ξάνθη",10]
    ]



distances=[['Αθήνα', 'Πάτρα', 211],
['Αθήνα', 'Θεσσαλονίκη', 501], ['Αθήνα', 'Ιωάννινα', 411],['Αθήνα', 'Ηράκλειο', 339],['Αθήνα', 'Βόλος', 328], ['Αθήνα', 'Χανιά', 323],
['Αθήνα', 'Λάρισα', 353], ['Αθήνα', 'Τρίκαλα', 327],['Αθήνα', 'Ξάνθη', 703],['Πάτρα', 'Θεσσαλονίκη', 466], ['Πάτρα', 'Ιωάννινα', 217],
['Πάτρα', 'Ηράκλειο', 541], ['Πάτρα', 'Βόλος', 300],['Πάτρα', 'Χανιά', 525], ['Πάτρα', 'Λάρισα', 323],['Πάτρα', 'Τρίκαλα', 230], ['Πάτρα', 'Ξάνθη', 426],
['Θεσσαλονίκη', 'Ιωάννινα', 261],['Θεσσαλονίκη', 'Ηράκλειο', 838], ['Θεσσαλονίκη', 'Βόλος', 211],['Θεσσαλονίκη', 'Χανιά', 822], ['Θεσσαλονίκη', 'Λάρισα', 151],
['Θεσσαλονίκη', 'Τρίκαλα', 213], ['Θεσσαλονίκη', 'Ξάνθη', 205],['Ιωάννινα', 'Ηράκλειο', 741],['Ιωάννινα', 'Βόλος', 247], 
['Ιωάννινα', 'Χανιά', 725],['Ιωάννινα', 'Λάρισα', 185], ['Ιωάννινα', 'Τρίκαλα', 124],
['Ιωάννινα', 'Ξάνθη', 462],['Ηράκλειο', 'Βόλος', 667], ['Ηράκλειο', 'Χανιά', 142],['Ηράκλειο', 'Λάρισα', 690], ['Ηράκλειο', 'Τρίκαλα', 670],
['Ηράκλειο', 'Ξάνθη', 1041], ['Βόλος', 'Χανιά', 649], ['Βόλος', 'Λάρισα', 60],['Βόλος', 'Τρίκαλα', 121], ['Βόλος', 'Ξάνθη', 411],
['Χανιά', 'Λάρισα', 674],['Χανιά', 'Τρίκαλα', 654], ['Χανιά', 'Ξάνθη', 1024],['Λάρισα', 'Τρίκαλα', 62],['Λάρισα', 'Ξάνθη', 353],['Τρίκαλα', 'Ξάνθη', 415]]