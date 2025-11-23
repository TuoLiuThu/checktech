import os
import datetime
import pytz
import google.generativeai as genai
import time

# 1. 配置 API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. 配置 Gemini 3 Pro 参数
# 注意：Pro 模型通常需要更精确的 Temperature
generation_config = {
    "temperature": 1.0, 
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# 3. 初始化模型 (关键修改点)
# 如果 gemini-3-pro-preview 报错，请改回 gemini-1.5-pro
model = genai.GenerativeModel(
    model_name="gemini-3-pro-preview", 
    generation_config=generation_config,
    tools='google_search_retrieval' # 强制开启联网搜索
)

def get_beijing_time():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.datetime.now(tz).strftime('%Y年%m月%d日 %H:%M')

def generate_report():
    current_time = get_beijing_time()
    print(f"开始生成日报，当前时间: {current_time}")
    print("正在调用 Gemini 3 Pro 进行深度搜索和推理... (可能会比较慢，请耐心等待)")

    prompt = f"""
    Current Time (Beijing): {current_time}
    
    Role: You are an elite AI Industry Analyst using the advanced Gemini 3 Pro model.
    Task: Conduct a deep-dive web search for the past 24 hours of AI news and generate a single-file HTML5 Dashboard.
    
    【核心搜索策略 - Gemini 3 Pro 专用】
    1.  **Deep Search**: Do not just skim headlines. Verify sources. 
    2.  **Authentic Links**: You MUST provide direct URL links to the content (tweets/papers/articles). If a direct tweet link is unsearchable, link to a reputable tech news article discussing it.
    3.  **No Hallucinations**: If a scientist has no updates today, explicitly state "今日无动态" (No updates today).
    
    【监测名单 (Monitor List)】
    * **DeepMind**: Demis Hassabis, Jeff Dean
    * **OpenAI**: Sam Altman, Greg Brockman, Noam Brown (Reasoning)
    * **Meta**: Yann LeCun, Thomas Scialom
    * **Anthropic**: Dario Amodei
    
    【HTML 输出规范】
    1.  **Style**: Use Tailwind CSS (CDN). Dark Mode (Slate-900 background).
    2.  **Layout**: Dashboard style with 4 sections (Scientists, Media, Industry, Papers).
    3.  **Interactivity**: Include Vanilla JS for Tab switching in the Scientist section.
    4.  **Language**: All visible text must be in **Simplified Chinese**.
    
    Output ONLY the raw HTML code. Start with <!DOCTYPE html>.
    """
    
    try:
        # 增加重试机制，应对可能的网络波动
        response = model.generate_content(prompt)
        html_content = response.text
        
        # 清理 Markdown 标记
        html_content = html_content.replace("```html", "").replace("```", "").strip()
        
        return html_content
    except Exception as e:
        print(f"Error occurred: {e}")
        # 如果出错，生成一个简单的错误页面
        return f"""
        <html>
        <body style="background:#0f172a; color:white; font-family:sans-serif; padding:50px; text-align:center;">
            <h1>生成失败 (Generation Failed)</h1>
            <p>错误信息: {e}</p>
            <p>可能是 Gemini 3 Pro 配额超限 (429) 或模型名称不正确。</p>
            <p>请尝试在 main.py 中将模型换回 gemini-1.5-flash。</p>
        </body>
        </html>
        """

if __name__ == "__main__":
    html = generate_report()
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Report generated and saved to index.html")
