import os
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph


class ChatGraph:
    @staticmethod
    def create_app():
        llm=ChatOpenAI(
            model='deepseek-v4-pro',
            openai_api_key=os.getenv('API_KEY'),#读取环境变量
            openai_api_base=os.getenv('API_BASE'),# 要访问的url
            streaming=True,#流式输出，不全部一次性输出
            model_kwargs={
                "stream_options": {
                    "include_usage": True,  # 输出token消耗数量
                }
            }
        )

        #相当于一个字典：{
        #   'message':[]
        # }
        # 继承自TypedDict，表示这是一个类型化的字典
        class AgentState(TypedDict):
            # 使用 Annotated 和 add_messages 注解
            # Sequence[BaseMessage]字段的类型：一个消息序列（可以是列表或元组）
            # add_messages元数据（特殊注解），告诉LangGraph如何处理这个字段
            # add_messages是一个归约器（Reducer）函数，它定义了当多个节点返回该字段时如何合并数据
            messages: Annotated[Sequence[BaseMessage], add_messages]

        def model_call(state:AgentState)->AgentState:
            # 对大模型的调用，将消息列表传进去
            res=llm.invoke(state['messages'])
            # 检测到messages字段有add_messages注解，自动调用 add_messages(旧消息列表, [res])将合并结果写回 state['messages']
            return {'messages':[res]}

        # 定义状态图，消息类型为AgentState
        graph=StateGraph(AgentState)
        # 定义自己传入的节点叫agent加入graph,模型调用节点
        graph.add_node('agent',model_call)
        #加2条边
        graph.add_edge(START,'agent')
        graph.add_edge('agent',END)

        #编译后自动返回APP
        # 将构建好的状态图编译成可执行的运行实例
        return graph.compile()

