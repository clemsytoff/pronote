from flask import Flask, jsonify, request
import mysql.connector
import bcrypt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration de la base de données
db = mysql.connector.connect(
 host="#",
 user="#",
 password="#",
 database="#"
)

cursor = db.cursor()


#créer un utilisateur
@app.route("/api/v1/public/create_user", methods=["POST"])
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
    if not 0<len(name)<=100 or not 0<len(surname)<=100 or not 0<len(classe)<=50 or not 0<len(password)<=255:
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
    users = [{"id": row[0], "name": row[1], "surname": row[2], "classe": row[3], "account_creation": row[5], "grade": row[6]} for row in data]
    return jsonify(users)



















#fin du programme
if __name__ == "__main__":
    app.run(debug=True)