import toml
from typing import List, Dict
from loguru import logger

from .models import Provider


class ProviderRepository:
    """Repository for loading provider configurations from TOML"""

    def __init__(self, config_file: str):
        """Initialize repository with config file path

        Args:
            config_file: Path to the TOML configuration file
        """
        self.config_file = config_file

    def load_providers(self) -> List[Provider]:
        """Load all provider configurations from TOML file

        Returns:
            List of Provider objects. Returns empty list if:
            - Config file doesn't exist
            - No providers section in config
            - All providers are invalid
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = toml.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_file}")
            return []
        except toml.TomlDecodeError as e:
            logger.error(f"Invalid TOML syntax in {self.config_file}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading config file {self.config_file}: {e}")
            return []

        # Get providers array from config
        providers_data = config.get('providers', [])

        if not providers_data:
            logger.debug("No providers section found in config")
            return []

        if not isinstance(providers_data, list):
            logger.error("providers section must be an array of tables")
            return []

        # Parse and validate each provider
        providers = []
        seen_names = {}

        for idx, provider_dict in enumerate(providers_data):
            try:
                # Validate required fields
                if not isinstance(provider_dict, dict):
                    logger.warning(f"Provider at index {idx} is not a table, skipping")
                    continue

                name = provider_dict.get('name')
                if not name:
                    logger.warning(f"Provider at index {idx} missing 'name' field, skipping")
                    continue

                if not provider_dict.get('base_url'):
                    logger.warning(f"Provider '{name}' missing 'base_url' field, skipping")
                    continue

                if not provider_dict.get('api_key'):
                    logger.warning(f"Provider '{name}' missing 'api_key' field, skipping")
                    continue

                # Check for duplicate names
                if name in seen_names:
                    logger.warning(f"Duplicate provider name '{name}', keeping last one")
                    # Remove previous provider with same name
                    providers = [p for p in providers if p.name != name]

                # Create Provider model
                provider = Provider(**provider_dict)
                providers.append(provider)
                seen_names[name] = True

            except Exception as e:
                logger.warning(f"Error loading provider at index {idx}: {e}, skipping")
                continue

        logger.info(f"Loaded {len(providers)} provider(s) from config")
        return providers
