"""CLI 入口"""
import click
import signal
import os
import random
import hashlib

from oss import __version__
from oss.logger.logger import Logger
from oss.plugin.manager import PluginManager
from oss.config import init_config, get_config
from oss.easter_eggs import (
    get_fortune, 
    get_quote, 
    get_time_based_greeting,
    get_random_fact,
    print_easter_egg_art,
    generate_lucky_number,
    check_special_date,
    _check_developer_easter_egg,
    _get_hidden_config_message,
    check_file_signature,
    get_achievements,
    get_all_achievements_info,
    get_achievement_progress,
    print_achievements_list,
)


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
    
    # 小概率显示特殊问候
    if random.random() < 0.05:  # 5% 概率
        log.info("🌟 检测到开发者光环！")
    
    log.info(f"Future OSS {__version__} 启动")
    log.info(f"监听地址：{config.host}:{config.http_api_port}")
    log.info(f"数据目录：{config.data_dir.absolute()}")
    log.info(f"插件仓库：{config.store_dir.absolute()}")

    plugin_mgr = PluginManager()
    plugin_mgr.load()
    plugin_mgr.start()

    log.info("就绪")
    
    # 小概率显示额外消息
    if random.random() < 0.1:  # 10% 概率
        log.info(get_fortune())

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
def fortune(ctx):
    """获取今日运势"""
    greeting = get_time_based_greeting()
    fortune_msg = get_fortune()
    special = check_special_date()
    
    click.echo(greeting)
    click.echo("")
    click.echo(f"🔮 {fortune_msg}")
    
    if special:
        click.echo("")
        click.echo(f"📅 {special}")
    
    # 小概率显示 ASCII 艺术
    if random.random() < 0.1:  # 10% 概率
        click.echo("")
        print_easter_egg_art()


@cli.command()
def quote():
    """获取名人名言"""
    author, text = get_quote()
    click.echo(f'"{text}"')
    click.echo(f" — {author}")


@cli.command()
def fact():
    """获取随机冷知识"""
    click.echo(get_random_fact())


@cli.command()
def lucky():
    """获取今日幸运数字"""
    number = generate_lucky_number()
    click.echo(f"🍀 今日幸运数字：{number}")


@cli.command(hidden=True)
def surprise():
    """隐藏命令：惊喜彩蛋"""
    surprises = [
        "🎉 你发现了隐藏命令！",
        "🥚 彩蛋猎手就是你！",
        "🌟 探索精神值得赞赏！",
        "🎁 这是给你的小惊喜！",
    ]
    click.echo(random.choice(surprises))
    click.echo("")
    click.echo(f"💡 提示：试试 'oss fortune' 或 'oss quote'")


@cli.command(hidden=True)
@click.pass_context
def achievements(ctx):
    """隐藏命令：查看成就列表"""
    print_achievements_list()


@cli.command(hidden=True)
@click.argument('text', required=False)
def hash(text):
    """隐藏命令：生成秘密哈希
    
    如果输入文本的 MD5 哈希以 '0000' 开头，会触发超级彩蛋
    （几乎不可能自然发生）
    """
    from oss.easter_eggs import _generate_secret_hash
    
    if not text:
        text = str(random.randint(1, 1000000))
    
    result = _generate_secret_hash(text)
    click.echo(result)
    
    if "天选之子" in result:
        click.echo("")
        click.echo("🎁 获得成就：hash_master")
    else:
        click.echo("")
        click.echo("💡 提示：继续尝试，也许下次就是你了！")


@cli.command()
@click.pass_context
def info(ctx):
    """显示系统信息"""
    config = ctx.obj.get('config', get_config())
    
    # 检查开发者彩蛋
    config_path = str(config._config_file) if config._config_file else ""
    if _check_developer_easter_egg(config_path):
        click.echo("")
        click.echo(_get_hidden_config_message())
        click.echo("")
    
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
