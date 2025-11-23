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

# 3. 初始化模型 (使用最新的 Flash 2.5)
# 依据 2025 年 11 月状态，gemini-1.5-flash 已弃用，必须使用 2.5 或 2.0
def get_model():
    # 优先尝试 2.5 Flash (最新活跃版)
    model_names = [
        "gemini-2.5-flash", 
        "gemini-2.0-flash", 
        "gemini-1.5-flash-002" # 最后尝试具体的旧版本号
    ]
    
    for name in model_names:
        try:
            print(f"尝试连接模型: {name} ...")
            model = genai.GenerativeModel(
                model_name=name,
                generation_config=generation_config,
                tools='google_search_retrieval'
            )
            return model, name
        except Exception as e:
            print(f"模型 {name} 不可用，尝试下一个...")
            continue
    # 如果都失败，强制返回一个默认值让主程序报错
    return genai.GenerativeModel("gemini-2.5-flash"), "gemini-2.5-flash"

model, used_model_name = get_model()
print(f"成功锁定模型: {used_model_name}")

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
    
    【核心要求 - 保持不变】
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
        response = model.generate_content(prompt)
        html_content = response.text
        # 清理 Markdown 标记
        html_content = html_content.replace("```html", "").replace("```", "").strip()
        return html_content
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"<html><body><h1>生成失败</h1><p>错误信息: {e}</p><p>当前尝试模型: {used_model_name}</p></body></html>"

if __name__ == "__main__":
    html = generate_report()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Report generated successfully.")
