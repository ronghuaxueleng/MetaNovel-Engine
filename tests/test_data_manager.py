"""
Unit tests for data_manager module
"""

import json
import unittest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch

# Add project root to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_manager import DataManager
import data_manager as data_manager_module
from project_manager import ProjectManager
# We import the global instance to be patched
import project_data_manager as pdm_module

class TestDataManager(unittest.TestCase):
    """测试DataManager类的功能"""

    def setUp(self):
        """每个测试前的设置"""
        # 1. 创建一个临时目录作为测试的根目录
        self.test_base_dir = Path(tempfile.mkdtemp())
        
        # 2. 创建一个只在这个测试中使用的 ProjectManager 实例
        self.test_pm = ProjectManager(base_dir=self.test_base_dir)
        
        # 3. 使用 patch 来替换全局的 project_manager 实例
        self.patcher = patch('project_data_manager.project_manager', self.test_pm)
        self.mock_project_manager = self.patcher.start()

        # 4. 现在，我们可以安全地使用 project_data_manager 了
        self.pdm = pdm_module.ProjectDataManager()
        
        # 创建一个测试项目
        self.test_project_name = "test_project"
        self.test_pm.create_project(self.test_project_name, display_name="Test Project")
        self.pdm.switch_project(self.test_project_name)
        
        # 获取这个测试项目专属的DataManager实例
        self.data_manager = self.pdm.get_data_manager()
        self.assertIsNotNone(self.data_manager, "测试项目的数据管理器应该被成功创建")
        self.assertEqual(self.pdm.get_current_project_name(), self.test_project_name)

    def tearDown(self):
        """每个测试后的清理"""
        # 停止 patch
        self.patcher.stop()
        # 删除临时目录
        shutil.rmtree(self.test_base_dir)

    def test_read_write_theme_one_line(self):
        """测试一句话主题的读写"""
        theme = "一个关于勇气的故事"
        self.data_manager.write_theme_one_line(theme)
        read_data = self.data_manager.read_theme_one_line()
        self.assertIsInstance(read_data, dict)
        self.assertEqual(read_data.get('theme'), theme)

    def test_read_write_theme_paragraph(self):
        """测试段落主题的读写"""
        paragraph = "这是一个详细的段落主题描述..."
        self.data_manager.write_theme_paragraph(paragraph)
        read_paragraph = self.data_manager.read_theme_paragraph()
        self.assertEqual(read_paragraph, paragraph)

    def test_character_operations(self):
        """测试角色CRUD操作"""
        char_name = "测试角色"
        char_desc = "这是一个测试角色的描述"
        
        self.data_manager.add_character(char_name, char_desc)
        characters = self.data_manager.read_characters()
        self.assertIn(char_name, characters)
        self.assertEqual(characters[char_name]["description"], char_desc)
        
        new_desc = "更新后的角色描述"
        self.data_manager.update_character(char_name, new_desc)
        updated_characters = self.data_manager.read_characters()
        self.assertEqual(updated_characters[char_name]["description"], new_desc)
        
        self.data_manager.delete_character(char_name)
        final_characters = self.data_manager.read_characters()
        self.assertNotIn(char_name, final_characters)

    def test_json_cache_hits_without_disk_reload(self):
        """重复读取同一文件时应命中缓存，避免重复磁盘读取"""
        characters_path = self.data_manager.file_paths["characters"]
        characters_path.parent.mkdir(parents=True, exist_ok=True)
        with characters_path.open("w", encoding="utf-8") as f:
            json.dump({"测试角色": {"description": "缓存测试"}}, f, ensure_ascii=False)

        # 使用全新实例确保缓存初始为空
        dm = DataManager(self.data_manager.project_path)

        original_load = data_manager_module.json.load
        load_counter = {"count": 0}

        def counting_load(*args, **kwargs):
            load_counter["count"] += 1
            return original_load(*args, **kwargs)

        with patch.object(data_manager_module.json, "load", side_effect=counting_load):
            first_read = dm.read_characters()
            second_read = dm.read_characters()

        self.assertEqual(load_counter["count"], 1, "缓存命中后不应再次触发 json.load")
        self.assertEqual(first_read, second_read)
        self.assertIn("测试角色", second_read)

    def test_json_cache_returns_copy(self):
        """读取结果应为副本，外部修改不会污染缓存"""
        self.data_manager.add_character("缓存角色", "原始描述")
        first_read = self.data_manager.read_characters()
        first_read["缓存角色"]["description"] = "被外部篡改"

        second_read = self.data_manager.read_characters()

        self.assertEqual(
            second_read["缓存角色"]["description"],
            "原始描述",
            "修改读取结果不应影响缓存中的数据"
        )

    def test_json_cache_invalidates_on_write(self):
        """写入后缓存应立即反映最新数据"""
        self.data_manager.add_character("缓存更新角色", "第一次描述")
        _ = self.data_manager.read_characters()

        self.data_manager.update_character("缓存更新角色", "第二次描述")
        updated_read = self.data_manager.read_characters()

        self.assertEqual(
            updated_read["缓存更新角色"]["description"],
            "第二次描述",
            "写入后缓存必须刷新以返回最新数据"
        )

if __name__ == '__main__':
    unittest.main()
