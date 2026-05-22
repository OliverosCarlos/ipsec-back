import argparse
import getpass
import sys
import psycopg2
from deploy_tracker import DeployTracker

STEP_CODE = "create_extensions"
START_INFO = "Iniciando creación de extensiones en PostgreSQL"

EXTENSIONS = [
    "pg_trgm",
]


def create_extensions(db_name, db_user, db_host, db_port, db_password):
    tracker = DeployTracker()
    tracker.reset(STEP_CODE)
    tracker.start(STEP_CODE, status_info=START_INFO)

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        tracker.success(STEP_CODE, f"Conectado a '{db_name}' en {db_host}:{db_port} (usuario: {db_user})")

        for ext in EXTENSIONS:
            cursor.execute(
                "SELECT 1 FROM pg_extension WHERE extname = %s;", (ext,)
            )
            if cursor.fetchone():
                msg = f"La extensión '{ext}' ya existe."
                print(msg)
                tracker.warning(STEP_CODE, msg)
            else:
                cursor.execute(f"CREATE EXTENSION IF NOT EXISTS {ext};")
                msg = f"Extensión '{ext}' creada exitosamente."
                print(msg)
                tracker.success(STEP_CODE, msg)

        cursor.close()
        conn.close()
        tracker.complete(STEP_CODE, status_info="Creación de extensiones completada")

    except Exception as e:
        msg = f"Error al crear extensiones: {e}"
        print(msg)
        tracker.error(STEP_CODE, msg)
        tracker.fail(STEP_CODE, status_info=str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crear extensiones requeridas en PostgreSQL")
    parser.add_argument("--db-name", default="ipsec-dev", help="Nombre de la base de datos (default: ipsec-dev)")
    parser.add_argument("--db-user", default="postgres", help="Usuario de PostgreSQL (default: postgres)")
    parser.add_argument("--db-host", default="localhost", help="Host de PostgreSQL (default: localhost)")
    parser.add_argument("--db-port", default="5432", help="Puerto de PostgreSQL (default: 5432)")
    parser.add_argument("--db-password", default=None, help="Password de PostgreSQL (opcional, si no se pasa se pedirá por consola)")

    args = parser.parse_args()

    print(f"\nSe crearán las extensiones {EXTENSIONS} en '{args.db_name}' ({args.db_host}:{args.db_port}, usuario: '{args.db_user}')")
    confirm = input("¿Deseas continuar? (s/n): ").strip().lower()
    if confirm != "s":
        print("Operación cancelada.")
        sys.exit(0)

    if args.db_password is not None:
        password = args.db_password
    else:
        password = getpass.getpass(f"Ingresa el password para el usuario '{args.db_user}': ")

    create_extensions(args.db_name, args.db_user, args.db_host, args.db_port, password)
