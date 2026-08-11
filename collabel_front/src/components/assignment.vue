<script>
    export default {
        props: ['assignment', 'mode', 'assignment_id'],
        data () {
            return {
                new_assignment: this.assignment,
                pending_count: 1,
                help_modal: false,
                guide_modal: false,
                mode: this.mode,
                assignment_id: this.assignment_id
            }
        },
        mounted() {
            var socket_proto = "ws://"
            if (location.protocol === 'https:') {
                socket_proto = "wss://"
            }
            const socket_host = window.location.host.replace(/:8000$/, ':8001');
            let connection = new WebSocket(socket_proto + socket_host + '/ws/state/' + this.assignment["worker_id"] + '/');
            connection.onmessage = (event) => {
                const new_assignment = JSON.parse(event.data);
                if (new_assignment.state === "as") {
                    window.location.reload();
                } else if (new_assignment.state === "fl") {
                    this.new_assignment = new_assignment;
                }
            }

            fetch("/game/pending").then(r => r.json()).then(json => {
                this.pending_count = json["panding_count"];
            });

            setInterval(() => {
                fetch("/game/pending").then(r => r.json()).then(json => {
                    this.pending_count = json["panding_count"];
                });
            }, 2500);
        },
    }
</script>

<template>
    Hello, player!<br>
    <span v-if="new_assignment.state == 'pd'">
        Looking for the room. Please wait - porcess can take up to 10 minutes. Gathered {{ pending_count }} out of 5 players
        <BProgress :value="pending_count * 20"  striped animated/>

        <BInputGroup style="margin-top: 37px;  margin-right: 20px; width: auto;">
            <BButton @click="help_modal = !help_modal" variant="success" size="lg" style="font-size: 1.7rem;">
                    Example </BButton>
            <BModal v-model="help_modal" title="Example" okTitle="Ok" id="helpModal" okOnly="true" size="lg">
                <help></help>
            </BModal>
            <BButton @click="guide_modal = !guide_modal" variant="success" size="lg" style="font-size: 1.7rem;">
                Guide </BButton>
            <BModal v-model="guide_modal" title="Help" okTitle="Ok" id="guideModal" okOnly="true" size="lg">
                <guide :mode='mode'></guide>
            </BModal>
        </BInputGroup>


    </span>
    <span v-if="new_assignment.state == 'fl'">
    Failed to assign the room for you. You can stil submit a hit to receive basic reward
        <form id = "endForm" :action='props.submit_url + "/mturk/externalSubmit"' method="POST">
            <input type="hidden" id="assignmentId" :value='assignment_id' name="assignmentId"/>
            <input type="hidden" id="user-input" value="test" name="user-input"/>
            <input type="submit" value="Submit HIT" />
        </form>
    </span>
</template>
