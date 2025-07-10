"""
Unit tests for storage module
"""
import pytest
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock
from io import BytesIO

from utils.storage import StorageManager


class TestStorageManager:
    """Test storage manager functionality"""
    
    @pytest.fixture
    def temp_storage_path(self):
        """Create temporary storage directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def local_storage_manager(self, temp_storage_path):
        """Create storage manager configured for local storage"""
        with patch('utils.storage.config') as mock_config:
            mock_config.storage.use_local_storage = True
            mock_config.storage.local_storage_path = temp_storage_path
            mock_config.storage.gcs_bucket_name = None
            
            # Create a new StorageManager instance
            manager = StorageManager()
            manager.use_local = True
            manager.local_path = temp_storage_path
            
            yield manager
    
    @pytest.fixture
    def gcs_storage_manager(self):
        """Create storage manager configured for GCS"""
        with patch('utils.storage.config') as mock_config:
            mock_config.storage.use_local_storage = False
            mock_config.storage.gcs_bucket_name = "test-bucket"
            mock_config.storage.gcs_project_id = "test-project"
            
            with patch('utils.storage.gcs') as mock_gcs:
                with patch('utils.storage.GCS_AVAILABLE', True):
                    mock_client = MagicMock()
                    mock_bucket = MagicMock()
                    mock_gcs.Client.return_value = mock_client
                    mock_client.bucket.return_value = mock_bucket
                    
                    manager = StorageManager()
                    manager.use_local = False
                    manager.bucket = mock_bucket
                    
                    yield manager
    
    @pytest.fixture
    def sample_pdf_content(self):
        """Generate sample PDF content"""
        return b"%PDF-1.4\n%Test PDF content\n%%EOF"
    
    def test_init_local_storage(self, temp_storage_path):
        """Test initialization with local storage"""
        with patch('utils.storage.config') as mock_config:
            mock_config.storage.use_local_storage = True
            mock_config.storage.local_storage_path = temp_storage_path
            
            manager = StorageManager()
            
            assert manager.use_local is True
            assert manager.local_path == temp_storage_path
            
            # Check directories were created
            assert (temp_storage_path / "templates").exists()
            assert (temp_storage_path / "generated").exists()
            assert (temp_storage_path / "metadata").exists()
    
    def test_init_gcs_storage_success(self):
        """Test initialization with GCS storage"""
        with patch('utils.storage.config') as mock_config:
            mock_config.storage.use_local_storage = False
            mock_config.storage.gcs_bucket_name = "test-bucket"
            mock_config.storage.gcs_project_id = "test-project"
            
            with patch('utils.storage.gcs') as mock_gcs:
                with patch('utils.storage.GCS_AVAILABLE', True):
                    mock_client = MagicMock()
                    mock_bucket = MagicMock()
                    mock_gcs.Client.return_value = mock_client
                    mock_client.bucket.return_value = mock_bucket
                    
                    manager = StorageManager()
                    
                    assert manager.use_local is False
                    assert manager.bucket == mock_bucket
    
    def test_init_gcs_fallback_to_local(self):
        """Test fallback to local storage when GCS fails"""
        with patch('utils.storage.config') as mock_config:
            mock_config.storage.use_local_storage = False
            mock_config.storage.gcs_bucket_name = "test-bucket"
            mock_config.storage.local_storage_path = Path("/tmp/test")
            
            with patch('utils.storage.gcs') as mock_gcs:
                with patch('utils.storage.GCS_AVAILABLE', True):
                    # Simulate GCS connection failure
                    mock_gcs.Client.side_effect = Exception("GCS connection failed")
                    
                    manager = StorageManager()
                    
                    assert manager.use_local is True
    
    def test_save_template_local(self, local_storage_manager, sample_pdf_content):
        """Test saving template to local storage"""
        result = local_storage_manager.save_template(
            sample_pdf_content,
            "test_template.pdf"
        )
        
        assert result is True
        
        # Check file was saved
        template_path = local_storage_manager.local_path / "templates" / "test_template.pdf"
        assert template_path.exists()
        assert template_path.read_bytes() == sample_pdf_content
        
        # Check metadata was saved
        metadata_path = local_storage_manager.local_path / "metadata" / "test_template.pdf.json"
        assert metadata_path.exists()
        
        metadata = json.loads(metadata_path.read_text())
        assert metadata["name"] == "test_template.pdf"
        assert metadata["size"] == len(sample_pdf_content)
        assert "uploaded_at" in metadata
    
    def test_save_template_gcs(self, gcs_storage_manager, sample_pdf_content):
        """Test saving template to GCS"""
        mock_blob = MagicMock()
        gcs_storage_manager.bucket.blob.return_value = mock_blob
        
        result = gcs_storage_manager.save_template(
            sample_pdf_content,
            "test_template.pdf"
        )
        
        assert result is True
        
        # Verify GCS operations
        gcs_storage_manager.bucket.blob.assert_called_with("templates/test_template.pdf")
        mock_blob.upload_from_string.assert_called_with(
            sample_pdf_content,
            content_type='application/pdf'
        )
        mock_blob.patch.assert_called_once()
    
    def test_save_template_with_metadata(self, local_storage_manager, sample_pdf_content):
        """Test saving template with custom metadata"""
        custom_metadata = {
            "course": "Python 101",
            "version": "1.0"
        }
        
        result = local_storage_manager.save_template(
            sample_pdf_content,
            "test_template.pdf",
            metadata=custom_metadata
        )
        
        assert result is True
        
        # Check metadata includes custom fields
        metadata_path = local_storage_manager.local_path / "metadata" / "test_template.pdf.json"
        metadata = json.loads(metadata_path.read_text())
        
        assert metadata["course"] == "Python 101"
        assert metadata["version"] == "1.0"
        assert metadata["name"] == "test_template.pdf"
    
    def test_save_template_bytesio(self, local_storage_manager, sample_pdf_content):
        """Test saving template from BytesIO object"""
        file_buffer = BytesIO(sample_pdf_content)
        
        result = local_storage_manager.save_template(
            file_buffer,
            "test_template.pdf"
        )
        
        assert result is True
        
        # Verify content was saved correctly
        template_path = local_storage_manager.local_path / "templates" / "test_template.pdf"
        assert template_path.read_bytes() == sample_pdf_content
    
    def test_save_template_clean_filename(self, local_storage_manager, sample_pdf_content):
        """Test filename cleaning during save"""
        result = local_storage_manager.save_template(
            sample_pdf_content,
            "Test Template (2024).pdf"
        )
        
        assert result is True
        
        # Check cleaned filename
        expected_path = local_storage_manager.local_path / "templates" / "Test_Template_2024_.pdf"
        assert expected_path.exists()
    
    def test_list_templates_local(self, local_storage_manager, sample_pdf_content):
        """Test listing templates from local storage"""
        # Save a few templates
        local_storage_manager.save_template(sample_pdf_content, "template1.pdf")
        local_storage_manager.save_template(sample_pdf_content, "template2.pdf")
        local_storage_manager.save_template(sample_pdf_content, "template3.pdf")
        
        # List templates
        templates = local_storage_manager.list_templates()
        
        assert len(templates) == 3
        assert all(t["filename"].endswith(".pdf") for t in templates)
        assert all("created" in t for t in templates)
        assert all("size" in t for t in templates)
        
        # Check sorting (newest first)
        created_times = [t["created"] for t in templates]
        assert created_times == sorted(created_times, reverse=True)
    
    def test_list_templates_gcs(self, gcs_storage_manager):
        """Test listing templates from GCS"""
        # Mock GCS blobs
        mock_blobs = []
        for i in range(3):
            mock_blob = MagicMock()
            mock_blob.name = f"templates/template{i}.pdf"
            mock_blob.time_created = datetime.now() - timedelta(days=i)
            mock_blob.size = 1000 + i * 100
            mock_blob.metadata = {"course": f"Course {i}"}
            mock_blobs.append(mock_blob)
        
        gcs_storage_manager.bucket.list_blobs.return_value = mock_blobs
        
        templates = gcs_storage_manager.list_templates()
        
        assert len(templates) == 3
        assert all("course" in t for t in templates)
        assert templates[0]["name"] == "template0"  # Newest first
    
    def test_get_template_local(self, local_storage_manager, sample_pdf_content):
        """Test getting template content from local storage"""
        # Save template
        local_storage_manager.save_template(sample_pdf_content, "test.pdf")
        
        # Get template
        content = local_storage_manager.get_template("test.pdf")
        
        assert content == sample_pdf_content
    
    def test_get_template_not_found(self, local_storage_manager):
        """Test getting non-existent template"""
        content = local_storage_manager.get_template("nonexistent.pdf")
        assert content is None
    
    def test_get_template_path_local(self, local_storage_manager, sample_pdf_content):
        """Test getting template path for local storage"""
        # Save template
        local_storage_manager.save_template(sample_pdf_content, "test.pdf")
        
        # Get path
        path = local_storage_manager.get_template_path("test.pdf")
        
        assert path is not None
        assert os.path.exists(path)
        assert path.endswith("test.pdf")
    
    def test_get_template_path_gcs(self, gcs_storage_manager, sample_pdf_content):
        """Test getting template path for GCS (downloads to temp)"""
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        gcs_storage_manager.bucket.blob.return_value = mock_blob
        
        with patch('utils.storage.config') as mock_config:
            mock_config.temp_file.temp_dir = Path("/tmp")
            
            path = gcs_storage_manager.get_template_path("test.pdf")
            
            assert path is not None
            mock_blob.download_to_filename.assert_called_once()
    
    def test_delete_template_local(self, local_storage_manager, sample_pdf_content):
        """Test deleting template from local storage"""
        # Save template
        local_storage_manager.save_template(sample_pdf_content, "test.pdf")
        
        # Verify it exists
        assert local_storage_manager.template_exists("test.pdf")
        
        # Delete
        result = local_storage_manager.delete_template("test.pdf")
        assert result is True
        
        # Verify it's gone
        assert not local_storage_manager.template_exists("test.pdf")
    
    def test_delete_template_gcs(self, gcs_storage_manager):
        """Test deleting template from GCS"""
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        gcs_storage_manager.bucket.blob.return_value = mock_blob
        
        result = gcs_storage_manager.delete_template("test.pdf")
        
        assert result is True
        mock_blob.delete.assert_called_once()
    
    def test_template_exists_local(self, local_storage_manager, sample_pdf_content):
        """Test checking template existence in local storage"""
        assert not local_storage_manager.template_exists("test.pdf")
        
        local_storage_manager.save_template(sample_pdf_content, "test.pdf")
        
        assert local_storage_manager.template_exists("test.pdf")
    
    def test_get_template_metadata_local(self, local_storage_manager, sample_pdf_content):
        """Test getting template metadata from local storage"""
        # Save template with metadata
        custom_metadata = {"course": "Test Course"}
        local_storage_manager.save_template(
            sample_pdf_content,
            "test.pdf",
            metadata=custom_metadata
        )
        
        # Get metadata
        metadata = local_storage_manager.get_template_metadata("test.pdf")
        
        assert metadata["name"] == "test.pdf"
        assert metadata["course"] == "Test Course"
        assert "size" in metadata
        assert "created" in metadata
    
    def test_cleanup_old_files(self, local_storage_manager):
        """Test cleanup of old files"""
        # Create old files
        temp_dir = local_storage_manager.local_path.parent / "cert_gen"
        temp_dir.mkdir(exist_ok=True)
        
        old_file = temp_dir / "old_file.pdf"
        old_file.write_text("old content")
        
        # Set modification time to 2 hours ago
        old_time = datetime.now().timestamp() - (2 * 3600)
        os.utime(old_file, (old_time, old_time))
        
        # Create recent file
        recent_file = temp_dir / "recent_file.pdf"
        recent_file.write_text("recent content")
        
        with patch('utils.storage.config') as mock_config:
            mock_config.temp_file.temp_dir = temp_dir
            
            # Run cleanup
            count = local_storage_manager.cleanup_old_files(age_hours=1)
            
            assert count == 1
            assert not old_file.exists()
            assert recent_file.exists()
    
    def test_log_certificate_generation_local(self, local_storage_manager):
        """Test logging certificate generation to local storage"""
        local_storage_manager.log_certificate_generation(
            user="testuser",
            template="test_template.pdf",
            count=10
        )
        
        # Check log file was created
        log_file = local_storage_manager.local_path / "logs" / "usage.jsonl"
        assert log_file.exists()
        
        # Read and verify log entry
        with open(log_file, 'r') as f:
            entry = json.loads(f.readline())
        
        assert entry["user"] == "testuser"
        assert entry["template"] == "test_template.pdf"
        assert entry["count"] == 10
        assert entry["type"] == "certificate_generation"
        assert "timestamp" in entry
    
    def test_get_usage_statistics_local(self, local_storage_manager):
        """Test getting usage statistics from local storage"""
        # Log some activity
        local_storage_manager.log_certificate_generation("user1", "template1", 5)
        local_storage_manager.log_certificate_generation("user2", "template1", 10)
        local_storage_manager.log_certificate_generation("user1", "template2", 3)
        
        # Get statistics
        stats = local_storage_manager.get_usage_statistics()
        
        assert stats["total_generations"] == 3
        assert stats["total_certificates"] == 18
        assert stats["unique_users"] == 2
        assert stats["template_usage"]["template1"] == 2
        assert stats["template_usage"]["template2"] == 1
    
    def test_get_activity_logs_local(self, local_storage_manager):
        """Test getting activity logs from local storage"""
        # Log some activity
        for i in range(5):
            local_storage_manager.log_certificate_generation(
                f"user{i}",
                "template.pdf",
                i + 1
            )
        
        # Get logs
        logs = local_storage_manager.get_activity_logs(limit=3)
        
        assert len(logs) == 3
        # Should be sorted newest first
        assert all("timestamp" in log for log in logs)
    
    def test_clean_filename(self, local_storage_manager):
        """Test filename cleaning"""
        assert local_storage_manager._clean_filename("test.pdf") == "test.pdf"
        assert local_storage_manager._clean_filename("Test File (2024).pdf") == "Test_File_2024_.pdf"
        assert local_storage_manager._clean_filename("file with  spaces.pdf") == "file_with_spaces.pdf"
        assert local_storage_manager._clean_filename("../../../etc/passwd") == "passwd"
        assert local_storage_manager._clean_filename("file__with___underscores.pdf") == "file_with_underscores.pdf"
    
    def test_save_template_error_handling(self, local_storage_manager):
        """Test error handling during template save"""
        # Make templates directory read-only
        templates_dir = local_storage_manager.local_path / "templates"
        templates_dir.chmod(0o444)
        
        try:
            result = local_storage_manager.save_template(
                b"content",
                "test.pdf"
            )
            assert result is False
        finally:
            # Restore permissions
            templates_dir.chmod(0o755)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])