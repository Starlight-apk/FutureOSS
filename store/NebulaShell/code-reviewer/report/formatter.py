
    def __init__(self, format_type: str = "console"):
        self.format_type = format_type

    def format(self, result: dict) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("代码审查报告")
        lines.append("=" * 60)
        lines.append(f"扫描文件: {result['files_scanned']}")
        lines.append(f"发现问题: {result['total_issues']}")
        lines.append(f"扫描时间: {result['scan_time']}s")
        lines.append("")

        critical = [i for i in result['issues'] if i['severity'] == 'critical']
        warning = [i for i in result['issues'] if i['severity'] == 'warning']
        info = [i for i in result['issues'] if i['severity'] == 'info']

        lines.append(f"🔴 严重: {len(critical)}")
        lines.append(f"🟡 警告: {len(warning)}")
        lines.append(f"🔵 提示: {len(info)}")
        lines.append("")

        if critical:
            lines.append("严重问题:")
            for issue in critical:
                lines.append(f"  - {issue['file']}:{issue['line']} - {issue['message']}")
            lines.append("")

        if warning:
            lines.append("警告:")
            for issue in warning[:10]:                lines.append(f"  - {issue['file']}:{issue['line']} - {issue['message']}")
            if len(warning) > 10:
                lines.append(f"  ... 还有 {len(warning) - 10} 个警告")
            lines.append("")

        lines.append("=" * 60)
        return '\n'.join(lines)

    def _format_json(self, result: dict) -> str:
