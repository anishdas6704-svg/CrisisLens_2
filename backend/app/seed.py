from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models import Crisis, CrisisUpdate, CrisisEntity, get_utc_now

def seed_database(db: Session):
    """
    Populates initial data for CrisisLens Command Center if empty.
    """
    if db.query(Crisis).count() > 0:
        return

    now = get_utc_now()

    # 1. Main Mission Crisis
    kolkata_crisis = Crisis(
        id="FLD-KOL-2026-0947",
        name="Kolkata Flood Response",
        description="Major urban and suburban flood response mission in North 24 Parganas and Kolkata metropolitan area.",
        status="active",
        location="Kolkata & North 24 Parganas",
        latitude=22.5726,
        longitude=88.3639,
        started_at=now - timedelta(days=2, hours=4),
        created_at=now - timedelta(days=2, hours=4)
    )

    # 2. Secondary Crises
    crises_list = [
        kolkata_crisis,
        Crisis(
            id="CYC-BOB-2026-0412",
            name="Cyclone Dana Alert — Bay of Bengal",
            description="Coastal surveillance and pre-emptive evacuation in coastal zones.",
            status="active",
            location="Coastal Odisha & WB",
            latitude=21.1458,
            longitude=86.8569,
            started_at=now - timedelta(days=1),
            created_at=now - timedelta(days=1)
        ),
        Crisis(
            id="LS-UTT-2026-0182",
            name="Uttarakhand Landslide Ops",
            description="Road clearing and stranded passenger evacuation along national highway.",
            status="active",
            location="Chamoli District",
            latitude=30.4227,
            longitude=79.3242,
            started_at=now - timedelta(days=3),
            created_at=now - timedelta(days=3)
        ),
        Crisis(
            id="DRT-RAJ-2026-0033",
            name="Rajasthan Drought Watch",
            description="Water tanker dispatch and groundwater monitoring.",
            status="monitoring",
            location="Barmer & Jaisalmer",
            latitude=25.7532,
            longitude=71.3967,
            started_at=now - timedelta(days=5),
            created_at=now - timedelta(days=5)
        ),
        Crisis(
            id="FLD-ASM-2026-0511",
            name="Brahmaputra Flood Relief",
            description="Assam flood relief and medical supply distribution.",
            status="resolved",
            location="Guwahati, Assam",
            latitude=26.1445,
            longitude=91.7362,
            started_at=now - timedelta(days=10),
            created_at=now - timedelta(days=10)
        )
    ]

    for c in crises_list:
        db.add(c)
    db.commit()

    # 3. Seed Entities for Kolkata Flood Response
    entities = [
        CrisisEntity(
            crisis_id=kolkata_crisis.id,
            name="North 24 Parganas Sector 4",
            entity_type="flood",
            status="high_risk",
            details="Water level 1.8m above normal threshold",
            latitude=22.7210,
            longitude=88.4830,
            updated_at=now - timedelta(minutes=10)
        ),
        CrisisEntity(
            crisis_id=kolkata_crisis.id,
            name="VIP Road / Airport Flyover",
            entity_type="infrastructure",
            status="closed",
            details="Waterlogging and debris blocking eastbound lanes",
            latitude=22.6250,
            longitude=88.4320,
            updated_at=now - timedelta(minutes=35)
        ),
        CrisisEntity(
            crisis_id=kolkata_crisis.id,
            name="Salt Lake Stadium Relief Camp",
            entity_type="shelter",
            status="operational",
            details="Capacity: 2,500 people, Medical camp active",
            latitude=22.5697,
            longitude=88.4069,
            updated_at=now - timedelta(minutes=22)
        ),
        CrisisEntity(
            crisis_id=kolkata_crisis.id,
            name="NDRF Team Alpha",
            entity_type="rescue",
            status="deployed",
            details="18 personnel + 4 power boats deployed for water rescue",
            latitude=22.5850,
            longitude=88.3900,
            updated_at=now - timedelta(minutes=15)
        ),
        CrisisEntity(
            crisis_id=kolkata_crisis.id,
            name="NH-12 Bridge Section",
            entity_type="infrastructure",
            status="damaged",
            details="Structural inspection underway",
            latitude=22.6500,
            longitude=88.3700,
            updated_at=now - timedelta(minutes=48)
        )
    ]
    for e in entities:
        db.add(e)

    # 4. Seed Live Updates for Kolkata Flood Response
    updates = [
        CrisisUpdate(
            crisis_id=kolkata_crisis.id,
            raw_text="Severe Flooding reported in North 24 Parganas. Water level rising rapidly in low-lying residential clusters.",
            source="sensor",
            change_detected=True,
            conflict_status="none",
            ai_extracted={"entity_type": "flood", "confidence": 0.96, "severity": "high", "action_recommended": "Issue immediate evacuation alert."},
            created_at=now - timedelta(minutes=2)
        ),
        CrisisUpdate(
            crisis_id=kolkata_crisis.id,
            raw_text="NH-12 bridge section submerged near Sector 7. Traffic disrupted and diverted to bypass.",
            source="agency",
            change_detected=True,
            conflict_status="none",
            ai_extracted={"entity_type": "infrastructure", "confidence": 0.92, "severity": "medium", "action_recommended": "Maintain road closure notices."},
            created_at=now - timedelta(minutes=8)
        ),
        CrisisUpdate(
            crisis_id=kolkata_crisis.id,
            raw_text="NDRF Rescue Team Alpha dispatched to Sector 7 with inflatable boats and emergency rations.",
            source="radio",
            change_detected=True,
            conflict_status="none",
            ai_extracted={"entity_type": "rescue", "confidence": 0.95, "severity": "info", "action_recommended": "Track GPS telemetry of rescue boats."},
            created_at=now - timedelta(minutes=15)
        ),
        CrisisUpdate(
            crisis_id=kolkata_crisis.id,
            raw_text="Relief Camp Established at Salt Lake Stadium. Food distribution and drinking water operational.",
            source="agency",
            change_detected=False,
            conflict_status="none",
            ai_extracted={"entity_type": "shelter", "confidence": 0.98, "severity": "info", "action_recommended": "Replenish medical supplies."},
            created_at=now - timedelta(minutes=22)
        ),
        CrisisUpdate(
            crisis_id=kolkata_crisis.id,
            raw_text="Partial power outage reported across Eastern Sector due to substation water infiltration.",
            source="sensor",
            change_detected=True,
            conflict_status="conflict",
            ai_extracted={"entity_type": "infrastructure", "confidence": 0.89, "severity": "low", "action_recommended": "Coordinate backup generators."},
            created_at=now - timedelta(minutes=35)
        ),
        CrisisUpdate(
            crisis_id=kolkata_crisis.id,
            raw_text="VIP Road eastbound corridor blocked near airport due to severe waterlogging.",
            source="social_media",
            change_detected=True,
            conflict_status="none",
            ai_extracted={"entity_type": "infrastructure", "confidence": 0.91, "severity": "medium", "action_recommended": "Broadcast detour routes."},
            created_at=now - timedelta(minutes=48)
        )
    ]
    for u in updates:
        db.add(u)

    db.commit()
