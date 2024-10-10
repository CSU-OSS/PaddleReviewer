import sys
import subprocess
import os
import re
import gradio as gr
import json
import time

sys.path.append("D:\\projectpy\\PaddleReviewer\\PaddleReviewer-server")
sys.path.append("D:\\projectpy\\PaddleReviewer\\PaddleReviewer-web")
from models.plms.inference.CRInferenceModel import cr_model
from ModelConfig import ModelConfig
from models.llms import model


def quickstart(diffs: str, model_config: ModelConfig):
    if model_config.method == 'llm':
        review = model.create_review(diffs,
                                     model_config.context,
                                     model_config.model_name,
                                     model_config.temperature,
                                     model_config.max_tokens,
                                     model_config.api_key,
                                     model_config.base_url)
        result = {"result": 1, "review": review} # name = diff
    else:
        result = cr_model.predict_review(diffs)  # name = diff
    return result


def get_commit_changes(repo_name):
    try:
        result = subprocess.run(['git', '-C', repo_name, 'show', '--stat', '-1'], check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError:
        return "获取提交更改信息失败。"


def get_diff(repo_name, num_commits):
    changes = []
    try:
        for i in range(num_commits):
            if i == 0:
                result = subprocess.run(['git', '-C', repo_name, 'diff', 'HEAD~1', 'HEAD'], check=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                commit_label = 'HEAD~1 vs HEAD'
            else:
                result = subprocess.run(['git', '-C', repo_name, 'diff', f'HEAD~{i + 1}', f'HEAD~{i}'], check=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                commit_label = f'HEAD~{i + 1} vs HEAD~{i}'

            diff_output = result.stdout.decode('utf-8')
            change = parse_diff(diff_output)
            changes.append({
                'commit': commit_label,
                'changes': change
            })
    except subprocess.CalledProcessError:
        return "获取差异信息失败。"

    return changes


def parse_diff(diff_output):
    changes = []
    current_file = None
    current_diff = []

    for line in diff_output.splitlines():
        if line.startswith("diff --git"):
            if current_file is not None:
                changes.append({
                    'old_path': current_file['old_path'],
                    'new_path': current_file['new_path'],
                    'diff': '\n'.join(current_diff)
                })
                current_diff = []

            match = re.search(r'diff --git a/(.+) b/(.+)', line)
            if match:
                current_file = {
                    'old_path': match.group(1),
                    'new_path': match.group(2)
                }
        elif current_file is not None and not line.startswith('---') and not line.startswith('+++'):
            current_diff.append(line)

    if current_file is not None:
        changes.append({
            'old_path': current_file['old_path'],
            'new_path': current_file['new_path'],
            'diff': '\n'.join(current_diff)
        })

    return changes


def generate_reviews(commit_changes, diff_output, model_config):
    results = {}
    for change in diff_output:
        commit_label = change['commit']
        results[commit_label] = []

        for file_change in change['changes']:
            old_path = file_change['old_path']
            new_path = file_change['new_path']
            diff_content = file_change['diff']
            print("11111111111111"+diff_content+"11111111111111111111111111111111111111")
            result = quickstart(diff_content, model_config)

            if result['result'] == 1:
                results[commit_label].append({
                    'old_path': old_path,
                    'new_path': new_path,
                    'result': result
                })

    return results


def process_input(input_text, method, model_name, api_key, base_url, temperature, max_output_tokens, num_commits):
    progress = gr.Progress()
    context = ""
    model_config: ModelConfig = ModelConfig(
        method,
        model_name,
        temperature,
        max_output_tokens,
        api_key,
        base_url,
        context
    )

    # 如果输入是代码段，直接调用 quickstart 方法
    if not (input_text.startswith("http://") or input_text.startswith("https://")):
        progress(0, desc="代码分析中...")  # 显示处理代码的进度
        result = quickstart(input_text, model_config)
        progress(100, desc="处理完成！")
        return (f"你输入的代码是: {input_text}<br><br>"
                f"<strong>处理结果:</strong><br><span style='color: green;'>{json.dumps(result, ensure_ascii=False)}</span>")

    # 否则，如果输入是 Git URL，进行克隆仓库
    repo_name = input_text.split('/')[-1].replace('.git', '')

    if not os.path.exists(repo_name):
        progress(0, desc="代码克隆中...")  # 显示克隆仓库中的进度
        try:
            subprocess.run(['git', 'clone', input_text], check=True)
            progress(100, desc="克隆完成！正在分析代码...")
        except subprocess.CalledProcessError:
            return "克隆仓库失败，请检查URL是否正确。"

    commit_changes = get_commit_changes(repo_name)

    progress(0, desc="代码分析中...")  # 显示分析代码的进度
    diff_output = get_diff(repo_name, num_commits)
    results = generate_reviews(commit_changes, diff_output, model_config)

    combined_results = []
    for commit, changes in results.items():
        if len(changes) > 0:
            combined_results.append(f"commit {commit} :")
            for r in changes:
                combined_results.append(f"{r['old_path']} -> {r['new_path']} : {json.dumps(r['result'])}")
        else:
            combined_results.append(f"commit {commit}")

    additional_info = f"<strong>提交信息：</strong><br>{commit_changes}<br><br>" \
                      f"<strong>差异信息：</strong><br>{json.dumps(diff_output, ensure_ascii=False)}<br>"

    # 将处理结果的内容用绿色表示
    results_display = "\n".join(combined_results)
    results_display = results_display.replace("\n", "<br>")

    processed_results = f"<strong>处理结果：</strong><br><span style='color: green;'>{results_display}</span>"

    progress(100, desc="分析完成！")
    return (
        f"<strong>项目路径:</strong> {os.path.abspath(repo_name)}<br>{additional_info}<br>{processed_results}"
    )

# 接口创建函数



method_options = ["llm", "ft"]

demo = gr.Interface(
    fn=process_input,
    inputs=[
        gr.Textbox(label="Git URL 或代码", placeholder="请输入 Git 仓库 URL 或代码段...", value="https://gitee.com/feeaarr/springooo.git", lines=2),
        gr.Dropdown(choices=method_options, label="选择方法", value="llm"),
        gr.Textbox(label="模型名称", placeholder="请输入 模型名称", value="deepseek-chat", lines=1),
        gr.Textbox(label="API_KEY", placeholder="请输入 API_KEY", value="sk-b045af0304a14a52b428dee2488e4944", lines=1),
        gr.Textbox(label="BASE_URL", placeholder="请输入 BASE_URL", value="https://api.deepseek.com/", lines=1),
        gr.Slider(minimum=0, maximum=1, step=0.1, label="选择温度", value=0.9),
        gr.Number(label="最大输出token数量", value=500),
        gr.Slider(minimum=1, maximum=10, step=1, label="比较前多少个版本", value=1)
    ],
    outputs="html",
    title="基于飞桨的代码审查意见生成助手处理工具",
    description="输入 Git 仓库 URL 或代码段，选择处理方法，获取最近提交的更改和差异。",
    theme="Soft",
    css=f"""
        .footer {{ display: none; }}
        .gradio-container {{
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            padding: 20px;
            height: 100vh; /* 设置容器高度以适应背景 */
            # background-image: url('https://cn.bing.com/images/search?view=detailV2&ccid=2KUBypHr&id=D22F4B4F1FFF397FA9CCA24C2AE82069B050F097&thid=OIP.2KUBypHrEr_a399J3b3-dAHaLJ&mediaurl=https%3A%2F%2Fbpic.588ku.com%2Fback_origin_min_pic%2F19%2F04%2F12%2Fd93eb197f39c59040f8bf6f112ec084a.jpg!%2Ffw%2F750%2Fquality%2F99%2Funsharp%2Ftrue%2Fcompress%2Ftrue&exph=1129&expw=750&q=%E8%83%8C%E6%99%AF%E5%9B%BE%E7%A7%91%E6%8A%80%E6%84%9F&simid=608040775847707705&form=IRPRST&ck=D91DBFE6F26D7257303A097425C8A704&selectedindex=32&itb=0&cw=1339&ch=664&ajaxhist=0&ajaxserp=0&vt=0&sim=11'); /* 使用网络上的图片URL */
            # background-size: cover; /* 使背景图像覆盖整个容器 */
            # background-position: center; /* 使背景图像居中 */
        }}
    """
)



demo.launch()
