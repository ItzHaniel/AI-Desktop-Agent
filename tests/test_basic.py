#!/usr/bin/env python3
"""
Basic tests for Jarvis modules
"""

import unittest
import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent / "modules"))

class TestJarvisModules(unittest.TestCase):
    """Basic smoke tests"""

    def test_project_structure(self):
        """Test that project structure exists"""
        base_path = Path(__file__).parent.parent

        # Check directories
        self.assertTrue((base_path / "modules").exists())
        self.assertTrue((base_path / "utils").exists())
        self.assertTrue((base_path / "data").exists())

        # Check main file
        self.assertTrue((base_path / "main.py").exists())

        print("Project structure test passed")

if __name__ == "__main__":
    unittest.main()
