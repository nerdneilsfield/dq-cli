from typing import List, Optional, Tuple

from .models import Provider
from .repository import ProviderRepository


class ProviderService:
    """Service layer for managing provider configurations"""

    def __init__(self, repository: ProviderRepository):
        """Initialize service with repository

        Args:
            repository: ProviderRepository instance for loading providers
        """
        self.repository = repository
        self._providers: Optional[List[Provider]] = None

    def _ensure_loaded(self):
        """Lazy load providers if not already loaded"""
        if self._providers is None:
            self._providers = self.repository.load_providers()

    def get_all_providers(self) -> List[Provider]:
        """Get all configured providers

        Returns:
            List of all Provider objects
        """
        self._ensure_loaded()
        return self._providers or []

    def get_provider(self, name: str) -> Optional[Provider]:
        """Find a provider by name

        Args:
            name: Provider name to search for

        Returns:
            Provider object if found, None otherwise
        """
        self._ensure_loaded()
        for provider in self._providers or []:
            if provider.name == name:
                return provider
        return None

    def get_model_from_provider(self, provider_name: str, model_name: str) -> Optional[Tuple[Provider, str]]:
        """Get provider and model pair

        Args:
            provider_name: Name of the provider
            model_name: Name of the model

        Returns:
            Tuple of (Provider, model_name) if provider exists, None otherwise
            Note: Does not validate if model exists in provider's models list
        """
        provider = self.get_provider(provider_name)
        if provider:
            return (provider, model_name)
        return None

    def list_all_models(self) -> List[Tuple[str, str]]:
        """Get all available provider/model pairs

        Returns:
            List of tuples: (provider_name, model_name)
            Returns empty list if no providers or no models defined
        """
        self._ensure_loaded()
        result = []

        for provider in self._providers or []:
            if provider.models:
                for model in provider.models:
                    result.append((provider.name, model))

        return result

    def reload(self):
        """Reload providers from configuration file"""
        self._providers = self.repository.load_providers()
