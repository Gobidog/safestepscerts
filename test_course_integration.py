#!/usr/bin/env python3
"""
Test script for course selection integration in certificate generation
"""

import streamlit as st
from utils.storage import list_course_templates, increment_course_usage

def test_course_integration():
    """Test course integration"""
    print("Testing Course Integration in Certificate Generation")
    print("=" * 50)
    
    # Test 1: List available courses
    print("\nTest 1: Listing available courses...")
    courses = list_course_templates()
    print(f"Found {len(courses)} courses:")
    for course in courses:
        print(f"  - Name: {course['name']}")
        print(f"    ID: {course['id']}")
        print(f"    Description: {course['description']}")
        print(f"    Usage Count: {course.get('usage_count', 0)}")
        print()
    
    # Test 2: Test course usage increment
    if courses:
        test_course = courses[0]
        print(f"\nTest 2: Testing usage increment for course '{test_course['name']}'...")
        
        initial_count = test_course.get('usage_count', 0)
        print(f"Initial usage count: {initial_count}")
        
        # Increment usage
        success = increment_course_usage(test_course['id'])
        print(f"Increment result: {'Success' if success else 'Failed'}")
        
        # Verify increment
        updated_courses = list_course_templates()
        updated_course = next((c for c in updated_courses if c['id'] == test_course['id']), None)
        
        if updated_course:
            new_count = updated_course.get('usage_count', 0)
            print(f"New usage count: {new_count}")
            print(f"Increment verified: {new_count == initial_count + 1}")
        else:
            print("ERROR: Could not find course after update")
    
    print("\nTest complete!")

if __name__ == "__main__":
    test_course_integration()