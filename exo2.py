import mysql.connector

import os           

from dotenv import load_dotenv

import datetime

load_dotenv()

def ajouter_utilisateur():
   nom = input("Nom de l'utilisateur : ")
   email = input("Email : ")
   cursor.execute("INSERT INTO utilisateurs (nom, email) VALUES (%s, %s)", (nom, email))
   conn.commit()
   print("Utilisateur ajouté ")

def ajouter_livre():
   titre = input("Titre du livre : ")
   auteur = input("Auteur : ")
   cursor.execute("INSERT INTO livres (titre, auteur) VALUES (%s, %s)", (titre, auteur))
   conn.commit()
   print("Livre ajouté ")
def enregistrer_emprunt():
   id_utilisateur = input("ID de l'utilisateur : ")
   id_livre = input("ID du livre : ")
   date_emprunt = datetime.date.today().isoformat()
   cursor.execute("""
       INSERT INTO emprunts (id_utilisateur, id_livre, date_emprunt, date_retour)
       VALUES (%s,%s,%s, NULL)
   """, (id_utilisateur, id_livre, date_emprunt))
   conn.commit()
   print("Emprunt enregistré ")
def afficher_emprunts_en_cours():
   cursor.execute("""
       SELECT u.nom, l.titre, e.date_emprunt
       FROM emprunts e
       JOIN utilisateurs u ON e.id_utilisateur = u.id
       JOIN livres l ON e.id_livre = l.id
       WHERE e.date_retour IS NULL
   """)
   rows = cursor.fetchall()
   if rows:
       print("\nEmprunts en cours :")
       for row in rows:
           print(f"Utilisateur: {row[0]} | Livre: {row[1]} | Date emprunt: {row[2]}")
   else:
       print("Aucun emprunt en cours")
def afficher_historique_utilisateur():
   id_utilisateur = input("ID de l'utilisateur : ")
   cursor.execute("""
       SELECT l.titre, e.date_emprunt, e.date_retour
       FROM emprunts e
       JOIN livres l ON e.id_livre = l.id
       WHERE e.id_utilisateur = %s
   """, (id_utilisateur,))
   rows = cursor.fetchall()
   if rows:
       print("\nHistorique des emprunts :")
       for row in rows:
           date_retour = row[2] if row[2] else "En cours"
           print(f"Livre: {row[0]} | Date emprunt: {row[1]} | Retour: {date_retour}")
   else:
       print("Aucun emprunt pour cet utilisateur.")

def main():
   while True:
       print("""
       Choisissez une option :
       1. ajouter un utilisateur
       2. ajouter un livre
       3. enregistrer un emprunt
       4. afficher les emprunts en cours
       5. afficher l'historique d'un utilisateur
       6. quitter
       """)
       choix = input("Votre choix : ")
       if choix == "1":
           ajouter_utilisateur()
       elif choix == "2":
           ajouter_livre()
       elif choix == "3":
           enregistrer_emprunt()
       elif choix == "4":
           afficher_emprunts_en_cours()
       elif choix == "5":
           afficher_historique_utilisateur()
       elif choix == "6":
           break
       else:
           print("Choix invalide.")

with mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("MYSQL_ROOT_PASSWORD"),
    database="custom_db"
    ) as conn:
        cursor = conn.cursor()

        if __name__ == "__main__":
            main()