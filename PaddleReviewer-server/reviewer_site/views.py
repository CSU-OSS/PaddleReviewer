from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from typing import List
import logging
from models.llms import model
from models.plms.inference.CRInferenceModel import cr_model

# 获取一个logger对象
logger = logging.getLogger('mylogger')

def hellowWorld(request):
    return HttpResponse("This is a server for commit message generation.")

@csrf_exempt
def generate_cr(request):
    result = {}
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
            print(request_data)
            model_name = request_data.get('model_name')
            api_key = request_data.get('api_key')
            base_url = request_data.get('base_url')
            temperature = request_data.get('temperature')
            max_tokens = request_data.get('max_tokens')
            mods = request_data.get('mods')
            diffs = ""
            for mod in mods:
                diffs += mod['diff'] + "\n"
            context = request_data.get('context')
            review = model.create_review(diffs, context, model_name, temperature, max_tokens, api_key, base_url)
            result = {"result": 1, "review": review}
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    return HttpResponse(json.dumps(result), content_type='application/json;charset=utf-8')

@csrf_exempt
def generate_cr_with_pllms(request):
    
    result = {}
    if request.method == 'GET':
        result = {"error": "Please use POST method"}
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
            print(request_data)
            mods = request_data.get('mods')
            granularity = request_data.get('granularity')
            if granularity == 'file':
                result_list = [cr_model.predict_review(mod['diff']) for mod in mods]
                result = result_list
            else:
                diffs = ""
                for mod in mods:
                    diffs += mod['diff'] + "\n"
                result = cr_model.predict_review(diffs)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        temperature = request_data.get('temperature')
        max_tokens = request_data.get('max_tokens')
    
    return HttpResponse(json.dumps(result), content_type='application/json;charset=utf-8')

        
