import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Service as ServiceSchema, BlogPost as BlogPostSchema, ContactMessage as ContactMessageSchema

app = FastAPI(title="CS Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactResponse(BaseModel):
    status: str
    message: str


def _seed_services_if_empty():
    try:
        existing = get_documents("service", {}, limit=1)
        if existing:
            return
    except Exception:
        # If database not available, just skip seeding
        return

    defaults: List[ServiceSchema] = [
        ServiceSchema(title="Company Incorporation (Pvt Ltd/LLP)", summary="End-to-end incorporation with DIN, DSC, name approval, MOA/AOA, PAN & TAN.", icon="building2", starting_price=8999, tags=["startup", "roc", "mca"]),
        ServiceSchema(title="Annual ROC Filings", summary="AOC-4, MGT-7, board reports, AGM documentation and compliance calendar.", icon="file-text", starting_price=4999, tags=["roc", "compliance"]),
        ServiceSchema(title="Director KYC (DIR-3 KYC)", summary="KYC for directors with DSC assistance and filing.", icon="id-card", starting_price=999, tags=["dir-3", "kyc"]),
        ServiceSchema(title="GST Registration & Returns", summary="GSTIN registration, monthly/quarterly returns and advisory.", icon="receipt", starting_price=1499, tags=["gst", "tax"]),
        ServiceSchema(title="Share Allotment & Transfer", summary="PAS-3, SH-7, share certificates issue/transfer and register maintenance.", icon="layers", starting_price=3499, tags=["secretarial", "shares"]),
        ServiceSchema(title="Secretarial Audit & Compliance", summary="Event-based filings, board/GM minutes, registers and due diligence.", icon="shield-check", starting_price=6999, tags=["audit", "secretarial"]),
        ServiceSchema(title="MSME/Udyam Registration", summary="Register your enterprise under Udyam for government benefits.", icon="badge-check", starting_price=799, tags=["msme", "udyam"]),
        ServiceSchema(title="Trademark Filing (Partner Network)", summary="Facilitated TM search and filing through trusted IP partners.", icon="copyright", starting_price=2999, tags=["ip", "brand"]),
        ServiceSchema(title="ESOP/Cap Table Advisory", summary="Design ESOP policies, grants and basic cap table setup.", icon="pie-chart", starting_price=5999, tags=["esop", "advisory"]),
        ServiceSchema(title="FEMA/FDI Compliance", summary="FC-GPR/FC-TRS filings, share pricing and RBI compliance.", icon="globe", starting_price=9999, tags=["fema", "fdi"]),
    ]
    for svc in defaults:
        try:
            create_document("service", svc)
        except Exception:
            pass


def _seed_blogs_if_empty():
    try:
        existing = get_documents("blogpost", {}, limit=1)
        if existing:
            return
    except Exception:
        return

    defaults: List[BlogPostSchema] = [
        BlogPostSchema(
            title="ROC Annual Filing Checklist for Private Companies (FY 2024-25)",
            slug="roc-annual-filing-checklist-2024-25",
            excerpt="A concise checklist to complete AOC-4, MGT-7 and key board approvals on time.",
            content="Step-by-step guide covering financial statements, board report, auditor report, AOC-4, MGT-7/7A, due dates and penalties.",
            tags=["roc", "checklist", "private-company"],
        ),
        BlogPostSchema(
            title="DIR-3 KYC: Due Dates, Forms and Penalties",
            slug="dir-3-kyc-due-dates-forms",
            excerpt="Everything about Director KYC and how to avoid deactivation.",
            content="Who needs to file DIR-3 KYC, documents required, e-Form vs Web KYC, timelines and fees.",
            tags=["dir-3", "kyc"],
        ),
        BlogPostSchema(
            title="Incorporation: Pvt Ltd vs LLP in India",
            slug="incorporation-pvtltd-vs-llp",
            excerpt="Structure, compliance and taxation comparison to choose the right entity.",
            content="We cover partner liability, compliance burden, funding readiness and exit scenarios.",
            tags=["incorporation", "llp", "pvtltd"],
        ),
    ]
    for post in defaults:
        try:
            create_document("blogpost", post)
        except Exception:
            pass


@app.on_event("startup")
async def startup_event():
    _seed_services_if_empty()
    _seed_blogs_if_empty()


@app.get("/")
def read_root():
    return {"message": "CS Portfolio API is running"}


@app.get("/api/services")
def list_services():
    try:
        services = get_documents("service")
        # Convert ObjectId to string
        for s in services:
            if s.get("_id"):
                s["id"] = str(s.pop("_id"))
        return {"data": services}
    except Exception as e:
        # Fallback static data if DB unavailable
        fallback = [
            {"title": "Company Incorporation", "summary": "End-to-end incorporation with MCA.", "icon": "building2", "starting_price": 8999, "tags": ["startup"]},
            {"title": "Annual ROC Filings", "summary": "AOC-4, MGT-7 & more.", "icon": "file-text", "starting_price": 4999, "tags": ["compliance"]},
        ]
        return {"data": fallback, "warning": str(e)[:120]}


@app.get("/api/blogs")
def list_blogs():
    try:
        posts = get_documents("blogpost")
        for p in posts:
            if p.get("_id"):
                p["id"] = str(p.pop("_id"))
        return {"data": posts}
    except Exception as e:
        fallback = [
            {"title": "ROC Annual Filing Checklist for Private Companies (FY 2024-25)", "slug": "roc-annual-filing-checklist-2024-25", "excerpt": "A concise checklist to complete AOC-4, MGT-7 and key approvals.", "tags": ["roc", "checklist"]},
            {"title": "DIR-3 KYC: Due Dates, Forms and Penalties", "slug": "dir-3-kyc-due-dates-forms", "excerpt": "Everything about Director KYC and how to avoid deactivation.", "tags": ["dir-3", "kyc"]},
        ]
        return {"data": fallback, "warning": str(e)[:120]}


@app.post("/api/contact", response_model=ContactResponse)
def submit_contact(message: ContactMessageSchema):
    try:
        create_document("contactmessage", message)
        return ContactResponse(status="ok", message="Thank you! We'll reach out shortly.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to submit right now: {str(e)[:100]}")


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
