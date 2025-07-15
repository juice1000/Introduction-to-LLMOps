import React, { useState, useRef, useEffect } from 'react';
import './styles/background.scss'; // switched from App.css to SCSS background

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'assistant';
  sources?: string[];
}

interface ChatResponse {
  response: string;
  sources?: string[];
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now(),
      text: inputValue.trim(),
      sender: 'user',
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.text,
          use_context: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      const assistantMessage: Message = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'assistant',
        sources: data.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please make sure the API server is running on localhost:8000');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e as any);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Insurance Chatbot</h1>
        <div className="subtitle">Ask me anything about insurance policies and claims</div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="message assistant">
            <div>
              Welcome! I'm your insurance assistant. I can help you with:
              <br />• Filing insurance claims
              <br />• Understanding coverage options
              <br />• Policy information
              <br />• General insurance questions
              <br />
              <br />
              How can I help you today?
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div>{message.text}</div>
            {message.sources && message.sources.length > 0 && (
              <div className="message-sources">Sources: {message.sources.map((source) => source.split('/').pop()).join(', ')}</div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="loading">
              <span>Thinking</span>
              <span className="loading-dots"></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="chat-input-container">
        <form onSubmit={sendMessage} className="chat-input-form">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about insurance policies, claims, or coverage..."
            className="chat-input"
            disabled={isLoading}
            rows={1}
          />
          <button type="submit" disabled={!inputValue.trim() || isLoading} className="send-button">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
