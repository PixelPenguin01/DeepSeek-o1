import streamlit as st
import os
import json
import time
import requests
from dotenv import load_dotenv
import logging

# 加载 .env 文件中的环境变量
load_dotenv()

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

logging.basicConfig(level=logging.INFO)

def make_api_call(messages, max_tokens, is_final_answer=False):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }
    
    for attempt in range(3):
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
            response.raise_for_status()
            response_json = response.json()
            content = response_json['choices'][0]['message']['content']
            logging.info(f"API Response: {content}")  # 添加日志
            
            try:
                parsed_content = json.loads(content)
                if isinstance(parsed_content, dict) and all(key in parsed_content for key in ['title', 'content', 'next_action']):
                    return parsed_content
                else:
                    raise ValueError("API返回的JSON格式不符合预期")
            except json.JSONDecodeError:
                # 如果无法解析为JSON，尝试从原始响应中提取有用信息
                return {
                    "title": "API响应解析错误",
                    "content": f"原始响应: {content}\n\n请检查并重新格式化以上内容。",
                    "next_action": "continue"
                }
        except Exception as e:
            logging.error(f"API调用错误 (尝试 {attempt + 1}/3): {str(e)}")
            if attempt == 2:
                if is_final_answer:
                    return {"title": "错误", "content": f"3次尝试后无法生成最终答案。错误: {str(e)}"}
                else:
                    return {"title": "错误", "content": f"3次尝试后无法生成步骤。错误: {str(e)}", "next_action": "continue"}
            time.sleep(1)  # 重试前等待1秒

def generate_response(prompt):
    messages = [
        {"role": "system", "content": """你是一个具有高级推理能力的专家AI助手。你的任务是提供详细的、逐步的思考过程解释。对于每一步：

1. 提供一个清晰、简洁的标题，描述当前的推理阶段。
2. 在内容部分详细阐述你的思考过程。
3. 决定是继续推理还是提供最终答案。

请务必以JSON格式响应，严格遵循以下结构：
{
    "title": "步骤标题",
    "content": "详细的思考过程",
    "next_action": "continue或final_answer"
}

请确保你的每个响应都是有效的JSON，并包含上述所有字段。
"""},
        {"role": "user", "content": prompt},
        {"role": "assistant",
         "content": "谢谢！我现在将按照指示逐步思考，从分解问题开始。"}
    ]

    steps = []
    step_count = 1
    total_thinking_time = 0

    while True:
        start_time = time.time()
        step_data = make_api_call(messages, 4000)
        end_time = time.time()
        thinking_time = end_time - start_time
        total_thinking_time += thinking_time

        # 检查步骤是否有实质性变化
        if steps and steps[-1][1] == step_data['content']:
            logging.warning("检测到重复步骤，跳转到最终答案")
            break

        # 修改这部分来处理内容
        content = step_data['content']
        
        # 转义Markdown特殊字符
        content = content.replace("_", "\\_").replace("*", "\\*").replace("#", "\\#")
        
        # 检查内容是否包含代码块
        if "```" in content:
            # 使用正则表达式提取代码块
            import re
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', content, re.DOTALL)
            for i, code in enumerate(code_blocks):
                # 替换原始的代码块为格式化的版本
                lang = re.findall(r'```(\w+)', content)[i] if re.findall(r'```(\w+)', content) else ""
                formatted_code = f"```{lang}\n{code.strip()}\n```"
                content = content.replace(f"```{lang}\n{code}\n```", formatted_code)

        steps.append((f"步骤 {step_count}: {step_data.get('title', '未知步骤')}", content, thinking_time))

        messages.append({"role": "assistant", "content": json.dumps(step_data)})

        if step_data.get('next_action') == 'final_answer':
            break

        step_count += 1

        # 限制最大步骤数
        if step_count > 10:
            logging.warning("达到最大步骤数，强制结束")
            break

        yield steps, None  # 我们在最后才yield总时间

    # 生成最终答案
    messages.append({"role": "user", "content": "请根据你上面的推理提供最终答案。"})

    start_time = time.time()
    final_data = make_api_call(messages, 4000, is_final_answer=True)
    end_time = time.time()
    thinking_time = end_time - start_time
    total_thinking_time += thinking_time

    steps.append(("最终答案", final_data['content'], thinking_time))

    yield steps, total_thinking_time

def local_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"无法找到样式文件：{file_name}")
    except Exception as e:
        st.error(f"读取样式文件时发生错误：{str(e)}")

def main():
    st.set_page_config(page_title="DeepSeek-o1", page_icon="🧠", layout="wide")
    
    # 加载自定义CSS
    local_css("style.css")
    
    # 使用HTML和CSS来美化标题
    st.markdown("""
    <h1 style='text-align: center; color: #4A90E2;'>
        <span style='font-size: 1.5em;'>🧠</span> DeepSeek-o1
    </h1>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align: center; font-style: italic; color: #666;'>
    这是一个使用DeepSeek模型创建推理链以提高输出准确性的原型。准确性尚未经过正式评估。
    </p>
    """, unsafe_allow_html=True)

    # 使用列来创建居中的输入区域
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        user_query = st.text_input("输入你的问题:", placeholder="例如，把一头大象放进冰箱里要几步？")
        submit_button = st.button("发送", key="submit")

    if user_query and submit_button:
        with st.spinner("正在生成回答..."):
            response_container = st.empty()
            time_container = st.empty()

            for steps, total_thinking_time in generate_response(user_query):
                with response_container.container():
                    for i, (title, content, thinking_time) in enumerate(steps):
                        if title.startswith("最终答案"):
                            st.markdown(f"<h3 style='color: #4A90E2;'>{title}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<div class='final-answer'>{content}</div>", unsafe_allow_html=True)
                        else:
                            with st.expander(title, expanded=True):
                                st.markdown(f"<div class='step-content'>{content}</div>", unsafe_allow_html=True)
                                st.markdown(f"<p class='thinking-time'>思考时间: {thinking_time:.2f} 秒</p>", unsafe_allow_html=True)

                if total_thinking_time is not None:
                    time_container.markdown(f"<p class='total-time'><strong>总思考时间:</strong> {total_thinking_time:.2f} 秒</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()