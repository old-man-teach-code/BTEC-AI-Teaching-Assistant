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
            required
          />

          <v-combobox
            v-model="localEvent.type"
            :items="eventTypes"
            label="Loại sự kiện"
            :rules="[(v) => !!v || 'Vui lòng chọn loại sự kiện']"
            clearable
            required
            hide-no-data
            hide-selected
          />

          <v-text-field
            v-model="localEvent.startTime"
            label="Thời gian bắt đầu"
            type="datetime-local"
            :rules="[(v) => !!v || 'Bắt đầu là bắt buộc']"
            required
          />

          <v-text-field
            v-model="localEvent.endTime"
            label="Thời gian kết thúc"
            type="datetime-local"
            :rules="[validateEndAfterStart]"
            required
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
  eventData: Object,
})
const eventTypes =ref( ['Cuộc họp', 'Thuyết trình', 'Thi cử', 'Báo cáo', 'Sinh hoạt', 'Workshop'])


const emit = defineEmits(['update:modelValue', 'save', 'delete'])

const internalDialog = ref(props.modelValue)
const formValid = ref(true)
const formRef = ref(null)
const localEvent = ref({})

watch(
  () => props.modelValue,
  (val) => {
    internalDialog.value = val
    if (val && props.eventData) {
      localEvent.value = {
        ...props.eventData,
        startTime: toDatetimeLocalInput(props.eventData.start),
        endTime: toDatetimeLocalInput(props.eventData.end),
      }
    }
  }
)
function toDatetimeLocalInput(date) {
  if (!(date instanceof Date)) date = new Date(date)
  const yyyy = date.getFullYear()
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  const hh = String(date.getHours()).padStart(2, '0')
  const mi = String(date.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}T${hh}:${mi}`
}

watch(internalDialog, (val) => emit('update:modelValue', val))
watch(() => localEvent.value.type, (newType) => {
  if (newType && !eventTypes.value.includes(newType)) {
    eventTypes.value.push(newType)
  }
})
const isEditMode = computed(() => !!localEvent.value?.id)

const validateEndAfterStart = (v) => {
  if (!v) return 'Thời gian kết thúc là bắt buộc'
  if (localEvent.value.startTime && v < localEvent.value.startTime)
    return 'Kết thúc phải sau bắt đầu'
  return true
}

const formatLocalDatetime = (datetimeStr) => {
  const date = new Date(datetimeStr)
  const yyyy = date.getFullYear()
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  const hh = String(date.getHours()).padStart(2, '0')
  const mi = String(date.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
}


const handleSave = () => {
  if (!formRef.value?.validate()) return

  emit('save', {
    ...localEvent.value,
    start: formatLocalDatetime(localEvent.value.startTime),
    end: formatLocalDatetime(localEvent.value.endTime),
    
  })

  internalDialog.value = false
}

const close = () => {
  internalDialog.value = false
}
function handleDelete() {
  emit('delete', localEvent.value.id)
  internalDialog.value = false
}


</script>
