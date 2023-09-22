
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from typing import List, Union
# from module.ai import AI
import json
import random
Message = Union[AIMessage, HumanMessage, SystemMessage]

# 玩家类
class Player():
    def __init__(self):
        self.age = 0
        self.appearance = random.randint(1, 10)
        self.gender = random.choice(["男", "女"])
        self.intelligence = random.randint(1, 10)
        self.health = random.randint(1, 10)
        self.wealth = random.randint(1, 10)
        self.mental_state = random.randint(1, 10)
        self.experiences = []

    def birth_event(self, ai, dbs):
        # 设置出生事件
        system_message = dbs.preprompts["system_message"] 
        messages: List[Message] = [ai.fsystem(system_message)]
        print(self.display_attributes())
        messages = ai.next(messages, self.display_attributes() + dbs.preprompts["birth_event"] , step_name="brith_event")
        self.experiences.append(messages[-1].content.strip()) 

    def event_gen(self, ai, dbs):
        # 生成事件
        system_message = dbs.preprompts["system_message"] 
        messages: List[Message] = [ai.fsystem(system_message)]
        print(self.display_attributes())
        messages = ai.next(messages, self.display_attributes() + dbs.preprompts["event_gen"] , step_name="brith_event")
        self.experiences.append(messages[-1].content.strip()) 


    def undergo_event(self, ai, dbs, feedback):
        system_message = dbs.preprompts["system_message"] 
        messages: List[Message] = [ai.fsystem(system_message)]
        user_feedback = self.experiences[-1] + "我的选择是" + feedback + "\n" + dbs.preprompts["event_undergo"] 
        messages = ai.next(messages, user_feedback, step_name="event_undergo")
        self.experiences.append(messages[-1].content.strip()) 
        # 根据事件更新玩家属性（这部分将根据你的具体需求进行定义）
        update = self.display_attributes() + dbs.preprompts["update_properties"] 
        messages = ai.next(messages, update, step_name="update_properties")
        return self.update_from_json(messages[-1].content.strip())

        
    def check_status(self, ai, dbs):
        system_message = dbs.preprompts["system_message"] 
        messages: List[Message] = [ai.fsystem(system_message)]
        if self.age > self.health * 10:
            messages = ai.next(messages, "玩家因健康原因死亡" + self.show_experiences() + dbs.preprompts["death"] , step_name="death")
            self.experiences.append(messages[-1].content.strip()) 
            return -1
        
        if self.mental_state < 0:
            messages = ai.next(messages, "玩家因心理健康原因死亡" + self.show_experiences() + dbs.preprompts["death"] , step_name="death")
            self.experiences.append(messages[-1].content.strip()) 
            return -1
        
        if self.wealth < 0:
            messages = ai.next(messages, "玩家因贫困死亡" + self.show_experiences() + dbs.preprompts["death"] , step_name="death")            
            self.experiences.append(messages[-1].content.strip()) 
            return -1
        return 1
    
    def display_attributes(self):
        attributes = [
            f"玩家属性   年龄：{self.age}",
            f"外貌：{self.appearance}",
            f"性别：{self.gender}",
            f"智力：{self.intelligence}",
            f"身体健康：{self.health}",
            f"心理健康：{self.mental_state}",
            f"财富：{self.wealth}",
        ]
        
        return "，".join(attributes)
    
    def show_experiences(self):
        experiences_str = []
        for i, experience in enumerate(self.experiences):
            experiences_str.append(f"经历 {i+1}: {experience}")
        
        return "\n".join(experiences_str)
    
    def update_from_json(self, s: str):
        start_idx = s.find('{')
        end_idx = s.rfind('}') + 1  # 加1是为了包括右花括号

        json_str = s[start_idx:end_idx]
        data = json.loads(json_str)

        # 使用字典的get方法是安全的，因为如果键不存在，它将返回None，而不是抛出异常
        self.age = data.get("年龄", self.age)
        self.appearance = data.get("外貌", self.appearance)
        self.gender = data.get("性别", self.gender)
        self.intelligence = data.get("智力", self.intelligence)
        self.health = data.get("身体健康", self.health)
        self.mental_state = data.get("心理健康", self.mental_state)
        self.wealth = data.get("财富", self.wealth)

        return s[0:start_idx-10]

    def to_dict(self) -> dict:
        """
        将玩家的属性转化为字典。
        """
        return {
            "age": self.age,
            "appearance": self.appearance,
            "gender": self.gender,
            "intelligence": self.intelligence,
            "health": self.health,
            "wealth": self.wealth,
            "mental_state": self.mental_state,
            "experiences": self.experiences
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        使用字典数据创建一个新的玩家对象。
        """
        player = cls()
        player.age = data.get("age", 0)
        player.appearance = data.get("appearance", random.randint(1, 10))
        player.gender = data.get("gender", random.choice(["男", "女"]))
        player.intelligence = data.get("intelligence", random.randint(1, 10))
        player.health = data.get("health", random.randint(1, 10))
        player.wealth = data.get("wealth", random.randint(1, 10))
        player.mental_state = data.get("mental_state", random.randint(1, 10))
        player.experiences = data.get("experiences", [])

        return player