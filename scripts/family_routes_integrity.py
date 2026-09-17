from __future__ import annotations

from fastapi import Depends, FastAPI

from backend.app.family_routes import register_family_auth, router as family_router
from backend.app.platform_models import FamilyMember


EXPECTED = {
    ("GET", "/v1/families/{family_id}"),
    ("POST", "/v1/families"),
    ("GET", "/v1/families/{family_id}/members"),
    ("POST", "/v1/families/{family_id}/members"),
    ("PATCH", "/v1/families/{family_id}/members/{member_user_id}"),
    ("DELETE", "/v1/families/{family_id}/members/{member_user_id}"),
    ("POST", "/v1/families/{family_id}/donate"),
    ("GET", "/v1/families/{family_id}/chat"),
    ("POST", "/v1/families/{family_id}/chat/messages"),
}


def main() -> None:
    # Registration is isolated from the production app so this gate cannot
    # accidentally change the runtime route table.
    register_family_auth(lambda: None)
    app = FastAPI()
    app.include_router(family_router)
    actual = {(route.methods and next(iter(route.methods)), route.path) for route in app.routes if getattr(route, "path", "").startswith("/v1/families")}
    missing = EXPECTED - actual
    if missing:
        raise SystemExit(f"Missing family routes: {sorted(missing)}")

    role_column = FamilyMember.__table__.c.role
    allowed = {"member", "admin"}
    check = getattr(role_column.type, "length", None)
    if check != 16:
        raise SystemExit(f"Unexpected family member role column length: {check}")

    print(f"FAMILY_ROUTES_INTEGRITY_PASS routes={len(actual)} role_length={check} allowed={sorted(allowed)}")


if __name__ == "__main__":
    main()
