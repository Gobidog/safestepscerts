"""
Course Management module for Certificate Generator.
Handles course template CRUD operations with metadata storage.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import structlog

# Configure logger
logger = structlog.get_logger()


class CourseManager:
    """Manages course templates for certificate generation"""
    
    def __init__(self, storage_path: Path):
        """
        Initialize the CourseManager.
        
        Args:
            storage_path: Base path for data storage (usually data/metadata)
        """
        self.storage_path = Path(storage_path)
        self.courses_file = self.storage_path / "course_templates.json"
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing courses or initialize empty
        self.courses = self._load_courses()
        
        logger.info(f"CourseManager initialized with {len(self.courses)} courses")
    
    def _load_courses(self) -> Dict[str, Dict]:
        """Load courses from storage file"""
        if self.courses_file.exists():
            try:
                with open(self.courses_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load courses: {e}")
                return {}
        return {}
    
    def _save_courses(self) -> bool:
        """Save courses to storage file"""
        try:
            with open(self.courses_file, 'w') as f:
                json.dump(self.courses, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save courses: {e}")
            return False
    
    def _generate_course_id(self) -> str:
        """Generate a unique course ID"""
        timestamp = int(time.time() * 1000000)  # Microsecond timestamp
        return f"course_{timestamp}"
    
    def create_course(self, name: str, description: str, created_by: str = "admin") -> Optional[Dict]:
        """
        Create a new course template.
        
        Args:
            name: Course name
            description: Course description
            created_by: Username of creator
            
        Returns:
            Created course dict or None if failed
        """
        try:
            # Validate inputs
            if not name or not name.strip():
                logger.error("Course name cannot be empty")
                return None
            
            if not description or not description.strip():
                logger.error("Course description cannot be empty")
                return None
            
            # Check for duplicate name
            for course in self.courses.values():
                if course['name'].lower() == name.strip().lower():
                    logger.error(f"Course with name '{name}' already exists")
                    return None
            
            # Create course
            course_id = self._generate_course_id()
            now = datetime.now().isoformat()
            
            course = {
                'id': course_id,
                'name': name.strip(),
                'description': description.strip(),
                'created_by': created_by,
                'created_at': now,
                'updated_at': now,
                'usage_count': 0,
                'last_used': None
            }
            
            # Save to storage
            self.courses[course_id] = course
            if self._save_courses():
                logger.info(f"Created course: {course_id} - {name}")
                return course
            else:
                # Rollback on save failure
                del self.courses[course_id]
                return None
                
        except Exception as e:
            logger.error(f"Failed to create course: {e}")
            return None
    
    def get_course(self, course_id: str) -> Optional[Dict]:
        """
        Get a course by ID.
        
        Args:
            course_id: Course ID
            
        Returns:
            Course dict or None if not found
        """
        return self.courses.get(course_id)
    
    def get_course_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a course by name (case-insensitive).
        
        Args:
            name: Course name
            
        Returns:
            Course dict or None if not found
        """
        name_lower = name.strip().lower()
        for course in self.courses.values():
            if course['name'].lower() == name_lower:
                return course
        return None
    
    def update_course(self, course_id: str, name: Optional[str] = None, 
                     description: Optional[str] = None) -> Optional[Dict]:
        """
        Update a course template.
        
        Args:
            course_id: Course ID to update
            name: New name (optional)
            description: New description (optional)
            
        Returns:
            Updated course dict or None if failed
        """
        try:
            if course_id not in self.courses:
                logger.error(f"Course not found: {course_id}")
                return None
            
            course = self.courses[course_id]
            updated = False
            
            # Update name if provided
            if name is not None and name.strip():
                # Check for duplicate name
                name_lower = name.strip().lower()
                for other_id, other_course in self.courses.items():
                    if other_id != course_id and other_course['name'].lower() == name_lower:
                        logger.error(f"Course with name '{name}' already exists")
                        return None
                
                course['name'] = name.strip()
                updated = True
            
            # Update description if provided
            if description is not None and description.strip():
                course['description'] = description.strip()
                updated = True
            
            # Update timestamp if changes were made
            if updated:
                course['updated_at'] = datetime.now().isoformat()
                
                if self._save_courses():
                    logger.info(f"Updated course: {course_id}")
                    return course
                else:
                    # Reload courses on save failure
                    self.courses = self._load_courses()
                    return None
            
            return course
            
        except Exception as e:
            logger.error(f"Failed to update course: {e}")
            return None
    
    def delete_course(self, course_id: str) -> bool:
        """
        Delete a course template.
        
        Args:
            course_id: Course ID to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            if course_id not in self.courses:
                logger.error(f"Course not found: {course_id}")
                return False
            
            # Save course for potential rollback
            deleted_course = self.courses[course_id]
            
            # Delete from memory
            del self.courses[course_id]
            
            # Save to storage
            if self._save_courses():
                logger.info(f"Deleted course: {course_id} - {deleted_course['name']}")
                return True
            else:
                # Rollback on save failure
                self.courses[course_id] = deleted_course
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete course: {e}")
            return False
    
    def list_courses(self, sort_by: str = 'created_at', reverse: bool = True) -> List[Dict]:
        """
        List all courses with optional sorting.
        
        Args:
            sort_by: Field to sort by ('created_at', 'updated_at', 'name', 'usage_count')
            reverse: Sort in reverse order (newest first for dates, highest first for counts)
            
        Returns:
            List of course dicts
        """
        try:
            courses = list(self.courses.values())
            
            # Sort courses
            if sort_by in ['created_at', 'updated_at', 'last_used']:
                # Date sorting
                courses.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse)
            elif sort_by == 'name':
                # Name sorting (alphabetical)
                courses.sort(key=lambda x: x.get(sort_by, '').lower(), reverse=not reverse)
            elif sort_by == 'usage_count':
                # Usage count sorting
                courses.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
            
            return courses
            
        except Exception as e:
            logger.error(f"Failed to list courses: {e}")
            return []
    
    def increment_usage(self, course_id: str) -> bool:
        """
        Increment usage count and update last used timestamp.
        
        Args:
            course_id: Course ID
            
        Returns:
            True if updated successfully
        """
        try:
            if course_id not in self.courses:
                logger.error(f"Course not found: {course_id}")
                return False
            
            course = self.courses[course_id]
            course['usage_count'] = course.get('usage_count', 0) + 1
            course['last_used'] = datetime.now().isoformat()
            
            if self._save_courses():
                logger.info(f"Updated usage for course: {course_id} - count: {course['usage_count']}")
                return True
            else:
                # Reload courses on save failure
                self.courses = self._load_courses()
                return False
                
        except Exception as e:
            logger.error(f"Failed to increment usage: {e}")
            return False
    
    def search_courses(self, query: str) -> List[Dict]:
        """
        Search courses by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching course dicts
        """
        try:
            if not query:
                return self.list_courses()
            
            query_lower = query.lower()
            matches = []
            
            for course in self.courses.values():
                if (query_lower in course['name'].lower() or 
                    query_lower in course['description'].lower()):
                    matches.append(course)
            
            # Sort by relevance (name matches first, then by usage)
            matches.sort(key=lambda x: (
                query_lower not in x['name'].lower(),  # Name matches first
                -x.get('usage_count', 0)  # Then by usage count
            ))
            
            return matches
            
        except Exception as e:
            logger.error(f"Failed to search courses: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """
        Get course usage statistics.
        
        Returns:
            Statistics dict
        """
        try:
            total_courses = len(self.courses)
            total_usage = sum(course.get('usage_count', 0) for course in self.courses.values())
            
            # Find most and least used courses
            courses_with_usage = [c for c in self.courses.values() if c.get('usage_count', 0) > 0]
            
            most_used = None
            least_used = None
            
            if courses_with_usage:
                most_used = max(courses_with_usage, key=lambda x: x.get('usage_count', 0))
                least_used = min(courses_with_usage, key=lambda x: x.get('usage_count', 0))
            
            # Get courses by creator
            creators = {}
            for course in self.courses.values():
                creator = course.get('created_by', 'unknown')
                creators[creator] = creators.get(creator, 0) + 1
            
            return {
                'total_courses': total_courses,
                'total_usage': total_usage,
                'average_usage': total_usage / total_courses if total_courses > 0 else 0,
                'most_used_course': most_used,
                'least_used_course': least_used,
                'courses_by_creator': creators,
                'courses_with_usage': len(courses_with_usage),
                'courses_without_usage': total_courses - len(courses_with_usage)
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def migrate_default_courses(self) -> int:
        """
        Migrate default courses if they don't exist.
        
        Returns:
            Number of courses migrated
        """
        default_courses = [
            {
                'name': 'Vapes and Vaping',
                'description': 'Educational course about vaping awareness and prevention'
            },
            {
                'name': 'Bullying',
                'description': 'Course on bullying prevention and awareness'
            }
        ]
        
        migrated = 0
        for course_data in default_courses:
            # Check if course already exists
            if not self.get_course_by_name(course_data['name']):
                if self.create_course(
                    name=course_data['name'],
                    description=course_data['description'],
                    created_by='system'
                ):
                    migrated += 1
                    logger.info(f"Migrated default course: {course_data['name']}")
        
        return migrated