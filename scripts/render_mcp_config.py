"""生成本机专用的 MCP 配置，输出时隐藏包含凭据的内容。"""
import json
import os
from pathlib import Path
from mcd_mcp import connection_settings


def write_local_config(root):
    url, token = connection_settings()
    directory = Path(root) / '.local'
    if directory.is_symlink():
        raise ValueError('Refusing a symlinked credential directory')
    directory.mkdir(mode=0o700, exist_ok=True)
    target = directory / 'mcp.json'
    data = {'mcpServers': {'mcd-mcp': {'type': 'streamablehttp', 'url': url,
                                    'headers': {'Authorization': 'Bearer ' + token}}}}
    # 仅新建文件，已有文件或符号链接都会被拒绝，避免覆盖原配置。
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return target


def main():
    try:
        target = write_local_config(Path(__file__).resolve().parents[1])
    except Exception as error:
        print(f'Local configuration not written ({type(error).__name__}). Check environment variables and whether .local/mcp.json already exists.')
        return 1
    print(f'Wrote private configuration: {target}. Import it locally; do not publish it.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
