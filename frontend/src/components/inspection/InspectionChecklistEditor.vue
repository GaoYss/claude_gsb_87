<script setup>
import { useDictionaryStore } from '@/stores/dictionary'

const model = defineModel({ type: Array, required: true })
const dictionary = useDictionaryStore()

function addItem() {
  model.value = [...model.value, { part: 'dam_body', result: 'normal', description: '' }]
}

function removeItem(index) {
  model.value = model.value.filter((_, position) => position !== index)
}

function updateItem(index, key, value) {
  model.value = model.value.map((item, position) =>
    position === index ? { ...item, [key]: value } : item,
  )
}

function markAllNormal() {
  model.value = model.value.map((item) => ({ ...item, result: 'normal' }))
}
</script>

<template>
  <div>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 190px">检查部位</th>
            <th style="width: 130px">检查结果</th>
            <th>情况说明（异常必填）</th>
            <th style="width: 80px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!model.length">
            <td class="table-state" colspan="4">尚未添加巡查项，可点击下方按钮逐项录入</td>
          </tr>
          <tr v-for="(item, index) in model" :key="index">
            <td>
              <select
                class="select"
                :value="item.part"
                @change="updateItem(index, 'part', $event.target.value)"
              >
                <option v-for="option in dictionary.options('structure_part')" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </td>
            <td>
              <select
                class="select"
                :value="item.result"
                @change="updateItem(index, 'result', $event.target.value)"
              >
                <option v-for="option in dictionary.options('item_result')" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </td>
            <td>
              <input
                class="input"
                :value="item.description || ''"
                placeholder="正常项可留空"
                @input="updateItem(index, 'description', $event.target.value)"
              />
            </td>
            <td>
              <button class="btn-link danger" type="button" @click="removeItem(index)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="row-gap" style="margin-top: 12px">
      <button class="btn btn-sm" type="button" @click="addItem">添加巡查项</button>
      <button class="btn btn-sm" type="button" :disabled="!model.length" @click="markAllNormal">
        全部标记为正常
      </button>
      <span v-if="model.some((item) => item.result === 'abnormal')" class="muted">
        存在异常项，保存后可立即登记隐患
      </span>
    </div>
  </div>
</template>

