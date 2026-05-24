import os
from pprint import pprint
from typing import TypedDict, Annotated, Sequence

import lancedb
from django.utils.timezone import localtime, now
from lancedb.pydantic import vector
from langchain_community.vectorstores import LanceDB
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode

from web.documents.utils.custom_embeddings import CustomEmbeddings


# # 用户输入
# "现在几点了？"
#
# # 流程：
# # 1. agent节点
# state['messages'] = [HumanMessage("现在几点了？")]
# AI返回：AIMessage(tool_calls=[{"name":"get_time"}])
#
# # 2. should_continue判断
# 发现有tool_calls → 返回 "tools"
#
# # 3. tools节点
# 根据返回的tool_calls中的name键知道要执行哪些工具函数，执行get_time() → 返回 ToolMessage("2026-01-15 14:30:00")
#
# # 4. 回到agent节点
# state['messages'] 现在包含：
#   - HumanMessage("现在几点了？")
#   - AIMessage(tool_calls=[...])
#   - ToolMessage("2026-01-15 14:30:00")
# AI看到工具结果后回答：AIMessage("现在是 2026-01-15 14:30:00")
#
# # 5. should_continue判断
# 无新工具调用 → 返回 "end" → 结束
class ChatGraph:
    @staticmethod
    def create_app():
        # 工具节点
        @tool
        def get_time()->str:
            # 下面的3对引号表示文档，当鼠标悬停时出现,工具函数一定要有文档，文档是告诉大模型干嘛的
            # 大模型会读取""""""(docstring)来理解这个工具是干什么的
            """当需要查询精确时间时，调用此函数。返回格式为：[年-月-日 时:分:秒]"""
            return localtime(now()).strftime('%Y-%m-%d %H:%M:%S')

        @tool
        def search_knowledge_base(query:str)->str:
            """当用户查询阿里云百炼平台的相关信息时，调用此函数，输入为要查询的问题，输出为查询结果"""
            db=lancedb.connect('./web/documents/lancedb_storage')
            embeddings=CustomEmbeddings()
            # 直接连接到已存在的数据库表,LanceDB.from_documents() - 创建新表并插入数据
            vector_db=LanceDB(
                connection=db,
                embedding=embeddings,
                table_name='my_knowledge_base',
            )
            # 根据问题，从数据库中找出最相关的3个文档片段,docs：返回的文档列表
            docs=vector_db.similarity_search(query,k=3)
            #越是人能看懂，大模型就能看懂
            context='\n\n'.join([f'内容片段：{i+1}\n{doc.page_content}' for i,doc in enumerate(docs)])
            return f'从知识库中找到以下相关信息：\n\n{context}\n'


        tools=[get_time,search_knowledge_base]


        llm=ChatOpenAI(
            model='deepseek-v4-pro',
            openai_api_key=os.getenv('API_KEY'),#读取环境变量
            # API 调用就是使用别人已经训练好的大模型，你不需要自己训练，只需要发送请求来获取结果。
            openai_api_base=os.getenv('API_BASE'),# 要访问的url告诉 ChatOpenAI 去哪个 URL 调用 API
            streaming=True,#流式输出，不全部一次性输出
            model_kwargs={
                "stream_options": {
                    "include_usage": True,  # 输出token消耗数量
                }
            }
        ).bind_tools(tools)

        # class AgentState(TypedDict): - 定义一个类型化字典,AgentState自定义的名称
        # Annotated[Sequence[BaseMessage], add_messages] - 值的类型
        # Sequence[BaseMessage]：值必须是消息序列，包含的元素类型是 BaseMessage（如 HumanMessage、AIMessage 等）
        # Sequence 代表任何有序的、可通过索引访问的集合e.g.list（列表）tuple（元组）str（字符串，字符序列）range（范围序列）
        # add_messages：额外的元数据（归约器）告诉 LangGraph 如何合并值
        # 默认行为：后者覆盖前者 ，add_messages 行为：合并列表
        # class AgentState(TypedDict): 是 Python 中定义类型化字典的语法，用于给字典的键和值添加类型约束。
        # TypedDict 的作用:定义一个字典的结构（有哪些键）,指定每个键对应的值类型,提供类型提示和 IDE 自动补全
        class AgentState(TypedDict):
            # AgentState 这个字典必须包含一个 messages 键，
            # 并且 messages 的值是一个消息列表 messages - 字典的键名
            # Annotated 不改变类型，只是附加说明书，就像说："这是消息序列，合并的时候要用 add_messages 方式"
            #e.g. class State(TypedDict):
            #     messages: Annotated[list, add_messages]  # 告诉：这是一个列表，合并时要 add_messages
            # BaseMessage (抽象基类)
            #     ├── HumanMessage      (用户)
            #     ├── AIMessage         (AI助手)
            #     ├── SystemMessage     (系统设定)  ← 是的，它是 BaseMessage
            #     ├── ToolMessage       (工具结果)
            #     ├── FunctionMessage   (已弃用)
            #     └── ChatMessage       (自定义角色)
            messages: Annotated[Sequence[BaseMessage], add_messages]

        # AI 调用节点
        def model_call(state:AgentState)->AgentState:
            # pprint(state)
            # 对大模型的调用，将消息列表传进去，传入历史消息
            # ↓↓↓ 这一行会发送 HTTP 请求到 API 服务器
            res = llm.invoke(state['messages'])  # ← API 调用在这里！
            # 检测到messages字段有add_messages注解，自动调用 add_messages(旧消息列表, [res])将合并结果写回 state['messages']
            # 如果没有用Annotated设置add_message注解，就会用我们传统的默认观念是覆盖原数据了
            #伪代码
            # # 更新状态时使用归约器
            # for key, new_value in new_values.items():
            #     if key in self.reducers:#self.reducers所有归约器
            #         # 使用归约器合并
            #         old_state[key] = self.reducers[key](old_state[key], new_value)
            #     else:
            #         # 直接覆盖
            #         old_state[key] = new_value
            # print('**********************************')
            # pprint(res)#当问时间时，第一次res里面有tool_calls=[{'name': 'get_time'
            return {'messages':[res]}

        # 设计路由节点
        def should_continue(state:AgentState)->str:
            #取出最后一条信息
            last_message=state['messages'][-1]
            #如果存在工具调用   所有工具的调用都会存在tool_calls对象里面
            if last_message.tool_calls:
                return "tools"
            return "end"

        # 定义工具节点，会自己根据ai的信息调用对应函数
        # LangGraph 中的一个节点类，专门用于自动执行 AI 模型调用的工具函数
        # 自动执行 AI 请求的工具
        # 将执行结果包装成 ToolMessage 返回,ToolNode 会将执行结果以 ToolMessage 的形式自动追加到 state['messages'] 中。
        tool_node=ToolNode(tools)

        # 定义状态图，消息类型为AgentState,所有节点返回的 {'messages': [...]} 都会自动使用这个归约器
        graph=StateGraph(AgentState)
        # 定义自己传入的节点叫agent加入graph,模型调用节点
        graph.add_node('agent',model_call)
        graph.add_node('tools', tool_node)
        #加2条边
        graph.add_edge(START,'agent')
        # 添加条件边
        graph.add_conditional_edges(
            'agent',
            should_continue,
            {
                'tools':'tools',#如果返回tools，就返回tools节点
                'end':END,#如果返回end就返回END节点
            }
        )
        graph.add_edge('tools','agent')

        #编译后自动返回APP
        # 将构建好的状态图编译成可执行的运行实例
        return graph.compile()

