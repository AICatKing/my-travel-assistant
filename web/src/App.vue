<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import { travelApi } from './api'
import type { TripPlan, TripPlanRequest } from './types'

// 高德地图相关变量
let map: any = null
let markers: any[] = []
let polylines: any[] = []

const loading = ref(false)
const error = ref<string | null>(null)
const tripPlan = ref<TripPlan | null>(null)
const currentStatus = ref<string>('正在准备规划...')

// 表单请求参数
const request = reactive<TripPlanRequest>({
  city: '西安',
  start_date: '2026-05-01',
  end_date: '2026-05-03',
  days: 3,
  preferences: '历史文化, 地道美食',
  budget: '中等',
  transportation: '公共交通',
  accommodation: '高档酒店'
})

// 初始化地图
const initMap = async () => {
  // 安全设置（高德地图 JS API 2.0 必填，本地测试时直接填入你的 Security Code）
  // 生产环境应通过环境变量加载
  (window as any)._AMapSecurityConfig = {
    securityJsCode: 'dfc440d9b54ef7b59367c3b28b7e713c', // 替换为你的安全密钥
  };

  try {
    const AMap = await AMapLoader.load({
      key: '64ca2418579d460e40854495574c8b20', // 替换为你的 Web 端 JS API Key
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.Polyline']
    })
    map = new AMap.Map('map-container', {
      zoom: 11,
      center: [108.940174, 34.341568], // 默认西安
      mapStyle: 'amap://styles/macaron'
    })
  } catch (e) {
    console.error('地图加载失败', e)
  }
}

// 清理地图覆盖物
const clearMap = () => {
  if (markers.length > 0) {
    map.remove(markers)
    markers = []
  }
  if (polylines.length > 0) {
    map.remove(polylines)
    polylines = []
  }
}

// 绘制打点和线路
const updateMapMarkers = () => {
  if (!map || !tripPlan.value) return
  clearMap()

  const allPoints: any[] = []
  const dailyPaths: any[][] = []

  tripPlan.value.days.forEach((day, dayIdx) => {
    const path: any[] = []
    
    // 处理酒店
    if (day.hotel && day.hotel.location) {
      const pos = [day.hotel.location.longitude, day.hotel.location.latitude]
      const marker = new (window as any).AMap.Marker({
        position: pos,
        title: day.hotel.name,
        label: { content: `Day ${dayIdx + 1}: ${day.hotel.name}`, direction: 'top' },
        icon: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png'
      })
      markers.push(marker)
      path.push(pos)
      allPoints.push(pos)
    }

    // 处理景点
    day.attractions.forEach((attr) => {
      const pos = [attr.location.longitude, attr.location.latitude]
      const marker = new (window as any).AMap.Marker({
        position: pos,
        title: attr.name,
        label: { content: attr.name, direction: 'top' }
      })
      markers.push(marker)
      path.push(pos)
      allPoints.push(pos)
    })
    
    if (path.length > 1) {
       dailyPaths.push(path)
    }
  })

  // 绘制路线
  dailyPaths.forEach((path, idx) => {
    const polyline = new (window as any).AMap.Polyline({
      path: path,
      strokeColor: ['#3b82f6', '#ef4444', '#10b981', '#f59e0b'][idx % 4], // 不同天不同颜色
      strokeWeight: 6,
      strokeOpacity: 0.8,
      showDir: true
    })
    polylines.push(polyline)
  })

  map.add(markers)
  map.add(polylines)
  
  // 自动调整视野
  if (allPoints.length > 0) {
    map.setFitView()
  }
}

const submitRequest = async () => {
  loading.value = true
  error.value = null
  tripPlan.value = null
  currentStatus.value = '正在连接 Agent 服务器...'
  
  await travelApi.createStreamPlan(
    request,
    (status) => {
      currentStatus.value = status
    },
    async (finalPlan) => {
      tripPlan.value = finalPlan
      loading.value = false
      // 必须等待 DOM 更新且组件加载后再绘制地图
      await nextTick()
      updateMapMarkers()
    },
    (err) => {
      error.value = err
      loading.value = false
    }
  )
}

onMounted(() => {
  initMap()
})
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden bg-slate-50">
    <!-- 头部 -->
    <header class="bg-white border-b border-slate-200 py-3 px-6 flex justify-between items-center z-10">
      <div class="flex items-center gap-2">
         <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">T</div>
         <h1 class="text-xl font-bold text-slate-800">智能旅行助手 <span class="text-blue-500 text-sm font-normal ml-2">v1.0 (Real-time AI)</span></h1>
      </div>
      <div class="hidden md:block text-slate-400 text-xs">基于 LangGraph & 高德地图 API</div>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <!-- 左侧：输入表单 (固定宽度) -->
      <aside class="w-80 bg-white border-r border-slate-200 p-6 overflow-y-auto hidden md:block">
        <h2 class="text-lg font-bold mb-4 flex items-center gap-2">
          <span class="w-1.5 h-6 bg-blue-600 rounded-full"></span>
          行程设置
        </h2>
        <form @submit.prevent="submitRequest" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1">目的地城市</label>
            <input v-model="request.city" type="text" class="w-full rounded-lg border-slate-200 bg-slate-50 p-2 text-sm focus:ring-blue-500 border" required />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1">开始日期</label>
              <input v-model="request.start_date" type="date" class="w-full rounded-lg border-slate-200 bg-slate-50 p-2 text-xs border" required />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1">结束日期</label>
              <input v-model="request.end_date" type="date" class="w-full rounded-lg border-slate-200 bg-slate-50 p-2 text-xs border" required />
            </div>
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1">旅行偏好</label>
            <textarea v-model="request.preferences" rows="3" class="w-full rounded-lg border-slate-200 bg-slate-50 p-2 text-sm border"></textarea>
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1">预算 & 住宿</label>
            <div class="flex gap-2">
               <select v-model="request.budget" class="flex-1 rounded-lg border-slate-200 bg-slate-50 p-2 text-xs border">
                <option>经济</option>
                <option>中等</option>
                <option>高档</option>
              </select>
               <select v-model="request.accommodation" class="flex-1 rounded-lg border-slate-200 bg-slate-50 p-2 text-xs border">
                <option>青年旅舍</option>
                <option>连锁酒店</option>
                <option>高档酒店</option>
                <option>特色民宿</option>
              </select>
            </div>
          </div>
          <button type="submit" :disabled="loading" class="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all disabled:bg-slate-300">
            {{ loading ? '规划中...' : '生成我的旅行计划' }}
          </button>
        </form>
      </aside>

      <!-- 中间：结果展示 (可滚动) -->
      <main class="flex-1 overflow-y-auto p-6 scroll-smooth">
        <div v-if="loading" class="max-w-2xl mx-auto py-12 text-center">
          <div class="flex flex-col items-center gap-8">
             <div class="relative">
                <div class="w-20 h-20 border-4 border-blue-50 border-t-blue-600 rounded-full animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center text-blue-600 font-bold">AI</div>
             </div>
             <div class="space-y-3">
               <p class="text-blue-600 font-bold text-2xl animate-pulse">{{ currentStatus }}</p>
               <p class="text-slate-400 text-sm">正在整合高德地图数据与 DeepSeek 深度思考...</p>
             </div>
          </div>
        </div>

        <div v-else-if="error" class="max-w-2xl mx-auto bg-red-50 border border-red-200 text-red-700 p-6 rounded-2xl">
          <h3 class="font-bold text-lg mb-2">规划请求失败</h3>
          <p>{{ error }}</p>
        </div>

        <div v-else-if="tripPlan" class="max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
          <!-- 封面卡片 -->
          <div class="relative h-64 rounded-3xl overflow-hidden shadow-2xl group">
             <img :src="tripPlan.days[0].attractions[0]?.image_url || 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&q=80&w=2000'" class="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110" />
             <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
             <div class="absolute bottom-8 left-8 text-white">
                <span class="bg-blue-600 px-3 py-1 rounded-full text-xs font-bold mb-2 inline-block">目的地</span>
                <h2 class="text-4xl font-bold">{{ tripPlan.city }}</h2>
                <p class="text-blue-200 mt-2">{{ tripPlan.start_date }} - {{ tripPlan.end_date }} · {{ tripPlan.days.length }}天完美行程</p>
             </div>
          </div>

          <!-- 每日明细 -->
          <div v-for="day in tripPlan.days" :key="day.day_index" class="space-y-4">
            <div class="flex items-center gap-4">
               <div class="w-12 h-12 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center justify-center">
                  <span class="text-[10px] text-slate-400 font-bold uppercase">Day</span>
                  <span class="text-xl font-bold text-blue-600 leading-none">{{ day.day_index + 1 }}</span>
               </div>
               <div>
                  <h3 class="text-xl font-bold text-slate-800">{{ day.date }}</h3>
                  <p class="text-sm text-slate-500">{{ day.description }}</p>
               </div>
            </div>

            <div class="grid grid-cols-1 gap-4">
              <!-- 酒店 -->
              <div v-if="day.hotel" class="bg-indigo-50/50 p-4 rounded-2xl border border-indigo-100 flex gap-4">
                 <div class="w-32 h-24 rounded-xl overflow-hidden shadow-sm flex-shrink-0">
                    <img :src="day.hotel.image_url" class="w-full h-full object-cover" />
                 </div>
                 <div class="flex-1">
                    <span class="text-[10px] font-bold text-indigo-500 uppercase">入住酒店</span>
                    <h4 class="font-bold text-slate-800 text-lg">{{ day.hotel.name }}</h4>
                    <p class="text-xs text-slate-500 mt-1">{{ day.hotel.address }}</p>
                    <div class="mt-2 flex items-center gap-4 text-[10px]">
                       <span class="text-indigo-600 font-bold">⭐ {{ day.hotel.rating }}</span>
                       <span class="text-slate-400">预估: ¥{{ day.hotel.estimated_cost }}/晚</span>
                    </div>
                 </div>
              </div>

              <!-- 景点 -->
              <div v-for="attr in day.attractions" :key="attr.name" class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm flex flex-col md:flex-row gap-4 hover:shadow-md transition-shadow">
                 <div class="w-full md:w-48 h-32 rounded-xl overflow-hidden flex-shrink-0">
                    <img :src="attr.image_url" class="w-full h-full object-cover" />
                 </div>
                 <div class="flex-1 py-1">
                    <div class="flex justify-between items-start">
                       <span class="text-[10px] font-bold text-orange-500 uppercase">必玩推荐</span>
                       <span class="text-[10px] text-slate-400">建议游览: {{ attr.visit_duration }}min</span>
                    </div>
                    <h4 class="font-bold text-slate-800 text-lg mt-1">{{ attr.name }}</h4>
                    <p class="text-xs text-slate-500 mt-1">{{ attr.address }}</p>
                    <p class="text-sm text-slate-600 mt-3 line-clamp-2 italic leading-relaxed">{{ attr.description }}</p>
                 </div>
              </div>
            </div>
          </div>
          
          <!-- 总体建议 -->
          <div class="bg-slate-900 text-white p-8 rounded-3xl shadow-xl relative overflow-hidden">
             <div class="relative z-10">
                <h3 class="text-xl font-bold mb-4 flex items-center gap-2 text-blue-400">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  专家建议
                </h3>
                <p class="text-slate-300 leading-relaxed">{{ tripPlan.overall_suggestions }}</p>
             </div>
             <div class="absolute top-0 right-0 w-32 h-32 bg-blue-600/20 rounded-full blur-3xl -mr-16 -mt-16"></div>
          </div>
        </div>

        <div v-else class="max-w-2xl mx-auto h-full flex flex-col items-center justify-center text-center px-6">
           <div class="w-32 h-32 bg-blue-50 rounded-full flex items-center justify-center mb-6">
              <svg class="w-16 h-16 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
           </div>
           <h2 class="text-2xl font-bold text-slate-800 mb-2">准备好出发了吗？</h2>
           <p class="text-slate-400 mb-8">填写左侧信息，让 AI 为您生成一份完美的、包含高德实时数据的旅行计划。</p>
        </div>
      </main>

      <!-- 右侧：地图容器 (固定显示) -->
      <section class="w-1/3 bg-slate-200 relative hidden lg:block">
         <div id="map-container" class="w-full h-full"></div>
         <!-- 地图上悬浮的控制提示 -->
         <div class="absolute top-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-2 rounded-lg shadow-sm border border-white/50 text-[10px] font-bold text-slate-600 z-10">
            LIVE MAP
         </div>
      </section>
    </div>
  </div>
</template>

<style>
/* 高德地图 Marker Label 样式 */
.amap-marker-label {
  border: none !important;
  background-color: #3b82f6 !important;
  color: white !important;
  padding: 4px 8px !important;
  border-radius: 6px !important;
  font-size: 10px !important;
  font-weight: bold !important;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

#map-container {
  background-color: #f1f5f9;
}
</style>
