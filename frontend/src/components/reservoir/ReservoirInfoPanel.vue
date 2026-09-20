<script setup>
import StatusTag from '@/components/common/StatusTag.vue'
import { useDictionaryStore } from '@/stores/dictionary'
import { formatDate, formatNumber } from '@/utils/format'

defineProps({
  reservoir: { type: Object, required: true },
})

const dictionary = useDictionaryStore()
</script>

<template>
  <section class="card">
    <header class="card-header">
      <div>
        <div class="card-title">工程台账信息</div>
        <div class="card-subtitle">更新于 {{ formatDate(reservoir.updated_at) }}</div>
      </div>
      <StatusTag kind="reservoir_status" :value="reservoir.status" />
    </header>
    <div class="card-body">
      <dl class="def-list">
        <div class="def-item">
          <dt>水库编码</dt>
          <dd class="mono">{{ reservoir.code }}</dd>
        </div>
        <div class="def-item">
          <dt>水库名称</dt>
          <dd>{{ reservoir.name }}</dd>
        </div>
        <div class="def-item">
          <dt>行政区</dt>
          <dd>{{ reservoir.region }}</dd>
        </div>
        <div class="def-item">
          <dt>所属流域</dt>
          <dd>{{ reservoir.basin || '—' }}</dd>
        </div>
        <div class="def-item">
          <dt>坝型</dt>
          <dd>{{ dictionary.labelOf('dam_type', reservoir.dam_type) }}</dd>
        </div>
        <div class="def-item">
          <dt>安全类别</dt>
          <dd><StatusTag kind="safety_class" :value="reservoir.safety_class" /></dd>
        </div>
        <div class="def-item">
          <dt>总库容</dt>
          <dd>{{ formatNumber(reservoir.total_capacity) }} 万 m³</dd>
        </div>
        <div class="def-item">
          <dt>正常蓄水位</dt>
          <dd>{{ formatNumber(reservoir.normal_level) }} m</dd>
        </div>
        <div class="def-item">
          <dt>汛限水位</dt>
          <dd>{{ formatNumber(reservoir.flood_limit_level) }} m</dd>
        </div>
        <div class="def-item">
          <dt>最大坝高</dt>
          <dd>{{ formatNumber(reservoir.dam_height) }} m</dd>
        </div>
        <div class="def-item">
          <dt>坝顶长度</dt>
          <dd>{{ formatNumber(reservoir.dam_length) }} m</dd>
        </div>
        <div class="def-item">
          <dt>建成年份</dt>
          <dd>{{ reservoir.build_year || '—' }}</dd>
        </div>
        <div class="def-item">
          <dt>管理单位</dt>
          <dd>{{ reservoir.manager || '—' }}</dd>
        </div>
        <div class="def-item">
          <dt>责任人电话</dt>
          <dd>{{ reservoir.manager_phone || '—' }}</dd>
        </div>
        <div class="def-item full">
          <dt>坝址位置</dt>
          <dd>{{ reservoir.location || '—' }}</dd>
        </div>
        <div class="def-item full">
          <dt>备注</dt>
          <dd>{{ reservoir.remark || '—' }}</dd>
        </div>
      </dl>
    </div>
  </section>
</template>

