import { Component, signal, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

interface Message {
  text: string;
  sender: 'bot' | 'user';
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {

  protected readonly title = signal('AI Chatbot');

  private http = inject(HttpClient);

  currentMessage = '';

  isTyping = false;

  messages: Message[] = [
    {
      text: 'Hello! 👋 Welcome to AI Chatbot.',
      sender: 'bot'
    },
    {
      text: 'Ask me anything.',
      sender: 'bot'
    }
  ];

  sendMessage(): void {

    const text = this.currentMessage.trim();

    if (!text) {
      return;
    }

    // Show user's message
    this.messages.push({
      text: text,
      sender: 'user'
    });

    this.currentMessage = '';

    this.isTyping = true;

    this.http.post<any>(
      'http://127.0.0.1:8000/chat',
      {
        message: text
      }
    ).subscribe({

      next: (response) => {

        this.isTyping = false;

        this.messages.push({
          text: response.response,
          sender: 'bot'
        });

      },

      error: (error) => {

        console.error(error);

        this.isTyping = false;

        this.messages.push({
          text: '❌ Unable to connect to FastAPI backend.',
          sender: 'bot'
        });

      }

    });

  }

}