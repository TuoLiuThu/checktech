import os
import datetime
import pytz
import google.generativeai as genai
import time

# 1. 配置 API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. 配置参数
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# 3. 初始化模型 (修复 Tool 参数)
# 错误原因：google_search_retrieval 已改名为 google_search
# 修复方法：使用字典列表格式 tools=[{"google_search": {}}]
def get_model():
    model_name = "gemini-2.5-flash" # 既然这个模型没有报404，我们就锁定它
    
    print(f"正在初始化模型: {model_name} ...")
    
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            # 【关键修改在这里】
            # 旧写法: tools='google_search_retrieval' (报错 400)
            # 新写法: 如下所示
            tools=[{"google_search": {}}] 
        )
        return model, model_name
    except Exception as e:
        print(f"初始化出错: {e}")
        return None, None

model, used_model_name = get_model()
print(f"模型初始化完成: {used_model_name}")

def get_beijing_time():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.datetime.now(tz).strftime('%Y年%m月%d日 %H:%M')

def generate_report():
    current_time = get_beijing_time()
    print(f"开始生成日报，当前时间: {current_time}")

    prompt = f"""
    Current Time (Beijing): {current_time}
    
    Role: You are an expert AI Analyst.
    Task: Search the web for AI news in the past 24 hours and generate a single-file HTML5 Dashboard.
    
    【核心要求】
    1.  **真实链接**: 必须提供 Search Tool 找到的真实 URL。
    2.  **替代策略**: 如果搜不到某位科学家的推特，请搜索报道了该推特的新闻文章。
    3.  **空状态**: 如果某人无动态，必须显示 "今日无动态"。
    
    【监测名单】
    * DeepMind: Demis Hassabis, Jeff Dean
    * OpenAI: Sam Altman, Greg Brockman, Noam Brown
    * Meta: Yann LeCun, Thomas Scialom
    * Anthropic: Dario Amodei
    
    【HTML 输出规范】
    1.  使用 Tailwind CSS (CDN)。
    2.  深色模式 (Dark Mode, Slate-900)。
    3.  包含 JavaScript 实现 Tab 切换。
    4.  所有文字为简体中文。
    
    Output ONLY the raw HTML code. Start with <!DOCTYPE html>.
    """
    
    try:
        # 这里的 request_options 可能需要处理，但通常 SDK 会自动处理
        response = model.generate_content(prompt)
        html_content = response.text
        # 清理 Markdown 标记
        html_content = html_content.replace("```html", "").replace("```", "").strip()
        return html_content
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"<html><body><h1>生成失败</h1><p>错误信息: {e}</p><p>模型: {used_model_name}</p></body></html>"

if __name__ == "__main__":
    if model:
        html = generate_report()
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Report generated successfully.")
    else:
        print("模型初始化失败，无法生成。")
