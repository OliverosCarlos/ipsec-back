import argparse
import getpass
import sys
import psycopg2
from psycopg2 import sql
from deploy_tracker import DeployTracker

STEP_CODE = "create_database"
START_INFO = "Iniciando creación de base de datos"

def create_database(db_name, db_user, db_host, db_port, db_password):
    tracker = DeployTracker()
    tracker.reset(STEP_CODE)
    tracker.start(STEP_CODE, status_info=START_INFO)
    tracker.success(STEP_CODE, f"Conectado a '{db_name}' en {db_host}:{db_port} (usuario: {db_user})")

    try:
        print(f"Creando base de datos '{db_name}' en {db_host}:{db_port}...")

        conn = psycopg2.connect(
            dbname="postgres",
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,)
        )

        if cursor.fetchone():
            msg = f"La base de datos '{db_name}' ya existe."
            print(msg)
            tracker.warning(STEP_CODE, msg)
        else:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
            )
            msg = f"Base de datos '{db_name}' creada exitosamente."
            print(msg)
            tracker.success(STEP_CODE, msg)

        cursor.close()
        conn.close()
        tracker.complete(STEP_CODE, status_info="Creación de base de datos completada")

    except Exception as e:
        msg = f"Error al crear la base de datos '{db_name}': {e}"
        print(msg)
        tracker.error(STEP_CODE, msg)
        tracker.fail(STEP_CODE, status_info=str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crear una base de datos en PostgreSQL")
    parser.add_argument("--db-name", default="ipsec-dev", help="Nombre de la base de datos (default: ipsec-dev)")
    parser.add_argument("--db-user", default="postgres", help="Usuario de PostgreSQL (default: postgres)")
    parser.add_argument("--db-host", default="localhost", help="Host de PostgreSQL (default: localhost)")
    parser.add_argument("--db-port", default="5432", help="Puerto de PostgreSQL (default: 5432)")

    args = parser.parse_args()

    print(f"\nSe creará la base de datos '{args.db_name}' en {args.db_host}:{args.db_port} con usuario '{args.db_user}'")
    confirm = input("¿Deseas continuar? (s/n): ").strip().lower()
    if confirm != "s":
        print("Operación cancelada.")
        sys.exit(0)

    password = getpass.getpass(f"Ingresa el password para el usuario '{args.db_user}': ")

    create_database(args.db_name, args.db_user, args.db_host, args.db_port, password)
