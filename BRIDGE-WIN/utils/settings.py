"""
BRIDGE-WIN Settings Management
Persistent application settings using JSON storage
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
import os


@dataclass
class BridgeSettings:
    """Application settings data class"""
    
    # Window settings
    window_width: int = 800
    window_height: int = 600
    window_x: int = -1  # -1 means center on screen
    window_y: int = -1
    
    # Port configuration
    last_port1: str = "COM10"
    last_port2: str = "COM11"
    auto_start_bridge: bool = False
    
    # Sniffing settings
    sniffing_enabled: bool = False
    sniff_tcp_enabled: bool = False
    sniff_tcp_port: int = 8888
    sniff_file_enabled: bool = False
    sniff_file_path: str = ""
    sniff_pipe_enabled: bool = False
    sniff_pipe_name: str = "bridge_sniff"
    sniff_direction: str = "both"  # "both", "rx", "tx"
    sniff_format: str = "hex"  # "raw", "hex", "text"
    
    # Logging settings
    log_level: str = "INFO"
    log_to_file: bool = False
    log_file_path: str = ""
    
    # UI preferences
    theme: str = "default"
    show_tooltips: bool = True
    
    # com0com settings
    com0com_path: str = ""  # Auto-detect if empty
    
    # Version (for settings migration)
    settings_version: str = "1.0"


class SettingsManager:
    """Manage application settings with JSON persistence"""
    
    DEFAULT_SETTINGS_DIR = Path(os.getenv("APPDATA", ".")) / "BRIDGE-WIN"
    DEFAULT_SETTINGS_FILE = "settings.json"
    
    def __init__(self, settings_path: Optional[Path] = None):
        """
        Initialize settings manager
        
        Args:
            settings_path: Custom path to settings file (default: AppData/BRIDGE-WIN/settings.json)
        """
        if settings_path is None:
            self.settings_dir = self.DEFAULT_SETTINGS_DIR
            self.settings_path = self.settings_dir / self.DEFAULT_SETTINGS_FILE
        else:
            self.settings_path = Path(settings_path)
            self.settings_dir = self.settings_path.parent
        
        # Ensure settings directory exists
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Current settings
        self.settings = BridgeSettings()
        
        # Load existing settings
        self.load()
    
    def load(self) -> bool:
        """
        Load settings from file
        
        Returns:
            True if settings loaded successfully, False otherwise
        """
        if not self.settings_path.exists():
            # No settings file, use defaults
            return False
        
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Update settings from loaded data
            for key, value in data.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
            
            # Check for settings version migration
            if self.settings.settings_version != BridgeSettings.settings_version:
                self._migrate_settings(self.settings.settings_version)
            
            return True
            
        except Exception as e:
            print(f"Warning: Failed to load settings: {e}")
            return False
    
    def save(self) -> bool:
        """
        Save settings to file
        
        Returns:
            True if settings saved successfully, False otherwise
        """
        try:
            # Convert settings to dictionary
            data = asdict(self.settings)
            
            # Write to file with pretty formatting
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error: Failed to save settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value
        
        Args:
            key: Setting key
            default: Default value if key doesn't exist
        
        Returns:
            Setting value or default
        """
        return getattr(self.settings, key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a setting value
        
        Args:
            key: Setting key
            value: Setting value
        
        Returns:
            True if setting was updated, False if key doesn't exist
        """
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
            return True
        return False
    
    def reset(self) -> None:
        """Reset all settings to defaults"""
        self.settings = BridgeSettings()
    
    def _migrate_settings(self, old_version: str) -> None:
        """
        Migrate settings from old version to current version
        
        Args:
            old_version: Old settings version
        """
        # Placeholder for future settings migrations
        # Example:
        # if old_version == "0.9":
        #     # Migrate from 0.9 to 1.0
        #     pass
        
        # Update version
        self.settings.settings_version = BridgeSettings.settings_version
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all settings as dictionary
        
        Returns:
            Dictionary of all settings
        """
        return asdict(self.settings)
    
    def __repr__(self) -> str:
        return f"SettingsManager(path={self.settings_path})"


# Global settings instance (singleton pattern)
_global_settings: Optional[SettingsManager] = None


def get_settings() -> SettingsManager:
    """
    Get global settings instance (singleton)
    
    Returns:
        Global SettingsManager instance
    """
    global _global_settings
    if _global_settings is None:
        _global_settings = SettingsManager()
    return _global_settings


if __name__ == "__main__":
    # Test settings functionality
    print("Testing SettingsManager...")
    
    # Create test settings
    settings = SettingsManager(Path("test_settings.json"))
    
    # Modify some settings
    settings.set("window_width", 1024)
    settings.set("window_height", 768)
    settings.set("last_port1", "COM20")
    settings.set("sniffing_enabled", True)
    
    # Save settings
    if settings.save():
        print("✓ Settings saved successfully")
    
    # Create new instance and load
    settings2 = SettingsManager(Path("test_settings.json"))
    
    # Verify loaded values
    assert settings2.get("window_width") == 1024
    assert settings2.get("window_height") == 768
    assert settings2.get("last_port1") == "COM20"
    assert settings2.get("sniffing_enabled") == True
    
    print("✓ Settings loaded and verified")
    
    # Clean up test file
    Path("test_settings.json").unlink()
    print("✓ Test complete!")

