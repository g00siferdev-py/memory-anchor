#!/usr/bin/env python3
"""
Test suite for Memory Anchor core functionality.
"""

import unittest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_system import init_db, store_memory, recall_recent, recall_by_topic


class TestMemorySystem(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary database for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_memory.db")
        os.environ["MEMORY_DB_PATH"] = self.db_path
        init_db(self.db_path)
    
    def tearDown(self):
        """Clean up temporary database."""
        shutil.rmtree(self.test_dir)
    
    def test_store_memory(self):
        """Test storing a memory."""
        result = store_memory("Test content", source="test", tags="test", db_path=self.db_path)
        self.assertTrue(result)
    
    def test_recall_recent(self):
        """Test recalling recent memories."""
        # Store a memory
        store_memory("Test memory content", source="test", tags="test", db_path=self.db_path)
        
        # Recall it
        recent = recall_recent(hours=24, db_path=self.db_path)
        
        self.assertEqual(recent['count'], 1)
        self.assertEqual(len(recent['raw']), 1)
    
    def test_recall_by_topic(self):
        """Test searching by topic."""
        # Store memories with different tags
        store_memory("Weather is sunny", source="test", tags="weather,sun", db_path=self.db_path)
        store_memory("Meeting at 3pm", source="test", tags="meeting,work", db_path=self.db_path)
        
        # Search for weather
        results = recall_by_topic("weather", db_path=self.db_path)
        
        self.assertEqual(len(results), 1)
        self.assertIn("sunny", results[0]['content'])
    
    def test_empty_recall(self):
        """Test recalling when no memories exist."""
        recent = recall_recent(hours=24, db_path=self.db_path)
        self.assertEqual(recent['count'], 0)
        self.assertEqual(len(recent['raw']), 0)


if __name__ == "__main__":
    unittest.main()