import os
import datetime
import pytz
from google import genai
from google.genai import types

# 1. 配置客户端 (使用新版 SDK)
# API Key 从环境变量中自动读取
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_beijing_time():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.datetime.now(tz).strftime('%Y年%m月%d日 %H:%M')

def generate_report():
    current_time = get_beijing_time()
    print(f"开始生成日报，当前时间: {current_time}")
    print("正在调用 Gemini 2.0 Flash (New SDK) 进行联网搜索...")

    # 2. 配置搜索工具 (新版语法)
    # 针对 Gemini 2.0/2.5，必须使用 google_search 而非旧版的 retrieval
    tool_config = [
        types.Tool(google_search=types.GoogleSearch())
    ]

    # 3. 配置生成参数
    generate_config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
        tools=tool_config,
        system_instruction="你是一个专业的AI行业情报分析师。你的任务是搜索最新信息并生成HTML日报。"
    )

    prompt = f"""
    Current Time (Beijing): {current_time}
    
    Task: Search the web for AI news in the past 24 hours and generate a single-file HTML5 Dashboard.
    
    【关键要求】
    1. **必须联网**: 使用 Google Search 工具获取真实信息。
    2. **真实链接**: 每个新闻必须附带 Search Tool 返回的原始 URL。
    3. **监测名单**: DeepMind (Demis Hassabis), OpenAI (Sam Altman), Meta (Yann LeCun), Anthropic (Dario Amodei)。
    4. **空状态**: 如果某人无动态，必须显示“今日无动态”。
    
    【HTML 输出规范】
    1. 使用 Tailwind CSS (CDN)。
    2. 深色模式 (Dark Mode, Slate-900)。
    3. 包含 JavaScript 实现 Tab 切换。
    4. 所有文字为简体中文。
    
    Output ONLY the raw HTML code. Start with <!DOCTYPE html>.
    """
    
    try:
        # 4. 调用模型 (Gemini 2.0 Flash)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=generate_config
        )
        
        html_content = response.text
        # 清理可能存在的 Markdown 标记
        html_content = html_content.replace("```html", "").replace("```", "").strip()
        return html_content

    except Exception as e:
        print(f"生成出错: {e}")
        return f"<html><body><h1>生成失败</h1><p>{e}</p></body></html>"

if __name__ == "__main__":
    html = generate_report()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Report generated successfully.")
