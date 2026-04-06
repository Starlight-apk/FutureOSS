"""CLI 入口"""
import click
import signal

from oss import __version__
from oss.logger.logger import Logger
from oss.plugin.manager import PluginManager


@click.group()
def cli():
    """Future OSS - 一切皆为插件"""
    pass


@cli.command()
def serve():
    """启动 Future OSS"""
    log = Logger()
    log.info(f"Future OSS {__version__} 启动")

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


def main():
    cli()


if __name__ == "__main__":
    main()
