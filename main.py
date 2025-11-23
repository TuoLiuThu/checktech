import os
import datetime
import pytz
import google.generativeai as genai
import time

# 1. 配置 API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. 配置参数 (针对 Flash 模型优化)
# Flash 模型不需要过高的 Temperature，0.7 较为平衡
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# 3. 初始化模型 (关键：使用免费且稳定的 Flash 模型)
# gemini-1.5-flash 拥有每日 1500 次的免费额度，且支持搜索
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    tools='google_search_retrieval' # 强制开启联网搜索
)

def get_beijing_time():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.datetime.now(tz).strftime('%Y年%m月%d日 %H:%M')

def generate_report():
    current_time = get_beijing_time()
    print(f"开始生成日报，当前时间: {current_time}")
    print("正在调用 Gemini 1.5 Flash 进行联网搜索... (免费版)")

    # 为了保证 Flash 模型也能输出高质量内容，Prompt 需要更加具体
    prompt = f"""
    Current Time (Beijing): {current_time}
    
    Role: You are an expert AI Analyst.
    Task: Search the web for AI news in the past 24 hours and generate a single-file HTML5 Dashboard.
    
    【关键要求 - 请严格执行】
    1.  **真实链接**: 必须提供 Search Tool 找到的真实 URL。不要编造链接。
    2.  **替代策略**: 如果搜不到某位科学家的推特，请搜索报道了该推特的新闻文章并链接到新闻。
    3.  **空状态**: 如果某人无动态，必须显示 "今日无动态"，不要过滤掉他。
    
    【监测名单】
    * DeepMind: Demis Hassabis, Jeff Dean
    * OpenAI: Sam Altman, Greg Brockman, Noam Brown
    * Meta: Yann LeCun, Thomas Scialom
    * Anthropic: Dario Amodei
    
    【HTML 输出规范】
    1.  使用 Tailwind CSS (通过 CDN)。
    2.  深色模式 (Dark Mode, Slate-900)。
    3.  包含 JavaScript 实现 Scientist 板块的 Tab 切换功能。
    4.  所有可见文字必须是**简体中文**。
    
    Output ONLY the raw HTML code. Start with <!DOCTYPE html>.
    """
    
    try:
        response = model.generate_content(prompt)
        html_content = response.text
        
        # 清理 Markdown 标记
        html_content = html_content.replace("```html", "").replace("```", "").strip()
        
        return html_content
    except Exception as e:
        print(f"Error occurred: {e}")
        # 错误处理页面
        return f"""
        <html>
        <body style="background:#0f172a; color:white; padding:50px; text-align:center;">
            <h1>生成遇到问题</h1>
            <p>错误信息: {e}</p>
            <p>请检查 GitHub Secrets 中的 API Key 是否正确。</p>
        </body>
        </html>
        """

if __name__ == "__main__":
    html = generate_report()
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Report generated and saved to index.html")
