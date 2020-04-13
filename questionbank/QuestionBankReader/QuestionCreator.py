'''
Created on Jun 13, 2017

@author: nambidiv
'''
from flask import Flask,render_template,redirect, url_for, request,session,escape
from flask_sqlalchemy  import SQLAlchemy
import pymysql
import os
import sys
import random 
from sqlalchemy import func
import LogQuestionCreator
from distutils.log import INFO


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:root@localhost/questioner"
db = SQLAlchemy(app)

logger = LogQuestionCreator.LogQuestionCreator()

#users table.
#role 1 is for administrator and role 2 for users  who wanted to generate question
class users(db.Model):
    _tablename_='users'
    ID  = db.Column('ID',db.Integer,primary_key=True)
    name = db.Column('name',db.String(2500))
    password = db.Column('pass',db.String(2000))
    role = db.column('role',db.Integer)
    
# question table. ID is the primary key   
class questions(db.Model):
    _tablename_= 'questions' 
    ID = db.Column('ID',db.Integer,primary_key=True)
    question = db.Column('question',db.String(2500))
    solution = db.Column('solution',db.String(2000))
    includegraphics = db.Column('includegraphics',db.String(2000))
    
    def _init_(self,question,solution,includegraphics):        
        self.question = questions
        self.solution = solution
        self.includegraphics = includegraphics

#choices table has choices for each question.  
#questions(ID) is the foreign key here
#isCorrectChoice=1 for  correct choice 
class choices(db.Model):
    _tablename_= 'choices' 
    ID = db.Column('ID',db.Integer,primary_key=True)
    questionID = db.Column('questionID',db.Integer)
    choice = db.Column('choice',db.String(2000))
    isCorrectChoice = db.Column('isCorrectChoice',db.Integer)
    
    def _init_(self,ID,questionID,choice,isCorrectChoice):
        self.ID = ID
        self.questionID = questionID
        self.choice = choice 
        self.isCorrectChoice = isCorrectChoice

# This class  will insert questions into DB
# And write  generated question for  user into file      
class QuestionReader : 
    def __init__(self): 
        self.qFilelines = None
        self.solFilelines = None
        self.questionStartindices = []
        self.questionEndEndindices = [] 
        self.choiceEndindices = [] 
        self.solutionStartindeces = []   
        self.solutionEndindeces = []   
        self.allQuestionIds = []
        self.randomQuestions = []               
        self.question = None
        self.choice = None
        self.solution = None                
        self.questionID = 0
        self.engine = None
        self.metadata = None
        self.getInitialConfig()
    
    #Getting logger and  SQL Alchemy
    def getInitialConfig(self):        
        pymysql.install_as_MySQLdb()     
    
    #Admin operations to insert question and solution to DB 
    def insertFileIntoDB(self,Questionfile,SolutionFile):
        self.readQuestionFile(Questionfile)
        self.readSolutionFile(SolutionFile)
        info = self.processQuetionAndSolution()
        return info                             
        
    #Reading question file and inserting into list qFilelines
    def readQuestionFile(self,Questionfile):
        try:
            with open(Questionfile,"r") as  f :                
                logger.log_info("Reading Question file "+Questionfile)
                self.qFilelines = f.read().splitlines()
        except :     
            logger.log_error("Error reading question File : "+str(sys.exc_info()[0]))
            raise
    #Reading solution file and inserting into list solFilelines
    def readSolutionFile(self,SolutionFile):
        try:
            with open(SolutionFile,"r") as  f :
                logger.log_info("Reading Solution file "+SolutionFile)
                self.solFilelines = f.read().splitlines()
        except :     
            logger.log_error("Error reading solution File : "+str(sys.exc_info()[0]))
            raise
             
    # Reading list qFilelines,solFilelines by index and processing questions and solutions     
    def processQuetionAndSolution(self):        
        try :                                            
            self.questionStartindices = [i for i, x in enumerate(self.qFilelines) if x.startswith("\\question")]                              
            self.questionEndEndindices = [i for i, x in enumerate(self.qFilelines) if x.endswith("\\begin{choices}")]               
            self.choiceEndindices = [i for i, x in enumerate(self.qFilelines) if x.endswith("\\end{choices}")]   
            self.solutionStartindeces = [i for i, x in enumerate(self.solFilelines) if x.startswith("\\begin{solution}")]             
            self.solutionEndindeces = [i for i, x in enumerate(self.solFilelines) if x.startswith("\\end{solution}")]
            index = 0
            while index < len(self.questionStartindices) :                
                logger.log_info("processing question : "+str(index+1))
                startQIndex = self.questionStartindices[index]                
                endQIndex = self.questionEndEndindices[index]                 
                endChoiceIndex = self.choiceEndindices[index]
                startSolIndex = self.solutionStartindeces[index]
                endSolIndex = self.solutionEndindeces[index]                     
                index = index + 1
                self.processQuestion(startQIndex,endChoiceIndex,endQIndex,startSolIndex,endSolIndex)
            return "Successfully  inserted data into DB !!" 
        except :     
            logger.log_error("Error While getting indices  for question or solution : "+str(sys.exc_info()[0]))
            raise        
            return "Insertion error!!"
    
    # Processing  of one question and solution   
    def processQuestion(self,startQIndex,endChoiceIndex,endQIndex,startSolIndex,endSolIndex): 
        try:
            qindex  = startQIndex
            sindex = startSolIndex
            question  = ""
            choiceList = []
            correctChoice =""
            solution  = "" 
            image =  ""  
            choiceStarted  = 0 
            
            while qindex <= endChoiceIndex :
                qline = self.qFilelines[qindex].lstrip().rstrip()           
                if choiceStarted==0 :                                
                    if "begin{choices}" in qline:
                        choiceStarted = 1
                        continue;
                    else:
                        question = question+qline
                else :    
                    if qindex  < endChoiceIndex :                                
                        if "correctchoice" in qline:
                            correctChoice = qline.replace("\\correctchoice","").strip()                  
                        qline = qline.replace("\\choice","").replace("\\correctchoice","").replace("\\begin{choices}","").strip()
                        if(len(qline)>0) :
                            choiceList.append(qline)            
                qindex = qindex + 1
            while sindex <=  endSolIndex :     
                sline = self.solFilelines[sindex].lstrip().rstrip()    
                if  "\\begin{solution}" in sline :
                    sline = sline.replace("\\begin{solution}","")
                if "includegraphics" in sline :
                    image = sline.replace("\\includegraphics","").strip()   
                else:        
                    solution = solution + sline   
                sindex = sindex + 1               
            question = question.replace("\\question","").strip()
                  
            solution = solution.replace("\\end{solution}", "").strip()
            logger.log_info("question is : "+question)
            qs = questions(question=question,solution=solution,includegraphics=image)
            db.session.add(qs)
            db.session.commit() 
            questionID = qs.ID            
            for c in choiceList:
                isCorChoice = 0 
                if (correctChoice==c) :
                    isCorChoice = 1
                ch = choices(questionID=questionID,choice=c,isCorrectChoice=isCorChoice)
                db.session.add(ch)
                db.session.commit()              
        except:
            logger.log_error("Error While  inserting  question/solution into DB : "+str(sys.exc_info()[0]))            
            raise
        
    #process choice  for question 
    def processChoice(self,id):
        choice = "\n" 
        try:            
            c = choices.query.filter_by(questionID=id).all()            
            count = 0         
            while count < len(c) :         
                if c[count].isCorrectChoice==1:
                    choice = choice + "\t\\correctchoice "+ c[count].choice+"\n"
                else: 
                    choice = choice +  "\t\\choice "+ c[count].choice +"\n " 
                count = count + 1                    
        except:
            logger.log_error("Error While  inserting  question/solution into DB : "+str(sys.exc_info()[0]))            
            raise
        return choice           
        
    # Getting one question and solution randomly 
    def getRandomQuestions(self,qoutputfile,soutputfile):   
        ids = db.session.query(func.min(questions.ID), func.max(questions.ID)).first()
        id  = random.randint(ids[0],ids[1])           
        q =  questions.query.filter_by(ID=id).all()
        if len(q) > 0 and not(id in self.randomQuestions) : 
            self.question = ("\n\\question " +q[0].question+"\n\t\\begin{choices} \n" )
            self.solution = ("\n\t\\begin{solution} " +q[0].solution )
            if q[0].includegraphics != None :
                self.solution = self.solution + ("\n\t\\includegraphics " +q[0].includegraphics )
            self.solution = self.solution + "\n\t\\end{solution}\n"    
            self.choice =  self.processChoice(id)         
            self.randomQuestions.append(id)      
            qoutputfile.write(self.question)
            qoutputfile.write(self.choice)
            qoutputfile.write("\t\\end{choices}")
            soutputfile.write(self.solution) 
        
    # Writing  N random questions to file from DB 
    def getNRandomQuestions(self,N,outputfileQuestion,outputFileSolution):    
        info = ""
        try:
            qoutputFile = open(outputfileQuestion,'w')
            soutputFile = open(outputFileSolution,'w')
            qoutputFile.write("\n\\begin{document}\n\\begin{questions} \n")       
            while(len(self.randomQuestions) < N):
                self.getRandomQuestions(qoutputFile,soutputFile)             
            qoutputFile.write('\\end{questions} \n')
            qoutputFile.write("\\end{document}")        
            qoutputFile.close()
            info = "Writing Done !!!"
        except:
            logger.log_error("Error While  writing into the file : "+str(sys.exc_info()[0])) 
            info  =   "Error While  writing into the file "         
            raise
        return info        
          
# Application root.
# This is for  administrator. 
# Currently you have to copy  the file inside static folder and browse     
@app.route('/', methods=['GET', 'POST'])
def admin():
    if 'username' in session:
        username_session = escape(session['username']).capitalize()
        info = ""    
        if request.method == 'POST':
            readQuestion_form  = request.form['readQuestion']
            readSolution_form  = request.form['readSolution']
            currentDir = os.getcwd()
            filePath=currentDir+"\\static"  
            questionFile=filePath+"\\"+ readQuestion_form 
            solutionFile=filePath+"\\"+ readSolution_form 
            questionBankReader = QuestionReader()
            info = questionBankReader.insertFileIntoDB(questionFile,solutionFile)
        return render_template('admin.html', session_user_name=username_session, info=info)
    return redirect(url_for('login'))

@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'username' in session:
        username_session = escape(session['username']).capitalize()
        info = ""
        if request.method == 'POST':
            N =  request.form['noquestions']
            outputfileQuestion =  request.form['writeQuestions']
            outputFileSolution =  request.form['writeSolutions']   
            questionBankReader = QuestionReader()
            logger.log_info(outputFileSolution)
            info = questionBankReader.getNRandomQuestions(int(N), outputfileQuestion, outputFileSolution)
            logger.log_info(info)      
        return render_template('user.html', session_user_name=username_session, info = info  )
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if 'username' in session:
        return redirect(url_for('admin'))
    if request.method == 'POST':
        username_form  = request.form['username']
        password_form  = request.form['password']
        pymysql.install_as_MySQLdb()   
        user_admin = users.query.filter_by(role=1).all()
        user_nonadmin = users.query.filter_by(role=2).all()
        user_exists = 0
        count = 0 
        while count < len(user_admin):
            if user_admin[count].name == username_form and user_admin[count].password==password_form:            
                session['username'] = username_form
                user_exists = 1          
                return redirect(url_for('admin'))
            else :
                count = count + 1
        if user_exists == 0:
            count = 0 
            while count < len(user_nonadmin) :
                if user_nonadmin[count].name == username_form and user_nonadmin[count].password==password_form:            
                    session['username'] = username_form
                    user_exists = 1          
                    return redirect(url_for('user'))
                else :
                    count = count + 1
        if user_exists == 0:           
            error = "Invalid Credential"       
    return render_template('login.html', error=error)

@app.route('/cool_form', methods=['GET', 'POST'])
def cool_form():
    if request.method == 'POST':        
        return redirect(url_for('admin'))

    # show the form, it wasn't submitted
    return render_template('cool_form.html')      

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('admin'))

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.run(debug=True)