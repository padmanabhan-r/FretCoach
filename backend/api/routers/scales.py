"""
Scales endpoint for FretCoach API
"""

from fastapi import APIRouter
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from scales import MAJOR_DIATONIC, MINOR_DIATONIC

router = APIRouter()


@router.get("/scales")
async def get_scales():
    """Get list of available musical scales grouped by type"""
    return {
        "major": sorted(MAJOR_DIATONIC.keys()),
        "minor": sorted(MINOR_DIATONIC.keys())
    }
