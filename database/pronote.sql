CREATE TABLE grades (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    grade_name VARCHAR(50) NOT NULL
);

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    account_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grade_id INT NOT NULL,
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE
);

CREATE TABLE matieres (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE devoirs (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    due_date DATE NOT NULL,
    user_id INT NOT NULL,
    matiere_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (matiere_id) REFERENCES matieres(id) ON DELETE CASCADE
);

CREATE TABLE messages (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE notes (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    note_name VARCHAR(100) NOT NULL,
    matiere_id INT NOT NULL,
    note_value FLOAT NOT NULL,
    note_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (matiere_id) REFERENCES matieres(id) ON DELETE CASCADE
);

-- Insertion des rôles de base
INSERT INTO grades (grade_name) VALUES 
    ('eleve'),
    ('professeur'),
    ('parent'),
    ('administration'),
    ('administrateur systeme');

-- Insertion de l'utilisateur admin système
INSERT INTO users (name, surname, class_name, password, grade_id) VALUES 
    ('Admin', 'Admin', 'System', 'Admin1234', 5);
