import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'b2da1.settings')
django.setup()

from bd2ap1.models import Cinemas, Salas, Lugares

def create_rooms():
    cinema = Cinemas.objects.first()
    if not cinema:
        print("No cinema found. Please create a cinema first.")
        return

    print(f"Adding rooms to Cinema: {cinema.nomecinema}")

    rooms_data = [
        {
            "nome": "Sala IMAX 1",
            "tipo": "IMAX",
            "filas": 10,
            "colunas": 15,
            "capacidade": 150
        },
        {
            "nome": "Sala VIP 1",
            "tipo": "VIP",
            "filas": 5,
            "colunas": 8,
            "capacidade": 40
        },
        {
            "nome": "Sala 4DX 1",
            "tipo": "4DX",
            "filas": 8,
            "colunas": 12,
            "capacidade": 96
        }
    ]

    for data in rooms_data:
        # Check if room already exists
        if Salas.objects.filter(nomesala=data["nome"], cinemaid=cinema).exists():
            print(f"Room {data['nome']} already exists. Skipping.")
            continue

        sala = Salas.objects.create(
            cinemaid=cinema,
            nomesala=data["nome"],
            tiposala=data["tipo"],
            filas=data["filas"],
            colunas=data["colunas"],
            capacidade=data["capacidade"]
        )
        print(f"Created Room: {sala.nomesala}")

        # Create Seats (Lugares)
        seats = []
        rows = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for r in range(data["filas"]):
            row_label = rows[r]
            for c in range(1, data["colunas"] + 1):
                seat_type = "Standard"
                if data["tipo"] == "VIP":
                    seat_type = "Recliner"
                
                seats.append(Lugares(
                    salaid=sala,
                    fila=row_label,
                    numero=c,
                    tipolugar=seat_type
                ))
        
        Lugares.objects.bulk_create(seats)
        print(f"  - Added {len(seats)} seats to {sala.nomesala}")

if __name__ == "__main__":
    create_rooms()
