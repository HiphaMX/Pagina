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

    current_followers = snapshots[0].followers if snapshots else 0
    initial_followers = snapshots[-1].followers if snapshots else 0
    last_scanned = snapshots[0].recorded_at if snapshots else account.created_at

    growth_total = current_followers - initial_followers
    growth_pct = 0.0
    if initial_followers > 0:
        growth_pct = round((growth_total / initial_followers) * 100, 2)

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
    sparkline = [s.followers for s in chronological] if chronological else [current_followers]

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
        current_followers=current_followers,
        initial_followers=initial_followers,
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
        # Si la extracción falla de inicio, creamos la cuenta con 0 y el usuario puede ajustarla
        meta = {
            "platform": platform,
            "handle": handle,
            "name": payload.name or handle,
            "url": clean_url,
            "avatar_url": None,
            "followers": 0,
        }

    account_name = payload.name or meta.get("name") or handle

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
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    # Registrar snapshot inicial
    initial_snapshot = SocialSnapshot(
        account_id=new_account.id,
        followers=meta.get("followers", 0),
        growth_count=0,
        is_manual=False,
    )
    db.add(initial_snapshot)
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

    # Obtener el último conteo para calcular la diferencia neta
    last_snap = (
        db.query(SocialSnapshot)
        .filter(SocialSnapshot.account_id == account.id)
        .order_by(desc(SocialSnapshot.recorded_at))
        .first()
    )
    prev_followers = last_snap.followers if last_snap else new_followers
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


@router.post("/accounts/scan-all")
def scan_all_social_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    accounts = (
        db.query(SocialAccount)
        .filter(SocialAccount.status == "active")
        .all()
    )

    scanned_count = 0
    errors = []

    for acc in accounts:
        try:
            meta = fetch_social_metadata(acc.url, acc.platform)
            new_followers = meta.get("followers", 0)

            last_snap = (
                db.query(SocialSnapshot)
                .filter(SocialSnapshot.account_id == acc.id)
                .order_by(desc(SocialSnapshot.recorded_at))
                .first()
            )
            prev_followers = last_snap.followers if last_snap else new_followers
            growth_count = new_followers - prev_followers

            if meta.get("avatar_url"):
                acc.avatar_url = meta.get("avatar_url")

            snap = SocialSnapshot(
                account_id=acc.id,
                followers=new_followers,
                growth_count=growth_count,
                is_manual=False,
            )
            db.add(snap)
            scanned_count += 1
        except Exception as err:
            errors.append({"account": acc.name, "error": str(err)})

    db.commit()
    return {
        "success": True,
        "scanned_count": scanned_count,
        "total_active": len(accounts),
        "errors": errors,
    }


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

    last_snap = (
        db.query(SocialSnapshot)
        .filter(SocialSnapshot.account_id == account.id)
        .order_by(desc(SocialSnapshot.recorded_at))
        .first()
    )
    prev_followers = last_snap.followers if last_snap else payload.followers
    growth_count = payload.followers - prev_followers

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
