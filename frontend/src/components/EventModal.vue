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
            label="Loại sự kiện"
            :items="Object.keys(typeColorMap)"
            :rules="[(v) => !!v || 'Vui lòng chọn loại sự kiện']"
            clearable
            required
          />

          <v-text-field
            v-model="localEvent.startTime"
            label="Thời gian bắt đầu"
            type="datetime-local"
            :rules="[validateStartBeforeEnd]"
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
  eventData: { type: Object, default: () => ({}) },
  typeColorMap: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue', 'save', 'delete'])

const internalDialog = ref(false)
watch(() => props.modelValue, (v) => internalDialog.value = v)
watch(() => internalDialog.value, (v) => emit('update:modelValue', v))

const localEvent = ref({ ...props.eventData })

watch(() => props.eventData, (val) => {
  localEvent.value = {
    ...val,
    startTime: formatDatetime(val.start),
    endTime: formatDatetime(val.end),
  }
})

// format "yyyy-MM-ddTHH:mm"
function formatDatetime(input) {
  if (!input) return ''
  const date = new Date(input)
  if (isNaN(date)) return ''
  return date.toISOString().slice(0, 16)
}

const isEditMode = computed(() => !!localEvent.value?.id)
const formRef = ref(null)
const formValid = ref(true)

function validateStartBeforeEnd() {
  const s = new Date(localEvent.value.startTime)
  const e = new Date(localEvent.value.endTime)
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
      start: new Date(localEvent.value.startTime).toISOString(),
      end: new Date(localEvent.value.endTime).toISOString(),
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
