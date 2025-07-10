"""
集成测试 - translatebook.sh 主脚本
"""

import os
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestTranslateBookScript(unittest.TestCase):
    """测试主翻译脚本"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.script_path = os.path.join(self.script_dir, "translatebook.sh")
        
        # 创建测试文件
        self.test_pdf = os.path.join(self.temp_dir, "test.pdf")
        with open(self.test_pdf, 'wb') as f:
            # 创建一个简单的PDF文件头
            f.write(b'%PDF-1.4\n')
            f.write(b'1 0 obj\n')
            f.write(b'<<\n')
            f.write(b'/Type /Catalog\n')
            f.write(b'/Pages 2 0 R\n')
            f.write(b'>>\n')
            f.write(b'endobj\n')
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_script_exists(self):
        """测试脚本文件存在"""
        self.assertTrue(os.path.exists(self.script_path))
    
    def test_script_executable(self):
        """测试脚本是否可执行"""
        self.assertTrue(os.access(self.script_path, os.X_OK))
    
    def test_help_option(self):
        """测试帮助选项"""
        try:
            result = subprocess.run([
                self.script_path, "--help"
            ], capture_output=True, text=True, timeout=30)
            
            # 帮助信息应该正常显示
            self.assertEqual(result.returncode, 0)
            self.assertIn("电子书翻译系统", result.stdout)
            self.assertIn("用法:", result.stdout)
            
        except subprocess.TimeoutExpired:
            self.fail("帮助命令超时")
        except FileNotFoundError:
            self.skipTest("无法执行shell脚本，可能缺少bash")
    
    def test_invalid_file(self):
        """测试无效文件处理"""
        try:
            result = subprocess.run([
                self.script_path, "nonexistent.pdf"
            ], capture_output=True, text=True, timeout=30)
            
            # 应该返回错误
            self.assertNotEqual(result.returncode, 0)
            
        except subprocess.TimeoutExpired:
            self.fail("无效文件测试超时")
        except FileNotFoundError:
            self.skipTest("无法执行shell脚本，可能缺少bash")
    
    def test_parameter_parsing(self):
        """测试参数解析（不实际执行翻译）"""
        # 这个测试只验证参数解析，不执行实际翻译
        try:
            # 运行脚本但使用不存在的文件，主要测试参数解析逻辑
            result = subprocess.run([
                self.script_path, "test.pdf", "-l", "en", "--olang", "zh", "-v"
            ], capture_output=True, text=True, timeout=10)
            
            # 由于文件不存在，应该会失败，但不应该是参数解析错误
            self.assertNotEqual(result.returncode, 0)
            # 错误信息应该是文件不存在，而不是参数错误
            self.assertIn("文件不存在", result.stderr)
            
        except subprocess.TimeoutExpired:
            self.fail("参数解析测试超时")
        except FileNotFoundError:
            self.skipTest("无法执行shell脚本，可能缺少bash")


class TestPythonScriptsExist(unittest.TestCase):
    """测试所有Python脚本是否存在"""
    
    def setUp(self):
        """测试前准备"""
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def test_all_scripts_exist(self):
        """测试所有必需的脚本都存在"""
        required_scripts = [
            "01_prepare_env.py",
            "02_split_to_md.py", 
            "03_translate_md.py",
            "04_merge_md.py",
            "05_md_to_html.py",
            "06_add_toc.py"
        ]
        
        for script in required_scripts:
            script_path = os.path.join(self.script_dir, script)
            self.assertTrue(
                os.path.exists(script_path),
                f"脚本不存在: {script}"
            )
    
    def test_template_exists(self):
        """测试HTML模板存在"""
        template_path = os.path.join(self.script_dir, "template.html")
        self.assertTrue(os.path.exists(template_path))
    
    def test_requirements_exists(self):
        """测试requirements.txt存在"""
        requirements_path = os.path.join(self.script_dir, "requirements.txt")
        self.assertTrue(os.path.exists(requirements_path))


class TestProjectStructure(unittest.TestCase):
    """测试项目结构"""
    
    def setUp(self):
        """测试前准备"""
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def test_readme_exists(self):
        """测试README文件存在"""
        readme_path = os.path.join(self.project_dir, "README.md")
        self.assertTrue(os.path.exists(readme_path))
    
    def test_gitignore_exists(self):
        """测试.gitignore存在"""
        gitignore_path = os.path.join(self.project_dir, ".gitignore")
        self.assertTrue(os.path.exists(gitignore_path))
    
    def test_pytest_config_exists(self):
        """测试pytest配置存在"""
        pytest_ini = os.path.join(self.project_dir, "pytest.ini")
        self.assertTrue(os.path.exists(pytest_ini))
    
    def test_tests_directory_structure(self):
        """测试测试目录结构"""
        tests_dir = os.path.join(self.project_dir, "tests")
        self.assertTrue(os.path.exists(tests_dir))
        
        unit_tests_dir = os.path.join(tests_dir, "unit")
        self.assertTrue(os.path.exists(unit_tests_dir))
        
        integration_tests_dir = os.path.join(tests_dir, "integration")
        self.assertTrue(os.path.exists(integration_tests_dir))


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)