<script setup>
import tower from "./tower.vue";
import timer from "./timer.vue";
import { computed, reactive, ref, watch } from 'vue';
import { defineProps } from "vue";
import { useToast } from "vue-toastification";
import help from "./help.vue";
import guide from "./guide.vue";

const suggestions = ref([]);
const toast = useToast();

var count_to = ref(null);
var counter_enabled = ref(false);
var time_left = ref(120);

const choice = ref(null);
const confirm = ref(false);

const props = defineProps(['question', 'worker', 'room_id', 'mode']);
const state = reactive({});
const room_state = ref(
    {
        "q": { "id": null },
        "logins": {},
        "avatars": {},
        "chat": [],
        "participants": [],
        "scores": {},
        "room_score": 0,
        "progress": 0,
        "q_set_size": 0,
        "level": 0,
        "lb": []
    }
);
let show_modal = ref(false);
let done_disabled = ref(true);
let new_level = ref(false);
let last_level = ref(0);
const quit_modal = ref(false);
const quit_reason = ref(null);
const help_modal = ref(false);
const guide_modal = ref(false);

const score_delta = ref(0);
const accuracy_delta = ref(0);
const worker_accuracy_delta = ref(0);
const accuracy_max = ref(0);
const agreement_delta = ref(0);
const agreement_max = ref(0);
const base_delta = ref(0);
const old_score = ref(0);
function format_points(value) {
    const rounded = Math.round(value * 100) / 100;
    if (Number.isInteger(rounded)) {
        return rounded.toString();
    }
    return rounded.toFixed(2).replace(/0+$/, '').replace(/\.$/, '');
}
const next_level = computed(() => last_level.value + 1);
const total_team_score = computed(() => old_score.value + score_delta.value);
const can_quit_with_reward = computed(() => last_level.value > 1);
const has_next_level = computed(() => next_level.value <= 5);
const player_count = computed(() => Math.max(Object.keys(room_state.value.scores || {}).length, 1));
const per_player_accuracy_delta = computed(() => format_points(accuracy_delta.value / player_count.value));
const per_player_agreement_delta = computed(() => format_points(agreement_delta.value / player_count.value));

const autoconfirm_timer = ref(8);
const autoconfirm_enabled = ref(false);


const chat_endabled = ref(((props.mode != "no_chat") && (props.mode != "individual")) ? true : false);
const individual = (props.mode == "individual") ? true : false;
const lb_endabled = ref(((props.mode != "chat_only") && (props.mode != "no_chat") && (props.mode != "individual")) ? true : false);
const tower_enabled = ref(((props.mode != "chat_only") && (props.mode != "no_chat") && (props.mode != "individual")) ? true : false);
const levels_enabled = ref(((props.mode != "chat_only") && (props.mode != "no_chat") && (props.mode != "individual")) ? true : false);
const score_enabled = ref(((props.mode != "chat_only") && (props.mode != "no_chat") && (props.mode != "individual")) ? true : false);



fetch("/game/room/" + props.room_id).then(r => r.json()).then(json => {
    json.chat = json.chat.map(function (x) {
        let msg = { type: 'text', author: `me`, data: { text: x[1] }, suggestions: suggestions };
        if (x[0] !== props.worker) {
            msg["author"] = x[0];
        }
        return msg;
    });

    json.participants = [];
    for (const [key, value] of Object.entries(json["logins"])) {
        json.participants.push(
            {
                id: key,
                name: value,
                imageUrl: json.avatars[key]
            }
        )
    }
    json.chat.unshift({ type: 'system', id: 1, data: { text: 'Welcome to the collaborative labeling game!' }, suggestions: suggestions });
    room_state.value = json;

    for (const [key, value] of Object.entries(json["votes"])) {
        state[key] = value;
    }

    if (json["has_deadline"]) {
        count_to.value = json["deadline"];
        const current_time = new Date().getTime();
        let time_diff = (count_to.value - current_time) / 1000;
        if (time_diff < 0) { time_diff = 0; }
        time_left.value = Math.round(time_diff);
        console.log(time_left.value)
        counter_enabled.value = true;
    }

    done_disabled.value = confirm.value || (choice.value == null)

    suggestions.value = ["Agree", "Disagree"]

    for (const ans of room_state.value.q.answers) {
        suggestions.value.push("I suggest " + ans)
    }

    if (room_state.value.level == 1 && room_state.value.progress == 1) {
        help_modal.value = true;
    }
});

var socket_proto = "ws://"
if (location.protocol === 'https:') {
    socket_proto = "wss://"
}
const socket_host = window.location.host.replace(/:8000$/, ':8001');

const ready_sound = new Audio('/static/sound/ready.mp3');
const message_sound = new Audio('/static/sound/message.mp3');
const timer_sound = new Audio('/static/sound/timer.wav');

const connection = new WebSocket(socket_proto + socket_host + '/ws/vote/' + props.room_id + '/');
const chat_connection = new WebSocket(socket_proto + socket_host + '/ws/chat/' + props.room_id + '/');

connection.onmessage = (event) => {
    let data = JSON.parse(event.data);
    if (data["has_deadline"]) {
        count_to.value = data["deadline"];
        const current_time = new Date().getTime();
        let time_diff = (count_to.value - current_time) / 1000;
        if (time_diff < 0) { time_diff = 0; }
        time_left.value = Math.round(time_diff);
        var old_enabled = counter_enabled.value;
        counter_enabled.value = true;
        if (!old_enabled && data["vote"][0] !== props.worker) {
            toast.clear();
            toast.info('Most players have woted and question will be automatically submitted in 2 minutes')
            timer_sound.play();
        }
    } else {
        counter_enabled.value = false;
    }

    console.log(data);

    if (data["vote"]) {
        data = data["vote"]
        if (data[0] !== props.worker && data[1] === room_state.value["q"]["id"]) {
            console.log("dbg");
            console.log(data[0]);

            let old_state = false;

            if (state[data[0]] !== undefined) {
                old_state = state[data[0]][1];
            }
            if (old_state == false && data[3] == true) {
                ready_sound.play();
            }
            state[data[0]] = [data[2], data[3]];
        }
    }
    else if (data["next"]) {
        if (data["quits"]) {
            for (const wid of data["quits"]) {
                if (props.worker == wid) {
                    window.location.reload();
                }
            }
        }
        toast.clear();
        timer_sound.pause();
        autoconfirm_enabled.value = false;
        autoconfirm_timer.value = 8;

        if (data["scores"]) {
            score_delta.value = data["scores"][props.worker][0];
            agreement_delta.value = data["scores"][props.worker][1];
            agreement_max.value = data["scores"][props.worker][2];
            accuracy_delta.value = data["scores"][props.worker][3];
            accuracy_max.value = data["scores"][props.worker][4];
            worker_accuracy_delta.value = data["scores"][props.worker][5];
            base_delta.value = score_delta.value - agreement_delta.value - accuracy_delta.value;
            new_level.value = true;
            last_level.value = room_state.value['level'];
            old_score.value = room_state.value['room_score'];
            console.log("level");
            console.log(last_level.value);
        } else {
            new_level.value = false;
        }

        show_modal.value = true;
        Object.keys(state).forEach(function (key) { delete state[key] });
        fetch("/game/room/" + props.room_id).then(r => r.json()).then(json => {
            json.chat = json.chat.map(function (x) {
                let msg = { type: 'text', author: `me`, data: { text: x[1] }, suggestions: suggestions };
                if (x[0] !== props.worker) {
                    msg["author"] = x[0];
                }
                return msg;
            });
            json.chat.unshift({ type: 'system', id: 1, data: { text: 'Welcome to the collaborative labeling game!' }, suggestions: suggestions });

            json.participants = [];
            for (const [key, value] of Object.entries(json["logins"])) {
                json.participants.push(
                    {
                        id: key,
                        name: value,
                        imageUrl: json.avatars[key]
                    }
                )
            }

            room_state.value = json;
            confirm.value = false;
            done_disabled.value = true;
            choice.value = null;
            for (const [key, value] of Object.entries(json["votes"])) {
                state[key] = value;
            }
            suggestions.value = ["Agree", "Disagree"]

            for (const ans of room_state.value.q.answers) {
                suggestions.value.push("I suggest " + ans)
            }

            if (data["has_deadline"]) {
                count_to.value = data["deadline"];
                counter_enabled.value = true;
            } else {
                counter_enabled.value = false;
            }
            if (json["finished"]) {
                window.location.reload();
            }
        });
    } else if (data["quit"]) {
        window.location.reload();
    } else if (data["renew"]) {
        window.location.reload();
    }
};

chat_connection.onmessage = (event) => {
    let data = JSON.parse(event.data);

    let msg = { type: 'text', author: `me`, data: { text: data["data"][1] }, suggestions: suggestions };

    if (data["data"][0] !== props.worker) {
        msg["author"] = data["data"][0];
        message_sound.play();
    }
    room_state.value.chat.push(msg);
};

function autosubmit() {
    if (autoconfirm_enabled.value == false) {
        return
    } else {
        if (autoconfirm_timer.value > 0) {
            autoconfirm_timer.value = autoconfirm_timer.value - 1;
            if (autoconfirm_timer.value == 0) {
                autoconfirm_enabled.value = false;
                autoconfirm_timer.value = 8;
                confirm.value = true;
                return;
            }
        }
    }
}

setInterval(autosubmit, 1000);

watch(choice, () => {
    state[props.worker] = [choice.value, confirm.value];

    done_disabled.value = confirm.value || (choice.value == null)
    connection.send(JSON.stringify([props.worker, room_state.value.q.id, choice.value, confirm.value]));

    if (!confirm.value &&  state[props.worker][0] !== null && !autoconfirm_enabled.value) {
        autoconfirm_enabled.value = true;
    }
});

watch(confirm, () => {
    done_disabled.value = confirm.value || (choice.value == null)

    state[props.worker] = [choice.value, confirm.value];
    if (choice.value != null) {
        connection.send(JSON.stringify([props.worker, room_state.value.q.id, choice.value, confirm.value]));
    }
});

function quit() {
    connection.send(JSON.stringify(['quit', props.worker, quit_reason.value]));
}
const newMessagesCount = ref(0);
const showTypingIndicator = ref('');
const colors = {
    header: {
        bg: 'rgb(108, 117, 125)',
        text: '#ffffff'
    },
    launcher: {
        bg: '#4e8cff'
    },
    messageList: {
        bg: '#ffffff'
    },
    sentMessage: {
        bg: '#198754',
        text: '#ffffff'
    },
    receivedMessage: {
        bg: '#eaeaea',
        text: '#222222'
    },
    userInput: {
        bg: '#f4f7f9',
        text: '#565867'
    }
};

const messageStyling = true;

function onMessageWasSent(message) {
    if (message.data.text.length > 0) {
        chat_connection.send(JSON.stringify([props.worker, message.data.text]));
    }
}

function handleOnType() {
    console.log('Emit typing event');
}

function editMessage(message) {
    console.log('edit');
}

</script>

<template>
    <BModal v-model="show_modal" centered :title="new_level && score_enabled ? 'Congratulations!' : 'Question submitted!'"
        size="md" okTitle="Continue" cancelTitle="Quit" :ok-only="!can_quit_with_reward"
        @cancel="quit_modal = !quit_modal">
        <div v-if="new_level && score_enabled">
            You and your team have completed <b>Level {{ last_level }}</b> with
            <br>
            <br>

            <BTableSimple hover small stripped>
                <BTbody>
                    <BTr>
                        <BTd><b>Team Score:</b></BTd>
                        <BTd>{{ score_delta }} points</BTd>
                    </BTr>
                    <BTr>
                        <BTd><b>Your Accuracy Contribution:</b></BTd>
                        <BTd>{{ worker_accuracy_delta }} points</BTd>
                    </BTr>
                </BTbody>
            </BTableSimple>
            <BTableSimple hover small stripped>
                <BTfoot>
                    <BTr>
                        <BTd>Honeypot:</BTd>
                        <BTd>{{ per_player_accuracy_delta }} points</BTd>
                        <BTd>Agreement:</BTd>
                        <BTd>{{ per_player_agreement_delta }} points</BTd>
                    </BTr>
                </BTfoot>
            </BTableSimple>

            <br>
            <template v-if="has_next_level">
                🔹 You are now proceeding to <b>Level {{ next_level }} of 5</b>. Current total team score is
                {{ total_team_score }} points.
                <br>
                💡 Keep collaborating in the chat and aiming for accurate agreement to maximize your score!
            </template>
            <template v-else>
                Your team has completed all levels. Final team score is {{ total_team_score }} points.
            </template>
            <BAlert v-if="can_quit_with_reward" :model-value="true" variant="success">
                You reached minimum payment requirement and can quit now with current rewards.
            </BAlert>
        </div>
        <div v-else>
            Next question!
        </div>
    </BModal>

    <div class="game-container shadow-lg rounded">
        <div class="game-question-area">
            <div
                style="display: flex; align-items: center;  margin-left: 20px;  margin-top: 20px;  margin-right: 20px; width: auto">
                <BInputGroup style="margin-bottom: 37px;  margin-right: 20px; width: auto;">
                    <BButton @click="help_modal = !help_modal" variant="success" size="lg" style="font-size: 1.7rem;">
                        Example </BButton>
                    <BModal v-model="help_modal" title="Example" okTitle="Ok" id="helpModal" okOnly="true" size="lg">
                        <help></help>
                    </BModal>
                    <BButton @click="guide_modal = !guide_modal" variant="success" size="lg" style="font-size: 1.7rem;">
                        Guide </BButton>
                    <BModal v-model="guide_modal" title="Help" okTitle="Ok" id="guideModal" okOnly="true" size="lg">
                        <guide :mode="props.mode"></guide>
                    </BModal>
                    <BButton @click="quit_modal = !quit_modal" size="lg" style="font-size: 1.7rem;"> Quit </BButton>
                    <BModal v-model="quit_modal" title="Exit session" okTitle="Quit" id="quitModal" @ok="quit">
                        <div v-if="room_state.level < 3">
                            <div v-if="score_enabled">
                                You did'not reach level 3 so you will receive 0 score!
                            </div>
                            <div v-else>
                                You did'not label 20 images so you will not receive reward!
                            </div>
                        </div>
                        <div v-else>
                            If you quit now - you will receive {{ room_state.scores[props.worker] }} points!
                        </div>
                        <br>
                        <b>Please</b>, describe breafily why do you quit so we could improve the system.
                        <BFormInput v-model="quit_reason" placeholder="" />
                    </BModal>
                </BInputGroup>

                <div>
                    <h3 style="font-size: 1.3em; margin-bottom: 25px; margin-left: 20px; margin-right: 20px;" v-if='levels_enabled'>Level:
                        {{ room_state.level }} / 5.&nbsp;&nbsp;&nbsp;&nbsp;Image {{ room_state.progress }} / {{ room_state.q_set_size }}</h3>
                    <h3 style="font-size: 1.3em; margin-bottom: 25px; margin-left: 20px; margin-right: 20px;" v-else>
                        Image {{ (room_state.level - 1) * room_state.q_set_size + room_state.progress }} / {{ 5 * room_state.q_set_size }}
                    </h3>
                </div>

                <div v-if="!individual">
                    <timer :count_to="count_to" :enabled="counter_enabled" :time_left="time_left" />
                </div>
            </div>
            <hr class="left-line">
            <div style="margin-left: 20px; margin-right: 20px; margin-top: 32px;">
                <div style="display: flex; column-gap: 10px">
                    <div style="display: block; text-align: center;">
                        <img :src="room_state.q.img" class="galaxy-image">
                    </div>
                    <div style="display: block">
                        <h3 v-html="room_state.q.text"></h3>

                        <div v-for="(ans, index) in room_state.q.answers" style="line-height: 2em;">
                            <div>
                                <BFormRadio type="radio" :value="index" v-model="choice">
                                    <label style="display: flex; column-gap: 10px">
                                        {{ ans }}
                                        <template v-for="(v, k) in state">
                                            <span v-if="v[0] === index" :class="{ 'answer-confirmed': v[1] }">
                                                <BAvatar :src="room_state.avatars[k]"
                                                    :badge="room_state.logins[k].substring(0, 8)" badge-top
                                                    badge-offset="-0.5em" />
                                            </span>
                                        </template>
                                    </label>
                                </BFormRadio>
                            </div>
                        </div>
                        <BButton @click="confirm = true" size="md" style="font-size: 1.7rem;" v-if="individual" :disabled="done_disabled"> Next </BButton>
                        <BFormCheckbox v-model="confirm" switch button-variant="success" :disabled="done_disabled"
                            size="lg" v-else>
                            I'm done. <span v-if="autoconfirm_enabled"> Autosubmit in {{ autoconfirm_timer }} s</span>
                        </BFormCheckbox>
                    </div>
                </div>
            </div>
        </div>
        <div class="game-left-panel" v-if="!individual">
            <BCard class="text-left" style="height: 100%">
                <div class="hello-area" style="display: flex; align-items: center; flex-direction: column;">
                    <BAvatar :src="room_state.avatars[props.worker]" size="8em" />
                    <h5>Hello, {{ room_state.logins[props.worker] }}</h5>
                </div>
            </BCard>

        </div>
        <div class="game-right-panel" v-if="!individual">
            <BCard class="text-left" style="height: 100%">
                <div class="tower" v-if='tower_enabled'>
                    <h4>Progress: level {{ room_state.level }} / 5 </h4>
                    <div id="tower-display" style="display:flex; justify-content:center;">
                        <tower :level="room_state.level"></tower>
                    </div>
                </div>
                <hr class="left-line">
                <h4>Your team:</h4>
                <BTableSimple hover small striped secondary>
                    <BTbody>
                        <BTr v-for="(s, w) in room_state.scores">
                            <BTd>
                                <BAvatar :src="room_state.avatars[w]" />&nbsp;
                                <b v-if="w == props.worker">{{ room_state.logins[w] }} (me) </b>
                                <span v-else>{{ room_state.logins[w] }} </span>
                            </BTd>
                        </BTr>
                    </BTbody>
                </BTableSimple>
                <hr class="left-line">
                <div class="lb" v-if='lb_endabled'>
                    <h4>Leaderboard</h4>
                    <template v-if='room_state["room_score"] == 0'>
                        <div style="display: flex; align-items: center; flex-direction: column;">
                            <BSpinner />
                            <p>Complete at least one level to see Leaderboard</p>
                        </div>
                    </template>
                    <template v-else>
                        <BTableSimple hover small striped secondary>
                            <BThead>
                                <BTh sm>Team</BTh>
                                <BTh sm>Score</BTh>
                            </BThead>
                            <BTbody>
                                <BTr v-for="stat in room_state.lb">
                                    <template v-if="stat['id'] !== props.room_id">
                                        <BTd> Team {{ stat["id"] }} </BTd>
                                        <BTd> {{ stat["score"] }} </BTd>
                                    </template>
                                    <template v-else>
                                        <BTd>Our team</BTd>
                                        <BTd>{{ stat["score"] }} (Bonus: {{ stat["bonus_score"] }})</BTd>
                                    </template>
                                </BTr>
                            </BTbody>
                        </BTableSimple>
                    </template>
                </div>
            </BCard>
        </div>
        <div v-if="chat_endabled" class="game-chat-area">
            <beautiful-chat :participants="room_state.participants" :onMessageWasSent="onMessageWasSent"
                :messageList="room_state.chat" :newMessagesCount="newMessagesCount" :isOpen="true" :showEmoji="false"
                :showFile="false" :showEdition="false" :showDeletion="false" :showTypingIndicator="showTypingIndicator"
                :showLauncher="false" :showCloseButton="false" :colors="colors" :alwaysScrollToBottom="true"
                :disableUserListToggle="true" :showHeader="true" :messageStyling="messageStyling" @onType="handleOnType"
                @edit="editMessage">
                <template v-slot:header>
                    Chat with others
                </template>

                <template v-slot:user-avatar="{ message, user }">
                    <div v-if="message.type === 'text' && user && user.name" style="margin-right: 10px;">
                        <BAvatar :src="user.imageUrl" :badge="user.name.substring(0, 8)" badge-top
                            badge-offset="-0.5em" />
                    </div>
                </template>
            </beautiful-chat>
        </div>
    </div>
</template>


<style>
.sc-chat-window {
    position: static !important;
    display: flex !important;
    width: auto !important;
    height: 67.5vh !important;
    max-height: 67.5vh !important;
}

.sc-message {
    width: 90% !important;
}

.sc-header {
    height: 5% !important;
    min-height: 35px !important;
}

.sc-message-list {
    height: 85% !important;
}
</style>