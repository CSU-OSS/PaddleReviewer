from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from typing import List
import logging

# 获取一个logger对象
logger = logging.getLogger('mylogger')

def hellowWorld(request):
    return HttpResponse("This is a server for commit message generation.")

@csrf_exempt
def generate_cr(request):
    logger.info(request.method)
    rep_dict = {"hello": "hello"}
    result = json.dumps(rep_dict)
    return HttpResponse(result, content_type='application/json;charset=utf-8')

#
# @csrf_exempt
# def generate_commit_message(request):
#     logger.info(request.method)
#     if request.method == 'GET':
#         diff = request.GET.get('diff')
#         temperature = request.GET.get('temperature')
#         max_tokens = request.GET.get('max_tokens')
#         historyMessage: List[str] = []
#         if request.GET.get('historyMessage') is not None:
#             historyMessage = json.loads(request.GET.get('historyMessage'))
#         needRec = False
#         if request.GET.get('needRec') is not None:
#             needRec = request.GET.get('needRec')
#             needRec = str_to_bool(needRec)
#
#     elif request.method == 'POST':
#         try:
#             request_data = json.loads(request.body)
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)
#
#         # 获取'diff'字段
#         diff = request_data.get('diff')
#         if not diff:
#             return JsonResponse({'error': 'No diff provided'}, status=400)
#         temperature = request_data.get('temperature')
#         max_tokens = request_data.get('max_tokens')
#         # 获取'history'字段
#         historyMessage: List[str] = request_data.get('historyMessage')
#         if not historyMessage:
#             historyMessage = []
#         # 获取needRec
#         needRec = request_data.get('needRec')
#
#     temperature = 0.9 if temperature is None else float(temperature)
#     max_tokens = 100 if max_tokens is None else int(max_tokens)
#     #False if needRec is None else bool(needRec)
#     # 调用模型生成commit message
#     rep_dict = {}
#     blue_llm = CmgModel(temperature=temperature, max_new_tokens=max_tokens)
#     rep_dict['commit_message'] = blue_llm.get_commit_messages(diff, historyMessage, needRec)
#     result = json.dumps(rep_dict)
#     return HttpResponse(result, content_type='application/json;charset=utf-8')
#
# @csrf_exempt
# def generate_commit_message_with_history(request):
#     logger.info(request.method)
#     if request.method == 'GET':
#         diff = request.GET.get('diff')
#         historyMessage: List[str] = []
#         if request.GET.get('historyMessage') is not None:
#             historyMessage = json.loads(request.GET.get('historyMessage'))
#
#         if not diff:
#             return JsonResponse({'error': 'No diff provided'}, status=400)
#         temperature = request.GET.get('temperature')
#         max_tokens = request.GET.get('max_tokens')
#
#     elif request.method == 'POST':
#         try:
#             request_data = json.loads(request.body)
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)
#
#         # 获取'diff'字段
#         diff = request_data.get('diff')
#         if not diff:
#             return JsonResponse({'error': 'No diff provided'}, status=400)
#
#         # 获取'history'字段
#         historyMessage: List[str] = request_data.get('historyMessage')
#         if not historyMessage:
#             historyMessage = []
#         temperature = request_data.get('temperature')
#         max_tokens = request_data.get('max_tokens')
#     # 调用模型生成commit message
#     temperature = 0.9 if temperature is None else float(temperature)
#     max_tokens = 15 if max_tokens is None else int(max_tokens)
#     rep_dict = {}
#     blue_llm = CmgModel(temperature=temperature, max_new_tokens=max_tokens)
#     rep_dict['commit_message'] = blue_llm.get_commit_message_with_history_message(diff, historyMessage)
#     result = json.dumps(rep_dict)
#     return HttpResponse(result, content_type='application/json;charset=utf-8')
