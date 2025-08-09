<template>
  <v-dialog :model-value="modelValue" max-width="600px" @update:model-value="$emit('update:modelValue', $event)">
    <v-card>
      <v-card-title class="text-h5 pa-4 d-flex justify-center align-center">
        <v-icon class="mr-2">mdi-calendar-tomorrow</v-icon>
        Tomorrow's Events
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text class="pa-4">
        <div v-if="tomorrowEvents.length === 0" class="text-center py-8">
          <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-calendar-blank</v-icon>
          <p class="text-h6 text-grey">No events scheduled for tomorrow</p>
        </div>
        
        <div v-else class="events-list">
          <div
            v-for="event in tomorrowEvents"
            :key="event.id"
            class="event-item-modal mb-3"
          >
            <div class="d-flex align-center">
              <v-icon class="mr-3" color="primary">mdi-clock-outline</v-icon>
              <div class="flex-grow-1">
                <div class="text-h6">{{ event.title }}</div>
                <div class="text-body-2 text-grey">
                  {{ formatEventTime(event.start) }}
                  <span v-if="event.location" class="ml-2">
                    <v-icon size="small">mdi-map-marker</v-icon>
                    {{ event.location }}
                  </span>
                </div>
                <div v-if="event.description" class="text-body-2 mt-1">
                  {{ event.description }}
                </div>
              </div>
            </div>
            <v-divider v-if="event !== tomorrowEvents[tomorrowEvents.length - 1]" class="mt-3"></v-divider>
          </div>
        </div>
      </v-card-text>
      
      <v-divider></v-divider>
      
      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          variant="text"
          @click="$emit('update:modelValue', false)"
        >
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  tomorrowEvents: Array,
  formatEventTime: Function
})

defineEmits(['update:modelValue'])
</script>
