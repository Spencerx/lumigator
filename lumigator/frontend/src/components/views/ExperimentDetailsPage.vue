<template>
  <div class="experiment-details-page">
    <div class="breadcrumbs">
      <i class="pi pi-arrow-left back-button" @click="handleBackButtonClicked"></i>
      <Breadcrumb :model="items">
        <template #separator> / </template>
      </Breadcrumb>
    </div>

    <Tabs :value="activeTab || defaultActiveTab" @update:value="activeTab = String($event)">
      <div class="experiment-container">
        <div class="experiment-details-header">
          <h3 class="experiment-title"><i class="pi pi-experiments"></i>{{ experiment?.name }}</h3>
          <TabList>
            <Tab value="model-runs" :class="{ 'is-running': hasRunningWorkflow }">Model Runs</Tab>
            <Tab value="models-selection">Models Selection</Tab>
            <Tab value="details">Experiment Details</Tab>
          </TabList>
        </div>
        <div class="experiment-details-tab-content">
          <TabPanels>
            <TabPanel value="model-runs">
              <WorkflowsTab
                v-if="experiment"
                @add-model-run-clicked="activeTab = 'models-selection'"
                :experiment="experiment"
              />
            </TabPanel>
            <TabPanel value="models-selection">
              <AddWorkflowsTab
                :experiment="experiment"
                v-if="experiment"
                @workflowCreated="handleWorkflowCreated"
              />
            </TabPanel>
            <TabPanel value="details">
              <ExperimentDetailsTab v-if="experiment" :experiment="experiment" />
            </TabPanel>
          </TabPanels>
        </div>
      </div>
    </Tabs>
  </div>
</template>

<script setup lang="ts">
import Breadcrumb from 'primevue/breadcrumb'

import { computed, ref, type ComputedRef } from 'vue'
import { useRouter } from 'vue-router'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import type { MenuItem } from 'primevue/menuitem'
import WorkflowsTab from '@/components/experiment-details/WorkflowsTab.vue'
import AddWorkflowsTab from '@/components/experiment-details/AddWorkflowsTab.vue'
import ExperimentDetailsTab from '@/components/experiment-details/ExperimentDetailsTab.vue'
import { useQuery } from '@tanstack/vue-query'
import { experimentsService } from '@/sdk/experimentsService'
import { WorkflowStatus } from '@/types/Workflow'

const { id } = defineProps<{
  id: string
}>()
const experimentId = computed(() => id)
const router = useRouter()
const { data: experiment } = useQuery({
  queryKey: ['experiment', experimentId],
  refetchInterval: 3000,
  queryFn: () => experimentsService.fetchExperiment(experimentId.value),
})

const activeTab = ref()
const defaultActiveTab = computed(() => {
  return experiment.value?.workflows.length ? 'model-runs' : 'models-selection'
})

const hasRunningWorkflow = computed(() => {
  return experiment.value?.workflows.some((workflow) => workflow.status === WorkflowStatus.RUNNING)
})

const items: ComputedRef<MenuItem[]> = computed(() => [
  {
    label: 'Experiments',
    command: (e) => {
      e.originalEvent.preventDefault()
      router.push('/experiments')
    },
    items: [],
    key: 'experiments',
  },
  {
    label: experiment.value?.name,
    command: (e) => {
      e.originalEvent.preventDefault()
      router.push(`/experiments/${id}`)
    },
    key: 'experiment-details',
  },
])

const handleBackButtonClicked = () => {
  router.back()
}

const handleWorkflowCreated = async () => {
  activeTab.value = 'model-runs'
}
</script>

<style scoped lang="scss">
@use '@/styles/mixins';

/* reset global css from _resetcss.scss */
:deep(a, li) {
  background-color: unset;
}

.is-running::before {
  content: ' ';
  display: inline-block;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: var(--l-primary-color);
  margin-right: 8px;
  margin-bottom: 2px;
  animation: pulse-dot 1.5s infinite ease-in-out;
}

.back-button {
  cursor: pointer;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--l-grey-200);

  @include mixins.caption;
}

.experiment-details-page {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  text-align: left;
  padding: 0 1.88rem;
}

.experiment-title {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--l-grey-100);
  @include mixins.heading-2;
}

.experiment-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.experiment-details-header {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.experiment-details-tab-content {
}
</style>
