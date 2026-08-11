<script setup>
    import {defineProps} from "vue";
    import {ref} from 'vue';

    const props = defineProps(['worker_id', 'has_code', 'score', 'submit_url', 'assignment_id', "mode"]);
    const code = ref('');

    const score_enabled = ref(((props.mode != "chat_only") && (props.mode != "no_chat") && (props.mode != "individual")) ? true : false);

    function submit() {
        let token = document.getElementsByName("csrfmiddlewaretoken");

        if (code.value.length == 0) {
            return
        }
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": token[0].value },
            body: JSON.stringify({"code": code.value})
        };
        fetch("/game/survey/" + props.worker_id, requestOptions)
            .then(r => r.json()).then(json => {
                if (json["result"] == "Error") {
                } else {
                    window.location.reload();
                }
            }
        );
    }
</script>
<template>
    <h3> Challenge completed! Thank you for participation! </h3>

    <div v-if="score_enabled">
        You received <b>{{ props.score }} points ({{ (props.score * 0.01).toFixed(2)}}$)</b> <br>
    </div>

    <div v-else>
        You earned <b>{{ (props.score * 0.01).toFixed(2)}}$</b> <br>
    </div>

    <div v-if="!props.has_code">
        <BAlert :model-value="true" variant="success">
            <BForm @submit="submit" @reset="reset">
                For additional <b>1.0$</b> reward please,
                complete <a v-if='props.mode == "no_chat"' href="https://strathsci.qualtrics.com/jfe/form/SV_9ytDtZDk1vAiL6S" target="_blank"> survey </a>
                <a v-if='props.mode == "chat_only"' href="https://strathsci.qualtrics.com/jfe/form/SV_brvyntHbdcH6l9Q" target="_blank"> survey </a>

                and <b>submit</b> survey code you will get on completion to below box
                <BFormGroup id="survey-group" label-for="input-survey">
                    <BFormInput id="input-survey" v-model="code" required></BFormInput>
                    <BButton variant="primary" type="submit">send survey code</BButton>
                </BFormGroup>
            </BForm>
        </BAlert>
    </div>
    <form id = "endForm" :action='props.submit_url + "/mturk/externalSubmit"' method="POST">
        <input type="hidden" id="assignmentId" :value='props.assignment_id' name="assignmentId"/>
        <input type="hidden" id="user-input" value="test" name="user-input"/>
        <input type="submit" value="Submit HIT"/>
    </form>
</template>
