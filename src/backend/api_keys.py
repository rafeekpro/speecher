"""
API Keys management module for storing provider credentials in MongoDB.
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime
from pymongo import MongoClient
from cryptography.fernet import Fernet
import base64
import hashlib

class APIKeysManager:
    def __init__(self, mongodb_uri: str, db_name: str):
        self.mongodb_available = False
        try:
            self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
            # Test connection
            self.client.server_info()
            self.db = self.client[db_name]
            self.collection = self.db['api_keys']
            self.mongodb_available = True
            
            # Try to create unique index on provider, but don't fail if it doesn't work
            try:
                self.collection.create_index("provider", unique=True)
            except Exception as e:
                print(f"Warning: Could not create index on api_keys collection: {e}")
        except Exception as e:
            print(f"Warning: MongoDB not available, using environment variables fallback: {e}")
            self.client = None
            self.db = None
            self.collection = None
        
        # Generate or load encryption key
        self.cipher_suite = self._get_cipher()
    
    def _get_cipher(self) -> Fernet:
        """Get or create encryption cipher for API keys."""
        # Use a master key from environment or generate one
        master_key = os.getenv("ENCRYPTION_KEY")
        if not master_key:
            # In production, this should be stored securely
            master_key = "speecher-default-encryption-key-change-in-production"
        
        # Derive a proper key from the master key
        key = base64.urlsafe_b64encode(
            hashlib.sha256(master_key.encode()).digest()
        )
        return Fernet(key)
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a value."""
        if not value:
            return ""
        return self.cipher_suite.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a value."""
        if not encrypted_value:
            return ""
        try:
            return self.cipher_suite.decrypt(encrypted_value.encode()).decode()
        except:
            return ""
    
    def save_api_keys(self, provider: str, keys: Dict[str, Any]) -> bool:
        """Save or update API keys for a provider."""
        try:
            # Encrypt sensitive values
            encrypted_keys = {}
            for key, value in keys.items():
                if value and any(sensitive in key.lower() for sensitive in ['key', 'secret', 'token', 'password']):
                    encrypted_keys[key] = self.encrypt_value(str(value))
                else:
                    encrypted_keys[key] = value
            
            document = {
                "provider": provider,
                "keys": encrypted_keys,
                "updated_at": datetime.utcnow(),
                "enabled": True
            }
            
            # Upsert (update or insert)
            self.collection.replace_one(
                {"provider": provider},
                document,
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving API keys: {e}")
            return False
    
    def get_api_keys(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get decrypted API keys for a provider."""
        # If MongoDB is not available, use environment variables
        if not self.mongodb_available:
            result = self._get_env_keys(provider)
            if result:
                result["source"] = "environment"
            return result
            
        try:
            document = self.collection.find_one({"provider": provider})
            if not document:
                # Fallback to environment variables
                result = self._get_env_keys(provider)
                if result:
                    result["source"] = "environment"
                return result
            
            # Decrypt sensitive values
            decrypted_keys = {}
            for key, value in document.get("keys", {}).items():
                if value and any(sensitive in key.lower() for sensitive in ['key', 'secret', 'token', 'password']):
                    decrypted_keys[key] = self.decrypt_value(str(value))
                else:
                    decrypted_keys[key] = value
            
            # Check if provider is properly configured
            is_configured = self.validate_provider_config(document["provider"], decrypted_keys)
            
            return {
                "provider": document["provider"],
                "keys": decrypted_keys,
                "enabled": document.get("enabled", True),
                "configured": is_configured,
                "updated_at": document.get("updated_at"),
                "source": "mongodb"
            }
        except Exception as e:
            print(f"Error getting API keys from MongoDB, falling back to environment: {e}")
            result = self._get_env_keys(provider)
            if result:
                result["source"] = "environment"
            return result
    
    def _get_env_keys(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get API keys from environment variables."""
        import os
        
        if provider == "aws":
            access_key = os.getenv("AWS_ACCESS_KEY_ID")
            secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            if access_key and secret_key:
                keys = {
                    "access_key_id": access_key,
                    "secret_access_key": secret_key,
                    "region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                    "s3_bucket_name": os.getenv("S3_BUCKET_NAME", "speecher-rafal-app")
                }
                return {
                    "provider": "aws",
                    "keys": keys,
                    "enabled": True,
                    "configured": self.validate_provider_config("aws", keys),
                    "updated_at": None
                }
        elif provider == "azure":
            subscription_key = os.getenv("AZURE_SPEECH_KEY")
            if subscription_key:
                keys = {
                    "subscription_key": subscription_key,
                    "region": os.getenv("AZURE_SPEECH_REGION", "eastus")
                }
                return {
                    "provider": "azure",
                    "keys": keys,
                    "enabled": True,
                    "configured": self.validate_provider_config("azure", keys),
                    "updated_at": None
                }
        elif provider == "gcp":
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path and os.path.exists(credentials_path):
                with open(credentials_path, 'r') as f:
                    keys = {
                        "credentials_json": f.read(),
                        "project_id": os.getenv("GCP_PROJECT_ID"),
                        "gcs_bucket_name": os.getenv("GCP_BUCKET_NAME", "speecher-gcp")
                    }
                    return {
                        "provider": "gcp",
                        "keys": keys,
                        "enabled": True,
                        "configured": self.validate_provider_config("gcp", keys),
                        "updated_at": None
                    }
        
        return None
    
    def validate_provider_config(self, provider: str, keys: Dict[str, Any]) -> bool:
        """Validate that all required keys are present and not empty for a provider."""
        required_keys = {
            "aws": ["access_key_id", "secret_access_key", "region", "s3_bucket_name"],
            "azure": ["subscription_key", "region"],
            "gcp": ["credentials_json", "project_id", "gcs_bucket_name"]
        }
        
        if provider not in required_keys:
            return False
            
        for key in required_keys[provider]:
            if key not in keys or not keys[key] or str(keys[key]).strip() == "":
                return False
                
        return True
    
    def get_all_providers(self) -> list:
        """Get all configured providers with their status."""
        # If MongoDB is not available, check environment variables
        if not self.mongodb_available:
            providers = []
            for provider in ["aws", "azure", "gcp"]:
                env_keys = self._get_env_keys(provider)
                if env_keys:
                    is_properly_configured = self.validate_provider_config(provider, env_keys["keys"])
                    providers.append({
                        "provider": provider,
                        "enabled": is_properly_configured,
                        "configured": is_properly_configured,
                        "updated_at": None,
                        "source": "environment"
                    })
                else:
                    providers.append({
                        "provider": provider,
                        "enabled": False,
                        "configured": False,
                        "updated_at": None,
                        "source": None
                    })
            return providers
            
        try:
            providers = []
            for doc in self.collection.find({}, {"provider": 1, "keys": 1, "enabled": 1, "updated_at": 1}):
                # Decrypt keys to validate configuration
                decrypted_keys = {}
                for key, value in doc.get("keys", {}).items():
                    if value and any(sensitive in key.lower() for sensitive in ['key', 'secret', 'token', 'password']):
                        try:
                            decrypted_keys[key] = self.decrypt_value(value)
                        except:
                            decrypted_keys[key] = value
                    else:
                        decrypted_keys[key] = value
                
                # Check if provider is properly configured
                is_properly_configured = self.validate_provider_config(doc["provider"], decrypted_keys)
                
                providers.append({
                    "provider": doc["provider"],
                    "enabled": doc.get("enabled", True) and is_properly_configured,  # Only enabled if properly configured
                    "configured": is_properly_configured,
                    "updated_at": doc.get("updated_at"),
                    "source": "mongodb"
                })
            
            # Add unconfigured providers
            all_providers = ["aws", "azure", "gcp"]
            configured = [p["provider"] for p in providers]
            for provider in all_providers:
                if provider not in configured:
                    # Check environment variables for unconfigured providers
                    env_keys = self._get_env_keys(provider)
                    if env_keys:
                        is_properly_configured = self.validate_provider_config(provider, env_keys["keys"])
                        providers.append({
                            "provider": provider,
                            "enabled": is_properly_configured,
                            "configured": is_properly_configured,
                            "updated_at": None,
                            "source": "environment"
                        })
                    else:
                        providers.append({
                            "provider": provider,
                            "enabled": False,
                            "configured": False,
                            "updated_at": None,
                            "source": None
                        })
            
            return providers
        except Exception as e:
            print(f"Error getting providers from MongoDB, using environment fallback: {e}")
            # Fallback to environment-only mode
            providers = []
            for provider in ["aws", "azure", "gcp"]:
                env_keys = self._get_env_keys(provider)
                if env_keys:
                    is_properly_configured = self.validate_provider_config(provider, env_keys["keys"])
                    providers.append({
                        "provider": provider,
                        "enabled": is_properly_configured,
                        "configured": is_properly_configured,
                        "updated_at": None,
                        "source": "environment"
                    })
                else:
                    providers.append({
                        "provider": provider,
                        "enabled": False,
                        "configured": False,
                        "updated_at": None,
                        "source": None
                    })
            return providers
    
    def delete_api_keys(self, provider: str) -> bool:
        """Delete API keys for a provider."""
        try:
            result = self.collection.delete_one({"provider": provider})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting API keys: {e}")
            return False
    
    def toggle_provider(self, provider: str, enabled: bool) -> bool:
        """Enable or disable a provider."""
        try:
            result = self.collection.update_one(
                {"provider": provider},
                {"$set": {"enabled": enabled}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error toggling provider: {e}")
            return False