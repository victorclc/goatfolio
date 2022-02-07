from datetime import datetime
from typing import Protocol

from application.models.assets_quantities import AssetQuantities


class AssetRepository(Protocol):
    def save(self, asset: AssetQuantities):
        pass


def save_asset_quantities(subject: str, asset_quantities: dict, date: datetime.date, repository: AssetRepository):
    asset = AssetQuantities(subject=subject, asset_quantities=asset_quantities, date=date)
    repository.save(asset)
