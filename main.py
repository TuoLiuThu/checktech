import os
import datetime
import pytz
import google.generativeai as genai
from google.generativeai import protos # 关键：引入底层协议库

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

# 3. 初始化模型 (使用底层 Protos 修复工具调用)
def get_model():
    # 既然 gemini-2.5-flash 之前没有报 404，说明模型存在，我们继续用它
    model_name = "gemini-2.5-flash" 
    
    print(f"正在初始化模型: {model_name} ...")
    
    # 【关键修复】
    # 使用 protos.Tool 直接构建工具对象，避免字典被误判为函数定义
    # 这是目前最稳妥的开启搜索的方法
    search_tool = protos.Tool(
        google_search=protos.GoogleSearch()
    )

    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            tools=[search_tool] # 传入工具对象列表
        )
        return model, model_name
    except Exception as e:
        print(f"初始化出错: {e}")
        return None, None

model, used_model_name = get_model()

def get_beijing_time():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.datetime.now(tz).strftime('%Y年%m月%d日 %H:%M')

def generate_report():
    if not model:
        return "<html><body><h1>初始化失败</h1><p>无法连接到模型</p></body></html>"

    current_time = get_beijing_time()
    print(f"开始生成日报，当前时间: {current_time}")
    print(f"使用模型: {used_model_name}")

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
        response = model.generate_content(prompt)
        html_content = response.text
        # 清理 Markdown 标记
        html_content = html_content.replace("```html", "").replace("```", "").strip()
        return html_content
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"<html><body><h1>生成失败</h1><p>错误信息: {e}</p><p>模型: {used_model_name}</p></body></html>"

if __name__ == "__main__":
    html = generate_report()
    # 无论成功失败，都写入文件，方便在网页查看错误信息
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Process finished.")
