"""CLI 入口"""
import click
import signal
import os

from oss import __version__
from oss.logger.logger import Logger
from oss.plugin.manager import PluginManager
from oss.config import init_config, get_config


@click.group()
@click.option('--config', '-c', type=str, help='配置文件路径')
@click.pass_context
def cli(ctx, config):
    """Future OSS - 一切皆为插件"""
    # 初始化配置
    ctx.ensure_object(dict)
    ctx.obj['config'] = init_config(config)


@cli.command()
@click.option('--host', type=str, default=None, help='监听地址')
@click.option('--port', type=int, default=None, help='HTTP API 端口')
@click.option('--tcp-port', type=int, default=None, help='HTTP TCP 端口')
@click.pass_context
def serve(ctx, host, port, tcp_port):
    """启动 Future OSS"""
    config = ctx.obj.get('config', get_config())
    
    # 命令行参数覆盖配置
    if host:
        config.set('HOST', host)
    if port:
        config.set('HTTP_API_PORT', port)
    if tcp_port:
        config.set('HTTP_TCP_PORT', tcp_port)
    
    log = Logger()
    log.info(f"Future OSS {__version__} 启动")
    log.info(f"监听地址：{config.host}:{config.http_api_port}")
    log.info(f"数据目录：{config.data_dir.absolute()}")
    log.info(f"插件仓库：{config.store_dir.absolute()}")

    plugin_mgr = PluginManager()
    plugin_mgr.load()
    plugin_mgr.start()

    log.info("就绪")

    def shutdown(sig, frame):
        log.info("停止中...")
        plugin_mgr.stop()
        log.info("已停止")
        raise SystemExit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        signal.pause()
    except AttributeError:
        import time
        while True:
            time.sleep(1)


@cli.command()
def version():
    """显示版本"""
    click.echo(f"Future OSS {__version__}")


@cli.command()
@click.pass_context
def info(ctx):
    """显示系统信息"""
    config = ctx.obj.get('config', get_config())
    click.echo(f"Future OSS {__version__}")
    click.echo(f"配置文件：{config._config_file or '无'}")
    click.echo(f"HTTP API 端口：{config.http_api_port}")
    click.echo(f"HTTP TCP 端口：{config.http_tcp_port}")
    click.echo(f"主机地址：{config.host}")
    click.echo(f"数据目录：{config.data_dir.absolute()}")
    click.echo(f"插件仓库：{config.store_dir.absolute()}")
    click.echo(f"日志级别：{config.log_level}")
    click.echo(f"权限检查：{'启用' if config.permission_check else '禁用'}")


def main():
    cli()


if __name__ == "__main__":
    main()
