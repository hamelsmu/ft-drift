# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_compare_funcs.ipynb.

# %% auto 0
__all__ = ['diff_funcs', 'explain_func_diff']

# %% ../nbs/02_compare_funcs.ipynb 2
import re
from typing import List
from .parse import ChatData

# %% ../nbs/02_compare_funcs.ipynb 5
def _clean_string(s):
    patterns = [r"current date is: .*?\)", r"Instead of \[Your Name\] use [A-Za-z\s\-']+(?:\.\s*)?"]
    for pattern in patterns:
        s = re.sub(pattern, '', s)
    return s.strip()

def _deep_diff(d1, d2, path=""):
    differences = []
    
    if not (isinstance(d1, (dict, list)) and isinstance(d2, (dict, list))):
        val1, val2 = (_clean_string(val) if isinstance(val, str) else val for val in (d1, d2))
        if val1 != val2:
            differences.append(f"{path} - {val1} != {val2}")
        return differences
    
    if isinstance(d1, dict) and isinstance(d2, dict):
        for key in set(d1).union(d2):
            new_path = f"{path}/{key}" if path else key
            if key in d1 and key in d2:
                differences.extend(_deep_diff(d1[key], d2[key], new_path))
            else:
                if key not in d1:
                    differences.append(f"{new_path} - Key missing in first")
                if key not in d2:
                    differences.append(f"{new_path} - Key missing in second")
    elif isinstance(d1, list) and isinstance(d2, list):
        if len(d1) != len(d2):
            differences.append(f"{path} - List sizes differ")
        else:
            for i, (item1, item2) in enumerate(zip(d1, d2)):
                differences.extend(_deep_diff(item1, item2, f"{path}[{i}]"))
    
    return differences


def diff_funcs(list1:List[dict], list2:List[dict]):
    "Compare two lists of functions."
    differences = []
    for item1, item2 in ((item1, next((item for item in list2 if item['name'] == item1['name']), None)) for item1 in list1):
        if item2:
            diff = _deep_diff(item1, item2)
            if diff:
                differences.append((item1['name'], diff))
        else:
            differences.append((item1['name'], None))
    for item2 in (item2 for item2 in list2 if not any(item1['name'] == item2['name'] for item1 in list1)):
        differences.append((None, item2['name']))
    
    msg = "No differences found." if not differences else "The following differences were found:\n" + \
          "\n".join(f"- Function {name or 'Unnamed'} differences:\n" + "\n".join(f"  {d}" for d in diff) if diff else f"- Function {name} is missing in one of the files" for name, diff in differences)
    
    return {'diff': bool(differences), 'msg': msg}

# %% ../nbs/02_compare_funcs.ipynb 7
def explain_func_diff(differences_output):
    "Use a LLM to provide a human-readable explanation of differences in function definitions."
    if not differences_output['diff']:
        return 'The comparison of the function definitions did not identify any differences.'

    else:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        context = "Given the following output from a program that compares two lists of dictionaries\
    representing function definitions, explain the differences identified. The function looks for matches based\
    on the 'name' field, compares other fields for differences, and generates a message based on the differences found.\
    There is no need to mention that this analysis is based on the output of a program.  Focus on giving the user actionable information."
        
        prompt = context + "\
    \
    Output of 'highlight_differences':\
    " + differences_output['msg']
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        # Extracting and returning the text from the response
        return response.choices[0].message.content
