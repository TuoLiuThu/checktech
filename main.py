import os
import datetime
import pytz
import google.generativeai as genai

# 配置 API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 配置模型，使用搜索工具
generation_config = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp", # 使用最新的 Flash 模型，速度快且联网能力强
    generation_config=generation_config,
    tools='google_search_retrieval' # 强制开启搜索
)

def get_beijing_time():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.datetime.now(tz).strftime('%Y年%m月%d日 %H:%M')

def generate_report():
    current_time = get_beijing_time()
    
    # 你的 Prompt，经过深度优化以确保链接准确
    prompt = f"""
    Current Time (Beijing): {current_time}
    
    任务：你是一个全栈工程师。请联网搜索过去24小时的AI行业动态，生成一个单文件 HTML5 网页。
    
    【核心要求 - 关于链接】
    1. 你必须使用 Google Search 找到的**真实 URL**。
    2. 如果找不到某位科学家的推特原文，请**务必**链接到报道该推特的新闻页面。
    3. 严禁生成死链接（如 placeholder）。
    
    【内容板块】
    1. 顶尖科学家 (DeepMind: Demis/Jeff, OpenAI: Sam/Greg, Meta: Yann/Jason, Anthropic: Dario)。
    2. 深度媒体 (The Information, SemiAnalysis)。
    3. 产业大事件 (融资, GPU, 离职)。
    4. 前沿论文 (arXiv)。
    
    【HTML 结构要求】
    1. 使用 Tailwind CSS (CDN)。
    2. 深色模式 (Dark Mode)。
    3. 必须包含 JavaScript 实现 Tab 切换（DeepMind/OpenAI/Meta/Anthropic）。
    4. 直接输出 HTML 代码，不要 Markdown 标记。
    5. 在 Header 显示“更新时间：{current_time}”。
    
    请开始生成 HTML：
    """
    
    try:
        response = model.generate_content(prompt)
        html_content = response.text
        
        # 清理可能存在的 Markdown 标记
        html_content = html_content.replace("```html", "").replace("```", "")
        
        return html_content
    except Exception as e:
        print(f"Error: {e}")
        return f"<h1>生成失败</h1><p>{e}</p>"

if __name__ == "__main__":
    html = generate_report()
    
    # 将生成的内容写入 index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Report generated successfully.")
