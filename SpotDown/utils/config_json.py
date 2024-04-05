# 05.04.2024

import os
import sys
import json
import logging
from typing import Any, List


# External imports
import httpx


# Internal utils
from SpotDown.utils.headers import get_headers


class ConfigManager:
    def __init__(self, file_name: str = 'config.json') -> None:
        """
        Initialize the ConfigManager.
        
        Args:
            file_name (str, optional): Configuration file name. Default: 'config.json'.
        """
        # Determine the base path - use the current working directory
        if getattr(sys, 'frozen', False):
            # If the application is frozen (e.g., PyInstaller)
            base_path = os.path.dirname(sys.executable)

        else:
            # Use the current working directory where the script is executed
            base_path = os.getcwd()
            
        # Initialize file paths
        self.file_path = os.path.join(base_path, file_name)
        
        # Initialize data structures
        self.config = {}
        self.cache = {}

        # Load the configuration
        self.load_config()
        
    def download_config(self) -> None:
        """Download config.json from the Arrowar/SpotDown GitHub repository."""
        url = "https://raw.githubusercontent.com/Arrowar/SpotDown/refs/heads/main/config.json"
        try:
            with httpx.Client(timeout=10, headers=get_headers()) as client:
                response = client.get(url)
                response.raise_for_status()

                with open(self.file_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
            
            logging.info("Downloaded config.json from Arrowar/SpotDown repository.")
        
        except Exception as e:
            logging.error(f"Failed to download config.json: {e}")
            sys.exit(1)

    def load_config(self) -> None:
        """Load the configuration and initialize all settings."""
        if not os.path.exists(self.file_path):
            self.download_config()

        try:
            with open(self.file_path, 'r', encoding="utf-8") as f:
                self.config = json.load(f)

        except json.JSONDecodeError as e:
            logging.error(f"Error decoding config.json: {e}")
            sys.exit(1)

        except Exception as e:
            logging.error(f"Error loading config.json: {e}")
            sys.exit(1)
    
    def get(self, section: str, key: str, data_type: type = str) -> Any:
        """
        Read a value from the configuration.
        
        Args:
            section (str): Section in the configuration
            key (str): Key to read
            data_type (type, optional): Expected data type. Default: str
            
        Returns:
            Any: The key value converted to the specified data type
        """
        cache_key = f"config.{section}.{key}"
        logging.info(f"Reading key: {cache_key}")
        
        # Check if the value is in the cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        config_source = self.config
        
        # Check if the section and key exist
        if section not in config_source:
            raise ValueError(f"Section '{section}' not found in main configuration")
        
        if key not in config_source[section]:
            raise ValueError(f"Key '{key}' not found in section '{section}' of main configuration")
        
        # Get and convert the value
        value = config_source[section][key]
        converted_value = self._convert_to_data_type(value, data_type)
        
        # Save in cache
        self.cache[cache_key] = converted_value
        
        return converted_value
    
    def _convert_to_data_type(self, value: Any, data_type: type) -> Any:
        """
        Convert the value to the specified data type.
        
        Args:
            value (Any): Value to convert
            data_type (type): Target data type
            
        Returns:
            Any: Converted value
        """
        try:
            if data_type is int:
                return int(value)
            
            elif data_type is float:
                return float(value)
            
            elif data_type is bool:
                if isinstance(value, str):
                    return value.lower() in ("yes", "true", "t", "1")
                return bool(value)
            
            elif data_type is list:
                if isinstance(value, list):
                    return value
                if isinstance(value, str):
                    return [item.strip() for item in value.split(',')]
                return [value]

            elif data_type is dict:
                if isinstance(value, dict):
                    return value
                
                raise ValueError(f"Cannot convert {type(value).__name__} to dict")
            else:
                return value
            
        except Exception as e:
            logging.error(f"Error converting to {data_type.__name__}: {e}")
            raise ValueError(f"Cannot convert '{value}' to {data_type.__name__}: {str(e)}")
    
    def get_string(self, section: str, key: str) -> str:
        """Read a string from the main configuration."""
        return self.get(section, key, str)
    
    def get_int(self, section: str, key: str) -> int:
        """Read an integer from the main configuration."""
        return self.get(section, key, int)
    
    def get_float(self, section: str, key: str) -> float:
        """Read a float from the main configuration."""
        return self.get(section, key, float)
    
    def get_bool(self, section: str, key: str) -> bool:
        """Read a boolean from the main configuration."""
        return self.get(section, key, bool)
    
    def get_list(self, section: str, key: str) -> List[str]:
        """Read a list from the main configuration."""
        return self.get(section, key, list)
    
    def get_dict(self, section: str, key: str) -> dict:
        """Read a dictionary from the main configuration."""
        return self.get(section, key, dict)
    
    def set_key(self, section: str, key: str, value: Any) -> None:
        """
        Set a key in the configuration.
        
        Args:
            section (str): Section in the configuration
            key (str): Key to set
            value (Any): Value to associate with the key
        """
        try:
            config_target = self.config
            
            if section not in config_target:
                config_target[section] = {}
            
            config_target[section][key] = value
            
            # Update the cache
            cache_key = f"config.{section}.{key}"
            self.cache[cache_key] = value
            
            logging.info(f"Key '{key}' set in section '{section}' of main configuration")
        
        except Exception as e:
            error_msg = f"Error setting key '{key}' in section '{section}' of main configuration: {e}"
            logging.error(error_msg)
    
    def has_section(self, section: str) -> bool:
        """
        Check if a section exists in the configuration.
        
        Args:
            section (str): Section name
            
        Returns:
            bool: True if the section exists, False otherwise
        """
        config_source = self.config
        return section in config_source


config_manager = ConfigManager()
