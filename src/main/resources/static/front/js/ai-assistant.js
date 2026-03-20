/**
 * AI智能助手 - 纯JavaScript实现，不依赖Vue
 */

(function() {
    'use strict';
    
    // 样式
    const styles = document.createElement('style');
    styles.textContent = `
        #ai-chat-bubble {
            position: fixed;
            right: 30px;
            bottom: 30px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 99999;
            transition: transform 0.3s;
        }
        #ai-chat-bubble:hover { transform: scale(1.1); }
        #ai-chat-bubble svg { width: 32px; height: 32px; fill: white; }
        
        #ai-chat-window {
            position: fixed;
            right: 30px;
            bottom: 100px;
            width: 380px;
            height: 520px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            z-index: 99998;
            display: none;
            flex-direction: column;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        #ai-chat-window.open { display: flex; animation: aiSlideUp 0.3s; }
        @keyframes aiSlideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .ai-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .ai-header-title { font-size: 16px; font-weight: 600; }
        .ai-header-status { font-size: 12px; opacity: 0.8; }
        .ai-close { 
            background: rgba(255,255,255,0.2); 
            border: none; 
            color: white; 
            width: 28px; 
            height: 28px; 
            border-radius: 50%; 
            cursor: pointer;
            font-size: 18px;
            line-height: 1;
        }
        .ai-close:hover { background: rgba(255,255,255,0.3); }
        
        .ai-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f8f9fa;
        }
        .ai-msg {
            margin-bottom: 12px;
            display: flex;
            flex-direction: column;
        }
        .ai-msg.user { align-items: flex-end; }
        .ai-msg.assistant { align-items: flex-start; }
        .ai-bubble {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.5;
        }
        .ai-msg.user .ai-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .ai-msg.assistant .ai-bubble {
            background: white;
            color: #333;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .ai-typing {
            display: flex;
            gap: 4px;
            padding: 10px 14px;
        }
        .ai-typing span {
            width: 8px;
            height: 8px;
            background: #667eea;
            border-radius: 50%;
            animation: aiBounce 1.4s infinite;
        }
        .ai-typing span:nth-child(2) { animation-delay: 0.16s; }
        .ai-typing span:nth-child(3) { animation-delay: 0.32s; }
        @keyframes aiBounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        .ai-input-area {
            padding: 12px 16px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        .ai-input-area input {
            flex: 1;
            padding: 10px 14px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 14px;
            outline: none;
        }
        .ai-input-area input:focus { border-color: #667eea; }
        .ai-send {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .ai-send:disabled { opacity: 0.5; cursor: not-allowed; }
        .ai-send svg { width: 18px; height: 18px; fill: white; }
    `;
    document.head.appendChild(styles);
    
    // 创建DOM
    const bubble = document.createElement('div');
    bubble.id = 'ai-chat-bubble';
    bubble.innerHTML = '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>';
    document.body.appendChild(bubble);
    
    const chatWindow = document.createElement('div');
    chatWindow.id = 'ai-chat-window';
    chatWindow.innerHTML = `
        <div class="ai-header">
            <div>
                <div class="ai-header-title">智能助手</div>
                <div class="ai-header-status" id="ai-status">检测中...</div>
            </div>
            <button class="ai-close" id="ai-close-btn">×</button>
        </div>
        <div class="ai-messages" id="ai-messages">
            <div class="ai-msg assistant">
                <div class="ai-bubble">你好！我是智能助手，有什么可以帮助你的吗？</div>
            </div>
        </div>
        <div class="ai-input-area">
            <input type="text" id="ai-input" placeholder="输入你的问题...">
            <button class="ai-send" id="ai-send-btn">
                <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
        </div>
    `;
    document.body.appendChild(chatWindow);
    
    // 状态
    let isLoading = false;
    const messages = [];
    const msgBox = document.getElementById('ai-messages');
    const input = document.getElementById('ai-input');
    const statusEl = document.getElementById('ai-status');
    
    // 切换显示
    bubble.onclick = function() {
        chatWindow.classList.toggle('open');
    };
    
    document.getElementById('ai-close-btn').onclick = function() {
        chatWindow.classList.remove('open');
    };
    
    // 滚动到底部
    function scroll() {
        msgBox.scrollTop = msgBox.scrollHeight;
    }
    
    // 添加消息
    function addMsg(role, content) {
        const div = document.createElement('div');
        div.className = 'ai-msg ' + role;
        div.innerHTML = '<div class="ai-bubble">' + content.replace(/\n/g, '<br>') + '</div>';
        msgBox.appendChild(div);
        scroll();
    }
    
    // 显示加载
    function showLoading() {
        const div = document.createElement('div');
        div.className = 'ai-msg assistant';
        div.id = 'ai-loading';
        div.innerHTML = '<div class="ai-bubble"><div class="ai-typing"><span></span><span></span><span></span></div></div>';
        msgBox.appendChild(div);
        scroll();
    }
    
    // 隐藏加载
    function hideLoading() {
        const el = document.getElementById('ai-loading');
        if (el) el.remove();
    }
    
    // 发送消息
    async function send() {
        const text = input.value.trim();
        if (!text || isLoading) return;
        
        addMsg('user', text);
        input.value = '';
        isLoading = true;
        document.getElementById('ai-send-btn').disabled = true;
        showLoading();
        
        try {
            const res = await fetch('/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    question: text,
                    history: messages.slice(-6)
                })
            });
            const data = await res.json();
            hideLoading();
            
            if (data.code === '0' && data.data && data.data.status === 'success') {
                addMsg('assistant', data.data.answer);
                messages.push({ role: 'user', content: text });
                messages.push({ role: 'assistant', content: data.data.answer });
            } else {
                addMsg('assistant', '抱歉，处理出现问题，请稍后再试。');
            }
        } catch (e) {
            console.error(e);
            hideLoading();
            addMsg('assistant', '抱歉，服务暂时不可用。');
        }
        
        isLoading = false;
        document.getElementById('ai-send-btn').disabled = false;
    }
    
    // 绑定事件
    document.getElementById('ai-send-btn').onclick = send;
    input.onkeypress = function(e) {
        if (e.key === 'Enter') send();
    };
    
    // 检测服务状态
    async function check() {
        try {
            const res = await fetch('/ai/health');
            const data = await res.json();
            if (data.code === '0' && data.data && data.data.status === 'healthy') {
                statusEl.textContent = '服务正常';
            } else {
                statusEl.textContent = '服务异常';
            }
        } catch (e) {
            statusEl.textContent = '服务未启动';
        }
    }
    
    check();
    setInterval(check, 30000);
})();
