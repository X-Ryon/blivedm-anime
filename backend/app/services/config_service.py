import json
import os
from pathlib import Path
from backend.app.schemas.config import AppConfig
from backend.core.conf import settings

class ConfigService:
    def __init__(self):
        # 配置文件路径
        self.config_path = settings.BACKEND_DIR / "config.json"

    def get_config(self) -> AppConfig:
        """读取并解析配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return AppConfig(**data)

    def update_config(self, config: AppConfig) -> AppConfig:
        """更新配置文件"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
        return config

    def reset_config(self) -> AppConfig:
        """恢复默认配置"""
        # 模板文件路径：与 config.json 同级
        template_path = self.config_path.parent / "config_template.json"
        
        if not template_path.exists():
            raise FileNotFoundError(f"配置模板文件未找到: {template_path}")
        
        with open(template_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # 写入 config.json
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return AppConfig(**data)

config_service = ConfigService()
