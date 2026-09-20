<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { addRectification, deleteHazard, fetchHazard, transitionHazard } from '@/api/hazards'
import BaseCard from '@/components/common/BaseCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import RectificationForm from '@/components/hazard/RectificationForm.vue'
import RectificationTimeline from '@/components/hazard/RectificationTimeline.vue'
import HazardStatusActions from '@/components/hazard/HazardStatusActions.vue'
import { useConfirmStore } from '@/stores/confirm'
import { useDictionaryStore } from '@/stores/dictionary'
import { useToastStore } from '@/stores/toast'
import { deadlineHint, formatDate } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()
const confirm = useConfirmStore()
const dictionary = useDictionaryStore()

const hazard = ref(null)
const loading = ref(true)
const submitting = ref(false)

async function load() {
  loading.value = true
  try {
    hazard.value = await fetchHazard(route.params.id)
  } catch (error) {
    toast.error(error.message)
    router.replace({ name: 'hazard-list' })
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function onTransition(payload) {
  submitting.value = true
  try {
    hazard.value = await transitionHazard(hazard.value.id, payload)
    toast.success('隐患状态已更新')
  } catch (error) {
    toast.error(error.message)
  } finally {
    submitting.value = false
  }
}

async function onAddRecord(payload) {
  submitting.value = true
  try {
    hazard.value = await addRectification(hazard.value.id, payload)
    toast.success('整改跟踪记录已追加')
  } catch (error) {
    toast.error(error.message)
  } finally {
    submitting.value = false
  }
}

async function remove() {
  const ok = await confirm.ask(`确认删除隐患「${hazard.value.title}」？关联的整改记录会一并删除。`)
  if (!ok) return
  try {
    await deleteHazard(hazard.value.id)
    toast.success('隐患已删除')
    router.replace({ name: 'hazard-list' })
  } catch (error) {
    toast.error(error.message)
  }
}
</script>

<template>
  <div v-if="loading" class="muted">加载中…</div>
  <div v-else-if="hazard">
    <PageHeader
      :title="hazard.title"
      :description="`${hazard.code} · ${hazard.reservoir?.name || '未知水库'}`"
    >
      <template #badge>
        <StatusTag kind="hazard_status" :value="hazard.status" />
        <StatusTag kind="hazard_severity" :value="hazard.severity" />
        <span v-if="hazard.is_overdue" class="tag tag-overdue">逾期未整改</span>
      </template>
      <template #actions>
        <RouterLink class="btn" :to="`/hazards/${hazard.id}/edit`">编辑</RouterLink>
        <button class="btn btn-danger" type="button" @click="remove">删除</button>
      </template>
    </PageHeader>

    <div class="split-2">
      <div>
        <BaseCard title="隐患信息">
          <dl class="def-list">
            <div class="def-item">
              <dt>所属水库</dt>
              <dd>
                <RouterLink :to="`/reservoirs/${hazard.reservoir_id}`">
                  {{ hazard.reservoir?.name }}
                </RouterLink>
              </dd>
            </div>
            <div class="def-item">
              <dt>隐患类别</dt>
              <dd>{{ dictionary.labelOf('structure_part', hazard.category) }}</dd>
            </div>
            <div class="def-item">
              <dt>隐患等级</dt>
              <dd>{{ dictionary.labelOf('hazard_severity', hazard.severity) }}</dd>
            </div>
            <div class="def-item">
              <dt>隐患来源</dt>
              <dd>{{ dictionary.labelOf('hazard_source', hazard.source) }}</dd>
            </div>
            <div class="def-item">
              <dt>发现日期</dt>
              <dd>{{ formatDate(hazard.discovered_on) }}</dd>
            </div>
            <div class="def-item">
              <dt>发现人</dt>
              <dd>{{ hazard.discoverer || '—' }}</dd>
            </div>
            <div class="def-item">
              <dt>整改期限</dt>
              <dd>
                {{ formatDate(hazard.deadline) }}
                <span class="muted">（{{ deadlineHint(hazard.deadline, hazard.status === 'closed') }}）</span>
              </dd>
            </div>
            <div class="def-item">
              <dt>销号日期</dt>
              <dd>{{ formatDate(hazard.closed_on) }}</dd>
            </div>
            <div class="def-item">
              <dt>整改责任人</dt>
              <dd>{{ hazard.assignee || '—' }}</dd>
            </div>
            <div class="def-item">
              <dt>来源巡查</dt>
              <dd>
                <RouterLink v-if="hazard.inspection_id" :to="`/inspections/${hazard.inspection_id}`">
                  查看巡查记录
                </RouterLink>
                <span v-else class="muted">未关联</span>
              </dd>
            </div>
            <div class="def-item full">
              <dt>隐患描述</dt>
              <dd>{{ hazard.description || '—' }}</dd>
            </div>
            <div class="def-item full">
              <dt>整改要求</dt>
              <dd>{{ hazard.plan || '—' }}</dd>
            </div>
          </dl>
        </BaseCard>

        <BaseCard
          title="整改跟踪"
          :subtitle="`共 ${hazard.rectifications.length} 条记录，按时间顺序排列`"
        >
          <RectificationTimeline :records="hazard.rectifications" />
        </BaseCard>
      </div>

      <div>
        <HazardStatusActions
          :status="hazard.status"
          :assignee="hazard.assignee"
          :submitting="submitting"
          @submit="onTransition"
        />
        <BaseCard title="追加整改记录" subtitle="用于补充措施、进展、验收等过程材料">
          <RectificationForm
            :submitting="submitting"
            :assignee="hazard.assignee"
            :disabled="hazard.status === 'closed'"
            @submit="onAddRecord"
          />
        </BaseCard>
      </div>
    </div>
  </div>
</template>

