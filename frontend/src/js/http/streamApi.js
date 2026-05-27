/*
    将HTTP请求修改成SSE请求。
 * 功能：在每个请求头里自动添加`access token`。
 * 然后拦截请求结果，如果返回结果是身份认证失败（401），
 * 则说明`access_token`过期了，那么调用api刷新token`，
 * 如果刷新成功，则重新发送原请求。
   */

import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useUserStore } from "@/stores/user.js";
import api from "./api.js";
import CONFIG_API from "@/js/config/config.js";

const BASE_URL = CONFIG_API.HTTP_URL

/**

 * 通用的流式请求工具

 * @param {string} url 请求地址

 * @param {object} options 配置项 (method, body, onmessage, onerror等)
 *
 * streamApi (SSE请求) → 发送请求（带 token）→ 后端返回 401 → 调用 axios refresh_token → 重试 SSE 请求
 *
 * 调用 streamApi()
 *     ↓
 * 进入函数，获取 userStore
 *     ↓
 * 定义 startFetch 函数（不执行）
 *     ↓
 * 执行 startFetch() 并等待
 *     ↓
 * startFetch 内部执行 fetchEventSource 并等待
 *     ↓
 * fetchEventSource 建立 SSE 连接
 *     ↓
 * 返回连接结果
   */
export default async function streamApi(url, options = {}) {
    // 1. 获取用户信息
   const userStore = useUserStore();
    // 2. 定义内部函数
   const startFetch = async () => {
       // 3. 建立 SSE 连接并等待
       //是 @microsoft/fetch-event-source 库提供的函数，用于建立 SSE 连接
       return await fetchEventSource(BASE_URL + url, {
           method: options.method || 'POST',
           headers: {
               'Content-Type': 'application/json',
               'Authorization': `Bearer ${userStore.accessToken}`,
               ...options.headers,// 合并自定义 headers
           },
           body: JSON.stringify(options.body || {}),

           openWhenHidden: true,  // 允许后台运行，防止浏览器因隐藏页面而强制关闭它
           async onopen(response) {// ← 流式连接建立时触发
               // 1. 处理 401 Token 过期
               if (response.status === 401) {
                   try {
                       // 触发 api.js 中的 Axios 拦截器进行静默刷新，会返回access_token
                       await api.post('/api/user/account/refresh_token/', {});
                       // 刷新成功，抛出特定错误触发下面的 onerror 重试逻辑
                       throw new Error("TOKEN_REFRESHED");
                   } catch (err) {
                       // 如果刷新失败（refresh_token也过期），直接报错由上层处理
                       throw err;
                   }
               }

               if (!response.ok || !response.headers.get('content-type')?.includes('text/event-stream')) {
                   const errorData = await response.json().catch(() => ({}));
                   throw new Error(errorData.detail || `请求失败: ${response.status}`);
               }
           },

           //msg.data是chat.py中传来的yield（相当于return） f'data:{json.dumps({'content':msg.content},ensure_ascii=False)}\n\n'，
           // 然后msg的其它属性是fetch-event-source 库封装添加的。即msg是封装后的消息对象。
           onmessage(msg) {// ← 收到流式数据块时触发
               if (msg.data === '[DONE]') {
                   //options.onmessage:传过来的回调函数onmessage，可以自定义名字，只是这样好记
                   if (options.onmessage) options.onmessage('', true);
                   return
               }
               // 尝试解析 JSON，将 JSON 字符串解析为 JavaScript 对象
               try {
                   const json = JSON.parse(msg.data);
                   if (options.onmessage) options.onmessage(json, false);
               } catch (e) {
                   console.error("流解析失败:", e);
               }
           },
           //streamApi 内部错误触发
           onerror(err) {// ← 流式连接出错时触发
               // 2. 捕获重试信号并递归
               if (err.message === "TOKEN_REFRESHED") {
                   return startFetch();
               }

               // 其他错误则按用户定义的 onerror 处理
               // 🔥 流式连接过程中的错误（网络中断、服务器断开等）
               // 这些错误触发你传入的 onerror 回调
               if (options.onerror) {
                   options.onerror(err);// ← 你的 onerror 被调用
               }
               throw err; // 停止自动重试
           },

           onclose: options.onclose,// ← 流式连接关闭时触发
       });

   };
    // 4. 执行内部函数并等待
   return await startFetch();
}
