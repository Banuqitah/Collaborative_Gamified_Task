<script setup>
  import { ref } from 'vue'
  import assignment from './components/assignment.vue'
  import question from './components/question.vue'
  import new_user from "./components/new_user.vue";
  import doc from "./components/doc.vue";
  import done from "./components/done.vue";
  let state = ref(JSON.parse(document.getElementById('state').textContent));
  console.log("mode:", state.value['mode']);
</script>

<template>
  <div v-if="state.assignment.state == `nw`">
    <new_user :mode=state.mode :worker="state.worker_id" :submit_url="state.submit_url" :assignment_id="state.assignment_id"></new_user>
  </div>
  <div v-else-if="state.assignment.state == `pr`">
    <doc :mode=state.mode></doc>
  </div>
  <div v-else-if="state.assignment.state == `dn`">
    <done :worker_id="state.worker_id" :has_code="state.has_code" :score="state.score" :submit_url="state.submit_url" :assignment_id="state.assignment_id" :mode=state.mode></done>
  </div>
  <div v-else-if="state.room_id">
    <question :mode=state.mode  :worker="state.worker_id" :room_id="state.room_id"></question>
  </div>
  <div v-else>
    <assignment :assignment="state.assignment" :mode=state.mode :assignment_id="state.assignment_id"></assignment>
  </div>
</template>
