import mysql.connector as mysql
from getpass import getpass
import datetime

SUCCESS = 0
LOGIN_ERR = -5
VERIFICATION_ERROR = -3
ERROR = -1
VALUE_DNE = -4
VALUE_EXIST = -6
OCCUPIED = -7
DUES_LEFT = -8

class Person:
    def __init__(self,cur,db,ID,fname,username):
        self.id = ID
        self.fname = fname
        self.username = username
        self.cur = cur
        self.db = db
        
    def open_book(self,BookID):
        try:
            exe = "SELECT * FROM Books WHERE ID=%(id)s;"
            self.cur.execute(exe,{'id':BookID})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("No book with this ID exists!")
                return VALUE_DNE
            print("ID:",rows[0][0])
            print("Title:",rows[0][1])
            print("Edition:",rows[0][2])
            print("Position:\nShelf:",rows[0][3],",Row:",rows[0][4],",Section:",rows[0][5])
            print("Stock:",rows[0][6])
            print("CourseID:",rows[0][7])
            print("TotalBooks:",rows[0][8])
        except mysql.Error as e:
            print(e)
            return ERROR
    
    def book_search_name(self,book_name):
        try:
            exe = "SELECT ID,Title,Edition FROM Books WHERE Title=%(name)s;"
            self.cur.execute(exe,{'name':book_name})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("No book with this title exists!")
                return VALUE_DNE
            return rows
        except mysql.Error as e:
            print(e)
            return ERROR
    
    def book_search_auth(self,auth):
        try:
            fname = auth.lower().split()[0]
            lname = ('NULL' if len(auth.split())==1 else auth.lower().split()[-1])
            if lname=='NULL':
                exe = (
                    "SELECT ID,Title,Edition FROM Books " 
                    "WHERE ID IN "
                    "(SELECT Author_Books.BookID FROM Author_Books, Author WHERE " 
                    "Author_Books.AuthorID=Author.ID AND Author.FName=%(fname)s);"
                )
                self.cur.execute(exe,{'fname':fname})
            else:
                exe = (
                    "SELECT ID,Title,Edition FROM Books " 
                    "WHERE ID IN "
                    "(SELECT Author_Books.BookID FROM Author_Books, Author WHERE " 
                    "Author_Books.AuthorID=Author.ID AND Author.FName=%(fname)s AND Author.LName=%(lname)s);"
                )
                self.cur.execute(exe,{'fname':fname,'lname':lname})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("No author with this name exists!")
                return VALUE_DNE
            return rows
        except mysql.Error as e:
            print(e)
            return ERROR
    
    def book_search_course(self,course):
        try:
            exe = "SELECT ID,Title,Edition FROM Books WHERE CourseID=%(id)s"
            self.cur.execute(exe,{'id':course})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("No course with this name exists!")
                return VALUE_DNE
            return rows
        except mysql.Error as e:
            print(e)
            return ERROR
    
    def book_search_dept(self,dept):
        try:
            exe = (
                "SELECT ID,Title,Edition FROM Books WHERE CourseID IN" 
                "(SELECT ID FROM Course WHERE Dept=%(name)s);"
            )
            self.cur.execute(exe,{'name':dept})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("No department with this name exists!")
                return VALUE_DNE
            return rows
        except mysql.Error as e:
            print(e)
            return ERROR
        
    def book_search(self):
        while True:
            print("SEARCH BY:\n1. TITLE\n2. AUTHOR\n3. COURSE\n4. DEPARTMENT\n5. GO BACK")
            i=int(input("?:"))
            if i<5:
                param = input("Provide keyword for search:")
            if i>0 and i<6:
                if i==1:
                    rows = self.book_search_name(param)
                elif i==2:
                    rows = self.book_search_auth(param)
                elif i==3:
                    rows = self.book_search_course(param)
                elif i==4:
                    rows = self.book_search_dept(param)
                elif i==5 or (not isinstance(rows,int)):
                    return None
                if isinstance(rows,int):
                    return None
                if len(rows)==1:
                    self.open_book(rows[0][0])
                else:
                    print("{:<10}{:<30}{:<10}".format("BookID","BookTitle","Edition"))
                    for i in rows:
                        print("{:<10}{:<30}{:<10}".format(i[0],i[1],i[2]))
                    i = int(input("Give BookID to open or -1 to GO BACK:"))
                    if i!=-1:
                        return i
            else:
                print("Please choose an option from the menu.")
            
    
    def edit_profile(self,mode):
        try:
            #verify password
            prevPass = getpass("Provide current password to proceed further:\n")
            if mode=='Staff':
                exe = "SELECT * FROM Staff WHERE ID=%(id)s AND Password=AES_ENCRYPT(%(passw)s,%(key)s);"
            else:
                exe = "SELECT * FROM Member WHERE ID=%(id)s AND Password=AES_ENCRYPT(%(passw)s,%(key)s);"                
            self.cur.execute(exe,{'id':self.id, 'passw':prevPass, 'key':key})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("Incorrect password")
                return VERIFICATION_ERROR
            #update profile
            lname = input("Provide updated Last name:")
            phn = input("Provide new phone number:")
            newpassw = getpass("Provide new password:")
            if mode=='Staff':
                exe = (
                    "UPDATE Staff SET LName = %(lname)s, Phone = %(phn)s, "
                    "Password = AES_ENCRYPT(%(pass)s,%(key)s) WHERE ID=%(id)s;"
                )
            else:
                exe = (
                    "UPDATE Member SET LName = %(lname)s, Phone = %(phn)s, "
                    "Password = AES_ENCRYPT(%(pass)s,%(key)s) WHERE ID=%(id)s;"
                )
            self.cur.execute(exe,{'lname':lname,'phn':phn,'pass':newpassw,'key':key,'id':self.id})
            self.db.commit()
            return SUCCESS
        except mysql.Error as e:
            print(e)
            return ERROR

class Staff(Person):
    def edit_staff_profile(self):
        return self.edit_profile('Staff')
    
    def add_new_staff(self):
        try:
            fname = input("First name:")
            email = input("Email id:")
            username = input("Username:")
            password = getpass("Password:")
            #check if staff exist
            exe = "SELECT * FROM Staff WHERE Username=%(user)s"
            self.cur.execute(exe,{'user':username})
            rows = self.cur.fetchall()
            if len(rows)>0:
                print("Username exists try a different username")
                return VALUE_EXIST
            #add staff
            exe = (
                "INSERT INTO Staff (FName,Email,Username,Password) "
                "VALUES (%(fname)s, %(email)s, %(user)s, AES_ENCRYPT(%(passw)s,%(key)s));"
            )
            self.cur.execute(exe,{'fname':fname,'email':email,'user':username,'passw':password,'key':key})
            self.db.commit()
            print(username," successfully added!!!")
            return SUCCESS
        except mysql.Error as e:
            print(e)
            return ERROR
    
    def add_new_member(self):
        try:
            fname = input("First name:")
            email = input("Email id:")
            username = input("Username:")
            password = getpass("Password:")
            #check if member exist
            exe = "SELECT * FROM Member WHERE Username=%(user)s"
            self.cur.execute(exe,{'user':username})
            rows = self.cur.fetchall()
            if len(rows)>0:
                print("Username exists try a different username")
                return VALUE_EXIST
            #add member
            exe = (
                "INSERT INTO Member (FName,Email,Username,Password) "
                "VALUES (%(fname)s, %(email)s, %(user)s, AES_ENCRYPT(%(passw)s,%(key)s));"
            )
            self.cur.execute(exe,{'fname':fname,'email':email,'user':username,'passw':password,'key':key})
            self.db.commit()
            print(username," successfully added!!!")
            i = int(input("Mode: \n1. Normal\n2. Student\n:"))
            if i==2:
                i = input("Provide Roll No.:")
                exe  = "SELECT ID FROM Member WHERE Username=%(user)s;"
                self.cur.execute(exe,{'user':username})
                rows = self.cur.fetchall()
                if len(rows)==0:
                    print("Username doesn't exist!")
                    return VALUE_DNE
                memID = rows[0][0]
                exe = "INSERT INTO Student (MemID,RollNo) VALUES (%(mem)s,%(roll)s);"
                self.cur.execute(exe,{'mem':memID,'roll':i})
                self.db.commit()
            return SUCCESS
        except mysql.Error as e:
            print(e)
            return ERROR
    
    def delete_member(self,memID):
        try:
            #check for dues
            exe = "SELECT * FROM Borrow_log WHERE MemberID=%(id)s AND ReturnDate IS NULL;"
            self.cur.execute(exe,{'id':memID})
            rows = self.cur.fetchall()
            if len(rows)>0:
                print("User's dues are not clear, can't be deleted!!")
                return DUES_LEFT
            exe = "SELECT * FROM Borrow_log WHERE MemberID=%(id)s AND Paid=0 AND DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)>7;"
            self.cur.execute(exe,{'id':memID})
            rows = self.cur.fetchall()
            if len(rows)>0:
                print("User's dues are not clear, can't be deleted!!")
                return DUES_LEFT
            #delete borrow log
            exe = "DELETE FROM Borrow_log WHERE MemberID=%(id)s;"
            self.cur.execute(exe,{'id':memID})
            self.db.commit()
            #delete from Student
            exe = "DELETE FROM Student WHERE MemID=%(id)s;"
            self.cur.execute(exe,{'id':memID})
            self.db.commit()
            #delete user
            exe = "DELETE FROM Member WHERE ID=%(id)s;"
            self.cur.execute(exe,{'id':memID})
            self.db.commit()
            print(memID," deleted from database!!!")
            return SUCCESS
        except mysql.Error as e:
            print(e)
            return ERROR
        
    def add_course(self):
        try:
            name = input("Course name:")
            ID = input("Course ID:")
            dept = input("Department:")
            #check if course exist
            exe  = "SELECT ID FROM Course WHERE Name=%(course)s;"
            self.cur.execute(exe,{'course':name})
            rows = self.cur.fetchall()
            if len(rows)>0:
                print("Course already exists!")
                return VALUE_EXIST
            #insert course
            exe = "INSERT INTO Course(ID,Name,Dept) VALUES(%(id)s,%(name)s,%(dept)s);"
            self.cur.execute(exe,{'id':ID,'name':name,'dept':dept})
            self.db.commit()
            print("Course added!!!")
            return SUCCESS
        except mysql.Error as e:
            print(e)
            return ERROR

    def add_book(self):
        try:
            title = input("Book title:")
            edition = int(input("Edition:"))
            #check if book exists
            exe = "SELECT * FROM Books WHERE Title=%(title)s AND Edition=%(edition)s;"
            self.cur.execute(exe,{'title':title,'edition':edition})
            rows = self.cur.fetchall()
            if len(rows)>0:
                print("Book already exists!")
                return VALUE_EXIST
            #get courseID from course table
            course = input("If book is from a course provide course ID else input NULL:")
            if course!='NULL':
                exe  = "SELECT ID FROM Course WHERE ID=%(course)s;"
                self.cur.execute(exe,{'course':course})
                rows = self.cur.fetchall()
                if len(rows)==0:
                    print("Course doesn't exit!")
                    return VALUE_DNE
                course = rows[0][0]
            #check if position is empty
            print("Provide book position:")
            shelfno = int(input("Shelf No.:"))
            row = int(input("Row:"))
            section = input("Section:")
            exe = "SELECT * FROM Books WHERE ShelfNo=%(shelf)s AND Books.Row=%(row)s AND Section=%(section)s;"
            self.cur.execute(exe,{'shelf':shelfno,'row':row,'section':section})
            rows = self.cur.fetchall()
            if len(rows)>0:
                print("Position already occupied!!")
                return OCCUPIED
            #insert book in table
            nos = int(input("Number of books:"))
            exe = (
                    "INSERT INTO Books (Title,Edition,ShelfNo,Books.Row,Section,Stock,Total) "
                    "VALUES (%(title)s,%(ed)s,%(shelf)s,%(row)s,%(sec)s,%(nos)s,%(tot)s);"
            )
            self.cur.execute(exe,{'title':title,'ed':edition,'shelf':shelfno,
                             'row':row,'sec':section,'nos':nos,'tot':nos})
            self.db.commit()
            if course!='NULL':
                exe = "UPDATE Books SET CourseID=%(id)s WHERE Title=%(tt)s AND Edition=%(ee)s;"
                self.cur.execute(exe,{'id':course,'tt':title,'ee':edition})
                self.db.commit()
            #get bookID
            exe = "SELECT ID FROM Books WHERE Title=%(title)s AND Edition=%(edition)s;"
            self.cur.execute(exe,{'title':title,'edition':edition})
            rows = self.cur.fetchall()
            bookID = rows[0][0]
            print("Provide one author name for each input and lastly input None when you want to stop input.")
            i = input("Author:")
            #get AuthorID for each author and insert in Author_Books
            exe = "SELECT ID FROM Author WHERE FName=%(fname)s AND LName=%(lname)s;"
            exe1 = "INSERT INTO Author_Books (AuthorID,BookID) VALUES (%(aID)s,%(bID)s);"
            exe2 = "INSERT INTO Author (FName,LName) VALUES (%(fname)s,%(lname)s);"
            exe3 = "INSERT INTO Author (FName) VALUES (%(fname)s);"
            exe4 = "SELECT ID FROM Author WHERE FName=%(fname)s;"
            while i!="None":
                fname = i.lower().split()[0]
                if len(i.split())>1:
                    lname = i.lower().split()[-1]
                    self.cur.execute(exe,{'fname':fname,'lname':lname})

                else:
                    lname=None
                    self.cur.execute(exe4,{'fname':fname})
                rows = self.cur.fetchall()
                #if author DNE
                if len(rows)==0:
                    if lname is None:
                        self.cur.execute(exe3,{'fname':fname})
                    else:
                        self.cur.execute(exe2,{'fname':fname,'lname':lname})
                    self.db.commit()
                    if lname is None:
                        self.cur.execute(exe4,{'fname':fname})
                    else:
                        self.cur.execute(exe,{'fname':fname,'lname':lname})
                    rows = cur.fetchall()
                authID = rows[0][0]
                self.cur.execute(exe1,{'aID':authID,'bID':bookID})
                self.db.commit()
                i = input("Author:")
            return SUCCESS
        except mysql.Error as e:
            print(e)
            return ERROR
        
    def book_stock(self,bookID,nos):
        try:
            exe = "SELECT Stock,Total FROM Books WHERE ID=%(id)s"
            self.cur.execute(exe,{'id':bookID})
            rows = self.cur.fetchall()
            if len(rows)<1:
                return ERROR
            stock_no = rows[0][0]+nos
            total_no = rows[0][1]+nos
            if stock_no<0:
                stock_no=0
            if total_no<0:
                total_no=0
            exe = "UPDATE Books SET Stock=%(st)s,Total=%(tt)s WHERE ID=%(id)s"
            self.cur.execute(exe,{'st':stock_no,'tt':total_no,'id':bookID})
            self.db.commit()
            return SUCCESS
        except mysql.Error as e:
            print(e)
            return ERROR
        
    def add_book_stock(self,bookID):
        nos = int(input("Number of books to be added:"))
        return self.book_stock(bookID,nos)
    
    def del_book_stock(self,bookID):
        nos = int(input("Number of books to be deleted:"))
        return self.book_stock(bookID,-1*nos)
        
    def search_member(self):
        try:
            username = input("Provide Username:")
            exe = "SELECT ID,FName,Username FROM Member WHERE Username=%(user)s"
            self.cur.execute(exe,{'user':username})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("User not found!!")
                return VALUE_DNE
            print("ID:",rows[0][0])
            print("Name:",rows[0][1])
            print("Username:",rows[0][2])
            mem = Member(self.cur,self.db,rows[0][0],rows[0][1],rows[0][2])
            while True:
                i = int(input("What do you want to do?\n1. ISSUE BOOK\n2. RETURN BOOK\n3. SHOW DUES\n4. DELETE MEMBER\n5. GO BACK\n?:"))
                if i>5 or i<1:
                    print("Please choose an option from the menu.")
                elif i==1:
                    self.issue_book_member(rows[0][0])
                elif i==2:
                    mem.books_to_ret()
                    i = int(input("Provide BorrowID corresponding to book to return:"))
                    self.ret_book(i)
                elif i==3:
                    self.show_fine_due(memID=rows[0][0])
                elif i==4:
                    return self.delete_member(rows[0][0])
                elif i==5:
                    return
        except mysql.Error as e:
            print(e)
            return ERROR
        
    def fine_payment(self,borrowID,fine):
        try:
            exe = (
                "SELECT ReturnDate,Paid,"
                "DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)*5 AS Fine "
                "FROM Borrow_log WHERE ID=%(id)s;"
            )
            self.cur.execute(exe,{'id':borrowID})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("BorrowID Doesn't exist!!")
                return VALUE_DNE
            if rows[0][1]==1:
                print("Fine corresponding to this BorrowID already paid!!")
                return VALUE_EXIST
            if rows[0][0] is None:
                print("Book is not returned so fine can't be paid!!")
                return VALUE_DNE
            if rows[0][2]>fine:
                print("Given amount less than fine amount, can't clear borrow_log!!")
                return VALUE_DNE
            exe = "UPDATE Borrow_log SET Paid=1 WHERE ID=%(id)s;"
            self.cur.execute(exe,{'id':borrowID})
            self.db.commit()
            return SUCCESS
        except mysql.Error as e:
            print(e)
            return ERROR
        
    def show_fine_due(self,bookID=None,memID=None):
        try:
            if not (bookID or memID):
                exe = (
                    "SELECT Borrow_log.ID,IssueDate,ReturnDate,Books.Title,Member.Username,"
                    "DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)*5 AS Fine "
                    "FROM Borrow_log LEFT JOIN Books ON Borrow_log.BookID=Books.ID "
                    "LEFT JOIN Member ON Borrow_log.MemberID=Member.ID "
                    "WHERE Paid=0 AND DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)>7;"
                )
                self.cur.execute(exe)
                rows = self.cur.fetchall()
            elif bookID and memID:
                exe = (
                    "SELECT Borrow_log.ID,IssueDate,ReturnDate,Books.Title,Member.Username,"
                    "DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)*5 AS Fine "
                    "FROM Borrow_log LEFT JOIN Books ON Borrow_log.BookID=Books.ID "
                    "LEFT JOIN Member ON Borrow_log.MemberID=Member.ID "
                    "WHERE BookID=%(book)s AND MemberID=%(mem)s AND "
                    "Paid=0 AND DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)>7;"
                )
                self.cur.execute(exe,{'book':bookID,'mem':memID})
                rows = self.cur.fetchall()
            elif bookID:
                exe = (
                    "SELECT Borrow_log.ID,IssueDate,ReturnDate,Books.Title,Member.Username,"
                    "DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)*5 AS Fine "
                    "FROM Borrow_log LEFT JOIN Books ON Borrow_log.BookID=Books.ID "
                    "LEFT JOIN Member ON Borrow_log.MemberID=Member.ID "
                    "WHERE BookID=%(book)s AND "
                    "Paid=0 AND DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)>7;"
                )
                self.cur.execute(exe,{'book':bookID})
                rows = self.cur.fetchall()
            else:
                exe = (
                    "SELECT Borrow_log.ID,IssueDate,ReturnDate,Books.Title,Member.Username,"
                    "DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)*5 AS Fine "
                    "FROM Borrow_log LEFT JOIN Books ON Borrow_log.BookID=Books.ID "
                    "LEFT JOIN Member ON Borrow_log.MemberID=Member.ID "
                    "WHERE MemberID=%(mem)s AND "
                    "Paid=0 AND DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)>7;"
                )
                self.cur.execute(exe,{'mem':memID})
                rows = self.cur.fetchall()
            if len(rows)==0:
                print("No dues to show!")
                return
            print("{:<10}{:<11}{:<11}{:<30}{:<10}{:<10}".format("BorrowID","Issued","Return","BookTitle","Username","Fine"))
            for i in rows:
                k1 = str(i[1])
                k2 = str(i[2])
                print("{:<10}{:<11}{:<11}{:<30}{:<10}{:<10}".format(i[0],k1,k2,i[3],i[4],i[5]))
            while True:
                print("Select option from the menu:\n1. GO BACK\n2. PAY DUES")
                i = int(input("?:"))
                if i==1:
                    return
                elif i==2:
                    i = int(input("Give BorrowID:"))
                    j = int(input("Give fine amount paid:"))
                    self.fine_payment(i,j)
                else:
                    print("Please select an option from the menu.")
        except mysql.Error as e:
            print(e)
            return ERROR
    
    #edit
    def issue_book_member(self,memID):
        try:
            bookID = int(input("Provide BookID:"))
            exe = "SELECT Stock FROM Books WHERE ID=%(b)s;"
            self.cur.execute(exe,{'b':bookID})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("Book doesn't exist!!")
                return VALUE_DNE
            if rows[0][0]<1:
                print("Book not available!!")
                return VALUE_DNE
            exe = "UPDATE Books SET Stock=%(st)s WHERE ID=%(b)s"
            st = rows[0][0]-1
            self.cur.execute(exe,{'st':st,'b':bookID})
            self.db.commit()
            exe = "INSERT INTO Borrow_log (IssueDate, BookID, MemberID) VALUES (CURRENT_DATE(),%(b)s,%(m)s)"
            self.cur.execute(exe,{'b':bookID,'m':memID})
            self.db.commit()
            print("Book issued to member!")
            return SUCCESS
        except mysql.Error as e:
            print(e)
            return ERROR
        
    #edit
    def ret_book(self,borrowID):
        try:
            exe = "SELECT BookID FROM Borrow_log WHERE ID=%(id)s;"
            self.cur.execute(exe,{'id':borrowID})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("BorrowID doesn't exist!!")
                return VALUE_DNE
            bookID = rows[0][0]
            exe = "UPDATE Borrow_log SET ReturnDate=CURRENT_DATE() WHERE ID=%(id)s"
            self.cur.execute(exe,{'id':borrowID})
            self.db.commit()
            exe = "SELECT Stock FROM Books WHERE ID=%(id)s;"
            self.cur.execute(exe,{'id':bookID})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("There is some problem!")
                return VALUE_DNE
            st = rows[0][0]+1
            exe = "UPDATE Books SET Stock=%(st)s WHERE ID=%(id)s;"
            self.cur.execute(exe,{'st':st,'id':bookID})
            self.db.commit()
            return SUCCESS
        except mysql.Error as e:
            print(e)
            return ERROR
    
    def open_book(self,BookID):
        try:
            exe = "SELECT * FROM Books WHERE ID=%(id)s;"
            self.cur.execute(exe,{'id':BookID})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("No book with this ID exists!")
                return VALUE_DNE
            print("ID:",rows[0][0])
            print("Title:",rows[0][1])
            print("Edition:",rows[0][2])
            print("Position:\nShelf:",rows[0][3],",Row:",rows[0][4],",Section:",rows[0][5])
            print("Stock:",rows[0][6])
            print("CourseID:",rows[0][7])
            print("TotalBooks:",rows[0][8])
            print()
            while True:
                i = int(input("What do you want to do:\n1. ADD BOOKS TO STOCK\n2. DELETE BOOKS FROM STOCK\n3. SHOW DUES BY BOOK\n4. GO BACK\n:?"))
                if i==4:
                    return
                elif i==1:
                    self.add_book_stock(BookID)
                elif i==2:
                    self.del_book_stock(BookID)
                elif i==3:
                    self.show_fine_due(bookID=BookID)
                else:
                    print("Please choose an option provided in the menu.")
        except mysql.Error as e:
            print(e)
            return ERROR
        
class Member(Person):
    def edit_mem_profile(self):
        return self.edit_profile('Member')
    
    def fine_log(self):
        try:
            exe = (
                "SELECT Borrow_log.ID,Books.Title,IssueDate,"
                "DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)*5 AS Fine "
                "FROM Borrow_log LEFT JOIN Books ON Borrow_log.BookID=Books.ID WHERE MemberID=%(id)s AND "
                "Paid=0 AND DATEDIFF(IFNULL(ReturnDate,CURRENT_DATE()),IssueDate)>7;"
            )
            self.cur.execute(exe,{'id':self.id})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("No pending dues!!")
                return
            print("{:<10}{:<30}{:<11}{:<10}".format("BorrowID","BookTitle","IssueDate","Fine"))
            for i in rows:
                k = str(i[2])
                print("{:<10}{:<30}{:<11}{:<10}".format(i[0],i[1],k,i[3]))
        except mysql.Error as e:
            print(e)
            return ERROR
    def books_to_ret(self):
        try:
            exe = ("SELECT Borrow_log.ID,Books.Title, IssueDate+7 FROM Borrow_log LEFT JOIN Books ON Borrow_log.BookID=Books.ID "
                   "WHERE Books.ID=BookID AND MemberID=%(id)s AND ReturnDate IS NULL;")
            self.cur.execute(exe,{'id':self.id})
            rows = self.cur.fetchall()
            if len(rows)==0:
                print("No books to return!")
                return
            print("{:<10}{:<30}{:<11}".format("BorrowID","BookTitle","ReturnBy"))
            for i in rows:
                k=str(i[2])
                print("{:<10}{:<30}{:<11}".format(i[0],i[1],k))
        except mysql.Error as e:
            print(e)
            return ERROR
    
key = 'mynameissuzie'

def login(cur, db, mode, username, password):
    try:
        if mode==1:
            exe = "SELECT * FROM Staff WHERE Username=%(user)s AND Password=AES_ENCRYPT(%(passw)s,%(key)s);"
        else:
            exe = "SELECT * FROM Member WHERE Username=%(user)s AND Password=AES_ENCRYPT(%(passw)s,%(key)s);"
        cur.execute(exe,{'user':username, 'passw':password, 'key':key})
        rows = cur.fetchall()
        if len(rows)==0:
            print("Wrong usename or password!!")
            return LOGIN_ERR
        if mode==1:
            per = Staff(cur,db,rows[0][0],rows[0][1],rows[0][5])
        else:
            per = Member(cur,db,rows[0][0],rows[0][1],rows[0][5])
        return per
    except mysql.Error as e:
        print(e)
        return ERROR
        
def staff_menu(staff):
    print("HELLO ",staff.fname)
    j=0
    while j==0:
        print("INPUT THE NUMBER OF FUNCTION TO BE PERFORMED:")
        print("1. EDIT PROFILE")
        print("2. SEARCH BOOK")
        print("3. SEARCH MEMBER")
        print("4. ADD NEW STAFF")
        print("5. ADD NEW MEMBER")
        print("6. ADD COURSE")
        print("7. ADD BOOK")
        print("8. SHOW DUES")
        print("9. EXIT")
        i = int(input())
        if i==1:
            staff.edit_staff_profile()
        elif i==2:
            BookID = staff.book_search()
            if (BookID is not None) and BookID>0:
                staff.open_book(BookID)
        elif i==3:
            staff.search_member()
        elif i==4:
            staff.add_new_staff()
        elif i==5:
            staff.add_new_member()
        elif i==6:
            staff.add_course()
        elif i==7:
            staff.add_book()
        elif i==8:
            staff.show_fine_due()
        elif i==9:
            j=1
        else:
            print("Please choose an option in the menu.")
    
def member_menu(member):
    print("HELLO ",member.fname)
    j=0
    while j==0:
        print("INPUT THE NUMBER OF FUNCTION TO BE PERFORMED:")
        print("1. EDIT PROFILE")
        print("2. SEARCH BOOK")
        print("3. SHOW DUES")
        print("4. SHOW BOOKS TO RETURN")
        print("5. EXIT")
        i = int(input())
        if i==1:
            member.edit_mem_profile()
        elif i==2:
            k = member.book_search()
            if (k is not None) and k>0:
                member.open_book(k)
        elif i==3:
            member.fine_log()
        elif i==4:
            member.books_to_ret()
        elif i==5:
            j=1
        else:
            print("Please choose an option in the menu.")
            
db = mysql.connect(host = "localhost", user = "root", passwd = "Shreya35", database = "KitabGhar")
cur = db.cursor()
print("WELCOME TO KITABGHAR")
print("PLEASE LOGIN")
mode = int(input("CHOOSE LOGIN MODE\n1. STAFF\n2. MEMBER\n"))
i=0
tries=0
while isinstance(i,int) and tries<3:
    username = input("USERNAME:\n")
    password = getpass("PASSWORD:\n")
    i = login(cur,db,mode,username,password)
    tries+=1
if isinstance(i,int):
    print("Closing program. 3 failed attempts to login!")
elif mode==1:
    staff_menu(i)
else:
    member_menu(i)
