<script setup>
import { defineProps, ref } from "vue";
import help from "./help.vue";

const props = defineProps(['mode']);

const chat_endabled = ref(((props.mode != "no_chat") && (props.mode != "individual")) ? true : false);
const lb_endabled = ref(((props.mode != "chat_only") && (props.mode != "no_chat") && (props.mode != "individual")) ? true : false);
const tower_enabled = ref(((props.mode != "chat_only") && (props.mode != "no_chat") && (props.mode != "individual")) ? true : false);
const levels_enabled = ref(((props.mode != "chat_only") && (props.mode != "no_chat") && (props.mode != "individual")) ? true : false);
const score_enabled = ref(((props.mode != "chat_only") && (props.mode != "no_chat") && (props.mode != "individual")) ? true : false);
const individual = (props.mode == "individual") ? true : false;


</script>

<template>
  <h2> Task Instructions and Rules </h2>
  <div v-if="individual">

    <ol>
      <li><b>Classify</b> images of galaxies based on the number of arms they have.</li>
      <li><b>The task</b> has 50 images </li>
      <li><b>Complete at least 20 + survey</b> for reward</li>
      <li><b>Your reward</b> is based on the minimum wage per hour</li>
      <li><b>Additional reward</b> for accurate classifications of 'honeypot' images and for completing the post-task survey.</li>
      <li><b>Select</b> your answer using radio buttons beside each image</li>
      <li><b>Press "Next"</b> to proceed to the next image</li>

    </ol>

    <h3 style="color: #dc3545;"> Classification example </h3>
    <help></help>


    <h3 style="color: #dc3545;"> Ending the task </h3>

    <p>The task ends once you complete all levels or by pressing "Quit". You’ll then complete a brief survey to finalize
      your reward.
      <br><strong>Do not close task window until you enter survey code!</strong>
    </p>
    <p style="text-align: center;">Thank you for participating in the Galaxy Classification Task—your input helps
      improve crowdsourcing!</p>
    <h2 style="color: #dc3545; text-align: center;">Good luck and enjoy the experience.</h2>


  </div>
  <div v-else>
    <h3 style="color: #dc3545;">Overview</h3>
    <div v-if="score_enabled">
      <p><strong>Levels:</strong> 5 levels, each with 10 images.</p>
      <p><strong>Objective:</strong>Earn points for accurate labels to maximize your reward.</p>
      <h3 style="color: #dc3545;">Requirements</h3>
      <p><strong>Complete at least 2 levels + survey</strong> for a reward.</p>
      Additional reward for completing the survey at the end.
    </div>
    <div v-else>
      <p><strong>The task</strong> has 50 images</p>
      <p><strong>Objective:</strong> Make accurate labels to maximize your reward.</p>
      <h3 style="color: #dc3545;">Requirements</h3>
      <p><strong>Complete at least 20 + survey</strong> for a reward.</p>
      Additional reward for completing the survey at the end.
    </div>

    <!-- <h3 style="color: #dc3545;">Classification example</h3>
  <img :src='"/static/galaxy_help/guide.jpg"' style="width: 100%; object-fit: contain"> -->

    <h3 style="color: #dc3545;">How to label</h3>

    <ul>
      <li><b>Vote: </b> Select your answer using the radio buttons beside each image. Teammates' votes will display as avatars.</li>
      <li><b>Confirm: </b> Press "I'm done" when ready. Once all teammates confirm, you’ll move to the next image.
      </li>
      <li><b>Timer: </b> If half the team confirms, a 1-minute timer starts, and answers will auto-submit when time’s
        up.</li>

      <li v-if="chat_endabled">
        <b>Chat: </b> Use the chat to discuss and coordinate with your team. Accurate collaboration improves your score
        and potential rewards!
      </li>
    </ul>

    <div v-if="score_enabled">
    <h3 style="color: #dc3545;">Scoring</h3>


    <ul>
      <li><b>Progress:</b> Each labeled image earns <b>5 points.</b></li>
      <ul>
        <li>Points convert to rewards at the end of each task.</li>
      </ul>
      <li><b>Correct labels:</b> Each 10 has one image with a known answer (honeypot).</li>
      <ul>
        <li>The entire team earns bonus points for each correct honeypot label identified by any player. Score scales with level. <br> <b>First level honeypot image:</b> 5 points, <b>second level honeypot image:</b> 6 points and so on.</li>
      </ul>
      <li><b>Agreement</b></li>
      <ul>
        <li>+1 bonus point if the majority of the team selects the accurate label.</li>
        <li>+2 bonus points if all team members select the accurate label.</li>
      </ul>
    </ul>
    </div>
    <div v-else>
      <h3 style="color: #dc3545;">Reward</h3>
      <ol>
        <li><b>Base:</b> You’ll receive a base payment of $1 if requirements are met.</li>
        <li><b>Quality bonus:</b> You’ll receive bonus reward based on correct labels for honeypot images.</li>
        <li><b>Agreement bonus:</b></li>
        <ul>
          <li>Bonus for accurate majority agreement among teammates</li>
          <li>More bonus for accurate agreement among all teammates</li>
        </ul>

      </ol>

    </div>

    <div v-if="lb_endabled">
      <h3 style="color: #dc3545;"> Leaderboard </h3>
      Teams are ranked by total points, so accuracy and teamwork pay off!
    </div>

    <h3 style="color: #dc3545;"> Classification example </h3>
    <help></help>

    <h3 style="color: #dc3545;"> Ending the task </h3>
    <p>The task ends upon completing all levels or by pressing "quit". You’ll then complete a brief survey to finalize
      your reward.
      <br><strong>Do not close task
        window until you enter survey code!</strong>
    </p>
    <p style="text-align: center;">Thank you for participating in the Galaxy Classification Task—your input helps
      improve crowdsourcing!</p>
    <h2 style="color: #dc3545; text-align: center;">Good luck and enjoy the experience.</h2>
  </div>
</template>
