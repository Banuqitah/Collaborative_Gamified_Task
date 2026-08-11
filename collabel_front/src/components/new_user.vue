<script setup>
    import {defineProps} from "vue";
    import {ref} from 'vue';
    import doc from "./doc.vue";

    const individual = (props.mode == "individual") ? true : false;
    const props = defineProps(['worker', 'mode', 'submit_url', 'assignment_id']);
    const login = ref('');
    const avatars = ref([]);
    const moods = ref([]);
    const choice = ref(null);
    const mood_choice = ref(null);
    let show_modal = ref("doc");

    let errors = ref([]);

    let mood_names = [
        "cheerful / glad", "vivid / excited",
        "nervous / tense", "irritated / grumpy",
        "sad / gloomy", "bored / tired",
        "losen / relaxed", "calm / untroubled",
    ];

    fetch("/game/avatars").then(r => r.json()).then(json => {
        avatars.value = json["av"];
        moods.value = json["md"];
    });


    function send_action(action) {
        let token = document.getElementsByName("csrfmiddlewaretoken");
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": token[0].value },
            body: JSON.stringify({"action": action})
        };
        fetch("/game/action/" + props.worker, requestOptions);
    }

    function submit() {
      errors.value = [];

      if (!login.value) {
          errors.value.push('Enter non-empty nickname');
      }

      if (!choice.value) {
          errors.value.push('Chose an avatar');
      }

      if (!mood_choice.value) {
          errors.value.push('Chose mood picture');
      }

      if (errors.value.length > 0) {
          return;
      }

    let token = document.getElementsByName("csrfmiddlewaretoken");

    const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": token[0].value },
        body: JSON.stringify({"login": login.value, "avatar": choice.value, "mood": mood_choice.value})
    };
    fetch("/game/login/" + props.worker, requestOptions)
            .then(r => r.json()).then(json => {
                if (json["result"] == "Error") {
                    if (json["code"] == 1) {
                        errors.value.push('Login already occupied!');
                    }
                } else {
                    window.location.reload();
                }
            }
        );
    }
</script>

<template>

    <h3 v-if="individual"> Welcome To Image Labeling Task </h3>
    <h3 v-else> Welcome To Collaborative Image Labeling </h3>

    <transition name="slide-up">
        <section v-if='show_modal === "doc"'>
            <doc :worker=props.worker :mode="props.mode"></doc>
            <div style="display: flex;">
                <div class="login-buttons" style="margin-right: 25px;">
                    <BButton @click='send_action("accept rules"); show_modal = "form"' class="rules-button" variant="success">I have read the tutorial and agree to rules</BButton>
                </div>

                <form id = "endForm" :action='props.submit_url + "/mturk/externalSubmit"' method="POST">
                    <input type="hidden" id="assignmentId" :value='props.assignment_id' name="assignmentId"/>
                    <input type="hidden" id="user-input" value="test" name="user-input"/>
                    <input type="submit" value="Reject (quit without reward)" class="btn btn-md btn-secondary btn-danger" />
                </form>
            </div>

        </section>
        <section v-if='show_modal === "form"'>
        <BForm @submit="submit" @reset="reset">
            <BFormGroup id="login-group" label="Enter your nikname:" label-for="input-login" description="Nikname should be unique">
            <BFormInput id="input-1" v-model="login" placeholder="player_1" required></BFormInput>
            </BFormGroup>

            Chose avatar<br>
            <div class="avatars" style="margin: auto;">
                <div v-for="av in avatars" class="user-avatar-item">
                    <label>
                        <input type="radio" :value="av[0]" v-model="choice">
                        <img :src="av[1]">
                    </label>
                </div>
            </div>

            <br>
            The following photographs depict various emotions. Which of the following image best captures how you are feeling right now?
            <div class="avatars">

            <div class="avatars-container" style="--m: 8; --tan: 0.41; margin: auto;">
                <a class="avatar-item">
                    <input type="radio" :value="moods[moods.length - 1][0]" v-model="mood_choice">
                    <img :src="moods[moods.length - 1][1]" alt="alt text"/>
                    Neutral
                </a>
                <a v-for="(m, index) in moods.slice(0, -1)" class="avatar-item" :style="'--i: ' + index">
                    <input type="radio" :value="m[0]" v-model="mood_choice">
                    <img :src="m[1]">
                    {{ mood_names[index] }}
                </a>
                </div>
            </div>
            <br>

            <div v-if="errors.length > 0">
                <BAlert :model-value="true" variant="danger">
                Submission failed. Please do the following:
                <ul>
                    <li v-for="error in errors">{{ error }}</li>
                </ul>
                </BAlert>
            </div>
            <BButton type="submit" variant="primary" class="me-1">Submit</BButton>
            <BButton type="reset" variant="danger">Reset</BButton>
        </BForm>
        </section>
    </transition>
</template>
