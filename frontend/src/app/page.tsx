'use client'

import { useState } from 'react'
import { 
  Plus, 
  Play, 
  Settings, 
  BarChart3, 
  Clock, 
  CheckCircle,
  AlertCircle,
  Video,
  Sparkles
} from 'lucide-react'
import Link from 'next/link'

// نوع المشروع
interface Project {
  id: number
  topic: string
  title: string
  status: 'pending' | 'generating' | 'processing' | 'editing' | 'completed' | 'failed'
  progress: number
  created_at: string
  video_url?: string
}

// مكون بطاقة المشروع
function ProjectCard({ project }: { project: Project }) {
  const statusColors = {
    pending: 'bg-gray-500',
    generating: 'bg-yellow-500',
    processing: 'bg-blue-500',
    editing: 'bg-purple-500',
    completed: 'bg-green-500',
    failed: 'bg-red-500'
  }
  
  const statusLabels = {
    pending: 'قيد الانتظار',
    generating: 'جاري التوليد',
    processing: 'جاري المعالجة',
    editing: 'جاري التحرير',
    completed: 'مكتمل',
    failed: 'فشل'
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 hover:bg-gray-750 transition-all duration-300 border border-gray-700">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white mb-1">{project.title || project.topic}</h3>
          <p className="text-gray-400 text-sm">{project.topic}</p>
        </div>
        <span className={`${statusColors[project.status]} text-white text-xs px-3 py-1 rounded-full`}>
          {statusLabels[project.status]}
        </span>
      </div>
      
      {project.status !== 'completed' && project.status !== 'failed' && (
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-400 mb-1">
            <span>التقدم</span>
            <span>{project.progress}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className={`${statusColors[project.status]} h-2 rounded-full transition-all duration-500`}
              style={{ width: `${project.progress}%` }}
            />
          </div>
        </div>
      )}
      
      <div className="flex justify-between items-center pt-4 border-t border-gray-700">
        <span className="text-gray-500 text-sm">{project.created_at}</span>
        {project.video_url && (
          <a 
            href={project.video_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-primary-400 hover:text-primary-300 text-sm"
          >
            <Video size={16} />
            مشاهدة الفيديو
          </a>
        )}
      </div>
    </div>
  )
}

// مكون نموذج إنشاء مشروع
function CreateProjectForm({ onClose }: { onClose: () => void }) {
  const [topic, setTopic] = useState('')
  const [duration, setDuration] = useState(5)
  const [style, setStyle] = useState('documentary')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    // هنا يمكن استدعاء API لإنشاء المشروع
    console.log('Creating project:', { topic, duration, style })
    
    setTimeout(() => {
      setIsLoading(false)
      onClose()
    }, 2000)
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-2xl p-8 max-w-lg w-full animate-slide-up">
        <h2 className="text-2xl font-bold text-white mb-6">إنشاء فيديو جديد</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-300 mb-2">موضوع الفيديو</label>
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="أدخل موضوع الفيديو... (مثال: تاريخ القهوة العربية)"
              className="w-full bg-gray-700 text-white rounded-xl p-4 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              rows={4}
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-300 mb-2">المدة (دقائق)</label>
              <select
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="w-full bg-gray-700 text-white rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {[1, 2, 3, 5, 7, 10, 15, 20, 30].map(d => (
                  <option key={d} value={d}>{d} دقائق</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-gray-300 mb-2">أسلوب الفيديو</label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="w-full bg-gray-700 text-white rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="documentary">وثائقي</option>
                <option value="educational">تعليمي</option>
                <option value="entertaining">ترفيهي</option>
                <option value="news">أخباري</option>
              </select>
            </div>
          </div>
          
          <div className="flex gap-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-700 text-white py-3 rounded-xl hover:bg-gray-600 transition-colors"
            >
              إلغاء
            </button>
            <button
              type="submit"
              disabled={isLoading || !topic.trim()}
              className="flex-1 bg-primary-600 text-white py-3 rounded-xl hover:bg-primary-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  جاري الإنشاء...
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  إنشاء الفيديو
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function Home() {
  const [showCreateForm, setShowCreateForm] = useState(false)
  
  // بيانات تجريبية
  const projects: Project[] = [
    {
      id: 1,
      topic: 'تاريخ القهوة العربية',
      title: 'كيف بدأت القهوة في الجزيرة العربية',
      status: 'completed',
      progress: 100,
      created_at: 'منذ 2 ساعة',
      video_url: 'https://youtube.com/watch?v=dQw4w9WgXcQ'
    },
    {
      id: 2,
      topic: 'أساطير البحر الأحمر',
      title: 'قصة صائد اللؤلؤ',
      status: 'editing',
      progress: 75,
      created_at: 'منذ ساعة'
    },
    {
      id: 3,
      topic: 'الزراعة في الصحراء',
      title: 'كيف نجحت الصحراء في الإنتاج',
      status: 'generating',
      progress: 35,
      created_at: 'منذ 30 دقيقة'
    }
  ]

  const stats = [
    { label: 'إجمالي الفيديوهات', value: '156', icon: Video },
    { label: 'هذا الشهر', value: '23', icon: BarChart3 },
    { label: 'ساعات المعالجة', value: '48', icon: Clock },
    { label: 'مكتمل', value: '142', icon: CheckCircle },
  ]

  return (
    <div className="min-h-screen bg-gray-900">
      {/* شريط التنقل */}
      <nav className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <Sparkles className="text-white" size={24} />
              </div>
              <span className="text-xl font-bold text-white">AutoCreator AI</span>
            </div>
            
            <div className="flex items-center gap-4">
              <button className="p-2 text-gray-400 hover:text-white transition-colors">
                <Settings size={20} />
              </button>
              <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                <span className="text-white font-medium">م</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* المحتوى الرئيسي */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* عنوان الصفحة */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">لوحة التحكم</h1>
            <p className="text-gray-400">أضف مشروعك الجديد وابدأ بصناعة محتوى احترافي</p>
          </div>
          
          <button
            onClick={() => setShowCreateForm(true)}
            className="flex items-center gap-2 bg-primary-600 text-white px-6 py-3 rounded-xl hover:bg-primary-500 transition-all hover:scale-105 shadow-lg shadow-primary-600/25"
          >
            <Plus size={20} />
            مشروع جديد
          </button>
        </div>

        {/* الإحصائيات */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {stats.map((stat, index) => (
            <div key={index} className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-primary-600/20 rounded-lg">
                  <stat.icon className="text-primary-400" size={20} />
                </div>
              </div>
              <p className="text-2xl font-bold text-white">{stat.value}</p>
              <p className="text-gray-400 text-sm">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* المشاريع الحديثة */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-white mb-4">المشاريع الحديثة</h2>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map(project => (
            <ProjectCard key={project.id} project={project} />
          ))}
          
          {/* بطاقة إضافة مشروع جديد */}
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-gray-800/50 border-2 border-dashed border-gray-700 rounded-xl p-6 flex flex-col items-center justify-center gap-4 hover:border-primary-600 hover:bg-gray-800 transition-all group min-h-[200px]"
          >
            <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center group-hover:bg-primary-600 transition-colors">
              <Plus className="text-gray-400 group-hover:text-white" size={32} />
            </div>
            <p className="text-gray-400 group-hover:text-white transition-colors">إضافة مشروع جديد</p>
          </button>
        </div>
      </main>

      {/* نموذج إنشاء مشروع */}
      {showCreateForm && (
        <CreateProjectForm onClose={() => setShowCreateForm(false)} />
      )}
    </div>
  )
}
