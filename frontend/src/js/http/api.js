 /*
 * 功能：在每个请求头里自动添加`access token`。
 * 然后拦截请求结果，如果返回结果是身份认证失败（401），
 * 则说明`access_token`过期了，
 * 那么先用`cookie`中的`refresh_token`刷新`access_token`。
 * 如果刷新失败则说明`refreh_token`也过期了，
 * 则调用`user.logout()`在浏览器内存中删除登录状态；
 * 如果刷新成功，则重新发送原请求。
*/

import axios from "axios"
import {useUserStore} from "@/stores/user.js";
 import CONFIG_API from "@/js/config/config.js";

const BASE_URL = CONFIG_API.HTTP_URL

const api = axios.create({
    baseURL: BASE_URL,
    withCredentials: true,//表示跨域请求时携带身份凭证（cookies、HTTP 认证信息等）
})

//  axios 提供的请求拦截器注册方法，用于在请求发送到服务器之前拦截并处理请求配置config
api.interceptors.request.use(config => {
    // 在每个请求头里添加`access token`
    const user = useUserStore()
    if (user.accessToken) {
        config.headers.Authorization = `Bearer ${user.accessToken}`
    }
    return config
})

let isRefreshing = false
let refreshSubscribers = []

function subscribeTokenRefresh(callback) {
    refreshSubscribers.push(callback)
}

function onRefreshed(token) {
    refreshSubscribers.forEach(cb => cb(token))
    refreshSubscribers = []
}

function onRefreshFailed(err) {
    refreshSubscribers.forEach(cb => cb(null, err))
    refreshSubscribers = []
}

// 是 axios 提供的响应拦截器注册方法，用于在服务器返回响应之后、then/catch 之前拦截并处理响应数据
// 实现了一个完整的 Token 自动刷新机制，当访问令牌（access token）过期时（返回 401），自动使用刷新令牌（refresh token）获取新的 access token，然后重试原来的请求
api.interceptors.response.use(
    response => response,// 成功响应直接返回，不做处理
    async error => {// 只处理错误响应
        const user = useUserStore()
        const originalRequest = error?.config// 获取原始请求配置
        if (!originalRequest) {
            // Promise.reject(error) 会创建一个被拒绝（失败）的 Promise 对象，并将错误传递出去。
            return Promise.reject(error) // 没有请求配置，直接拒绝
        }
        //401
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            return new Promise((resolve, reject) => {
                //保存请求，将请求加入等待队列
                subscribeTokenRefresh((token, error) => {
                    if (error) {
                        // Promise 构造函数中的一个函数，用于手动将 Promise 标记为失败状态。
                        // 成功时调用 resolve(value)
                        // 失败时调用 reject(error)
                        reject(error)// 刷新失败
                    } else {
                        // 更新请求头的 token
                        originalRequest.headers.Authorization = `Bearer ${token}`
                         // 重新发送原请求
                        resolve(api(originalRequest))
                    }
                })

                //refresh_token
                if (!isRefreshing) {
                    isRefreshing = true
                    // 发送刷新 token 请求
                    axios.post(
                        `${BASE_URL}/api/user/account/refresh_token/`,
                        {},
                        {withCredentials: true, timeout: 5000}
                    ).then(res => {//成功
                        //保存access_token
                        user.setAccessToken(res.data.access)
                        // 通知所有等待的请求继续即再次发送原请求
                        onRefreshed(res.data.access)
                    }).catch(error => {
                        //失败退出
                        user.logout()
                        // 通知所有等待的请求失败
                        onRefreshFailed(error)
                        reject(error)
                    }).finally(() => {
                        isRefreshing = false// 重置刷新标志
                    })
                }
            })
        }

        return Promise.reject(error)
    }
)
//将一个模块中的某个值作为“主要”导出内容。
export default api
