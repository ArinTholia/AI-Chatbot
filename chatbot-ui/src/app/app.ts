import { Component, inject, ViewChild, ElementRef, AfterViewChecked, OnDestroy, OnInit, ChangeDetectorRef, NgZone } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ChatService, ChatMessage, Source } from './chat.service';

export interface Message {
  text: string;
  sender: 'bot' | 'user';
  sources?: Source[];
  responseTime?: number;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit, AfterViewChecked, OnDestroy {
  private chatService = inject(ChatService);
  private sanitizer = inject(DomSanitizer);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  
  @ViewChild('chatContainer') private chatContainer!: ElementRef;

  currentMessage = '';
  isTyping = false;
  isConnected = true;
  showSidebar = true;
  copiedMessageIndex: number | null = null;
  elapsedSeconds = 0;
  activeChatId: string = '';
  savedChats: { id: string; title: string; date: string }[] = [];
  
  messages: Message[] = [];
  
  suggestions = [
    'What is the fee for B.Tech?',
    'Tell me about hostel facilities',
    'What are the eligibility criteria?',
    'What is the placement record?',
    'Which companies visit for placements?',
    'Are there any scholarships available?'
  ];

  private healthTimer: any;
  private elapsedTimer: any;

  ngOnInit() {
    this.loadSavedChatsList();
    this.startNewChat();
    this.checkHealth();
    this.healthTimer = setInterval(() => {
      this.checkHealth();
    }, 30000);
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  ngOnDestroy() {
    if (this.healthTimer) clearInterval(this.healthTimer);
    if (this.elapsedTimer) clearInterval(this.elapsedTimer);
  }

  private addWelcomeMessages() {
    this.messages = [
      { text: 'Hello! 👋 Welcome to the SRMIST Admission Assistant.', sender: 'bot' },
      { text: 'Ask me any questions about admissions, courses, fees, placements, or campus life.', sender: 'bot' }
    ];
  }

  private checkHealth() {
    this.chatService.healthCheck().subscribe({
      next: (res) => {
        this.isConnected = res.status === 'healthy' && res.ollama_connected;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isConnected = false;
        this.cdr.detectChanges();
      }
    });
  }

  scrollToBottom(): void {
    try {
      if (this.chatContainer) {
        this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
      }
    } catch(err) { }
  }

  toggleSidebar() {
    this.showSidebar = !this.showSidebar;
  }

  askSuggestion(question: string) {
    this.currentMessage = question;
    this.sendMessage();
  }

  clearChat() {
    this.isTyping = false;
    this.elapsedSeconds = 0;
    if (this.elapsedTimer) clearInterval(this.elapsedTimer);
    this.startNewChat();
  }

  startNewChat() {
    this.activeChatId = 'chat_' + Date.now();
    this.addWelcomeMessages();
  }

  private loadSavedChatsList() {
    try {
      const list = localStorage.getItem('srmist_chat_list');
      this.savedChats = list ? JSON.parse(list) : [];
    } catch { this.savedChats = []; }
  }

  private saveCurrentChat() {
    try {
      const userMessages = this.messages.filter(m => m.sender === 'user');
      if (userMessages.length === 0) return;
      
      const title = userMessages[0].text.substring(0, 40) + (userMessages[0].text.length > 40 ? '...' : '');
      localStorage.setItem('srmist_chat_' + this.activeChatId, JSON.stringify(this.messages));
      
      const existingIndex = this.savedChats.findIndex(c => c.id === this.activeChatId);
      const chatEntry = { id: this.activeChatId, title, date: new Date().toLocaleString() };
      if (existingIndex >= 0) {
        this.savedChats[existingIndex] = chatEntry;
      } else {
        this.savedChats.unshift(chatEntry);
      }
      // Keep only last 10 chats
      if (this.savedChats.length > 10) {
        const removed = this.savedChats.pop();
        if (removed) localStorage.removeItem('srmist_chat_' + removed.id);
      }
      localStorage.setItem('srmist_chat_list', JSON.stringify(this.savedChats));
    } catch { }
  }

  loadChat(chatId: string) {
    try {
      const data = localStorage.getItem('srmist_chat_' + chatId);
      if (data) {
        this.activeChatId = chatId;
        this.messages = JSON.parse(data);
        this.cdr.detectChanges();
      }
    } catch { }
  }

  deleteChat(chatId: string, event: Event) {
    event.stopPropagation();
    localStorage.removeItem('srmist_chat_' + chatId);
    this.savedChats = this.savedChats.filter(c => c.id !== chatId);
    localStorage.setItem('srmist_chat_list', JSON.stringify(this.savedChats));
    if (chatId === this.activeChatId) {
      this.startNewChat();
    }
    this.cdr.detectChanges();
  }

  copyMessage(text: string, index: number) {
    navigator.clipboard.writeText(text).then(() => {
      this.copiedMessageIndex = index;
      setTimeout(() => {
        this.copiedMessageIndex = null;
        this.cdr.detectChanges();
      }, 2000);
    });
  }

  sendMessage(): void {
    const text = this.currentMessage.trim();
    if (!text || this.isTyping) return;

    const history: ChatMessage[] = this.messages
      .filter(msg => msg.sender === 'user' || msg.sender === 'bot')
      .filter(msg => !msg.text.startsWith('Hello! 👋') && !msg.text.startsWith('Ask me any questions about'))
      .slice(-4)
      .map(msg => ({ role: msg.sender === 'user' ? 'user' : 'assistant', content: msg.text } as ChatMessage));

    this.messages.push({ text: text, sender: 'user' });
    this.currentMessage = '';
    this.isTyping = true;
    this.elapsedSeconds = 0;
    this.cdr.detectChanges();

    // Start a visible timer so user knows AI is thinking
    this.elapsedTimer = setInterval(() => {
      this.elapsedSeconds++;
      this.cdr.detectChanges();
    }, 1000);
    
    const startTime = Date.now();

    this.chatService.sendMessage(text, history).subscribe({
      next: (result) => {
        this.ngZone.run(() => {
          clearInterval(this.elapsedTimer);
          this.isTyping = false;
          this.elapsedSeconds = 0;
          this.messages.push({ 
            text: result.response, 
            sender: 'bot', 
            sources: result.sources,
            responseTime: result.response_time_ms || (Date.now() - startTime)
          });
          this.saveCurrentChat();
          this.cdr.detectChanges();
        });
      },
      error: (error) => {
        this.ngZone.run(() => {
          clearInterval(this.elapsedTimer);
          this.isTyping = false;
          this.elapsedSeconds = 0;
          this.messages.push({ 
            text: 'Sorry, something went wrong: ' + (error.message || 'Unknown error'), 
            sender: 'bot' 
          });
          this.saveCurrentChat();
          this.cdr.detectChanges();
        });
      }
    });
  }
  
  onKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  formatMarkdown(text: string): SafeHtml {
    let formatted = text;
    
    // Code blocks
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre class="code-block"><code>$1</code></pre>');
    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
    // Bold
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Headings
    formatted = formatted.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    formatted = formatted.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    formatted = formatted.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    // Lists
    formatted = formatted.replace(/^\s*[-*]\s+(.*)$/gim, '<li>$1</li>');
    // Wrap consecutive list items in <ul>
    formatted = formatted.replace(/(<li>.*<\/li>\s*)+/g, '<ul>$&</ul>');
    // New lines outside of HTML tags
    formatted = formatted.replace(/\n(?![^<]*>)/g, '<br>');
    // Clean up empty br tags next to pre
    formatted = formatted.replace(/<br>\s*<pre>/g, '<pre>');
    formatted = formatted.replace(/<\/pre>\s*<br>/g, '</pre>');

    return this.sanitizer.bypassSecurityTrustHtml(formatted);
  }

  getScorePercent(distance: number): number {
    const score = Math.max(0, Math.min(100, (1 - distance / 2) * 100));
    return Math.round(score);
  }

  getScoreColor(distance: number): string {
    const percent = this.getScorePercent(distance);
    if (percent >= 80) return 'var(--accent-green)';
    if (percent >= 50) return 'var(--accent-amber)';
    return 'var(--accent-red)';
  }
}