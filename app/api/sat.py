from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.models.sat import SatAccount, SatInvoice, SatDownloadRequest
from app.schemas.sat import (
    SatAccount as SatAccountSchema,
    SatAccountCreate,
    SatAccountUpdate,
    SatInvoice as SatInvoiceSchema,
    SatDownloadRequest as SatDownloadRequestSchema,
    SatSyncRequest
)
from app.services.sat_service import SatService

router = APIRouter()


# --- Cuentas Fiscales ---

@router.post("/accounts", response_model=SatAccountSchema)
def create_sat_account(account_in: SatAccountCreate, db: Session = Depends(get_db)):
    """
    Registra o actualiza una cuenta fiscal (RFC) para descargas.
    """
    db_account = db.query(SatAccount).filter(SatAccount.rfc == account_in.rfc.upper()).first()
    if db_account:
        # Si ya existe, actualizamos los datos
        db_account.name = account_in.name
        db_account.is_active = account_in.is_active
        db.commit()
        db.refresh(db_account)
        return db_account

    db_account = SatAccount(
        rfc=account_in.rfc.upper(),
        name=account_in.name,
        is_active=account_in.is_active
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.get("/accounts", response_model=List[SatAccountSchema])
def list_sat_accounts(db: Session = Depends(get_db)):
    """
    Lista todas las cuentas fiscales configuradas.
    """
    return db.query(SatAccount).all()


@router.put("/accounts/{rfc}", response_model=SatAccountSchema)
def update_sat_account(rfc: str, account_in: SatAccountUpdate, db: Session = Depends(get_db)):
    """
    Modifica una cuenta fiscal existente.
    """
    db_account = db.query(SatAccount).filter(SatAccount.rfc == rfc.upper()).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Cuenta fiscal no encontrada")
    
    if account_in.name is not None:
        db_account.name = account_in.name
    if account_in.is_active is not None:
        db_account.is_active = account_in.is_active
        
    db.commit()
    db.refresh(db_account)
    return db_account


# --- Facturas y Sincronización ---

@router.post("/sync")
def sync_sat_invoices(sync_in: SatSyncRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Solicita al SAT la descarga masiva de facturas de un RFC en un rango de fechas.
    El proceso es asíncrono y se ejecuta en segundo plano.
    """
    # Validar que exista la cuenta
    account = db.query(SatAccount).filter(SatAccount.rfc == sync_in.rfc.upper()).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"El RFC {sync_in.rfc} no está registrado en el sistema")

    try:
        fecha_ini = date.fromisoformat(sync_in.fecha_inicio)
        fecha_f = date.fromisoformat(sync_in.fecha_fin)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usar YYYY-MM-DD")

    # Si se selecciona "ambas" o un tipo específico
    tipos = []
    if sync_in.tipo == "ambas":
        tipos = ["emitidas", "recibidas"]
    elif sync_in.tipo in ["emitidas", "recibidas"]:
        tipos = [sync_in.tipo]
    else:
        raise HTTPException(status_code=400, detail="El tipo debe ser 'emitidas', 'recibidas' o 'ambas'")

    solicitudes = []
    for tipo_peticion in tipos:
        # Buscar si ya existe una solicitud para este RFC, tipo y rango de fechas exacto
        existing_request = db.query(SatDownloadRequest).filter(
            SatDownloadRequest.account_rfc == account.rfc,
            SatDownloadRequest.tipo_cfdi == tipo_peticion,
            SatDownloadRequest.fecha_inicio == fecha_ini,
            SatDownloadRequest.fecha_fin == fecha_f
        ).order_by(SatDownloadRequest.id.desc()).first()

        # Si ya existe una solicitud y está pendiente o es un error que podemos reintentar (no rechazada con código 5)
        if existing_request and (
            existing_request.status == "pendiente" or 
            (existing_request.status == "error" and "Estatus del SAT no soportado: 5" not in (existing_request.mensaje_error or ""))
        ):
            # Reactivar la solicitud existente para verificación
            existing_request.status = "pendiente"
            existing_request.intentos = 0
            existing_request.mensaje_error = None
            db.commit()
            
            solicitudes.append({
                "id_solicitud": existing_request.id_solicitud,
                "status": "pendiente",
                "cod_estatus": "5000",
                "mensaje": "Se reutiliza y reactiva la solicitud existente para este periodo."
            })
            continue

        try:
            res = SatService.solicitar_descarga(
                db=db,
                rfc=account.rfc,
                fecha_inicio=fecha_ini,
                fecha_fin=fecha_f,
                tipo=tipo_peticion
            )
            solicitudes.append(res)
        except Exception as e:
            solicitudes.append({
                "tipo": tipo_peticion,
                "error": str(e)
            })

    # Ejecutar verificación de solicitudes pendientes de forma asíncrona
    background_tasks.add_task(SatService.verificar_peticiones_pendientes, db)

    return {
        "message": "Solicitudes enviadas al SAT e inicio de sincronización en segundo plano",
        "solicitudes": solicitudes
    }


@router.post("/check-pending")
def check_pending_downloads(db: Session = Depends(get_db)):
    """
    Trigger manual para verificar el estatus de las descargas que siguen pendientes en el SAT.
    """
    resumen = SatService.verificar_peticiones_pendientes(db)
    return {
        "message": "Revisión de solicitudes pendientes finalizada",
        "resumen": resumen
    }


@router.get("/invoices", response_model=List[SatInvoiceSchema])
def list_invoices(
    rfc: str = Query(..., description="RFC del contribuyente"),
    tipo: Optional[str] = Query(None, description="Filtrar por 'emitida' o 'recibida'"),
    start_date: Optional[str] = Query(None, description="Fecha inicio YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Fecha fin YYYY-MM-DD"),
    query: Optional[str] = Query(None, description="Búsqueda de texto (emisor, receptor, conceptos)"),
    db: Session = Depends(get_db)
):
    """
    Devuelve la lista de facturas descargadas de un RFC con filtros aplicados.
    """
    q = db.query(SatInvoice).filter(SatInvoice.account_rfc == rfc.upper())
    
    if tipo:
        q = q.filter(SatInvoice.tipo_cfdi == tipo.lower())
        
    if start_date:
        try:
            dt_start = datetime.combine(date.fromisoformat(start_date), datetime.min.time())
            q = q.filter(SatInvoice.fecha_emision >= dt_start)
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date inválido")
            
    if end_date:
        try:
            dt_end = datetime.combine(date.fromisoformat(end_date), datetime.max.time())
            q = q.filter(SatInvoice.fecha_emision <= dt_end)
        except ValueError:
            raise HTTPException(status_code=400, detail="end_date inválido")
            
    if query:
        search_filter = f"%{query}%"
        q = q.filter(
            (SatInvoice.emisor_rfc.ilike(search_filter)) |
            (SatInvoice.emisor_nombre.ilike(search_filter)) |
            (SatInvoice.receptor_rfc.ilike(search_filter)) |
            (SatInvoice.receptor_nombre.ilike(search_filter)) |
            (SatInvoice.conceptos_resumen.ilike(search_filter)) |
            (SatInvoice.uuid.ilike(search_filter))
        )
        
    return q.order_by(SatInvoice.fecha_emision.desc()).all()


# --- Reportes ---

@router.get("/report")
def get_accounting_report(
    rfc: str = Query(..., description="RFC del contribuyente"),
    mes: str = Query(..., description="Mes del reporte YYYY-MM"),
    db: Session = Depends(get_db)
):
    """
    Genera y descarga el archivo Excel contable para un RFC y mes en particular.
    """
    try:
        year, month = map(int, mes.split("-"))
    except ValueError:
        raise HTTPException(status_code=400, detail="El mes debe estar en formato YYYY-MM")

    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    invoices = db.query(SatInvoice).filter(
        SatInvoice.account_rfc == rfc.upper(),
        SatInvoice.fecha_emision >= start_date,
        SatInvoice.fecha_emision < end_date
    ).order_by(SatInvoice.fecha_emision.asc()).all()

    report_filename = f"reporte_fiscal_{rfc}_{mes}.xlsx"
    temp_dir = "/tmp"
    os.makedirs(temp_dir, exist_ok=True)
    filepath = os.path.join(temp_dir, report_filename)

    try:
        SatService.generar_reporte_excel(invoices, filepath, rfc, mes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte Excel: {str(e)}")

    if not os.path.exists(filepath):
        raise HTTPException(status_code=500, detail="No se pudo crear el archivo de reporte")

    return FileResponse(
        path=filepath,
        filename=report_filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
