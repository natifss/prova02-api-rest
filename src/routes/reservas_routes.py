import random

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlmodel import select

from src.config.database import get_session
from src.models.reservas_model import Reserva
from src.models.voos_model import Voo

reservas_router = APIRouter(prefix="/reservas")


@reservas_router.get("/{id_voo}")
def lista_reservas_voo(id_voo: int):
    with get_session() as session:
        statement = select(Reserva).where(Reserva.voo_id == id_voo)
        reservas = session.exec(statement).all()
        return reservas


@reservas_router.post("")
def cria_reserva(reserva: Reserva):
    with get_session() as session:
        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                content={"message": f"Voo com id {reserva.voo_id} não encontrado."},
                status_code=404,
            )

        # TODO - Validar se existe uma reserva para o mesmo documento
        existing_reserva = session.exec(select(Reserva).where(Reserva.documento == reserva.documento)).first()
        if existing_reserva:
            return JSONResponse(
                content={"message": "Já existe uma reserva com este número de documento."},
                status_code=400,
            )

        codigo_reserva = "".join(
            [str(random.randint(0, 999)).zfill(3) for _ in range(2)]
        )

        reserva.codigo_reserva = codigo_reserva
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva


@reservas_router.post("/{codigo_reserva}/checkin/{num_poltrona}")
def faz_checkin(codigo_reserva: str, num_poltrona: str):
    # TODO - Implementar reserva de poltrona
    pass
    with get_session() as session:
        reserva = session.exec(select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)).first()
        if not reserva:
            return JSONResponse(
                content={"message": "Reserva não encontrada."},
                status_code=404,
            )
        
        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                content={"message": "Voo não encontrado"},
                status_code=404,
            )
        
# TODO - Implementar troca de reserva de poltrona
        
        ultimo_digito = int(num_poltrona[-1])

        poltrona = getattr(voo, f"poltrona_{ultimo_digito}")

        if poltrona:
            return JSONResponse(
                content={"message": "Poltrona já ocupada"},
                status_code=400,
            )

        setattr(voo, f"poltrona_{ultimo_digito}", codigo_reserva)
        session.commit()
        return JSONResponse(
            content={"message": "Check-in efetuado com sucesso"},
            status_code=200,
        )
