"""
单元测试 - 01_prepare_env.py
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from prepare_env import (
        parse_arguments, validate_input_file, check_dependencies,
        create_temp_directory, save_config, prepare_environment
    )
except ImportError:
    # 如果直接导入失败，尝试导入模块
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "prepare_env", 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "01_prepare_env.py")
    )
    prepare_env = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prepare_env)
    
    parse_arguments = prepare_env.parse_arguments
    validate_input_file = prepare_env.validate_input_file
    check_dependencies = prepare_env.check_dependencies
    create_temp_directory = prepare_env.create_temp_directory
    save_config = prepare_env.save_config
    prepare_environment = prepare_env.prepare_environment


class TestPrepareEnv(unittest.TestCase):
    """测试环境准备模块"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf = os.path.join(self.temp_dir, "test.pdf")
        self.test_docx = os.path.join(self.temp_dir, "test.docx")
        self.test_epub = os.path.join(self.temp_dir, "test.epub")
        self.test_invalid = os.path.join(self.temp_dir, "test.txt")
        
        # 创建测试文件
        for file_path in [self.test_pdf, self.test_docx, self.test_epub, self.test_invalid]:
            with open(file_path, 'w') as f:
                f.write("test content")
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_validate_input_file_valid_pdf(self):
        """测试PDF文件验证"""
        self.assertTrue(validate_input_file(self.test_pdf))
    
    def test_validate_input_file_valid_docx(self):
        """测试DOCX文件验证"""
        self.assertTrue(validate_input_file(self.test_docx))
    
    def test_validate_input_file_valid_epub(self):
        """测试EPUB文件验证"""
        self.assertTrue(validate_input_file(self.test_epub))
    
    def test_validate_input_file_invalid_format(self):
        """测试无效文件格式"""
        self.assertFalse(validate_input_file(self.test_invalid))
    
    def test_validate_input_file_nonexistent(self):
        """测试不存在的文件"""
        self.assertFalse(validate_input_file("nonexistent.pdf"))
    
    def test_create_temp_directory(self):
        """测试临时目录创建"""
        test_file = "/path/to/test.pdf"
        temp_dir = create_temp_directory(test_file)
        
        self.assertEqual(temp_dir, "test_temp")
        self.assertTrue(os.path.exists(temp_dir))
        
        # 清理
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_create_temp_directory_custom(self):
        """测试自定义临时目录"""
        test_file = "/path/to/test.pdf"
        custom_dir = "custom_temp"
        temp_dir = create_temp_directory(test_file, custom_dir)
        
        self.assertEqual(temp_dir, custom_dir)
        self.assertTrue(os.path.exists(temp_dir))
        
        # 清理
        import shutil
        shutil.rmtree(custom_dir)
    
    def test_save_config(self):
        """测试配置文件保存"""
        config = {
            "input_file": "test.pdf",
            "output_lang": "zh",
            "input_lang": "en"
        }
        
        config_path = save_config(config, self.temp_dir)
        
        self.assertTrue(os.path.exists(config_path))
        
        # 验证内容
        with open(config_path, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config['input_file'], "test.pdf")
        self.assertEqual(loaded_config['output_lang'], "zh")
    
    @patch('subprocess.run')
    def test_check_dependencies(self, mock_run):
        """测试依赖检查"""
        # 模拟成功的依赖检查
        mock_run.return_value.returncode = 0
        
        deps = check_dependencies()
        
        self.assertIsInstance(deps, dict)
        self.assertIn('claude', deps)
        self.assertIn('pandoc', deps)
        self.assertIn('python', deps)
        self.assertTrue(deps['python'])  # Python应该总是可用的
    
    def test_prepare_environment_success(self):
        """测试完整环境准备流程"""
        config = prepare_environment(
            input_file=self.test_pdf,
            output_lang="zh",
            input_lang="en",
            custom_prompt="test prompt"
        )
        
        self.assertIsInstance(config, dict)
        self.assertEqual(config['output_lang'], "zh")
        self.assertEqual(config['input_lang'], "en")
        self.assertEqual(config['custom_prompt'], "test prompt")
        self.assertIn('temp_dir', config)
        self.assertIn('dependencies', config)
        
        # 验证临时目录存在
        self.assertTrue(os.path.exists(config['temp_dir']))
        
        # 验证配置文件存在
        config_file = os.path.join(config['temp_dir'], "config.json")
        self.assertTrue(os.path.exists(config_file))
        
        # 清理
        import shutil
        shutil.rmtree(config['temp_dir'])
    
    def test_prepare_environment_invalid_file(self):
        """测试无效文件的环境准备"""
        with self.assertRaises(ValueError):
            prepare_environment(
                input_file="nonexistent.pdf",
                output_lang="zh"
            )
    
    @patch('sys.argv', ['01_prepare_env.py', 'test.pdf'])
    def test_parse_arguments_basic(self):
        """测试基本参数解析"""
        args = parse_arguments()
        self.assertEqual(args.input_file, 'test.pdf')
        self.assertEqual(args.input_lang, 'auto')
        self.assertEqual(args.olang, 'zh')
        self.assertEqual(args.prompt, '')
    
    @patch('sys.argv', [
        '01_prepare_env.py', 'test.pdf', 
        '-l', 'en', '--olang', 'ja', 
        '-p', 'custom prompt', '--temp-dir', 'custom_temp'
    ])
    def test_parse_arguments_full(self):
        """测试完整参数解析"""
        args = parse_arguments()
        self.assertEqual(args.input_file, 'test.pdf')
        self.assertEqual(args.input_lang, 'en')
        self.assertEqual(args.olang, 'ja')
        self.assertEqual(args.prompt, 'custom prompt')
        self.assertEqual(args.temp_dir, 'custom_temp')


class TestPrepareEnvIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "integration_test.pdf")
        
        # 创建一个更真实的测试文件
        with open(self.test_file, 'wb') as f:
            # 写入PDF文件头
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
    
    def test_end_to_end_preparation(self):
        """测试端到端的环境准备"""
        config = prepare_environment(
            input_file=self.test_file,
            output_lang="zh",
            input_lang="auto",
            custom_prompt="integration test"
        )
        
        # 验证所有必要的配置项都存在
        required_keys = [
            'input_file', 'output_lang', 'input_lang', 
            'custom_prompt', 'temp_dir', 'dependencies'
        ]
        
        for key in required_keys:
            self.assertIn(key, config)
        
        # 验证文件路径是绝对路径
        self.assertTrue(os.path.isabs(config['input_file']))
        self.assertTrue(os.path.isabs(config['temp_dir']))
        
        # 验证临时目录结构
        temp_dir = config['temp_dir']
        self.assertTrue(os.path.exists(temp_dir))
        
        config_file = os.path.join(temp_dir, "config.json")
        self.assertTrue(os.path.exists(config_file))
        
        # 验证配置文件内容
        with open(config_file, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config['output_lang'], "zh")
        self.assertEqual(saved_config['custom_prompt'], "integration test")
        
        # 清理
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)