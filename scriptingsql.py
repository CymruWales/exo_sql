import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

with mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("MYSQL_ROOT_PASSWORD"),
    database="custom_db2"
) as connection:
   with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM adresse;")
    for row in cursor.fetchall():
        print(row)

    with connection.cursor() as cursor:
        print("Insertion d'un nouveau personnage ")
        titre = input("Entrez le titre : ")
        nom = input("Entrez le nom  : ")
        prenom = input("Entrez le prénom : ")
        telephone = input("Entrez le téléphone  : ")
        email = input("Entrez l'email : ")
        cursor.execute("INSERT INTO personne (titre, nom, prenom, email, telephone) VALUES (%s, %s, %s, %s, %s)",
         (titre, nom, prenom, email, telephone)
    )
   