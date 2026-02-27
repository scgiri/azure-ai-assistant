from __future__ import annotations

from tools.data_loader import load_json_data


def retrieve_crm_record(customer_id: str) -> dict:
    crm_records = load_json_data("crm_records.json")
    match = next(
        (
            record
            for record in crm_records
            if record.get("customer_id", "").lower() == customer_id.lower()
        ),
        None,
    )

    if match:
        return {
            **match,
            "system": "Azure-CRM-Mock",
        }

    return {
        "customer_id": customer_id,
        "name": "Contoso Holdings",
        "tier": "gold",
        "region": "APAC",
        "last_contact": "2026-02-10",
        "open_opportunities": 3,
        "account_manager": "Unassigned",
        "system": "Azure-CRM-Mock",
    }
