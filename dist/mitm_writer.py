from mitmproxy import http
import json
import os
import datetime

ALLOWED_DOMAINS = os.environ.get('ALLOWED_DOMAINS', '')
ALLOWED_DOMAINS = [d.strip() for d in ALLOWED_DOMAINS.split(',') if d.strip()]

def response(flow: http.HTTPFlow):
    try:
        # 域名过滤
        if ALLOWED_DOMAINS and flow.request.host not in ALLOWED_DOMAINS:
            return
        text = flow.response.text
        try:
            data = json.loads(text)
        except Exception:
            return  # 不是合法JSON，跳过
        # 格式化时间戳为年月日时分秒
        ts = flow.response.timestamp_end
        if ts:
            dt_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        else:
            dt_str = ''
        captured_item = {
            "url": flow.request.url,
            "method": flow.request.method,
            "host": flow.request.host,
            "path": flow.request.path,
            "status_code": flow.response.status_code,
            "response_data": data,
            "timestamp": dt_str
        }
        with open('captured_data.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(captured_item, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"处理响应时出错: {e}") 