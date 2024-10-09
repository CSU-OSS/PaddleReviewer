from openai import OpenAI

def create_review(code_diff, context, model_name, temperature, max_tokens, api_key, base_url):
    prompt = generate_review_prompt(code_diff, context)
    response = get_chatgptapi_response(prompt, model_name, temperature, max_tokens, api_key, base_url)
    return response

def few_shot_prompt():
    prompt = """There are samples about code_diff to review:
code_diff:{\\"luigi/contrib/hive.py\\": \\"@@ -184,7 +184,7 @@ def table_location(self, table, database='default', partition=None):\\n                     import hive_metastore.ttypes\\n                     partition_str = self.partition_spec(partition)\\n                     thrift_table = client.get_partition_by_name(database, table, partition_str)\\n-                except hive_metastore.ttypes.NoSuchObjectException as e:\\n+                except hive_metastore.ttypes.NoSuchObjectException:\\n                     return ''\\n             else:\\n                 thrift_table = client.get_table(database, table)\\"};
review:can you fix this flake8 issue? \`./luigi/contrib/hive.py:187:71: F841 local variable ''e'' is assigned to but never used\` (btw you can run \`tox -e flake8\` locally to test)
code_diff:{\\"luigi/contrib/spark.py\\": \\"@@ -299,9 +299,9 @@ def app_command(self):\\n         return [self.app, pickle_loc] + self.app_options()\\n \\n     def run(self):\\n-        name = re.sub(r'[^\\\\w]', '_', self.name)\\n-        self.run_path = tempfile.mkdtemp(prefix=name)\\n-        self.run_pickle = os.path.join(self.run_path, '.'.join([name, 'pickle']))\\n+        path_name_fragment = re.sub(r'[^\\\\w]', '_', self.name)\\n+        self.run_path = tempfile.mkdtemp(prefix=path_name_fragment)\\n+        self.run_pickle = os.path.join(self.run_path, '.'.join([path_name_fragment, 'pickle']))\\n         with open(self.run_pickle, 'wb') as fd:\\n             # Copy module file to run path.\\n             module_path = os.path.abspath(inspect.getfile(self.__class__))\\"};
review:I''d rename variable \`name\` to something like \`run_path_prefix\` (maybe some better option) due to two reasons: - it is actually a path, not a name anymore - we must be having a hard time dealing with \`name\` and \`self.name\` in the same place
code_diff:{\\"luigi/task.py\\": \\"@@ -817,10 +817,7 @@ def getpaths(struct):\\n     if isinstance(struct, Task):\\n         return struct.output()\\n     elif isinstance(struct, dict):\\n-        r = struct.__class__()\\n-        for k, v in six.iteritems(struct):\\n-            r[k] = getpaths(v)\\n-        return r\\n+        return struct.__class__((k, getpaths(v)) for k, v in six.iteritems(struct))\\n     elif isinstance(struct, (list, tuple)):\\n         return struct.__class__(getpaths(r) for r in struct)\\n     else:\\"};
review:What''s this? The constructor for the dict subtype? Will this work if it''s a immutable type?"""
    return prompt

def generate_review_prompt(code_diff, context):
    '''
    Given a code diff and its context, generate a prompt for writing a concise and precise code review.
    '''
    prompt = "As a reviewer, you are examining a proposed code change in a pull request. "
    prompt += "You have the following code changes:\n"
    prompt += "```\n{}\n```\n".format(code_diff)
    prompt += "And the context provided with the changes is:\n"
    prompt += "```\n{}\n```\n".format(context)
    prompt += "Based on the code changes and the context, please provide a concise and precise review. "
    prompt += "Only output the review,which should be no more than 3 sentences within 30 words."
    prompt += "The review needs to mimic human tone and be centred around only one point.\n"
    prompt += few_shot_prompt()
    print(prompt)
    return prompt


def get_chatgptapi_response(prompt, model_name, temperature=1.0, max_tokens=100, api_key="", base_url="https://api.deepseek.com/"):
    client = OpenAI(
        api_key=api_key, base_url=base_url
    )
    response = client.chat.completions.create(
        model=model_name,  # 确保使用正确的模型名称
        messages=[
            {"role": "system", "content": "You are an experienced reviewer reviewing code changes."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    print(response)
    answer = response.choices[0].message.content
    print("answer: ",answer)
    return answer