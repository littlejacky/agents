# coding=utf-8
# Copyright 2023  The AIWaves Inc. team.

#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Components (modularized prompts) of a Node in an LLM Autonomous agent
"""

from abc import abstractmethod
from text2vec import SentenceModel, semantic_search
from utils import *

class Component():
    def __init__(self):
        self.prompt = ""
    
    def get_prompt(self):
        return self.prompt
    
class TaskComponent(Component):
    
    def __init__(self,task):
        super().__init__()
        self.task = task

    def get_prompt(self):
        return f"""你需要执行的任务是:{self.task}。"""
    
class InputComponent(Component):
    
    def __init__(self):
        super().__init__()
        self.user_input = ""
        
    def get_prompt(self):
        if self.user_input == "":
            return ""
        return  f"用户的输入是:{self.user_input}。"

class OutputComponent(Component):

    def __init__(self, output):
        super().__init__()
        self.output = output
    
    def get_prompt(self):
        return  f"""请联系上文，进行<{self.output}>和</{self.output}>的提取。
切记，输出格式为： 
```
<{self.output}>
...
</{self.output}>
```
"""

class StyleComponent(Component):
    """
    角色、风格组件
    """

    def __init__(self, agent, style):
        super().__init__()
        self.agent = agent
        self.style = style

    def get_prompt(self):
        return  f"""现在你来模拟一个{self.agent}。你需要遵循以下的输出风格：
f{self.style}。
"""

class RuleComponent(Component):

    def __init__(self, rule):
        super().__init__()
        self.rule = rule

    def get_prompt(self):
        return  f"""你需要遵循的规则是:{self.rule}。"""

class DemonstrationComponent(Component):
    """
    input a list,the example of answer.
    """

    def __init__(self, demonstrations):
        super().__init__()
        self.demonstrations = demonstrations

    def add_demonstration(self, demonstration):
        self.demonstrations.append(demonstration)

    def get_prompt(self):
        prompt = "以下是你可以参考的例子：\n"
        for demonstration in self.demonstrations:
            prompt +="\n" + demonstration
        return prompt

class KnowledgeBaseComponent(Component):
    """
    KnowledgeBase
    """
    def __init__(self,knowledge_base,top_k = 2):
        super().__init__()
        self.top_k = top_k
        self.knowledge_base_path = knowledge_base
        self.user_input = ""
        self.embedding_model = SentenceModel('shibing624/text2vec-base-chinese',device="cpu")
        self.kb_embeddings,self.kb_questions,self.kb_answers,self.kb_chunks = load_knowledge_base(self.knowledge_base_path)
        
    def get_knowledge(self,user_input):
        
        knowledge = ""
        query_embedding = self.embedding_model.encode(user_input)
        hits = semantic_search(query_embedding, self.kb_embeddings, top_k=50)
        hits = hits[0]
        temp = []
        for hit in hits:
            matching_idx = hit['corpus_id']
            score = hit["score"]
            if self.kb_chunks[matching_idx] in temp:
                pass
            else:
                knowledge = knowledge + f'{self.kb_questions[matching_idx]}的答案是：{self.kb_chunks[matching_idx]}\n 以上这段话与问题的语义匹配度是{score}\n'
                temp.append(self.kb_chunks[matching_idx])
                if len(temp) == self.top_k:
                    break
        print("user_input:" + "********************************************")
        print(user_input)
        print("knowledge:********************************************")
        print(knowledge)
        return knowledge

    def get_prompt(self):
        prompt = f"用户的输入是:{self.user_input}"+"\n"+f"与之最匹配的知识库内容是{self.get_knowledge(self.user_input)}"
        return prompt
    

class KnowledgeComponent:
    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def get_prompt():
        pass
    

class Information_KnowledgeComponent(KnowledgeComponent):
    def __init__(self) -> None:
        super().__init__()
    
    def get_prompt(self,long_memory,temp_memory):
        memory = {"extract_category":"","top_category":""}
        memory.update(long_memory)
        memory.update(temp_memory)
        
        return f"""你需要知道的是：用户目前选择的商品是{memory["extract_category"]}，而我们店里没有这类商品，但是我们店里有一些近似商品，如{memory["top_category"]}"""
        
    
        
        