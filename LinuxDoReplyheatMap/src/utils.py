import json
from datetime import datetime
from venv import logger

def parse_timestamp(timestamp_str):
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', ''))
    except Exception as e:
        logger.error(f"时间解析错误: {timestamp_str}, 错误: {e}")
        return None

def save_to_file(data, filename, mode='a'):
    with open(filename, mode, encoding='utf-8') as f:
        if isinstance(data, list):
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        else:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        f.flush() 