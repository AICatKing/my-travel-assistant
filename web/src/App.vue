<script setup lang="ts">
import { ref, reactive } from 'vue'
import { travelApi } from './api'
import type { TripPlan, TripPlanRequest } from './types'

const loading = ref(false)
const error = ref<string | null>(null)
const tripPlan = ref<TripPlan | null>(null)

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

const submitRequest = async () => {
  loading.value = true
  error.value = null
  tripPlan.value = null
  
  try {
    const result = await travelApi.createPlan(request)
    tripPlan.value = result
  } catch (err: any) {
    console.error(err)
    error.value = err.response?.data?.detail || err.message || '生成计划失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen p-4 md:p-8 max-w-5xl mx-auto">
    <header class="mb-8 text-center">
      <h1 class="text-3xl font-bold text-blue-600 mb-2">智能旅行助手</h1>
      <p class="text-slate-500">规划您的下一段完美旅程</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- 输入表单 -->
      <aside class="md:col-span-1">
        <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h2 class="text-xl font-semibold mb-4 border-b pb-2">行程设置</h2>
          <form @submit.prevent="submitRequest" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700">目的地城市</label>
              <input v-model="request.city" type="text" class="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-slate-50 p-2 border" required />
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-sm font-medium text-slate-700">开始日期</label>
                <input v-model="request.start_date" type="date" class="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-slate-50 p-2 border text-sm" required />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700">结束日期</label>
                <input v-model="request.end_date" type="date" class="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-slate-50 p-2 border text-sm" required />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700">旅行偏好</label>
              <textarea v-model="request.preferences" rows="3" class="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-slate-50 p-2 border"></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700">预算范围</label>
              <select v-model="request.budget" class="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-slate-50 p-2 border">
                <option>经济</option>
                <option>中等</option>
                <option>高档</option>
              </select>
            </div>
            <button type="submit" :disabled="loading" class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-300 transition-colors">
              {{ loading ? '生成中...' : '开始生成计划' }}
            </button>
          </form>
        </div>
      </aside>

      <!-- 结果展示 -->
      <main class="md:col-span-2">
        <div v-if="loading" class="bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center animate-pulse">
          <div class="h-8 bg-slate-200 rounded w-3/4 mx-auto mb-4"></div>
          <div class="h-4 bg-slate-100 rounded w-full mb-2"></div>
          <div class="h-4 bg-slate-100 rounded w-5/6 mb-2"></div>
          <p class="mt-4 text-blue-500 font-medium">Agent 正在为您规划行程，请耐心等待...</p>
        </div>

        <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl">
          <h3 class="font-bold">发生错误</h3>
          <p>{{ error }}</p>
        </div>

        <div v-else-if="tripPlan" class="space-y-6">
          <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h2 class="text-2xl font-bold text-slate-800">{{ tripPlan.city }}之旅</h2>
            <p class="text-slate-500">{{ tripPlan.start_date }} 至 {{ tripPlan.end_date }}</p>
            <div class="mt-4 p-4 bg-blue-50 rounded-lg text-blue-800 italic">
              {{ tripPlan.overall_suggestions }}
            </div>
          </div>

          <!-- 每日行程 -->
          <div v-for="day in tripPlan.days" :key="day.day_index" class="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 class="text-xl font-bold text-slate-800 mb-2">第 {{ day.day_index + 1 }} 天: {{ day.date }}</h3>
            <p class="text-slate-600 mb-4">{{ day.description }}</p>
            
            <div class="space-y-4">
              <div v-for="attraction in day.attractions" :key="attraction.name" class="flex flex-col md:flex-row gap-4 p-4 bg-slate-50 rounded-xl border border-slate-100 overflow-hidden">
                <div v-if="attraction.image_url" class="w-full md:w-48 h-32 flex-shrink-0">
                  <img :src="attraction.image_url" :alt="attraction.name" class="w-full h-full object-cover rounded-lg shadow-sm" />
                </div>
                <div v-else class="w-full md:w-48 h-32 flex-shrink-0 bg-slate-200 rounded-lg flex items-center justify-center text-slate-400">
                   <span class="text-xs">无图片</span>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="bg-orange-500 text-white px-2 py-0.5 rounded text-[10px] font-bold uppercase">景点</span>
                    <h4 class="font-bold text-lg">{{ attraction.name }}</h4>
                  </div>
                  <p class="text-sm text-slate-500 mb-2">{{ attraction.address }}</p>
                  <p class="text-sm text-slate-600 line-clamp-2 italic">{{ attraction.description }}</p>
                </div>
              </div>

              <div v-if="day.hotel" class="flex flex-col md:flex-row gap-4 p-4 bg-indigo-50 rounded-xl border border-indigo-100 overflow-hidden">
                <div v-if="day.hotel.image_url" class="w-full md:w-48 h-32 flex-shrink-0">
                  <img :src="day.hotel.image_url" :alt="day.hotel.name" class="w-full h-full object-cover rounded-lg shadow-sm" />
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="bg-indigo-600 text-white px-2 py-0.5 rounded text-[10px] font-bold uppercase">住宿</span>
                    <h4 class="font-bold text-lg">{{ day.hotel.name }}</h4>
                  </div>
                  <p class="text-sm text-slate-500">{{ day.hotel.address }}</p>
                  <p class="text-sm text-indigo-700 mt-2 font-medium">评分: {{ day.hotel.rating }} | 预估: ¥{{ day.hotel.estimated_cost }}/晚</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="bg-slate-100 p-12 rounded-xl border-2 border-dashed border-slate-300 text-center text-slate-500">
          <p class="text-lg">在左侧填写信息并点击“开始生成计划”</p>
        </div>
      </main>
    </div>
  </div>
</template>

<style>
/* 引用我们在 src/style.css 定义的 Tailwind 指令 */
</style>
