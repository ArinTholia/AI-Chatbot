import { Injectable } from '@angular/core';
import { Observable, from } from 'rxjs';

export interface Source {
  name: string;
  distance: number;
}

export interface ChatResponse {
  response: string;
  sources: Source[];
  response_time_ms?: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface HealthResponse {
  status: string;
  ollama_connected: boolean;
  model: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://127.0.0.1:8000';

  sendMessage(message: string, history: ChatMessage[] = []): Observable<ChatResponse> {
    return from(this.fetchChat(message, history));
  }

  private async fetchChat(message: string, history: ChatMessage[]): Promise<ChatResponse> {
    console.log('[SRMIST-AI] Sending fetch to backend...');
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 600000);

    try {
      const res = await fetch(`${this.apiUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, history }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = await res.json();
      console.log('[SRMIST-AI] Got response:', data.response?.substring(0, 80));
      return data as ChatResponse;
    } catch (err: any) {
      clearTimeout(timeoutId);
      console.error('[SRMIST-AI] Fetch error:', err);
      if (err.name === 'AbortError') {
        throw new Error('Request timed out. The AI is taking too long to respond.');
      }
      throw new Error(err.message || 'Failed to connect to the server.');
    }
  }

  healthCheck(): Observable<HealthResponse> {
    return from(
      fetch(`${this.apiUrl}/health`)
        .then(res => res.json())
        .catch(() => ({ status: 'error', ollama_connected: false, model: 'unknown' }))
    );
  }
}