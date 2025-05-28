import mysql.connector
import os
import random
import time
from dotenv import load_dotenv
load_dotenv()
def get_connection():
   return mysql.connector.connect(
       host="localhost",
       user="root",
       password=os.getenv("MYSQL_ROOT_PASSWORD"),
       database="custom_db2"
   )
def create_release():
   version = input("Version de la release : ")
   tag = input("Tag git : ")
   conn = get_connection()
   cursor = conn.cursor()
   cursor.execute("""
       INSERT INTO releases (version, tag_git, date_creation)
       VALUES (%s, %s, NOW())
   """, (version, tag))
   conn.commit()
   print(f"Release {version} créée avec le tag {tag}.")
   cursor.close()
   conn.close()
def plan_deployment():
   release_id = input("ID de la release : ")
   env = input("Environnement (dev, staging, prod) : ")
   conn = get_connection()
   cursor = conn.cursor()
   cursor.execute("SELECT id FROM environnements WHERE nom = %s", (env,))
   env_row = cursor.fetchone()
   if not env_row:
       print(f"Environnement {env} introuvable.")
       return
   cursor.execute("""
       INSERT INTO deploiements (id_release, id_env, etat, date_deploiement)
       VALUES (%s, %s, 'planifié', NOW())
   """, (release_id, env_row[0]))
   conn.commit()
   print(f"Déploiement planifié pour release {release_id} sur {env}.")
   cursor.close()
   conn.close()
def validate_and_execute_deployment():
   deploy_id = input("ID du déploiement : ")
   conn = get_connection()
   cursor = conn.cursor(dictionary=True)
   try:
       cursor.execute("""
           SELECT d.id, e.nom, d.etat
           FROM deploiements d
           JOIN environnements e ON d.id_env = e.id
           WHERE d.id = %s
       """, (deploy_id,))
       deploy = cursor.fetchone()
       if not deploy:
           print(f"Aucun déploiement avec l'ID {deploy_id}.")
           return
       env = deploy['nom']
       cursor.execute("""
           SELECT d.id FROM deploiements d
           JOIN environnements e ON d.id_env = e.id
           WHERE e.nom = %s AND d.etat = 'en_cours'
       """, (env,))
       ongoing = cursor.fetchone()
       if ongoing:
           print(f"Un déploiement est déjà en cours sur {env}.")
           return
       cursor.execute("""
           UPDATE deploiements SET etat = 'en_cours' WHERE id = %s
       """, (deploy_id,))
       conn.commit()
       print(f"Déploiement {deploy_id} → en_cours...")
       time.sleep(2)
       success = random.choice([True, False])
       if success:
           cursor.execute("""
               UPDATE deploiements SET etat = 'réussi' WHERE id = %s
           """, (deploy_id,))
           cursor.execute("""
               INSERT INTO audit_logs (message, date_creation)
               VALUES (%s, NOW())
           """, (f"Déploiement {deploy_id} réussi",))
           conn.commit()
           print("Déploiement réussi !")
       else:
           cursor.execute("""
               UPDATE deploiements SET etat = 'planifié' WHERE id = %s
           """, (deploy_id,))
           cursor.execute("""
               INSERT INTO audit_logs (message, date_creation)
               VALUES (%s, NOW())
           """, (f"Déploiement {deploy_id} échoué. Rollback effectué.",))
           conn.commit()
           print("Échec : rollback en planifié.")
   except Exception as e:
       conn.rollback()
       print("Erreur pendant le déploiement:", e)
   finally:
       cursor.close()
       conn.close()
def show_status():
   env = input("Environnement (dev, staging, prod) : ")
   conn = get_connection()
   cursor = conn.cursor(dictionary=True)
   cursor.execute("""
       SELECT d.id, r.version, d.etat, d.date_deploiement
       FROM deploiements d
       JOIN environnements e ON d.id_env = e.id
       JOIN releases r ON d.id_release = r.id
       WHERE e.nom = %s
   """, (env,))
   rows = cursor.fetchall()
   if not rows:
       print(f"Aucun déploiement pour l'environnement {env}.")
   else:
       for row in rows:
           print(row)
   cursor.close()
   conn.close()
def rollback_deployment():
   deploy_id = input("ID du déploiement à annuler : ")
   conn = get_connection()
   cursor = conn.cursor()
   cursor.execute("""
       UPDATE deploiements SET etat = 'annulé' WHERE id = %s
   """, (deploy_id,))
   conn.commit()
   print(f"Déploiement {deploy_id} → annulé.")
   cursor.close()
   conn.close()
def main_menu():
   while True:
       print("\n=== MENU DEPLOIEMENT ===")
       print("1. Créer une release")
       print("2. Planifier un déploiement")
       print("3. Valider et exécuter un déploiement")
       print("4. Voir le statut d’un environnement")
       print("5. Rollback (annuler) un déploiement")
       print("0. Quitter")
       choix = input("Choix : ")
       if choix == "1":
           create_release()
       elif choix == "2":
           plan_deployment()
       elif choix == "3":
           validate_and_execute_deployment()
       elif choix == "4":
           show_status()
       elif choix == "5":
           rollback_deployment()
       elif choix == "0":
           print("Au revoir !")
           break
       else:
           print("Choix invalide.")
if __name__ == "__main__":
   main_menu()