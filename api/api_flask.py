from flask import Flask, jsonify, request
import mysql.connector
import bcrypt
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

def log(msg, status="..."):
    print(f"[LOG] {msg} {status}")
    time.sleep(2)

print("⏳ Lancement du serveur...")
time.sleep(3)
log("✅ Téléchargement de la dernière version", "OK")

print("⚙️  Configuration de la base de données en cours...")
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pronote" #NE PAS OUBLIER DE CHANGER LES INFOS DE LA DB AVEC VOS PROPRES LOGINS
    )
except Exception as e:
    print(f"[ERREUR] ❌ Connexion à la base de données impossible : {e}")
    exit()
log("✅ Connexion à la base de données", "OK")
log("✅ Connexion au front-end", "OK")

try:
    log("✅ API lancée", "OK")
except Exception as e:
    print(f"[ERREUR] ❌ Lancement de l'API échoué : {e}")
    exit()

try:
    cursor = db.cursor()
    print("🚀 Serveur lancé avec succès !")
except Exception as e:
    print(f"[ERREUR] ❌ Impossible de créer un curseur MySQL : {e}")
    exit()



#route root
@app.route("/", methods=["GET"])
def root():
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



# a ajouter : edit user, suppr user, liste user par id





#---------------------------------------------------------------------------DEVOIRS------------------------------------------------------

#creer un devoir
@app.route("/api/v1/public/homeworks/create", methods=["POST"])
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
@app.route("/api/v1/public/homeworks/all", methods=["GET"])
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
@app.route("/api/v1/public/homeworks/list/<int:id>", methods=["GET"])
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



#ajouter modif devoirs





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


#modifier une matière par son id ---- A FINIR
@app.route("/api/v1/public/matieres/edit/<int:matiere_id>", methods=["PUT"])
def update_matiere(matiere_id):
    data = request.json
    new_content = data.get("content")
    if not new_content:
        return jsonify({"error": "Content is required"}), 400
    cursor.execute("UPDATE comments SET content = %s WHERE id = %s", (new_content, comment_id))
    db.commit()
    return jsonify({"message": "Comment updated successfully"})





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
















































































#fin du programme
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)