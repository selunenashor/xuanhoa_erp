<template>
  <Teleport to="body">
    <Transition name="modal">
      <div 
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="onCancel"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
        
        <!-- Modal -->
        <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-md transform transition-all">
          <!-- Header -->
          <div class="flex items-start gap-4 p-6 pb-4">
            <!-- Icon -->
            <div :class="[
              'flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center',
              iconBgClass
            ]">
              <!-- Warning Icon -->
              <svg v-if="type === 'warning'" class="w-6 h-6 text-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <!-- Danger Icon -->
              <svg v-else-if="type === 'danger'" class="w-6 h-6 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <!-- Success/Confirm Icon -->
              <svg v-else-if="type === 'success'" class="w-6 h-6 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <!-- Info Icon (default) -->
              <svg v-else class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            
            <!-- Title & Message -->
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
              <p class="mt-1 text-sm text-gray-600 whitespace-pre-line">{{ message }}</p>
            </div>
            
            <!-- Close button -->
            <button 
              @click="onCancel"
              class="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <!-- Actions -->
          <div class="flex justify-end gap-3 px-6 py-4 bg-gray-50 rounded-b-xl">
            <button
              v-if="cancelText"
              @click="onCancel"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              {{ cancelText }}
            </button>
            <button
              @click="onConfirm"
              :disabled="loading"
              :class="[
                'px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50',
                confirmBtnClass
              ]"
            >
              <svg v-if="loading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Xác nhận'
  },
  message: {
    type: String,
    default: 'Bạn có chắc chắn muốn thực hiện hành động này?'
  },
  type: {
    type: String,
    default: 'info', // info, warning, danger, success
    validator: (v) => ['info', 'warning', 'danger', 'success'].includes(v)
  },
  confirmText: {
    type: String,
    default: 'Xác nhận'
  },
  cancelText: {
    type: String,
    default: 'Hủy'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const iconBgClass = computed(() => {
  const classes = {
    info: 'bg-primary/10',
    warning: 'bg-warning/10',
    danger: 'bg-error/10',
    success: 'bg-success/10'
  }
  return classes[props.type] || classes.info
})

const confirmBtnClass = computed(() => {
  const classes = {
    info: 'bg-primary hover:bg-primary-dark',
    warning: 'bg-warning hover:bg-warning-dark',
    danger: 'bg-error hover:bg-error-dark',
    success: 'bg-success hover:bg-success-dark'
  }
  return classes[props.type] || classes.info
})

const onConfirm = () => {
  emit('confirm')
}

const onCancel = () => {
  emit('update:modelValue', false)
  emit('cancel')
}
</script>

<style scoped>
/* Modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.2s ease;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.95);
}

/* Colors */
.bg-primary { background-color: #055568; }
.bg-primary-dark { background-color: #044454; }
.bg-primary\/10 { background-color: rgba(5, 85, 104, 0.1); }
.text-primary { color: #055568; }
.hover\:bg-primary-dark:hover { background-color: #044454; }

.bg-success { background-color: #4CAF50; }
.bg-success-dark { background-color: #388E3C; }
.bg-success\/10 { background-color: rgba(76, 175, 80, 0.1); }
.text-success { color: #4CAF50; }
.hover\:bg-success-dark:hover { background-color: #388E3C; }

.bg-warning { background-color: #FF9800; }
.bg-warning-dark { background-color: #F57C00; }
.bg-warning\/10 { background-color: rgba(255, 152, 0, 0.1); }
.text-warning { color: #FF9800; }
.hover\:bg-warning-dark:hover { background-color: #F57C00; }

.bg-error { background-color: #f44336; }
.bg-error-dark { background-color: #d32f2f; }
.bg-error\/10 { background-color: rgba(244, 67, 54, 0.1); }
.text-error { color: #f44336; }
.hover\:bg-error-dark:hover { background-color: #d32f2f; }
</style>
