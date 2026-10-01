import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.client import AgencyClient
from app.models.social_tracker import SocialAccount, SocialSnapshot
from app.models.user import User
from app.schemas.social_tracker import (
    SocialAccountCreate,
    SocialAccountResponse,
    SocialAccountUpdate,
    SocialObservatoryOverview,
    SocialSnapshotResponse,
    ManualSnapshotCreate,
)
from app.services.social_extractor import (
    detect_platform_and_handle,
    fetch_social_metadata,
)

router = APIRouter()


def _to_utc(dt: Optional[datetime.datetime]) -> Optional[datetime.datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def _build_account_response(account: SocialAccount, db: Session) -> SocialAccountResponse:
    snapshots = (
        db.query(SocialSnapshot)
        .filter(SocialSnapshot.account_id == account.id)
        .order_by(desc(SocialSnapshot.recorded_at))
        .all()
    )

    current_followers = snapshots[0].followers if snapshots else (account.initial_followers or 0)
    initial_followers = account.initial_followers if account.initial_followers is not None else (snapshots[-1].followers if snapshots else 0)
    last_scanned = snapshots[0].recorded_at if snapshots else account.created_at

    growth_total = current_followers - initial_followers
    growth_pct = 0.0
    if initial_followers > 0:
        growth_pct = round((growth_total / initial_followers) * 100, 2)
    elif initial_followers == 0 and current_followers > 0:
        growth_pct = 100.0  # Cuenta nueva arrancada en 0

    # Crecimiento mensual (comparado con el registro más cercano a hace 30 días)
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    thirty_days_ago = now_utc - datetime.timedelta(days=30)
    month_snapshots = [
        s for s in snapshots
        if s.recorded_at and _to_utc(s.recorded_at) <= thirty_days_ago
    ]
    base_month_followers = month_snapshots[0].followers if month_snapshots else initial_followers
    growth_monthly = current_followers - base_month_followers

    # Histórico de sparkline ordenado cronológicamente (máx 15 puntos)
    chronological = list(reversed(snapshots[:15]))
    sparkline = [s.followers for s in chronological] if chronological else [initial_followers, current_followers]
    if len(sparkline) == 1 and initial_followers != current_followers:
        sparkline = [initial_followers, current_followers]

    client_name = account.client.name if account.client else None

    return SocialAccountResponse(
        id=account.id,
        client_id=account.client_id,
        client_name=client_name,
        platform=account.platform,
        name=account.name,
        handle=account.handle,
        url=account.url,
        avatar_url=account.avatar_url,
        status=account.status,
        notes=account.notes,
        created_at=account.created_at,
        initial_followers=initial_followers,
        initial_date=account.initial_date,
        current_followers=current_followers,
        growth_total=growth_total,
        growth_monthly=growth_monthly,
        growth_percentage=growth_pct,
        last_scanned_at=last_scanned,
        sparkline_history=sparkline,
        snapshots=[SocialSnapshotResponse.model_validate(s) for s in snapshots[:20]],
    )




@router.get("/overview", response_model=SocialObservatoryOverview)
def get_social_observatory_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    accounts = (
        db.query(SocialAccount)
        .order_by(desc(SocialAccount.created_at))
        .all()
    )

    account_responses = [_build_account_response(acc, db) for acc in accounts]

    total_audience = sum(a.current_followers for a in account_responses)
    total_monthly_growth = sum(a.growth_monthly for a in account_responses)
    ig_count = sum(1 for a in account_responses if a.platform == "instagram")
    fb_count = sum(1 for a in account_responses if a.platform == "facebook")

    return SocialObservatoryOverview(
        total_accounts=len(account_responses),
        total_audience=total_audience,
        total_monthly_growth=total_monthly_growth,
        instagram_accounts=ig_count,
        facebook_accounts=fb_count,
        accounts=account_responses,
    )


@router.post("/accounts", response_model=SocialAccountResponse)
def create_social_account(
    payload: SocialAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Validar y detectar plataforma
    try:
        platform, handle, clean_url = detect_platform_and_handle(payload.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Verificar si la URL ya existe registrada
    existing = db.query(SocialAccount).filter(SocialAccount.url == clean_url).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Esta cuenta ya está registrada en el observatorio ({existing.name}).",
        )

    # Extraer metadatos iniciales en vivo
    try:
        meta = fetch_social_metadata(clean_url, platform)
    except Exception as err:
        # Si la extracción falla de inicio, creamos la cuenta con datos mínimos y seguidores provistos
        meta = {
            "platform": platform,
            "handle": handle,
            "name": payload.name or handle,
            "url": clean_url,
            "avatar_url": None,
            "followers": payload.initial_followers or 0,
        }

    account_name = payload.name or meta.get("name") or handle

    # Línea base inicial
    initial_base = payload.initial_followers if payload.initial_followers is not None else meta.get("followers", 0)
    init_date = payload.initial_date or datetime.datetime.now(datetime.timezone.utc)
    current_count = meta.get("followers", 0)
    if current_count == 0 and initial_base > 0:
        current_count = initial_base

    # Validar cliente asignado si se proporcionó
    if payload.client_id:
        client = db.query(AgencyClient).filter(AgencyClient.id == payload.client_id).first()
        if not client:
            payload.client_id = None

    new_account = SocialAccount(
        client_id=payload.client_id,
        platform=platform,
        name=account_name,
        handle=handle,
        url=clean_url,
        avatar_url=meta.get("avatar_url"),
        status="active",
        notes=payload.notes,
        initial_followers=initial_base,
        initial_date=init_date,
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    # 1. Registrar snapshot de línea base (con la fecha de arranque)
    base_snapshot = SocialSnapshot(
        account_id=new_account.id,
        followers=initial_base,
        growth_count=0,
        is_manual=True,
        recorded_at=init_date,
    )
    db.add(base_snapshot)

    # 2. Si el conteo actual detectado difiere de la base inicial, registrar el snapshot actual
    if current_count != initial_base:
        now_dt = datetime.datetime.now(datetime.timezone.utc)
        curr_snapshot = SocialSnapshot(
            account_id=new_account.id,
            followers=current_count,
            growth_count=current_count - initial_base,
            is_manual=False,
            recorded_at=now_dt,
        )
        db.add(curr_snapshot)

    db.commit()
    db.refresh(new_account)

    return _build_account_response(new_account, db)


@router.post("/accounts/{account_id}/scan", response_model=SocialAccountResponse)
def scan_social_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    account = db.query(SocialAccount).filter(SocialAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada.")

    try:
        meta = fetch_social_metadata(account.url, account.platform)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"No se pudo consultar la red social en este momento: {str(e)}",
        )

    new_followers = meta.get("followers", 0)

    # 1. Obtener todos los snapshots existentes para verificar el historial
    existing_snaps = (
        db.query(SocialSnapshot)
        .filter(SocialSnapshot.account_id == account.id)
        .order_by(desc(SocialSnapshot.recorded_at))
        .all()
    )

    # 2. Si la cuenta solo tenía mediciones en 0 (debido a fallas iniciales de extracción),
    # y ahora logramos extraer un conteo real positivo, normalizamos los ceros previos
    # para que este valor sea su base inicial genuina y no un falso salto.
    if new_followers > 0 and (not existing_snaps or all(s.followers == 0 for s in existing_snaps)):
        for s in existing_snaps:
            s.followers = new_followers
            s.growth_count = 0
        prev_followers = new_followers
        growth_count = 0
    else:
        last_snap = existing_snaps[0] if existing_snaps else None
        prev_followers = last_snap.followers if last_snap else new_followers
        # Evitar sobreescribir un conteo válido previo con 0 si la red social falla momentáneamente
        if new_followers == 0 and prev_followers > 0:
            new_followers = prev_followers
            growth_count = 0
        else:
            growth_count = new_followers - prev_followers

    # Actualizar avatar si se obtuvo uno más reciente
    if meta.get("avatar_url"):
        account.avatar_url = meta.get("avatar_url")
    if meta.get("name") and meta.get("name") != account.handle:
        account.name = meta.get("name")

    new_snapshot = SocialSnapshot(
        account_id=account.id,
        followers=new_followers,
        growth_count=growth_count,
        is_manual=False,
    )
    db.add(new_snapshot)
    db.commit()
    db.refresh(account)

    return _build_account_response(account, db)


def _do_scan_all(db: Session):
    accounts = (
        db.query(SocialAccount)
        .filter(SocialAccount.status == "active")
        .all()
    )

    scanned_count = 0
    errors = []
    results = []

    for acc in accounts:
        try:
            meta = fetch_social_metadata(acc.url, acc.platform)
            new_followers = meta.get("followers", 0)

            existing_snaps = (
                db.query(SocialSnapshot)
                .filter(SocialSnapshot.account_id == acc.id)
                .order_by(desc(SocialSnapshot.recorded_at))
                .all()
            )

            if new_followers > 0 and (not existing_snaps or all(s.followers == 0 for s in existing_snaps)):
                for s in existing_snaps:
                    s.followers = new_followers
                    s.growth_count = 0
                prev_followers = new_followers
                growth_count = 0
            else:
                last_snap = existing_snaps[0] if existing_snaps else None
                prev_followers = last_snap.followers if last_snap else new_followers
                if new_followers == 0 and prev_followers > 0:
                    new_followers = prev_followers
                    growth_count = 0
                else:
                    growth_count = new_followers - prev_followers

            if meta.get("avatar_url"):
                acc.avatar_url = meta.get("avatar_url")
            if meta.get("name") and meta.get("name") != acc.handle:
                acc.name = meta.get("name")

            snap = SocialSnapshot(
                account_id=acc.id,
                followers=new_followers,
                growth_count=growth_count,
                is_manual=False,
            )
            db.add(snap)
            scanned_count += 1
            results.append({"name": acc.name, "handle": acc.handle, "followers": new_followers})
        except Exception as err:
            errors.append({"account": acc.name, "error": str(err)})

    db.commit()
    return {
        "success": True,
        "scanned_count": scanned_count,
        "total_active": len(accounts),
        "results": results,
        "errors": errors,
    }


@router.post("/accounts/scan-all")
def scan_all_social_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return _do_scan_all(db)


@router.post("/accounts/{account_id}/manual-snapshot", response_model=SocialAccountResponse)
def add_manual_snapshot(
    account_id: int,
    payload: ManualSnapshotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    account = db.query(SocialAccount).filter(SocialAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada.")

    existing_snaps = (
        db.query(SocialSnapshot)
        .filter(SocialSnapshot.account_id == account.id)
        .order_by(desc(SocialSnapshot.recorded_at))
        .all()
    )

    # Si la cuenta solo tenía mediciones en 0, normalizar para que este conteo manual sea la base inicial
    if payload.followers > 0 and (not existing_snaps or all(s.followers == 0 for s in existing_snaps)):
        for s in existing_snaps:
            s.followers = payload.followers
            s.growth_count = 0
        prev_followers = payload.followers
        growth_count = 0
    else:
        last_snap = existing_snaps[0] if existing_snaps else None
        prev_followers = last_snap.followers if last_snap else payload.followers
        growth_count = payload.followers - prev_followers

    # Si se proporcionaron seguidores o fecha inicial, actualizar los campos de la cuenta
    if payload.initial_followers is not None:
        account.initial_followers = payload.initial_followers
    if payload.initial_date is not None:
        account.initial_date = payload.initial_date

    snap = SocialSnapshot(
        account_id=account.id,
        followers=payload.followers,
        growth_count=growth_count,
        is_manual=True,
        recorded_at=payload.recorded_at or datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(snap)
    db.commit()
    db.refresh(account)

    return _build_account_response(account, db)


@router.put("/accounts/{account_id}", response_model=SocialAccountResponse)
def update_social_account(
    account_id: int,
    payload: SocialAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    account = db.query(SocialAccount).filter(SocialAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada.")

    if payload.name is not None:
        account.name = payload.name.strip()
    if payload.client_id is not None:
        account.client_id = payload.client_id if payload.client_id > 0 else None
    if payload.status is not None:
        account.status = payload.status
    if payload.notes is not None:
        account.notes = payload.notes
    if payload.initial_followers is not None:
        account.initial_followers = payload.initial_followers
    if payload.initial_date is not None:
        account.initial_date = payload.initial_date

    # Sincronizar snapshot base más antiguo si se actualiza la línea base
    if payload.initial_followers is not None or payload.initial_date is not None:
        oldest_snap = (
            db.query(SocialSnapshot)
            .filter(SocialSnapshot.account_id == account.id)
            .order_by(asc(SocialSnapshot.recorded_at))
            .first()
        )
        if oldest_snap:
            if payload.initial_followers is not None:
                oldest_snap.followers = payload.initial_followers
            if payload.initial_date is not None:
                oldest_snap.recorded_at = payload.initial_date
        else:
            base_snap = SocialSnapshot(
                account_id=account.id,
                followers=account.initial_followers or 0,
                growth_count=0,
                is_manual=True,
                recorded_at=account.initial_date or datetime.datetime.now(datetime.timezone.utc),
            )
            db.add(base_snap)

    db.commit()
    db.refresh(account)
    return _build_account_response(account, db)


@router.delete("/accounts/{account_id}")
def delete_social_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    account = db.query(SocialAccount).filter(SocialAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada.")

    db.delete(account)
    db.commit()
    return {"ok": True, "message": "Cuenta de red social eliminada con éxito."}
