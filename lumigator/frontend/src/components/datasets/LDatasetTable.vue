<template>
  <div class="l-dataset-table">
    <transition name="transition-fade" mode="out-in">
      <DataTable
        v-if="tableData.length"
        v-model:selection="focusedItem"
        selectionMode="single"
        dataKey="id"
        :value="tableData"
        :tableStyle="style"
        columnResizeMode="expand"
        sortField="created_at"
        :sortOrder="-1"
        scrollable
        scrollHeight="75vh"
        :pt="{ table: 'table-root' }"
        :loading="isLoading"
        @row-click="emit('l-dataset-selected', $event.data)"
        @row-unselect="showSlidingPanel = false"
      >
        <Column field="filename" header="Filename" />
        <Column field="id" header="dataset id">
          <template #body="slotProps">
            {{ shortenID(slotProps.data.id) }}
          </template>
        </Column>
        <Column field="created_at" header="submitted">
          <template #body="slotProps">
            {{ formatDate(slotProps.data.created_at) }}
          </template>
        </Column>
        <Column field="size" header="size">
          <template #body="slotProps"> {{ Math.floor(slotProps.data.size / 1000) }} KB </template>
        </Column>
        <Column field="ground_truth" header="Ground Truth">
          <template #body="slotProps">
            <span class="capitalize">
              {{ slotProps.data.generated ? 'True (AI Generated)' : slotProps.data.ground_truth }}
            </span>
          </template>
        </Column>
        <Column header="options">
          <template #body="slotProps">
            <span
              class="pi pi-fw pi-ellipsis-h l-dataset-table__options-trigger"
              aria-controls="optionsMenu"
              @click.stop="togglePopover($event, slotProps.data)"
            ></span>
          </template>
        </Column>
      </DataTable>
    </transition>

    <Menu
      id="options_menu"
      ref="optionsMenu"
      :model="options"
      :popup="true"
      :pt="ptConfigOptionsMenu"
    >
    </Menu>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Menu from 'primevue/menu'
import { useSlidePanel } from '@/composables/useSlidePanel'
import type { MenuItem } from 'primevue/menuitem'
import type { Dataset } from '@/types/Dataset'
import { formatDate } from '@/helpers/formatDate'

defineProps({
  tableData: {
    type: Array,
    required: true,
  },
  isLoading: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits([
  'l-delete-dataset',
  'l-dataset-selected',
  'use-in-experiment-clicked',
  'l-download-dataset',
  'view-dataset-clicked',
])

const { showSlidingPanel } = useSlidePanel()
const style = computed(() => {
  return showSlidingPanel.value ? 'min-width: 40vw' : 'min-width: min(80vw, 1200px)'
})

const focusedItem = ref()
const optionsMenu = ref()
const options = ref<MenuItem[]>([
  {
    label: 'Use in Experiment',
    icon: 'pi pi-experiments',
    disabled: false,
    command: () => {
      emit('use-in-experiment-clicked', focusedItem.value)
    },
  },
  {
    separator: true,
  },
  {
    label: 'View',
    icon: 'pi pi-external-link',
    command: () => {
      emit('view-dataset-clicked', focusedItem.value)
    },
  },
  {
    label: 'Download',
    icon: 'pi pi-download',
    command: () => {
      emit('l-download-dataset', focusedItem.value)
    },
  },
  {
    label: 'Delete',
    icon: 'pi pi-trash',
    command: () => {
      emit('l-delete-dataset', focusedItem.value)
    },
  },
])

const ptConfigOptionsMenu = ref({
  list: 'l-dataset-table__options-menu',
  itemLink: 'l-dataset-table__menu-option',
  itemIcon: 'l-dataset-table__menu-option-icon',
  separator: 'separator',
})

const shortenID = (id: string) => (id.length <= 20 ? id : `${id.slice(0, 20)}...`)

const togglePopover = (event: MouseEvent, dataset: Dataset) => {
  focusedItem.value = dataset
  const experimentOption = options.value.find((option) => option.label === 'Use in Experiment')
  if (experimentOption) {
    experimentOption.disabled = !dataset.ground_truth
  }
  optionsMenu.value.toggle(event)
}

watch(showSlidingPanel, (newValue) => {
  focusedItem.value = newValue ? focusedItem.value : undefined
})
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-dataset-table {
  $root: &;
  width: 100%;
  display: flex;
  place-content: center;

  & .p-datatable {
    width: 100%;
  }

  &__options-trigger {
    padding: 0;
    margin-left: 20% !important;
  }
}
</style>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

//  In order to have effect the following
// css rules must not be "scoped" because
// the popup-menu is attached to the DOM after the
// parent component is mounted
.l-dataset-table__options-menu {
  padding: 0 $l-spacing-1;
}

.l-dataset-table__menu-option {
  color: $l-grey-100;
  padding: $l-spacing-1 $l-spacing-1 $l-spacing-1 0 $l-spacing-1;
  font-size: $l-menu-font-size;

  &:hover {
    color: white;
  }

  &-icon,
  span.pi {
    color: $l-grey-100;
    font-size: $l-font-size-sm;
  }
}

.separator {
  padding: calc($l-spacing-1 / 2) 0;
}

.l-dataset-table__options-menu > :first-child .l-dataset-table__menu-option {
  padding-bottom: 1rem;
  padding-top: 0rem;
}
</style>
