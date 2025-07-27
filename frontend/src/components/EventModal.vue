<template>
  <v-dialog v-model="internalDialog" max-width="600" @keydown.esc="close">
    <v-card>
      <v-card-title>{{ isEditMode ? 'Chỉnh sửa sự kiện' : 'Tạo sự kiện mới' }}</v-card-title>
      <v-card-text>
        <v-form ref="formRef" v-model="formValid">
          <v-text-field
            v-model="localEvent.title"
            label="Tiêu đề"
            :rules="[(v) => !!v || 'Tiêu đề là bắt buộc']"
          />
          <v-combobox
            v-model="localEvent.type"
            label="Loại sự kiện"
            :items="Object.keys(typeColorMap)"
            :rules="[(v) => !!v || 'Vui lòng chọn loại sự kiện']"
            clearable
          />
          <v-text-field
            v-model="localEvent.startTime"
            label="Thời gian bắt đầu"
            type="datetime-local"
            :rules="[validateStartBeforeEnd]"
          />

          <v-text-field
            v-model="localEvent.endTime"
            label="Thời gian kết thúc"
            type="datetime-local"
            :rules="[validateEndAfterStart]"
          />

          <v-text-field v-model="localEvent.location" label="Địa điểm" />
          <v-text-field
            v-model.number="localEvent.remind"
            label="Nhắc trước (phút)"
            type="number"
            :rules="[(v) => v >= 0 || 'Phải là số không âm']"
          />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="error" @click="handleDelete" v-if="isEditMode">Xoá</v-btn>
        <v-spacer />
        <v-btn color="primary" @click="handleSave">Lưu</v-btn>
        <v-btn text @click="close">Huỷ</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  eventData: { type: Object, default: () => ({}) },
  typeColorMap: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue', 'save', 'delete'])

const internalDialog = ref(false)
watch(
  () => props.modelValue,
  (v) => (internalDialog.value = v)
)
watch(
  () => internalDialog.value,
  (v) => emit('update:modelValue', v)
)

const localEvent = ref({ ...props.eventData })
watch(
  () => props.eventData,
  (val) => {
    localEvent.value = { ...val }

    // Định dạng lại nếu là Date object
    if (val.start instanceof Date) {
      localEvent.value.startTime = formatDatetime(val.start)
      localEvent.value.endTime = formatDatetime(val.end)
    } else {
      localEvent.value.startTime = val.start || ''
      localEvent.value.endTime = val.end || ''
    }
  }
)

function formatDatetime(date) {
  const d = new Date(date)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}T${hh}:${min}`
}

const isEditMode = computed(() => !!localEvent.value?.id)

const formRef = ref(null)
const formValid = ref(true)



function validateStartBeforeEnd() {
  const s = new Date(localEvent.value.startTime.replace(' ', 'T'))
  const e = new Date(localEvent.value.endTime.replace(' ', 'T'))
  if (s >= e) return 'Thời gian bắt đầu phải trước thời gian kết thúc'
  return true
}
function validateEndAfterStart() {
  return validateStartBeforeEnd()
}

function handleSave() {
  formRef.value.validate().then((ok) => {
    if (!ok) return
    emit('save', {
      ...localEvent.value,
      start: localEvent.value.startTime,
      end: localEvent.value.endTime,
    })
  })
}

function handleDelete() {
  emit('delete', localEvent.value.id)
  internalDialog.value = false
}

function close() {
  internalDialog.value = false
}
</script>