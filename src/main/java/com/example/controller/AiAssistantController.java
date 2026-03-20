package com.example.controller;

import cn.hutool.core.util.StrUtil;
import cn.hutool.http.HttpUtil;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.example.common.Result;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * AI智能助手控制器
 * 代理转发请求到Python服务
 */
@RestController
@RequestMapping(value = "/ai")
public class AiAssistantController {

    @Value("${ai.service.url:http://127.0.0.1:8001}")
    private String aiServiceUrl;

    /**
     * 对话接口
     * @param requestBody 包含question和可选的history
     * @return AI回答
     */
    @PostMapping("/chat")
    public Result<Map<String, Object>> chat(@RequestBody Map<String, Object> requestBody) {
        String question = (String) requestBody.get("question");
        @SuppressWarnings("unchecked")
        List<Map<String, String>> history = (List<Map<String, String>>) requestBody.get("history");
        
        if (StrUtil.isBlank(question)) {
            return Result.error("400", "问题不能为空");
        }
        
        try {
            // 构建请求体
            Map<String, Object> request = new HashMap<>();
            request.put("question", question);
            if (history != null && !history.isEmpty()) {
                request.put("history", history);
            }
            
            // 发送请求到Python服务
            String response = HttpUtil.post(
                aiServiceUrl + "/chat",
                JSONUtil.toJsonStr(request),
                30000  // 30秒超时
            );
            
            // 解析响应
            JSONObject jsonResponse = JSONUtil.parseObj(response);
            
            Map<String, Object> result = new HashMap<>();
            result.put("status", jsonResponse.getStr("status"));
            result.put("answer", jsonResponse.getStr("answer"));
            result.put("sources", jsonResponse.get("sources"));
            
            return Result.success(result);
            
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("500", "AI服务暂时不可用，请稍后再试: " + e.getMessage());
        }
    }

    /**
     * 重新加载知识库
     * @return 操作结果
     */
    @PostMapping("/reload")
    public Result<Map<String, Object>> reloadKnowledge() {
        try {
            String response = HttpUtil.post(aiServiceUrl + "/reload", "");
            JSONObject jsonResponse = JSONUtil.parseObj(response);
            
            Map<String, Object> result = new HashMap<>();
            result.put("status", jsonResponse.getStr("status"));
            result.put("message", jsonResponse.getStr("message"));
            
            return Result.success(result);
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("500", "重新加载知识库失败: " + e.getMessage());
        }
    }

    /**
     * 获取知识库状态
     * @return 知识库状态信息
     */
    @GetMapping("/knowledge/status")
    public Result<Map<String, Object>> knowledgeStatus() {
        try {
            String response = HttpUtil.get(aiServiceUrl + "/knowledge/status");
            JSONObject jsonResponse = JSONUtil.parseObj(response);
            
            Map<String, Object> result = new HashMap<>();
            result.put("status", jsonResponse.getStr("status"));
            result.put("documentCount", jsonResponse.getInt("document_count"));
            result.put("documents", jsonResponse.get("documents"));
            
            return Result.success(result);
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("500", "获取知识库状态失败: " + e.getMessage());
        }
    }

    /**
     * 健康检查
     * @return 服务状态
     */
    @GetMapping("/health")
    public Result<Map<String, Object>> health() {
        try {
            String response = HttpUtil.get(aiServiceUrl + "/health", 5000);
            JSONObject jsonResponse = JSONUtil.parseObj(response);
            
            Map<String, Object> result = new HashMap<>();
            result.put("status", "healthy");
            result.put("aiService", jsonResponse.getStr("status"));
            
            return Result.success(result);
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("status", "unhealthy");
            result.put("error", e.getMessage());
            return Result.success(result);
        }
    }
}
