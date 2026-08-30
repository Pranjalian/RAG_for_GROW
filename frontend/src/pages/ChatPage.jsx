import { useState, useEffect, useRef } from 'react';


export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isConnecting, setIsConnecting] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  
  // Use a hardcoded session for demo/dev purposes
  const sessionId = "frontend-dev-session";

  useEffect(() => {
    // Connect WebSocket
    const wsUrl = `ws://localhost:8000/api/chat/ws?session_id=${sessionId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
      setIsConnecting(false);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'assistant_chunk') {
        setIsTyping(false);
        setMessages(prev => {
          const newMsgs = [...prev];
          const lastMsg = newMsgs[newMsgs.length - 1];
          if (lastMsg && lastMsg.role === 'assistant' && !lastMsg.done) {
            // Create a new object instead of mutating the existing one
            newMsgs[newMsgs.length - 1] = {
              ...lastMsg,
              content: lastMsg.content + data.content
            };
            return newMsgs;
          } else {
            // New assistant message starting
            return [...prev, { role: 'assistant', content: data.content, done: false, sources: [] }];
          }
        });
      } else if (data.type === 'assistant_message') {
        setIsTyping(false);
        setMessages(prev => {
          const newMsgs = [...prev];
          const lastMsg = newMsgs[newMsgs.length - 1];
          if (lastMsg && lastMsg.role === 'assistant') {
            newMsgs[newMsgs.length - 1] = {
              ...lastMsg,
              done: true,
              sources: data.sources ? data.sources : lastMsg.sources,
              content: (data.content && !lastMsg.content) ? data.content : lastMsg.content
            };
            return newMsgs;
          } else if (data.content) {
            // Full message sent at once
            return [...prev, { role: 'assistant', content: data.content, done: true, sources: data.sources || [] }];
          }
          return prev;
        });
      }
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setIsConnecting(true);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = () => {
    if (!input.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    
    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setIsTyping(true);
    
    // Send to backend
    wsRef.current.send(JSON.stringify({
      type: "user_message",
      content: input
    }));
    
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex-1 flex flex-col relative h-full">
      {/* Chat Scroll Area */}
      <div className="flex-1 overflow-y-auto p-lg flex flex-col gap-xl">
        
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-on-surface-variant opacity-70">
            <span className="material-symbols-outlined text-6xl mb-4">forum</span>
            <p className="font-title-md text-title-md">Ask Groww Market Intelligence</p>
            {isConnecting && <p className="text-sm mt-2 animate-pulse">Connecting to backend...</p>}
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} w-full`}>
            <div className={`max-w-[95%] md:max-w-[80%] flex gap-4 ${msg.role === 'user' ? 'flex-col items-end' : ''}`}>
              
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-primary-container/20 flex items-center justify-center shrink-0 border border-primary-container/30 mt-2">
                  <span className="material-symbols-outlined text-primary text-sm">smart_toy</span>
                </div>
              )}
              
              <div className="flex flex-col gap-2">
                <div className={`px-lg py-md rounded-2xl text-on-surface whitespace-pre-wrap
                  ${msg.role === 'user' 
                    ? 'card-level-2 rounded-tr-sm bg-primary-container/10 border-primary-container/20 border' 
                    : 'card-level-1 rounded-tl-sm'}`
                }>
                  {msg.content}
                </div>

                {/* Sources Badge */}
                {msg.role === 'assistant' && msg.done && msg.sources && msg.sources.length > 0 && (
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-container-highest rounded-lg border border-white/5 self-start mt-2">
                    <span className="material-symbols-outlined text-xs text-on-surface-variant">database</span>
                    <span className="font-label-mono text-label-mono text-on-surface-variant text-xs">
                      Sources: {msg.sources.length} active
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start w-full">
            <div className="max-w-[95%] md:max-w-[80%] flex gap-4">
              <div className="w-8 h-8 rounded-full bg-primary-container/20 flex items-center justify-center shrink-0 border border-primary-container/30 mt-2">
                <span className="material-symbols-outlined text-primary text-sm">smart_toy</span>
              </div>
              <div className="flex flex-col gap-2">
                <div className="card-level-1 px-lg py-md rounded-2xl rounded-tl-sm text-on-surface flex items-center gap-2 w-fit">
                  <span className="w-2 h-2 bg-on-surface-variant rounded-full animate-bounce" style={{animationDelay: '0s'}}></span>
                  <span className="w-2 h-2 bg-on-surface-variant rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></span>
                  <span className="w-2 h-2 bg-on-surface-variant rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></span>
                  <span className="font-label-mono text-label-mono text-on-surface-variant ml-2 text-xs">Thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input Area */}
      <div className="w-full p-lg shrink-0">
        <div className="max-w-4xl mx-auto relative">
          <div className="glass-panel rounded-2xl flex flex-col focus-within:border-primary transition-colors duration-300 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
            <textarea 
              className="w-full bg-transparent border-none text-on-surface placeholder:text-on-surface-variant p-md focus:outline-none resize-none min-h-[64px] max-h-[200px]" 
              placeholder="Ask about funds, stocks, or market trends..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isConnecting}
            />
            <div className="flex items-center justify-between p-2 border-t border-white/5">
              <div className="flex items-center gap-1">
                <button className="p-2 text-on-surface-variant hover:text-primary hover:bg-white/5 rounded-lg transition-colors" title="Attach Data Source">
                  <span className="material-symbols-outlined">attach_file</span>
                </button>
                <button className="p-2 text-on-surface-variant hover:text-primary hover:bg-white/5 rounded-lg transition-colors" title="Market Search">
                  <span className="material-symbols-outlined">troubleshoot</span>
                </button>
              </div>
              <button 
                onClick={handleSend}
                disabled={isConnecting || !input.trim()}
                className="bg-primary-container text-black px-4 py-2 rounded-lg font-title-md text-title-md hover:bg-primary transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                <span>Send</span>
                <span className="material-symbols-outlined text-sm">send</span>
              </button>
            </div>
          </div>
          <div className="text-center mt-2">
            <span className="font-caption text-caption text-on-surface-variant">Groww AI can make mistakes. Consider verifying important information.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
