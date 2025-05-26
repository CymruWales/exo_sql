import mysql.connector
from tabulate import tabulate
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
        print("ouverture dun tickets d'incidents")
        titre = input("Entrez le titre : ")
        detail = input("Entrez le detail : ")
        priorite = input("Entrez la priorite : ")
        statut = input("Entrez le statut : ")
        cursor.execute("INSERT INTO exo (titre, detail, priorite, statut) VALUES (%s, %s, %s, %s)", (titre, detail, priorite, statut)
    )
        print("Ticket d'incident ouvert avec succès !")
        rows = cursor.fetchall()
        for row in rows:
            print(row)  
            
        cursor.execute("SELECT * FROM exo")
        rows = cursor.fetchall()
        print(tabulate(rows, headers=[i[0] for i in cursor.description], tablefmt="grid"))
        
        connection.commit()
        print("Les modifications ont été enregistrées.")
        
        print("Liste des tickets d'incidents :")
        cursor.execute("SELECT * FROM exo")
        rows = cursor.fetchall()
        print(tabulate(rows, headers=[i[0] for i in cursor.description], tablefmt="grid"))
        print("Fermeture du ticket d'incident")
        ticket_id = input("Entrez l'ID du ticket à fermer : ")      
        cursor.execute("UPDATE exo SET statut = 'fermé' WHERE id = %s", (ticket_id,))
        connection.commit() 
        print("Ticket d'incident fermé avec succès !")
        cursor.execute("SELECT * FROM exo")
        rows = cursor.fetchall()
        print(tabulate(rows, headers=[i[0] for i in cursor.description], tablefmt="grid"))
        print('modification du ticket d\'incident')
        ticket_id = input("Entrez l'ID du ticket à modifier : ")    
        titre = input("Entrez le nouveau titre : ")
        detail = input("Entrez le nouveau détail : ")
        priorite = input("Entrez la nouvelle priorité : ")
        statut = input("Entrez le nouveau statut : ")
        cursor.execute("UPDATE exo SET titre = %s, detail = %s, priorite = %s, statut = %s WHERE id = %s", (titre, detail, priorite, statut, ticket_id))
        connection.commit()
        print("Ticket d'incident modifié avec succès !")
        cursor.execute("SELECT * FROM exo")
        rows = cursor.fetchall()
        print(tabulate(rows, headers=[i[0] for i in cursor.description], tablefmt="grid"))
        print('suppression du ticket d\'incident')
        ticket_id = input("Entrez l'ID du ticket à supprimer : ")     
        cursor.execute("DELETE FROM exo WHERE id = %s", (ticket_id,))
        connection.commit()
        print("Ticket d'incident supprimé avec succès !")
        cursor.execute("SELECT * FROM exo")
        rows = cursor.fetchall()
        print(tabulate(rows, headers=[i[0] for i in cursor.description], tablefmt="grid"))
        print("Fin du programme.")
        