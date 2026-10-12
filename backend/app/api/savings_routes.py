from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.savings_service import SavingsVerificationService

router = APIRouter(prefix="/api/savings", tags=["Savings Verification"])

@router.get("/baseline")
def get_savings_baseline():
    """
    Appendix E Contract (Estimated status):
    { "status": "estimated", "baselineKwh": 1200, "actualKwh": 1080, "savingKwh": 120, "costAvoided": 1950, "method": "comparable_period_baseline" }
    """
    summary = SavingsVerificationService.get_savings_summary(verified=False)
    return {
        "success": True,
        "data": summary,
        "meta": {
            "isSimulated": True,
            "disclaimer": "Savings are estimated from weather-normalized baseline model prior to completing required verification audit window."
        }
    }

@router.get("/verified")
def get_verified_savings():
    """
    Appendix E Contract (Verified status):
    { "status": "verified", "baselineKwh": 1245.0, "actualKwh": 1078.0, "savingKwh": 167.0, "costAvoided": 1636.6, "method": "comparable_period_baseline" }
    """
    summary = SavingsVerificationService.get_savings_summary(verified=True)
    return {
        "success": True,
        "data": summary,
        "meta": {
            "isSimulated": True,
            "verificationStandard": "ASHRAE Guideline 14 / IPMVP Option C compliant"
        }
    }

@router.get("/breakdown")
def get_device_savings_breakdown():
    breakdown = SavingsVerificationService.get_device_savings_breakdown()
    return {
        "success": True,
        "data": breakdown,
        "meta": {"isSimulated": True}
    }
