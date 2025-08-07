<template>
  <v-dialog v-model="internalDialog" max-width="550" @keydown.esc="close">
    <v-card>
      <v-card-title>{{ isEditMode ? 'Edit Event' : 'Create New Event' }}</v-card-title>

      <v-card-text>
        <v-form ref="formRef" v-model="formValid">
          <v-text-field
            v-model="localEvent.title"
            label="Title"
            :rules="[(v) => !!v || 'Title is required']"
            required
          />
             <v-text-field
            v-model="localEvent.description"
            label="Discription"
            :rules="[(v) => !!v || 'Discription is required']"
            required
          />

          <v-combobox
            v-model="localEvent.type"
            :items="eventTypes"
            label="Event Type"
            :rules="[(v) => !!v || 'Please select an event type']"
            clearable
            required
            hide-no-data
            hide-selected
          />

          <v-text-field
            v-model="localEvent.startTime"
            label="Start Time"
            type="datetime-local"
            :rules="[(v) => !!v || 'Start time is required']"
            required
          />

          <v-text-field
            v-model="localEvent.endTime"
            label="End Time"
            type="datetime-local"
            :rules="[validateEndAfterStart]"
            required
          />

          <v-text-field v-model="localEvent.location" label="Location" />
          <v-text-field
            v-model.number="localEvent.remind"
            label="Reminder (minutes before)"
            type="number"
            :rules="[(v) => v >= 0 || 'Must be a non-negative number']"
          />
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-btn color="error" @click="handleDelete" v-if="isEditMode">Delete</v-btn>
        <v-spacer />
        <v-btn color="primary" @click="handleSave">Save</v-btn>
        <v-btn text @click="close">Cancel</v-btn>
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
const eventTypes = ref(['Meeting', 'Presentation', 'Exam', 'Report', 'Activity', 'Workshop', 'Other'])

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
  if (!v) return 'End time is required'
  if (localEvent.value.startTime && v < localEvent.value.startTime)
    return 'End time must be after start time'
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

<style>
.v-dialog {
  width: 90%;
  max-width: 550px;
}
.v-card-title {
  margin: 10px 0 0 0;
  font-size: 1.6em;
  font-weight: bold;
  text-align: center;
}

/* Responsive styling for all devices */
@media (max-width: 600px) {
  v-dialog {
    width: 90%;
    max-width: 300px;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  v-field__field {
    font-size: 12px;
  }
}
</style>
