from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Secret Key"

# SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/crud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Notes(db.Model):
    student_id = db.Column (db.Integer, db.ForeignKey('student.id'), primary_key=True)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matiere.id'), primary_key=True)
    noteDs = db.Column(db.Float)
    noteExamen = db.Column(db.Float)

    student = db.relationship("Student", backref="parent_assocs")
    matiere = db.relationship("Matiere", backref="assoc")

    #student = db.relationship("Student", back_populates="matieres")
    #matiere = db.relationship("Matiere", back_populates="students")




    def __init__(self, student, matiere, noteDs, noteExamen):

        self.student_id= student
        self.matiere_id = matiere
        self.noteDs=noteDs
        self.noteExamen=noteExamen


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cin = db.Column(db.Integer)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    mail = db.Column(db.String(100))
    telf = db.Column(db.String(100))


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
    students = db.relationship("Notes", backref="matieres")


    def __init__(self, libelle_mat, coeff_mat, semestre):
        self.libelle_mat=libelle_mat
        self.coeff_mat=coeff_mat
        self.semestre=semestre



@app.route('/GestionEtudiants')
def Index():
    all_data = Student.query.all()
    data = Matiere.query.all()


    return render_template("index.html", students=all_data, matieres=data)


@app.route('/detail/<id>/')
def Detail(id):


    idd=str(id)
    print('id étudiant', idd)

    my_data = Student.query.get(idd)
    print('objet étudiant', my_data)

    cin=my_data.cin
    print('cin étudiant', cin)



    return render_template("detail.html", student=my_data)


@app.route('/')
def hello():


    return render_template("home.html")


@app.route('/test')
def heello():


    return render_template("detail.html")



@app.route('/insert', methods=['POST'])
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
def delete(id):
    my_data = Student.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Etudiant supprimé")

    return redirect(url_for('Index'))



@app.route('/GestionMatieres')
def IndexM():
    all_data = Matiere.query.all()

    return render_template("GérerMatiéres.html", matieres=all_data)



@app.route('/insertM', methods=['POST'])
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
def deleteM(id):
    my_data = Matiere.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Matière supprimée")

    return redirect(url_for('IndexM'))


@app.route('/ajoutNote', methods=['GET', 'POST'])
def ajoutNote():


    if request.method == 'POST':

        student = Student.query.get(request.form.get('id'))
        matiere = request.form['selected_class']

        id=student.id

        print('objet student ', student)
        print('id student', id)
        print('matière selectionné:', matiere)


        noteDs = request.form['noteDs']
        noteExamen = request.form['noteExamen']



        my_data = Notes(id, matiere, noteDs, noteExamen)
        db.session.add(my_data)
        db.session.commit()

        flash("Note ajoutée ")

        return redirect(url_for('Index'))


if __name__ == "__main__":
    app.run(debug=True)
