'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, MessageCircle, X, Send, Bot, User, RefreshCw } from 'lucide-react'
import { useBusiness } from '@/components/business-context'
import { advisorReply, formatCompactINR, formatINR } from '@/lib/data'
import { sendAiMessage } from '@/lib/api/ai'

const QUICK_QUESTIONS = [
  'Why did you recommend dairy farming?',
  'What if I only have ₹3 lakh?',
  'What documents do I need?',
  'Which scheme gives me the best financing?',
  'How much would my EMI be?',
]

export function AiAssistantDrawer() {
  const [isOpen, setIsOpen] = useState(false)
  const { profile, finance, onboarding, activeRecommendation } = useBusiness()
  const [messages, setMessages] = useState<
    { sender: 'ai' | 'user'; text: string; isError?: boolean }[]
  >([
    {
      sender: 'ai',
      text: `Namaste ${profile.ownerName || 'Entrepreneur'}! I am RuralEdge AI, powered by FastAPI & Gemini. Ask me anything about government schemes, financing, or your business in ${onboarding.village || 'Hosahalli'}!`,
    },
  ])
  const [input, setInput] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isOpen, isThinking])

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim()
    if (!query || isThinking) return

    setMessages((prev) => [...prev, { sender: 'user', text: query }])
    if (!textToSend) setInput('')
    setIsThinking(true)

    try {
      const response = await sendAiMessage({
        message: query,
        user_context: {
          state: onboarding.state,
          district: onboarding.district,
          age: profile.age,
          gender: profile.gender,
          occupation: onboarding.selectedInterests[0] || 'farmer',
          annual_income: profile.annualIncome,
        },
        language: 'English',
      })

      setMessages((prev) => [...prev, { sender: 'ai', text: response.reply }])
    } catch (err: any) {
      console.warn('FastAPI AI Endpoint Error, attempting fallback:', err)
      // Isolated Emergency Fallback
      let fallbackReply = ''
      const q = query.toLowerCase()
      if (q.includes('why') && (q.includes('recommend') || q.includes('dairy'))) {
        fallbackReply = `We recommended ${activeRecommendation.title} because your village (${onboarding.village || 'Hosahalli'}) has high demand, suitable land/water access, and high eligibility for loan coverage.`
      } else if (q.includes('3 lakh') || q.includes('3l')) {
        fallbackReply = `With ₹3 Lakh starting margin, you can unlock up to ₹30 Lakh in total project cost!`
      } else if (q.includes('document')) {
        fallbackReply = `To apply for loan sanction, you need: 1) Aadhaar Card, 2) Address Proof, 3) 6-Month Bank Statement, and 4) Business Viability Report.`
      } else {
        fallbackReply = advisorReply(query)
      }
      
      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: `${fallbackReply}\n\n(Note: ${err.message || 'FastAPI AI service unavailable'})`,
          isError: false,
        },
      ])
    } finally {
      setIsThinking(false)
    }
  }

  return (
    <>
      {/* Floating Trigger Button */}
      <motion.button
        type="button"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-40 flex items-center gap-2.5 rounded-full bg-primary px-5 py-3 font-extrabold text-white shadow-lift border border-primary/40 transition-transform hover:scale-105 hover:bg-primary-hover active:scale-95"
      >
        <Sparkles className="size-5 text-sand animate-pulse" />
        <span className="text-sm">✨ Ask RuralEdge AI</span>
      </motion.button>

      {/* Slide-over Drawer Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 flex justify-end bg-background/60 backdrop-blur-sm animate-in fade-in duration-200">
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="flex h-full w-full max-w-md flex-col border-l border-border bg-card shadow-lift"
            >
              {/* Drawer Header */}
              <div className="flex items-center justify-between border-b border-border bg-charcoal p-4 text-white">
                <div className="flex items-center gap-2.5">
                  <div className="grid size-10 place-items-center rounded-full bg-white/15">
                    <Bot className="size-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-display font-extrabold text-base leading-tight">
                      ✨ RuralEdge AI
                    </h3>
                    <p className="text-[11px] text-white/80">
                      FastAPI + Gemini 2.5 • {onboarding.village || 'Hosahalli'}
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="rounded-full p-2 text-white/80 hover:bg-white/10 hover:text-white"
                >
                  <X className="size-5" />
                </button>
              </div>

              {/* Chat Message List */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((m, idx) => (
                  <div
                    key={idx}
                    className={`flex items-start gap-2.5 ${
                      m.sender === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {m.sender === 'ai' && (
                      <div className="grid size-8 shrink-0 place-items-center rounded-full bg-charcoal text-white text-xs font-bold mt-1">
                        <Bot className="size-4 text-primary" />
                      </div>
                    )}
                    <div
                      className={`max-w-[82%] rounded-2xl p-3.5 text-xs leading-relaxed whitespace-pre-line ${
                        m.sender === 'user'
                          ? 'bg-primary text-white font-semibold rounded-br-none'
                          : m.isError
                          ? 'bg-destructive/10 border border-destructive/30 text-destructive rounded-bl-none'
                          : 'bg-background border border-border/80 text-foreground shadow-soft rounded-bl-none'
                      }`}
                    >
                      {m.text}
                    </div>
                    {m.sender === 'user' && (
                      <div className="grid size-8 shrink-0 place-items-center rounded-full bg-muted text-foreground text-xs font-bold mt-1">
                        <User className="size-4 text-foreground" />
                      </div>
                    )}
                  </div>
                ))}

                {isThinking && (
                  <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground p-2">
                    <RefreshCw className="size-3.5 animate-spin text-primary" />
                    <span>FastAPI Gemini AI is processing your query...</span>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Quick Questions Bar */}
              <div className="border-t border-border/60 bg-background/50 p-3">
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground block mb-2 px-1">
                  Suggested Questions:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {QUICK_QUESTIONS.map((q) => (
                    <button
                      key={q}
                      type="button"
                      disabled={isThinking}
                      onClick={() => handleSend(q)}
                      className="rounded-full border border-border bg-card px-3 py-1.5 text-[11px] font-semibold text-foreground transition-all hover:bg-primary/10 hover:border-primary/40 text-left disabled:opacity-50"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>

              {/* Input Bar */}
              <div className="border-t border-border bg-card p-3.5">
                <form
                  onSubmit={(e) => {
                    e.preventDefault()
                    handleSend()
                  }}
                  className="flex items-center gap-2"
                >
                  <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask RuralEdge AI anything..."
                    disabled={isThinking}
                    className="flex-1 rounded-full border border-input bg-background px-4 py-2.5 text-xs font-semibold text-foreground outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
                  />
                  <button
                    type="submit"
                    disabled={!input.trim() || isThinking}
                    className="grid size-9 place-items-center rounded-full bg-primary text-white shadow-soft transition-transform hover:scale-105 hover:bg-primary-hover disabled:opacity-50"
                  >
                    <Send className="size-4" />
                  </button>
                </form>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  )
}
