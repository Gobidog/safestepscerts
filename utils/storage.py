"""
Storage management module for Certificate Generator.
Handles Google Cloud Storage with local fallback for development.
"""
import os
import io
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Union, BinaryIO
from datetime import datetime, timedelta
import structlog

from config import config

# Configure logger
logger = structlog.get_logger()

# Try to import Google Cloud Storage
try:
    from google.cloud import storage as gcs
    from google.cloud.exceptions import NotFound
    GCS_AVAILABLE = True
except ImportError:
    logger.warning("Google Cloud Storage not available. Using local storage only.")
    GCS_AVAILABLE = False
    gcs = None
    NotFound = Exception


class StorageManager:
    """Manages storage operations with GCS and local fallback"""
    
    def __init__(self):
        self.use_local = config.storage.use_local_storage or not GCS_AVAILABLE
        self.local_path = config.storage.local_storage_path
        
        if not self.use_local and GCS_AVAILABLE:
            try:
                self.client = gcs.Client(project=config.storage.gcs_project_id)
                self.bucket = self.client.bucket(config.storage.gcs_bucket_name)
                logger.info(f"Connected to GCS bucket: {config.storage.gcs_bucket_name}")
            except Exception as e:
                logger.error(f"Failed to connect to GCS: {e}")
                logger.warning("Falling back to local storage")
                self.use_local = True
        
        if self.use_local:
            # Ensure local directories exist
            templates_dir = self.local_path / "templates"
            generated_dir = self.local_path / "generated"
            metadata_dir = self.local_path / "metadata"
            
            for directory in [templates_dir, generated_dir, metadata_dir]:
                directory.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Using local storage at: {self.local_path}")
    
    def save_template(self, file_buffer: Union[BinaryIO, bytes], template_name: str, 
                     metadata: Optional[Dict] = None) -> bool:
        """Save a PDF template to storage"""
        try:
            # Ensure file buffer is seekable
            if hasattr(file_buffer, 'read'):
                content = file_buffer.read()
                if hasattr(file_buffer, 'seek'):
                    file_buffer.seek(0)
            else:
                content = file_buffer
            
            # Clean template name
            template_name = self._clean_filename(template_name)
            if not template_name.endswith('.pdf'):
                template_name += '.pdf'
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata.update({
                'name': template_name,
                'uploaded_at': datetime.now().isoformat(),
                'size': len(content),
                'type': 'template'
            })
            
            if self.use_local:
                # Save to local storage
                template_path = self.local_path / "templates" / template_name
                with open(template_path, 'wb') as f:
                    f.write(content)
                
                # Save metadata
                metadata_path = self.local_path / "metadata" / f"{template_name}.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Template saved locally: {template_name}")
            else:
                # Save to GCS
                blob = self.bucket.blob(f"templates/{template_name}")
                blob.upload_from_string(content, content_type='application/pdf')
                blob.metadata = metadata
                blob.patch()
                
                logger.info(f"Template saved to GCS: {template_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save template {template_name}: {e}")
            return False
    
    def save_template_to_gcs(self, file_buffer: Union[BinaryIO, bytes], 
                            template_name: str, metadata: Optional[Dict] = None) -> bool:
        """Alias for save_template to match agent requirements"""
        return self.save_template(file_buffer, template_name, metadata)
    
    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates with metadata"""
        templates = []
        
        try:
            if self.use_local:
                # List from local storage
                templates_dir = self.local_path / "templates"
                metadata_dir = self.local_path / "metadata"
                
                for template_file in templates_dir.glob("*.pdf"):
                    template_info = {
                        'name': template_file.stem,
                        'filename': template_file.name,
                        'path': str(template_file),
                        'created': datetime.fromtimestamp(template_file.stat().st_ctime).isoformat(),
                        'size': template_file.stat().st_size
                    }
                    
                    # Try to load additional metadata
                    metadata_file = metadata_dir / f"{template_file.name}.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                saved_metadata = json.load(f)
                                template_info.update(saved_metadata)
                        except Exception:
                            pass
                    
                    templates.append(template_info)
            else:
                # List from GCS
                for blob in self.bucket.list_blobs(prefix="templates/"):
                    if blob.name.endswith('.pdf'):
                        template_info = {
                            'name': Path(blob.name).stem,
                            'filename': Path(blob.name).name,
                            'path': blob.name,
                            'created': blob.time_created.isoformat() if blob.time_created else '',
                            'size': blob.size
                        }
                        
                        if blob.metadata:
                            template_info.update(blob.metadata)
                        
                        templates.append(template_info)
            
            # Sort by creation date (newest first)
            templates.sort(key=lambda x: x.get('created', ''), reverse=True)
            logger.info(f"Listed {len(templates)} templates")
            
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
        
        return templates
    
    def get_template(self, template_name: str) -> Optional[bytes]:
        """Get template content as bytes"""
        try:
            # Clean template name
            template_name = self._clean_filename(template_name)
            if not template_name.endswith('.pdf'):
                template_name += '.pdf'
            
            if self.use_local:
                template_path = self.local_path / "templates" / template_name
                if template_path.exists():
                    with open(template_path, 'rb') as f:
                        return f.read()
            else:
                blob = self.bucket.blob(f"templates/{template_name}")
                if blob.exists():
                    return blob.download_as_bytes()
            
            logger.warning(f"Template not found: {template_name}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get template {template_name}: {e}")
            return None
    
    def get_template_path(self, template_name: str) -> Optional[str]:
        """Get the file path for a template (for PDF generator)"""
        try:
            # Clean template name
            template_name = self._clean_filename(template_name)
            if not template_name.endswith('.pdf'):
                template_name += '.pdf'
            
            if self.use_local:
                template_path = self.local_path / "templates" / template_name
                if template_path.exists():
                    return str(template_path)
            else:
                # For GCS, download to temp directory
                temp_path = config.temp_file.temp_dir / f"template_{template_name}"
                
                # Check if recently downloaded (cache for 5 minutes)
                if temp_path.exists() and (time.time() - temp_path.stat().st_mtime) < 300:
                    return str(temp_path)
                
                # Download from GCS
                blob = self.bucket.blob(f"templates/{template_name}")
                if blob.exists():
                    blob.download_to_filename(str(temp_path))
                    logger.info(f"Downloaded template from GCS to: {temp_path}")
                    return str(temp_path)
            
            logger.warning(f"Template not found: {template_name}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get template path for {template_name}: {e}")
            return None
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a template from storage"""
        try:
            # Clean template name
            template_name = self._clean_filename(template_name)
            if not template_name.endswith('.pdf'):
                template_name += '.pdf'
            
            if self.use_local:
                # Delete from local storage
                template_path = self.local_path / "templates" / template_name
                metadata_path = self.local_path / "metadata" / f"{template_name}.json"
                
                deleted = False
                if template_path.exists():
                    template_path.unlink()
                    deleted = True
                
                if metadata_path.exists():
                    metadata_path.unlink()
                
                if deleted:
                    logger.info(f"Template deleted locally: {template_name}")
                return deleted
            else:
                # Delete from GCS
                blob = self.bucket.blob(f"templates/{template_name}")
                if blob.exists():
                    blob.delete()
                    logger.info(f"Template deleted from GCS: {template_name}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete template {template_name}: {e}")
            return False
    
    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists"""
        try:
            # Clean template name
            template_name = self._clean_filename(template_name)
            if not template_name.endswith('.pdf'):
                template_name += '.pdf'
            
            if self.use_local:
                template_path = self.local_path / "templates" / template_name
                return template_path.exists()
            else:
                blob = self.bucket.blob(f"templates/{template_name}")
                return blob.exists()
                
        except Exception as e:
            logger.error(f"Failed to check template existence {template_name}: {e}")
            return False
    
    def get_template_metadata(self, template_name: str) -> Dict:
        """Get metadata about a template"""
        try:
            # Clean template name
            template_name = self._clean_filename(template_name)
            if not template_name.endswith('.pdf'):
                template_name += '.pdf'
            
            if self.use_local:
                template_path = self.local_path / "templates" / template_name
                metadata_path = self.local_path / "metadata" / f"{template_name}.json"
                
                if template_path.exists():
                    metadata = {
                        'name': template_name,
                        'size': template_path.stat().st_size,
                        'created': datetime.fromtimestamp(template_path.stat().st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(template_path.stat().st_mtime).isoformat()
                    }
                    
                    # Load additional metadata if exists
                    if metadata_path.exists():
                        try:
                            with open(metadata_path, 'r') as f:
                                saved_metadata = json.load(f)
                                metadata.update(saved_metadata)
                        except Exception:
                            pass
                    
                    return metadata
            else:
                blob = self.bucket.blob(f"templates/{template_name}")
                if blob.exists():
                    metadata = {
                        'name': template_name,
                        'size': blob.size,
                        'created': blob.time_created.isoformat() if blob.time_created else '',
                        'modified': blob.updated.isoformat() if blob.updated else '',
                        'content_type': blob.content_type
                    }
                    
                    if blob.metadata:
                        metadata.update(blob.metadata)
                    
                    return metadata
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get template metadata {template_name}: {e}")
            return {}
    
    def cleanup_old_files(self, age_hours: int = 1) -> int:
        """Clean up old temporary and generated files"""
        try:
            count = 0
            cutoff_time = datetime.now() - timedelta(hours=age_hours)
            
            # Clean temp files
            for temp_file in config.temp_file.temp_dir.glob("*"):
                if temp_file.is_file():
                    file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        temp_file.unlink()
                        count += 1
            
            # Clean old generated files from local storage
            if self.use_local:
                generated_dir = self.local_path / "generated"
                for gen_file in generated_dir.glob("*.pdf"):
                    file_time = datetime.fromtimestamp(gen_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        gen_file.unlink()
                        count += 1
            
            if count > 0:
                logger.info(f"Cleaned up {count} old files")
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old files: {e}")
            return 0
    
    def log_certificate_generation(self, user: str, template: str, count: int):
        """Log certificate generation for usage tracking"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'user': user,
                'template': template,
                'count': count,
                'type': 'certificate_generation'
            }
            
            if self.use_local:
                # Append to local log file
                log_file = self.local_path / "logs" / "usage.jsonl"
                log_file.parent.mkdir(exist_ok=True)
                
                with open(log_file, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
            else:
                # Log to GCS
                blob_name = f"logs/usage/{datetime.now().strftime('%Y-%m-%d')}.jsonl"
                blob = self.bucket.blob(blob_name)
                
                # Append to existing log
                existing_content = b''
                if blob.exists():
                    existing_content = blob.download_as_bytes()
                
                new_content = existing_content + (json.dumps(log_entry) + '\n').encode()
                blob.upload_from_string(new_content)
            
            logger.info(f"Logged certificate generation: {user} - {template} - {count}")
            
        except Exception as e:
            logger.error(f"Failed to log certificate generation: {e}")
    
    def get_usage_statistics(self) -> Dict:
        """Get usage statistics"""
        try:
            stats = {
                'total_generations': 0,
                'total_certificates': 0,
                'unique_users': set(),
                'template_usage': {},
                'daily_usage': {}
            }
            
            if self.use_local:
                log_file = self.local_path / "logs" / "usage.jsonl"
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                if entry.get('type') == 'certificate_generation':
                                    stats['total_generations'] += 1
                                    stats['total_certificates'] += entry.get('count', 0)
                                    stats['unique_users'].add(entry.get('user', 'unknown'))
                                    
                                    template = entry.get('template', 'unknown')
                                    stats['template_usage'][template] = stats['template_usage'].get(template, 0) + 1
                                    
                                    date = entry.get('timestamp', '')[:10]
                                    if date:
                                        stats['daily_usage'][date] = stats['daily_usage'].get(date, 0) + 1
                            except Exception:
                                pass
            else:
                # Read from GCS logs
                for blob in self.bucket.list_blobs(prefix="logs/usage/"):
                    content = blob.download_as_text()
                    for line in content.splitlines():
                        try:
                            entry = json.loads(line.strip())
                            if entry.get('type') == 'certificate_generation':
                                stats['total_generations'] += 1
                                stats['total_certificates'] += entry.get('count', 0)
                                stats['unique_users'].add(entry.get('user', 'unknown'))
                                
                                template = entry.get('template', 'unknown')
                                stats['template_usage'][template] = stats['template_usage'].get(template, 0) + 1
                                
                                date = entry.get('timestamp', '')[:10]
                                if date:
                                    stats['daily_usage'][date] = stats['daily_usage'].get(date, 0) + 1
                        except Exception:
                            pass
            
            # Convert set to count
            stats['unique_users'] = len(stats['unique_users'])
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get usage statistics: {e}")
            return {
                'total_generations': 0,
                'total_certificates': 0,
                'unique_users': 0,
                'template_usage': {},
                'daily_usage': {}
            }
    
    def get_activity_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent activity logs"""
        try:
            logs = []
            
            if self.use_local:
                log_file = self.local_path / "logs" / "usage.jsonl"
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        # Read all lines and take the last N
                        all_logs = []
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                all_logs.append(entry)
                            except Exception:
                                pass
                        logs = all_logs[-limit:]
            else:
                # Read from GCS logs (most recent files first)
                all_logs = []
                for blob in sorted(self.bucket.list_blobs(prefix="logs/usage/"), 
                                 key=lambda x: x.name, reverse=True):
                    if len(all_logs) >= limit:
                        break
                    
                    content = blob.download_as_text()
                    for line in content.splitlines():
                        try:
                            entry = json.loads(line.strip())
                            all_logs.append(entry)
                        except Exception:
                            pass
                
                logs = all_logs[:limit]
            
            # Sort by timestamp (newest first)
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return logs[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get activity logs: {e}")
            return []
    
    def _clean_filename(self, filename: str) -> str:
        """Clean filename to be safe for storage"""
        # Remove any path components
        filename = Path(filename).name
        
        # Replace spaces and special characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        cleaned = ''.join(c if c in safe_chars else '_' for c in filename)
        
        # Remove multiple underscores
        while '__' in cleaned:
            cleaned = cleaned.replace('__', '_')
        
        return cleaned.strip('_')


# Create singleton instance
storage_manager = StorageManager()

# Export convenience functions
save_template = storage_manager.save_template
save_template_to_gcs = storage_manager.save_template_to_gcs
list_templates = storage_manager.list_templates
get_template = storage_manager.get_template
get_template_path = storage_manager.get_template_path
delete_template = storage_manager.delete_template
template_exists = storage_manager.template_exists
get_template_metadata = storage_manager.get_template_metadata
cleanup_old_files = storage_manager.cleanup_old_files
log_certificate_generation = storage_manager.log_certificate_generation
get_usage_statistics = storage_manager.get_usage_statistics
get_activity_logs = storage_manager.get_activity_logs