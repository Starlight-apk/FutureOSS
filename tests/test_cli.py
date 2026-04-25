"""CLI 命令单元测试"""
import pytest
from click.testing import CliRunner
from oss.cli import cli, version, serve


class TestCLI:
    """测试 CLI 命令"""

    def test_version_command(self):
        """测试版本命令"""
        runner = CliRunner()
        result = runner.invoke(version)
        
        assert result.exit_code == 0
        assert "Future OSS" in result.output
        assert "1.2.0" in result.output

    def test_cli_help(self):
        """测试 CLI 帮助信息"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "Future OSS" in result.output
        assert "serve" in result.output
        assert "version" in result.output

    def test_serve_command_exists(self):
        """测试 serve 命令存在"""
        runner = CliRunner()
        result = runner.invoke(serve, ['--help'])
        
        assert result.exit_code == 0
        assert "启动 Future OSS" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
