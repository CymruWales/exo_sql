import mysql.connector

import os           

from dotenv import load_dotenv

import datetime

load_dotenv()

def get_connection():
   return mysql.connector.connect(
       host="localhost",
       user="root",
       password=os.getenv("MYSQL_ROOT_PASSWORD"),
       database="custom_db2"
   )

def create_release(version, tag):

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

# Planifier un déploiement

def plan_deployment(release_id, env):

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

# Valider et exécuter le déploiement (transactionnel)

def validate_and_execute_deployment(deploy_id):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    try:

        # Vérifie l'existence du déploiement

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

        # Vérifie s'il n'y a pas un autre déploiement en cours

        cursor.execute("""

            SELECT d.id FROM deploiements d

            JOIN environnements e ON d.id_env = e.id

            WHERE e.nom = %s AND d.etat = 'en_cours'

        """, (env,))

        ongoing = cursor.fetchone()

        if ongoing:

            print(f"Un déploiement est déjà en cours sur {env}.")

            return

        # Passe l'état à 'en_cours'

        cursor.execute("""

            UPDATE deploiements SET etat = 'en_cours' WHERE id = %s

        """, (deploy_id,))

        conn.commit()

        print(f"Déploiement {deploy_id} → en_cours...")

        # Simulation d'exécution (2s + aléatoire)

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

def show_status(env):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""

        SELECT d.id, r.version, d.etat, d.date_deploiement

        FROM deploiements d

        JOIN environnements e ON d.id_env = e.id

        JOIN releases r ON d.id_release = r.id

        WHERE e.nom = %s

    """, (env,))

    for row in cursor.fetchall():

        print(row)

    cursor.close()

    conn.close()
import argparse
import time

def rollback_deployment(deploy_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE deploiements SET etat = 'annulé' WHERE id = %s

    """, (deploy_id,))

    conn.commit()

    print(f"Déploiement {deploy_id} → annulé.")

    cursor.close()

    conn.close()

# Point d'entrée CLI

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")

    # release --create

    release_parser = subparsers.add_parser("release")

    release_parser.add_argument("--create", nargs=2, metavar=("VERSION", "TAG"))

    # deploy --release --env

    deploy_parser = subparsers.add_parser("deploy")

    deploy_parser.add_argument("--release", type=int, required=True)

    deploy_parser.add_argument("--env", required=True)

    # validate --deploy-id

    validate_parser = subparsers.add_parser("validate")

    validate_parser.add_argument("--deploy-id", type=int, required=True)

    # status --env

    status_parser = subparsers.add_parser("status")

    status_parser.add_argument("--env", required=True)

    # rollback --deploy-id

    rollback_parser = subparsers.add_parser("rollback")

    rollback_parser.add_argument("--deploy-id", type=int, required=True)

    args = parser.parse_args()

    if args.command == "release" and args.create:

        create_release(args.create[0], args.create[1])

    elif args.command == "deploy":

        plan_deployment(args.release, args.env)

    elif args.command == "validate":

        validate_and_execute_deployment(args.deploy_id)

    elif args.command == "status":

        show_status(args.env)

    elif args.command == "rollback":

        rollback_deployment(args.deploy_id)

    else:

        parser.print_help()
 