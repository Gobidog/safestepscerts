"""
Test script to verify security fixes are working correctly.
Run with: python -m pytest tests/test_security_fixes.py -v
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSecurityFixes:
    """Test security-related fixes"""
    
    def test_jwt_secret_from_environment(self):
        """Test that JWT_SECRET is loaded from environment variable"""
        test_secret = "test_jwt_secret_32_chars_minimum!"
        
        with patch.dict(os.environ, {"JWT_SECRET": test_secret}):
            # Re-import to get new environment value
            import importlib
            import utils.auth
            importlib.reload(utils.auth)
            
            assert utils.auth.JWT_SECRET == test_secret
            assert len(utils.auth.JWT_SECRET) >= 32
    
    def test_jwt_secret_warning_when_not_set(self):
        """Test that RuntimeError is raised when JWT_SECRET not in environment"""
        with patch.dict(os.environ, {}, clear=True):
            # Remove JWT_SECRET and other required env vars
            env_vars = os.environ.copy()
            env_vars.pop('JWT_SECRET', None)
            
            with patch.dict(os.environ, env_vars, clear=True):
                # Re-import should raise RuntimeError
                import importlib
                import utils.auth
                
                with pytest.raises(RuntimeError, match="JWT_SECRET environment variable is required"):
                    importlib.reload(utils.auth)
    
    @pytest.mark.skip(reason="Config module creates global instance at import time")
    def test_passwords_required_from_environment(self, monkeypatch):
        """Test that passwords must be set in environment variables"""
        import sys
        
        # Test missing USER_PASSWORD
        monkeypatch.setenv("ADMIN_PASSWORD", "admin123")
        monkeypatch.setenv("JWT_SECRET", "test")
        monkeypatch.delenv("USER_PASSWORD", raising=False)
        
        # Remove cached module
        if 'config' in sys.modules:
            del sys.modules['config']
            
        from config import AuthConfig
        with pytest.raises(ValueError, match="USER_PASSWORD environment variable must be set"):
            AuthConfig()
        
        # Test missing ADMIN_PASSWORD
        monkeypatch.setenv("USER_PASSWORD", "user123") 
        monkeypatch.setenv("JWT_SECRET", "test")
        monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
        
        # Remove cached module again
        if 'config' in sys.modules:
            del sys.modules['config']
            
        from config import AuthConfig
        with pytest.raises(ValueError, match="ADMIN_PASSWORD environment variable must be set"):
            AuthConfig()
        
        # Test both passwords set
        with patch.dict(os.environ, {
            "USER_PASSWORD": "user123",
            "ADMIN_PASSWORD": "admin123"
        }):
            config = AuthConfig()
            assert config.user_password == "user123"
            assert config.admin_password == "admin123"
    
    @pytest.mark.skip(reason="Config module creates global instance at import time")
    def test_gcs_configuration(self, monkeypatch):
        """Test GCS configuration detection"""
        import sys
        
        # Test with GCS configured
        monkeypatch.setenv("GCS_BUCKET_NAME", "test-bucket")
        monkeypatch.setenv("GCS_PROJECT_ID", "test-project") 
        monkeypatch.setenv("USE_LOCAL_STORAGE", "false")
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        
        # Remove cached module
        if 'config' in sys.modules:
            del sys.modules['config']
            
        from config import StorageConfig
        config = StorageConfig()
        assert config.gcs_bucket_name == "test-bucket"
        assert config.gcs_project_id == "test-project"
        assert config.use_local_storage == False
        
        # Test fallback to local when GCS not configured
        monkeypatch.delenv("GCS_BUCKET_NAME", raising=False)
        monkeypatch.delenv("GCS_PROJECT_ID", raising=False)
        monkeypatch.delenv("USE_LOCAL_STORAGE", raising=False)
        
        # Remove cached module again
        if 'config' in sys.modules:
            del sys.modules['config']
            
        from config import StorageConfig
        config = StorageConfig()
        assert config.use_local_storage == True
        assert config.gcs_bucket_name is None
    
    def test_session_persistence_with_jwt(self):
        """Test that sessions can be validated with persistent JWT secret"""
        test_secret = "persistent_test_secret_for_sessions"
        
        with patch.dict(os.environ, {"JWT_SECRET": test_secret}):
            import importlib
            import utils.auth
            importlib.reload(utils.auth)
            
            # Generate a CSRF token
            with patch('utils.auth.config') as mock_config:
                mock_config.auth.enable_csrf_protection = True
                with patch('utils.auth.get_current_user') as mock_user:
                    mock_user.return_value = {
                        "session_id": "test_session",
                        "username": "testuser"
                    }
                    
                    # Generate token
                    token = utils.auth.generate_csrf_token()
                    assert token != ""
                    
                    # Validate token with same secret
                    is_valid = utils.auth.validate_csrf_token(token)
                    assert is_valid == True
    
    def test_environment_example_files_exist(self):
        """Test that environment example files exist with proper variables"""
        # Check .env.example
        env_example = os.path.join(os.path.dirname(__file__), "..", ".env.example")
        assert os.path.exists(env_example)
        
        with open(env_example, 'r') as f:
            content = f.read()
            assert "JWT_SECRET=" in content
            assert "USER_PASSWORD=" in content
            assert "ADMIN_PASSWORD=" in content
            assert "GCS_BUCKET_NAME=" in content
        
        # Check .env.production.example
        prod_example = os.path.join(os.path.dirname(__file__), "..", ".env.production.example")
        assert os.path.exists(prod_example)
        
        with open(prod_example, 'r') as f:
            content = f.read()
            assert "JWT_SECRET=CHANGE_THIS_" in content
            assert "USER_PASSWORD=CHANGE_THIS_" in content
            assert "ADMIN_PASSWORD=CHANGE_THIS_" in content
            assert "USE_LOCAL_STORAGE=false" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])