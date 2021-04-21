from flask import Flask, render_template, request, redirect, url_for, flash, session

from flask_sqlalchemy import SQLAlchemy

from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from functools import wraps




from flask import Flask
from json import JSONEncoder

app = Flask(__name__)
app.secret_key = "Secret Key"

# SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/crud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crud'

# init MYSQL
mysql = MySQL(app)

db = SQLAlchemy(app)







class User(db.Model):

    idu = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    mail = db.Column(db.String(100))
    telf = db.Column(db.String(100))
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))


    def __init__(self, nom, prenom, mail, telf, username, password):


        self.nom = nom
        self.prenom = prenom
        self.mail = mail
        self.telf = telf
        self.username = username
        self.password = password



# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        nom = request.form['nom']
        print('nom utilisat', nom)
        prenom = request.form['prenom']
        mail = request.form['mail']
        telf = request.form['telf']
        username = request.form['username']
        password = sha256_crypt.encrypt(str(request.form['password']))
        db.engine.execute("insert into user (nom, prenom, mail, telf, username, password) VALUES (%s, %s, %s, %s, %s, %s)", (nom, prenom, mail, telf, username, password))
        db.session.commit()


        return redirect(url_for('Index'))
    return render_template('register.html')




# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM user WHERE username = %s", [username])

        if result :
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                user=session['username']
                response = redirect(url_for("Index"))
                response.set_cookie('YourSessionCookie', user)
                return response

                #return redirect(url_for('Index'))
            else:
                error = 'Identifiant invalide'
                return render_template('login.html', error=error)

            # Close connection
            cur.close()

        else:
            error = 'Nom d"utilisateur introuvable'
            return render_template('login.html', error=error)
    return render_template('login.html')




# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Non autorisé, veuillez vous connecter !', 'danger')
            return redirect(url_for('login'))
    return wrap




# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()

    return redirect(url_for('login'))









class Notes(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matiere.id'), primary_key=True)
    noteDs = db.Column(db.Float)
    noteExamen = db.Column(db.Float)
    moyenne = db.Column(db.Float)

    student = db.relationship("Student", backref="parent_assocs")
    matiere = db.relationship("Matiere", backref="assoc")

    #student = db.relationship("Student", back_populates="matieres")
    #matiere = db.relationship("Matiere", back_populates="students")




    def __init__(self, student, matiere, noteDs, noteExamen, moyenne):

        self.student_id= student
        self.matiere_id = matiere
        self.noteDs=noteDs
        self.noteExamen=noteExamen
        self.moyenne=moyenne


class Student(db.Model, JSONEncoder):
    id = db.Column(db.Integer, primary_key=True)
    cin = db.Column(db.Integer)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    mail = db.Column(db.String(100))
    telf = db.Column(db.String(100))
    matieres = db.relationship("Notes", backref="students", cascade="save-update, merge, " "delete, delete-orphan")


    #matieres= db.relationship('Matiere', secondary = notes, backref=db.backref('students'), lazy='dynamic')
    #matieres = db.relationship('Notes', back_populates=('student'))

    def __init__(self, cin, nom, prenom, mail, telf):
        self.cin = cin
        self.nom = nom
        self.prenom = prenom
        self.mail = mail
        self.telf = telf





class Matiere(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    libelle_mat = db.Column(db.String(150))
    coeff_mat = db.Column(db.Integer)
    semestre = db.Column(db.Integer)

    #students = db.association_proxy('matiere_students', 'student', creator=lambda cor: Notes(student=cor))
    #students = db.relationship('Notes', back_populates=('matiere'))
    students = db.relationship("Notes", backref="matieres", cascade="save-update, merge, " "delete, delete-orphan")


    def __init__(self, libelle_mat, coeff_mat, semestre):
        self.libelle_mat=libelle_mat
        self.coeff_mat=coeff_mat
        self.semestre=semestre



@app.route('/GestionEtudiants')
@is_logged_in
def Index():


    user = request.cookies.get('YourSessionCookie')

    all_data = Student.query.all()
    data = Matiere.query.all()


    return render_template("index.html", students=all_data, user=user, matieres=data )


@app.route('/detail/<id>/')
@is_logged_in
def Detail(id=None):

    user = request.cookies.get('YourSessionCookie')

    all_data = Matiere.query.all()


    idd=str(id)
    print('id étudiant', idd)

    my_data = Student.query.get(idd)
    print('objet étudiant', my_data)

    ids=my_data.id
    print('id étudiant', ids)

    sql = ("SELECT Matiere.libelle_mat, Notes.noteDs, Notes.noteExamen, Matiere.id, Notes.student_id,Notes.matiere_id,Notes.moyenne FROM Notes INNER JOIN Matiere ON Notes.matiere_id = Matiere.id where student_id= {};").format(ids)
    result = db.engine.execute(sql)
    res = [row for row in result]



    return render_template("detail.html", student= my_data, notess=res, matieres=all_data, user=user)




@app.route('/updateNotes', methods=['POST'])
@is_logged_in
def updateNotes():


    if request.method == 'POST':




        noteDs = request.form['noteDs']
        noteExamen = request.form['noteExamen']

        student_id = request.form['student_id']
        matiere_id = request.form['matiere_id']


        db.engine.execute("UPDATE notes SET noteDS=%s, noteExamen=%s WHERE student_id=%s and matiere_id=%s", (noteDs, noteExamen, student_id, matiere_id))

        flash("Etudiant modifié")




        flash("Note modifiée")
        return redirect(url_for('Detail', id = student_id))





@app.route('/')
def hello():


    return render_template("home.html")


@app.route('/test')
def heello():


    return render_template("detail.html")



@app.route('/insert', methods=['POST'])
@is_logged_in
def insert():

    if request.method == 'POST':
        cin = request.form['cin']
        nom = request.form['nom']
        prenom = request.form['prenom']
        mail = request.form['mail']
        telf = request.form['telf']

        my_data = Student(cin, nom, prenom, mail, telf)
        db.session.add(my_data)
        db.session.commit()

        flash("Etudiant ajouté avec succés")

        return redirect(url_for('Index'))


@app.route('/update', methods=['GET', 'POST'])
@is_logged_in
def update():

    if request.method == 'POST':
        my_data = Student.query.get(request.form.get('id'))

        my_data.cin = request.form['cin']
        my_data.nom = request.form['nom']
        my_data.prenom = request.form['prenom']
        my_data.mail = request.form['mail']
        my_data.telf = request.form['telf']

        db.session.commit()
        flash("Etudiant modifié")

        return redirect(url_for('Index'))


@app.route('/delete/<id>/', methods=['GET', 'POST'])
@is_logged_in
def delete(id):
    my_data = Student.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Etudiant supprimé")

    return redirect(url_for('Index'))



@app.route('/GestionMatieres')
def IndexM():
    all_data = Matiere.query.all()

    user = request.cookies.get('YourSessionCookie')

    return render_template("GérerMatiéres.html", matieres=all_data, user=user)



@app.route('/insertM', methods=['POST'])
@is_logged_in
def insertM():
    if request.method == 'POST':
        libelle_mat = request.form['libelle_mat']
        coeff_mat = request.form['coeff_mat']
        semestre = request.form['semestre']



        my_data = Matiere(libelle_mat, coeff_mat, semestre)
        db.session.add(my_data)
        db.session.commit()

        flash("Matière ajoutée avec succés")

        return redirect(url_for('IndexM'))


@app.route('/updateM', methods=['GET', 'POST'])
@is_logged_in
def updateM():
    if request.method == 'POST':
        my_data = Matiere.query.get(request.form.get('id'))

        my_data.libelle_mat = request.form['libelle_mat']
        my_data.coeff_mat = request.form['coeff_mat']
        my_data.semestre= request.form['semestre']


        db.session.commit()
        flash("Matière modifiée")

        return redirect(url_for('IndexM'))


@app.route('/deleteM/<id>/', methods=['GET', 'POST'])
@is_logged_in
def deleteM(id):
    my_data = Matiere.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Matière supprimée")

    return redirect(url_for('IndexM'))


@app.route('/ajoutNote', methods=['GET', 'POST'])
@is_logged_in
def ajoutNote():


    if request.method == 'POST':

        student = Student.query.get(request.form.get('id'))
        matiere = request.form['selected_class']

        id=student.id

        print('objet student ', student)
        print('id student', id)
        print('matière selectionné:', matiere)


        noteDs = float(request.form['noteDs'])
        noteExamen =float(request.form['noteExamen'])

        moyenne=float ((noteDs*0.3)+(noteExamen*0.7))
        print('moooooooyeeeeeeeeeeeennnnne:', moyenne)



        my_data = Notes(id, matiere, noteDs, noteExamen, moyenne)
        db.session.add(my_data)
        db.session.commit()

        flash("Note ajoutée ")

        return redirect(url_for('Detail', id = id))




if __name__ == "__main__":
    app.run(debug=True)
