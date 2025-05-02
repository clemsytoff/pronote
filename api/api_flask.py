from flask import Flask, jsonify, request
import mysql.connector
import bcrypt
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

#définition des fonctions systeme
def log(msg, status="..."):
    print(f"[LOG] {msg} {status}")
    time.sleep(2)

def sys_logs(message):
    with open("logs.txt", "a", encoding="utf-8") as f:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")
#LOGS A FINIR POUR TOUTES LES ROUTES

#début du programme

print("⏳ Lancement du serveur...")
sys_logs("⏳ Lancement du serveur...")
time.sleep(3)
log("✅ Téléchargement de la dernière version", "OK")
sys_logs("✅ Téléchargement de la dernière version OK")

print("⚙️  Configuration de la base de données en cours...")
sys_logs("⚙️  Configuration de la base de données en cours...")
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pronote" #NE PAS OUBLIER DE CHANGER LES INFOS DE LA DB AVEC VOS PROPRES LOGINS
    )
except Exception as e:
    print(f"[ERREUR] ❌ Connexion à la base de données impossible : {e}")
    sys_logs(f"[ERREUR] ❌ Connexion à la base de données impossible : {e}")
    exit()
log("✅ Connexion à la base de données", "OK")
sys_logs("✅ Connexion à la base de données OK")
log("✅ Connexion au front-end", "OK")
sys_logs("✅ Connexion au front-end OK")

try:
    log("✅ API lancée", "OK")
    sys_logs("✅ API lancée OK")
except Exception as e:
    print(f"[ERREUR] ❌ Lancement de l'API échoué : {e}")
    sys_logs(f"[ERREUR] ❌ Lancement de l'API échoué : {e}")
    exit()

try:
    cursor = db.cursor()
    print("🚀 Serveur lancé avec succès !")
    sys_logs("🚀 Serveur lancé avec succès !")
except Exception as e:
    print(f"[ERREUR] ❌ Impossible de créer un curseur MySQL : {e}")
    sys_logs(f"[ERREUR] ❌ Impossible de créer un curseur MySQL : {e}")
    exit()

#verif du mdp compte admin
cursor.execute("SELECT password FROM users WHERE name = %s", ("Admin",))
data = cursor.fetchone()

if data and data[0] == "Admin1234":
    print("\033[91m" + "="*60)
    print("⚠️  ATTENTION : CHANGEZ LE MOT DE PASSE DU COMPTE ADMINISTRATEUR SYSTEME IMMEDIATEMENT ! ⚠️")
    print("="*60 + "\033[0m")
    sys_logs("⚠️  CHANGEZ LE MOT DE PASSE DU COMPTE ADMINISTRATEUR SYSTEME IMMEDIATEMENT ! ⚠️")


#route root
@app.route("/", methods=["GET"])
def root():
 sys_logs("Route '/' 200 OK")
 return jsonify({"message": "API Pronote lancee et fonctionnelle!"}), 200



#---------------------------------------------------------------------------USERS------------------------------------------------------

#créer un utilisateur
@app.route("/api/v1/public/auth/register", methods=["POST"])
def create_user():
    data = request.json
    name = data.get("name")
    surname = data.get("surname")
    classe = data.get("classe")
    password = data.get("password")
    #vérifications

    if not name or not surname or not classe or not password:
        return jsonify({"error": "Veuillez remplir tous les champs"}), 400
    
    #verif admin
    if name == "Admin" or surname == "Admin":
        return jsonify({"error": "Impossible de créer un compte nommé 'Admin'"}), 400
    
    #verif longueurs
    if not 0<int(len(name))<=100 or not 0<int(len(surname))<=100 or not 0<int(len(classe))<=50 or not 0<len(password)<=255:
        return jsonify({"error": "Veuillez respecter la longueur de chaque champ"}), 400
    
    #hash du mdp
    hashed_password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    #ajout à la db
    cursor.execute("INSERT INTO users (name,surname,classe,password,grade) VALUES (%s,%s,%s,%s,%s)", (name,surname,classe,hashed_password,0,)) #on met le grade à 0 (élève)
    db.commit()
    return jsonify({"message": "Utilisateur créé avec succès"}), 201

#liste utilisateurs
@app.route("/api/v1/admin/users", methods=["GET"])
def get_users():
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()

    users = [
        {
            "id": row[0],
            "name": row[1],
            "surname": row[2],
            "classe": row[3],
            "account_creation": row[5],
            "grade": row[6]
        }
        for row in data
    ]

    return jsonify(users)


#supprimer un utilisateur
@app.route("/api/v1/admin/users/delete/<int:user_id>", methods=["DELETE"])
def delete_cuser(user_id):
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    return jsonify({"message": "Utilisateur supprimé avec succès"})


#liste utilisateurs par id
@app.route("/api/v1/admin/users/<int:user_id>", methods=["GET"])
def get_users_by_id(user_id):
    cursor.execute("SELECT * FROM users WHERE id = %s",(user_id,))
    data = cursor.fetchall()

    users = [
        {
            "id": row[0],
            "name": row[1],
            "surname": row[2],
            "classe": row[3],
            "account_creation": row[5],
            "grade": row[6]
        }
        for row in data
    ]

    return jsonify(users)




# a ajouter : edit user





#---------------------------------------------------------------------------DEVOIRS------------------------------------------------------

#creer un devoir
@app.route("/api/v1/prof/homeworks/create", methods=["POST"])
def add_homework():
    data = request.json
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date") #BUG AVEC LA DATE
    user_id = data.get("user_id")
    matiere_id = data.get("matiere_id")

    #verifs
    if not title or not description or not due_date or not user_id or not matiere_id:
        return jsonify({"error": "Veuillez remplir tous les champs"}), 400
    #verif de longueur
    if not 0<int(len(title))<=255:
        return jsonify({"error": "Veuillez respecter la taille des champs"}), 400
    
    #ajout à la db
    cursor.execute("INSERT INTO devoirs (title,description,due_date,user_id,matiere_id) VALUES (%s,%s,%s,%s,%s)", (title,description,due_date,user_id,matiere_id,))
    db.commit()
    return jsonify({"message": "Devoirs ajouté avec succès"}), 201



#liste de tous les devoirs
@app.route("/api/v1/prof/homeworks/all", methods=["GET"])
def get_homeworks():
    cursor.execute("""
SELECT 
    devoirs.title, 
    devoirs.description, 
    devoirs.due_date, 
    users.name AS prof_nom, 
    users.surname AS prof_prenom,
    matieres.name AS matiere
FROM devoirs
JOIN users ON devoirs.user_id = users.id
JOIN matieres ON devoirs.matiere_id = matieres.id;
    """)
    data = cursor.fetchall()

    homeworks = [
        {
            "title": row[0],
            "description": row[1],
            "due_date": row[2],
            "prof_name": row[3],
            "prof_surname": row[4],
            "matiere": row[5]
        }
        for row in data
    ]

    return jsonify(homeworks)

# Liste des devoirs par matière
@app.route("/api/v1/prof/homeworks/list/<int:id>", methods=["GET"])
def get_homeworks_by_matiere(id):
    cursor.execute("""
    SELECT 
        devoirs.title, 
        devoirs.description, 
        devoirs.due_date, 
        users.name AS prof_nom, 
        users.surname AS prof_prenom,
        matieres.name AS matiere
    FROM devoirs
    JOIN users ON devoirs.user_id = users.id
    JOIN matieres ON devoirs.matiere_id = matieres.id
    WHERE matieres.id = %s;
    """, (id,))
    data = cursor.fetchall()
    homeworks = [{
        "title": row[0],
        "description": row[1],
        "due_date": row[2],
        "prof_name": row[3],
        "prof_surname": row[4],
        "matiere": row[5]
    } for row in data]
    return jsonify(homeworks)



#ajouter modif devoirs et suppr





#---------------------------------------------------------------------------MATIERES------------------------------------------------------


#ajout matière
@app.route("/api/v1/admin/matieres/create", methods=["POST"])
def create_matiere():
    data = request.json
    name = data.get("name")
    #vérifications

    if not name:
        return jsonify({"error": "Veuillez remplir tous les champs"}), 400
    #verif longueurs
    if not 0<int(len(name))<=100:
        return jsonify({"error": "Veuillez respecter la longueur de chaque champ"}), 400
    
    #ajout à la db
    cursor.execute("INSERT INTO matieres (name) VALUES (%s)", (name,))
    db.commit()
    return jsonify({"message": "Matière créée avec succès"}), 201



#suppression matière
@app.route("/api/v1/admin/matieres/delete/<int:matiere_id>", methods=["DELETE"])
def delete_matiere(matiere_id):
    cursor.execute("DELETE FROM matieres WHERE id = %s", (matiere_id,))
    db.commit()
    return jsonify({"message": "Matière supprimée avec succès"})




#liste matières
@app.route("/api/v1/admin/matieres/all", methods=["GET"])
def list_matieres():
    cursor.execute("""
SELECT *
FROM matieres
    """)
    data = cursor.fetchall()

    matieres = [
        {
            "id": row[0],
            "name": row[1]
        }
        for row in data
    ]

    return jsonify(matieres)


#modifier une matière par son id
@app.route("/api/v1/public/matieres/edit/<int:matiere_id>", methods=["PUT"])
def update_matiere(matiere_id):
    data = request.json
    new_name = data.get("name")
    if not new_name:
        return jsonify({"error": "Veuillez remplir tous les champs"}), 400
    cursor.execute("UPDATE matieres SET name = %s WHERE id = %s", (new_name, matiere_id))
    db.commit()
    return jsonify({"message": "Matière modifiée avec succès"})





#---------------------------------------------------------------------------MESSAGES------------------------------------------------------


#créer un message

@app.route("/api/v1/public/messages/create", methods=["POST"])
def add_message():
    data = request.json
    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    subject = data.get("subject")
    body = data.get("body")
    
    #verifs
    if not sender_id or not receiver_id or not subject or not body:
        return jsonify({"error": "Veuillez remplir tous les champs"}), 400
    #verif longueur
    if not 0<int(len(subject))<=255:
        return jsonify({"error": "Veuillez respecter la longueur des champs"}), 400
    #ajout à la db
    cursor.execute("INSERT INTO messages (sender_id,receiver_id,subject,body) VALUES (%s,%s,%s,%s)", (sender_id,receiver_id,subject,body,))
    db.commit()
    return jsonify({"message": "Message créé (envoyé) avec succès"}), 201


#liste de tous les messages
@app.route("/api/v1/admin/messages/all", methods=["GET"])
def list_messages():
    cursor.execute("""
SELECT *
FROM messages
    """)
    data = cursor.fetchall()

    messages = [
        {
            "id": row[0],
            "sender_id": row[1],
            "receiver_id": row[2],
            "subject": row[3],
            "body": row[4],
            "send_at": row[5]
        }
        for row in data
    ]

    return jsonify(messages)


#liste messages par envoyeur
@app.route("/api/v1/admin/messages/sender/<int:sender_id>", methods=["GET"])
def list_messages_by_sender(sender_id):
    cursor.execute("""
SELECT *
FROM messages
WHERE sender_id = %s
    """,(sender_id,))
    data = cursor.fetchall()

    messages = [
        {
            "id": row[0],
            "sender_id": row[1],
            "receiver_id": row[2],
            "subject": row[3],
            "body": row[4],
            "send_at": row[5]
        }
        for row in data
    ]

    return jsonify(messages)




#liste messages par destinataire
@app.route("/api/v1/admin/messages/receiver/<int:receiver_id>", methods=["GET"])
def list_messages_by_receiver(receiver_id):
    cursor.execute("""
SELECT *
FROM messages
WHERE receiver_id = %s
    """,(receiver_id,))
    data = cursor.fetchall()

    messages = [
        {
            "id": row[0],
            "sender_id": row[1],
            "receiver_id": row[2],
            "subject": row[3],
            "body": row[4],
            "send_at": row[5]
        }
        for row in data
    ]

    return jsonify(messages)





#---------------------------------------------------------------------------NOTES------------------------------------------------------



#créer une note
@app.route("/api/v1/prof/notes/create", methods=["POST"])
def add_note():
    data = request.json
    user_id = data.get("user_id")
    matiere_id = data.get("matiere_id")
    note_value = data.get("note_value")
    note_name = data.get("note_name")

    #verifs
    if not user_id or not matiere_id or not note_value or not note_name:
        return jsonify({"error": "Veuillez remplir tous les champs"}), 400
    #verif longueurs
    if not 0<int(len(note_name))<=100:
        return jsonify({"error": "Veuillez respecter la longueur des champs"}), 400
    if not 0<=note_value<=20: #on prend en charge que les notes / 20
        return jsonify({"error": "La note doit être comprise en 0 et 20"}), 400

    #ajout à la db
    cursor.execute("INSERT INTO notes (user_id,matiere_id,note_value,note_name) VALUES (%s,%s,%s,%s)", (user_id,matiere_id,note_value,note_name,))
    db.commit()
    return jsonify({"message": "Note ajoutée avec succès"}), 201



#list toutes les notes
@app.route("/api/v1/prof/notes/all", methods=["GET"])
def get_notes():
    cursor.execute("SELECT * FROM notes")
    data = cursor.fetchall()
    notes = [{"id": row[0], "user_id": row[1], "note_name": row[2], "matiere_id": row[3], "note_value": row[4], "note_date": row[5]} for row in data]
    return jsonify(notes)


#list notes par id (élève)
@app.route("/api/v1/prof/notes/user/<int:user_id>", methods=["GET"])
def get_notes_by_id_user(user_id):
    cursor.execute("SELECT * FROM notes WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    notes = [{"id": row[0], "user_id": row[1], "note_name": row[2], "matiere_id": row[3], "note_value": row[4], "note_date": row[5]} for row in data]
    return jsonify(notes)

#list notes par matiere
@app.route("/api/v1/prof/notes/matiere/<int:matiere_id>", methods=["GET"])
def get_notes_by_id_matiere(matiere_id):
    cursor.execute("SELECT * FROM notes WHERE matiere_id = %s", (matiere_id,))
    data = cursor.fetchall()
    notes = [{"id": row[0], "user_id": row[1], "note_name": row[2], "matiere_id": row[3], "note_value": row[4], "note_date": row[5]} for row in data]
    return jsonify(notes)

@app.route("/api/v1/prof/notes/delete/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    db.commit()
    return jsonify({"message": "Note supprimée avec succès"})

#a faire : edit note



























#---------------------------------------------------------------------------SYSTEME [NE PAS MODIFIER]------------------------------------------------------
#la partie qui suis est une partie pour les développeurs, lors de l'utilisation professionnelle de Pronote Reimagined, pour le bon fonctionnement du systeme 
# veuillez ne pas utiliser les routes suivantes sans faire de sauvegarde.

#---------------------------------------------------------------------------GRADES------------------------------------------------------

#ajouter un grade
@app.route("/api/v1/dev/grades/create", methods=["POST"])
def add_grade():
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "Veuillez remplir tous les champs"}), 400
    if not 0<int(len(name))<=50:
        return jsonify({"error": "Veuillez respecter la longueur des champs"}), 400
    cursor.execute("INSERT INTO grades (grade_name) VALUES (%s)", (name,))
    db.commit()

    print("\033[91m" + "="*60)
    print("⚠️  ATTENTION : Route de développement utilisée ! Ne pas utiliser en production. ⚠️")
    print("="*60 + "\033[0m")
    sys_logs("⚠️  ATTENTION : Route de développement '/api/v1/dev/grades/create' utilisée ! Ne pas utiliser en production. ⚠️")

    return jsonify({"message": "Grade créé avec succès"}), 201

#supprimer un grade
@app.route("/api/v1/dev/grades/delete/<int:grade_id>", methods=["DELETE"])
def delete_grade(grade_id):
    cursor.execute("DELETE FROM grades WHERE id = %s", (grade_id,))
    db.commit()

    print("\033[91m" + "="*60)
    print("⚠️  ATTENTION : Route de développement '/api/v1/dev/grades/delete/<int:grade_id>' utilisée ! Ne pas utiliser en production. ⚠️")
    print("="*60 + "\033[0m")

    return jsonify({"message": "Grade supprimé avec succès"})

#liste des grades -- Fonction non dev
@app.route("/api/v1/admin/grades/all", methods=["GET"])
def get_grades():
    cursor.execute("SELECT * FROM grades")
    data = cursor.fetchall()
    grades = [{"id": row[0], "name": row[1]} for row in data]
    return jsonify(grades)

#liste des grades par ID -- Fonction non dev
@app.route("/api/v1/admin/grades/list/<int:grade_id>", methods=["GET"])
def get_grades_by_id(grade_id):
    cursor.execute("SELECT * FROM grades WHERE id = %s",(grade_id,))
    data = cursor.fetchall()
    grades = [{"id": row[0], "name": row[1]} for row in data]
    return jsonify(grades)



#fin du programme -- NE SURTOUT PAS TOUCHER
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)