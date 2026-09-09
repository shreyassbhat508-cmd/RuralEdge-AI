'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import {
  Send,
  Sparkles,
  Bot,
  User,
  Mic,
  MicOff,
  Globe,
  Sun,
  Moon,
  Landmark,
  FileText,
  ShieldAlert,
  ArrowRight,
  CheckCircle2,
  HelpCircle,
  TrendingUp,
  Sprout,
  Coins,
  ChevronDown,
} from 'lucide-react'
import { useBusiness } from '@/components/business-context'
import { useTheme } from '@/components/theme-provider'
import {
  processChatbotQuery,
  SUGGESTED_ACTIONS,
  QUICK_QUESTIONS,
  type ChatbotResponse,
  type StructuredCard,
} from '@/lib/chatbot-engine'
import { LANGUAGES } from '@/lib/data'
import { cn } from '@/lib/utils'

interface ChatMessage {
  id: string
  sender: 'user' | 'bot'
  text?: string
  response?: ChatbotResponse
  time: string
}

export function AdvisorView() {
  const { profile } = useBusiness()
  const { theme, toggleTheme } = useTheme()

  const [input, setInput] = useState('')
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const [langDropdownOpen, setLangDropdownOpen] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [hasInteracted, setHasInteracted] = useState(false)

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-init',
      sender: 'bot',
      response: {
        explanation: `👋 Namaste! I'm RuralEdge.\n\nI can help you understand government schemes, loans, subsidies and business opportunities.`,
      },
      time: 'Just now',
    },
  ])

  const chatScrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom on message updates
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight
    }
  }, [messages, isTyping])

  const handleSend = (queryText?: string) => {
    const textToSend = (queryText || input).trim()
    if (!textToSend) return

    setHasInteracted(true)

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      sender: 'user',
      text: textToSend,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMsg])
    if (!queryText) setInput('')
    setIsTyping(true)

    // Simulate real-time response generation
    setTimeout(() => {
      const botResponse = processChatbotQuery(textToSend)
      const botMsg: ChatMessage = {
        id: `b-${Date.now()}`,
        sender: 'bot',
        response: botResponse,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }

      setMessages((prev) => [...prev, botMsg])
      setIsTyping(false)
    }, 550)
  }

  // Voice Input Speech Recognition Handler
  const toggleSpeechRecognition = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition is not supported in this browser. Please type your message.')
      return
    }

    if (isListening) {
      setIsListening(false)
      return
    }

    try {
      const SpeechRecognition =
        (window as unknown as { SpeechRecognition: new () => SpeechRecognition }).SpeechRecognition ||
        (window as unknown as { webkitSpeechRecognition: new () => SpeechRecognition }).webkitSpeechRecognition

      const recognition = new SpeechRecognition()
      recognition.continuous = false
      recognition.interimResults = false
      recognition.lang = selectedLanguage === 'hi' ? 'hi-IN' : 'en-IN'

      recognition.onstart = () => setIsListening(true)
      recognition.onend = () => setIsListening(false)

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = event.results[0][0].transcript
        if (transcript) {
          setInput(transcript)
        }
      }

      recognition.onerror = () => setIsListening(false)

      recognition.start()
    } catch {
      setIsListening(false)
    }
  }

  const currentLang = LANGUAGES.find((l) => l.code === selectedLanguage) || LANGUAGES[0]

  return (
    <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-6xl flex-col px-3 py-4 sm:px-6 sm:py-6">
      {/* ==================================================
          CHATBOT HEADER
          ================================================== */}
      <header className="mb-4 rounded-3xl border border-border bg-card/95 backdrop-blur-md p-4 sm:p-5 shadow-soft transition-all">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="grid size-8 place-items-center rounded-xl bg-primary text-white shadow-soft">
                <Sprout className="size-4.5" />
              </span>
              <div>
                <h1 className="font-display text-xl font-black tracking-tight text-foreground sm:text-2xl">
                  RuralEdge <span className="text-xs font-bold uppercase tracking-wider text-primary">Chatbot</span>
                </h1>
                <p className="text-xs font-medium text-muted-foreground">
                  “Your guide to rural business & government schemes”
                </p>
              </div>
            </div>
            <p className="mt-2 hidden text-[11px] font-semibold text-muted-foreground/90 md:block">
              AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for Rural Micro-Entrepreneurs
            </p>
          </div>

          <div className="flex items-center justify-between gap-3 border-t border-border/60 pt-3 sm:border-t-0 sm:pt-0">
            {/* Online Status */}
            <div className="inline-flex items-center gap-1.5 rounded-full border border-border bg-background px-3 py-1 text-xs font-extrabold text-foreground">
              <span className="relative flex size-2">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex size-2 rounded-full bg-emerald-500" />
              </span>
              Online / Ready
            </div>

            {/* Language Selector Dropdown */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setLangDropdownOpen((v) => !v)}
                className="inline-flex items-center gap-1.5 rounded-full border border-border bg-background px-3 py-1.5 text-xs font-bold text-foreground transition-all hover:bg-muted"
                aria-label="Select Language"
              >
                <Globe className="size-3.5 text-primary" />
                <span>{currentLang.label}</span>
                <ChevronDown className="size-3 text-muted-foreground" />
              </button>

              {langDropdownOpen && (
                <div className="absolute right-0 top-full z-50 mt-1 w-44 rounded-2xl border border-border bg-card p-1.5 shadow-lift animate-in fade-in zoom-in-95 duration-150">
                  <div className="px-2.5 py-1 text-[10px] font-extrabold uppercase text-muted-foreground">
                    Select Language
                  </div>
                  {LANGUAGES.map((lang) => (
                    <button
                      key={lang.code}
                      type="button"
                      onClick={() => {
                        setSelectedLanguage(lang.code)
                        setLangDropdownOpen(false)
                      }}
                      className={cn(
                        'flex w-full items-center justify-between rounded-xl px-2.5 py-1.5 text-xs font-medium transition-colors',
                        selectedLanguage === lang.code
                          ? 'bg-primary/10 text-primary font-bold'
                          : 'text-foreground hover:bg-muted',
                      )}
                    >
                      <span>{lang.label}</span>
                      <span className="text-[11px] text-muted-foreground">{lang.native}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Theme Toggle Button */}
            <button
              type="button"
              onClick={toggleTheme}
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              className="grid size-8.5 place-items-center rounded-full border border-border bg-card text-foreground transition-transform hover:scale-105 active:scale-95"
            >
              {theme === 'dark' ? <Sun className="size-4 text-sand" /> : <Moon className="size-4 text-charcoal" />}
            </button>
          </div>
        </div>
      </header>

      {/* ==================================================
          MAIN CHAT CONTAINER
          ================================================== */}
      <div className="relative flex flex-1 flex-col overflow-hidden rounded-3xl border border-border bg-card/95 backdrop-blur-md shadow-soft">
        {/* Subtle Rural Field Texture */}
        <div className="absolute inset-0 bg-field-lines opacity-15 pointer-events-none" />
        <div className="absolute inset-0 bg-contour opacity-20 pointer-events-none" />

        {/* Scrollable Conversation Surface */}
        <div
          ref={chatScrollRef}
          className="relative flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scroll-smooth"
        >
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={cn(
                'flex gap-3 max-w-full',
                msg.sender === 'user' ? 'justify-end' : 'justify-start',
              )}
            >
              {/* Bot Avatar */}
              {msg.sender === 'bot' && (
                <div className="grid size-9 shrink-0 place-items-center rounded-2xl bg-primary text-white font-bold shadow-soft mt-0.5">
                  <Bot className="size-5" />
                </div>
              )}

              {/* User Bubble */}
              {msg.sender === 'user' && (
                <div className="flex flex-col items-end gap-1 max-w-[85%] sm:max-w-[75%]">
                  <div className="rounded-2xl bg-primary px-4 py-3 text-sm font-medium text-white shadow-soft rounded-tr-none leading-relaxed">
                    {msg.text}
                  </div>
                  <span className="text-[10px] text-muted-foreground px-1">{msg.time}</span>
                </div>
              )}

              {/* Bot Response Content */}
              {msg.sender === 'bot' && msg.response && (
                <div className="flex flex-col gap-3 max-w-[92%] sm:max-w-[85%] text-foreground">
                  <div className="rounded-2xl border border-border bg-background/90 p-4 sm:p-5 shadow-soft rounded-tl-none space-y-4">
                    {/* Explanation */}
                    <div className="whitespace-pre-line text-sm font-medium leading-relaxed">
                      {msg.response.explanation}
                    </div>

                    {/* Number Highlights */}
                    {msg.response.numbers && msg.response.numbers.length > 0 && (
                      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 pt-1">
                        {msg.response.numbers.map((n, i) => (
                          <div
                            key={i}
                            className="rounded-xl border border-primary/25 bg-primary/8 p-2.5 text-center"
                          >
                            <span className="block text-[10px] font-bold uppercase text-muted-foreground">
                              {n.label}
                            </span>
                            <span className="font-display text-base font-black text-primary sm:text-lg">
                              {n.value}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Bullet Points */}
                    {msg.response.bulletPoints && msg.response.bulletPoints.length > 0 && (
                      <div className="space-y-2 pt-1 border-t border-border/60">
                        <span className="text-xs font-bold text-foreground block">Key Considerations:</span>
                        <ul className="space-y-1.5 text-xs text-foreground/90">
                          {msg.response.bulletPoints.map((bp, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <CheckCircle2 className="size-3.5 text-primary shrink-0 mt-0.5" />
                              <span>{bp}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Step-by-Step Instructions */}
                    {msg.response.steps && msg.response.steps.length > 0 && (
                      <div className="space-y-2 pt-2 border-t border-border/60">
                        <span className="text-xs font-bold text-foreground block">Action Roadmap:</span>
                        <div className="space-y-2 text-xs">
                          {msg.response.steps.map((st, i) => (
                            <div key={i} className="flex items-start gap-2.5 rounded-xl border border-border bg-card p-2.5">
                              <span className="grid size-5 shrink-0 place-items-center rounded-full bg-primary text-white text-[10px] font-black">
                                {i + 1}
                              </span>
                              <span className="text-foreground/90 font-medium leading-snug">{st}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Structured Scheme / Document Card */}
                    {msg.response.card && (
                      <StructuredResponseCard card={msg.response.card} />
                    )}

                    {/* Accuracy Notice for Unverified Queries */}
                    {msg.response.isUnverified && (
                      <div className="mt-3 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-3.5 text-xs space-y-2">
                        <div className="flex items-center gap-2 font-bold text-amber-700 dark:text-amber-400">
                          <ShieldAlert className="size-4 shrink-0" />
                          <span>Official Verification Recommended</span>
                        </div>
                        <p className="text-muted-foreground leading-relaxed">
                          For official scheme rules, interest rates, and loan disbursements, please verify details with your local Gram Panchayat, District Industries Centre (DIC), or Bank Branch Manager.
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Quick Suggestions underneath Unverified State */}
                  {msg.response.isUnverified && (
                    <div className="flex flex-wrap gap-2 pt-1">
                      {QUICK_QUESTIONS.slice(0, 3).map((q, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => handleSend(q)}
                          className="rounded-full border border-border bg-card px-3 py-1.5 text-xs font-bold text-primary transition-all hover:bg-primary/10 hover:border-primary/40"
                        >
                          {q} →
                        </button>
                      ))}
                    </div>
                  )}

                  <span className="text-[10px] text-muted-foreground px-1">{msg.time}</span>
                </div>
              )}
            </div>
          ))}

          {/* WELCOME STATE CARDS & SUGGESTIONS */}
          {!hasInteracted && messages.length === 1 && (
            <div className="my-4 space-y-6 animate-in fade-in slide-in-from-bottom-3 duration-300">
              {/* Suggested Action Chips */}
              <div className="rounded-3xl border border-primary/30 bg-primary/8 p-5 space-y-3">
                <span className="text-xs font-extrabold uppercase tracking-wider text-primary block">
                  Select a topic to get started:
                </span>
                <div className="flex flex-wrap gap-2">
                  {SUGGESTED_ACTIONS.map((act, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSend(act.query)}
                      className="rounded-full border border-primary/40 bg-card px-4 py-2 text-xs font-bold text-primary shadow-soft transition-all hover:bg-primary hover:text-white hover:scale-105 active:scale-95"
                    >
                      {act.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Quick Questions List */}
              <div className="space-y-3">
                <span className="text-xs font-extrabold uppercase text-muted-foreground block px-1">
                  Frequently Asked Questions:
                </span>
                <div className="grid gap-2.5 sm:grid-cols-2">
                  {QUICK_QUESTIONS.map((qq, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSend(qq)}
                      className="flex items-center justify-between rounded-2xl border border-border bg-card p-3.5 text-left text-xs font-semibold text-foreground shadow-soft transition-all hover:border-primary/40 hover:bg-primary/8 group"
                    >
                      <span>{qq}</span>
                      <ArrowRight className="size-4 text-primary transition-transform group-hover:translate-x-1 shrink-0 ml-2" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex items-center gap-3">
              <div className="grid size-9 shrink-0 place-items-center rounded-2xl bg-primary text-white font-bold shadow-soft">
                <Bot className="size-5" />
              </div>
              <div className="flex items-center gap-2 rounded-2xl border border-border bg-background px-4 py-3 text-xs font-semibold text-muted-foreground shadow-soft">
                <span className="relative flex size-2">
                  <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-75" />
                  <span className="relative inline-flex size-2 rounded-full bg-primary" />
                </span>
                RuralEdge is thinking...
              </div>
            </div>
          )}
        </div>

        {/* ==================================================
            CHAT INPUT BAR
            ================================================== */}
        <div className="border-t border-border/60 bg-card/80 backdrop-blur-xl p-4 sm:p-6">
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSend()
            }}
            className="flex items-center gap-2"
          >
            {/* Microphone Voice Button */}
            <button
              type="button"
              onClick={toggleSpeechRecognition}
              aria-label={isListening ? 'Stop listening' : 'Start voice input'}
              className={cn(
                'grid size-11 shrink-0 place-items-center rounded-2xl border border-border transition-all',
                isListening
                  ? 'bg-rose-500 text-white animate-pulse border-rose-500'
                  : 'bg-background text-foreground hover:bg-muted hover:border-primary/40',
              )}
            >
              {isListening ? <MicOff className="size-5" /> : <Mic className="size-5 text-primary" />}
            </button>

            {/* Main Message Input */}
            <input
              type="text"
              placeholder="Ask about schemes, loans, subsidies or starting a business…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 rounded-2xl border border-input bg-background px-4 py-3 text-sm font-medium text-foreground outline-none transition-all placeholder:text-muted-foreground focus:border-primary focus:ring-2 focus:ring-primary/20"
            />

            {/* Send Button */}
            <button
              type="submit"
              disabled={!input.trim()}
              aria-label="Send Message"
              className={cn(
                'grid size-11 shrink-0 place-items-center rounded-2xl bg-primary text-white font-bold shadow-soft transition-all',
                input.trim()
                  ? 'hover:bg-primary-hover hover:scale-105 active:scale-95 cursor-pointer'
                  : 'opacity-50 cursor-not-allowed',
              )}
            >
              <Send className="size-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

/** Component for rendering structured Scheme/Document cards inside bot responses */
function StructuredResponseCard({ card }: { card: StructuredCard }) {
  return (
    <div className="mt-2 rounded-2xl border border-primary/30 bg-card p-4 sm:p-5 shadow-soft space-y-3.5">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between border-b border-border/80 pb-3">
        <div>
          <h4 className="font-display text-base font-extrabold text-foreground">{card.title}</h4>
          {card.code && <span className="text-[10px] font-mono font-bold text-muted-foreground">{card.code}</span>}
        </div>
        {card.subsidyBadge && (
          <span className="self-start sm:self-auto rounded-full bg-primary/15 px-3 py-1 text-[11px] font-extrabold text-primary border border-primary/30">
            {card.subsidyBadge}
          </span>
        )}
      </div>

      {/* Eligibility */}
      <div className="space-y-1">
        <span className="text-xs font-bold text-primary uppercase tracking-wider block">Eligibility</span>
        <p className="text-xs text-foreground/90 font-medium leading-relaxed">{card.eligibility}</p>
      </div>

      {/* Potential Support */}
      <div className="space-y-1">
        <span className="text-xs font-bold text-primary uppercase tracking-wider block">Potential Support</span>
        <p className="text-xs text-foreground/90 font-medium leading-relaxed">{card.support}</p>
      </div>

      {/* Documents */}
      {card.documents && card.documents.length > 0 && (
        <div className="space-y-1.5 pt-1">
          <span className="text-xs font-bold text-foreground block">Required Documents:</span>
          <div className="grid gap-1.5 sm:grid-cols-2 text-xs">
            {card.documents.map((doc, idx) => (
              <div key={idx} className="flex items-center gap-2 rounded-xl border border-border bg-background p-2 text-muted-foreground font-semibold">
                <FileText className="size-3.5 text-primary shrink-0" />
                <span className="truncate">{doc}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Next Steps */}
      {card.nextSteps && card.nextSteps.length > 0 && (
        <div className="space-y-1.5 pt-1">
          <span className="text-xs font-bold text-foreground block">Next Steps:</span>
          <ol className="space-y-1 text-xs text-foreground/90">
            {card.nextSteps.map((ns, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="font-bold text-primary">{idx + 1}.</span>
                <span>{ns}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Action Button */}
      {card.linkHref && (
        <div className="pt-2">
          <Link
            href={card.linkHref}
            className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2 text-xs font-bold text-white shadow-soft transition-transform hover:scale-105 hover:bg-primary-hover"
          >
            <span>{card.linkText || 'Learn More'}</span>
            <ArrowRight className="size-3.5" />
          </Link>
        </div>
      )}
    </div>
  )
}
