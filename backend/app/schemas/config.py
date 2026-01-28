from typing import List, Optional
from pydantic import BaseModel, Field

class SystemConfig(BaseModel):
    auto_login: bool = False
    last_sessdata: str = ""
    auto_connect: bool = False
    last_room_id: str = ""

class DisplayConfig(BaseModel):
    history_range: int = 7

class GiftAnimation(BaseModel):
    gift_id: int
    gift_name: str
    animation_path: str

class GuardSkins(BaseModel):
    common: str = ""
    captain: str = ""
    admiral: str = ""
    governor: str = ""

class ResourcesConfig(BaseModel):
    gift_animations: List[GiftAnimation] = Field(default_factory=list)
    guard_skins: GuardSkins = Field(default_factory=GuardSkins)

class AppConfig(BaseModel):
    system: SystemConfig = Field(default_factory=SystemConfig)
    display: DisplayConfig = Field(default_factory=DisplayConfig)
    resources: ResourcesConfig = Field(default_factory=ResourcesConfig)
