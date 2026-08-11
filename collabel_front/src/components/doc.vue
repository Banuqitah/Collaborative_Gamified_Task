<script setup>
import guide from "./guide.vue";
import { defineProps } from "vue";

function send_action(action) {
  let token = document.getElementsByName("csrfmiddlewaretoken");
  const requestOptions = {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": token[0].value },
    body: JSON.stringify({ "action": action })
  };
  fetch("/game/action/" + props.worker, requestOptions);
}

const props = defineProps(['worker', 'mode']);
const individual = (props.mode == "individual") ? true : false;

console.log(props.mode)
</script>

<template>

  <BAccordion>
    <template v-if="individual">
      <BAccordionItem title="Task tutorial" @show="send_action('show guide')" visible>
        <div class=intro-section>
          <guide :mode="props.mode"></guide>
        </div>
      </BAccordionItem>
    </template>
    <template v-else>
      <BAccordionItem title="Task tutorial" @show="send_action('show guide')" visible>
        <div class=intro-section>
          <guide :mode="props.mode"></guide>
        </div>
      </BAccordionItem>
    </template>

    <BAccordionItem title="User consent" @show="send_action('show consent')">
      <div class=intro-section>
        <p>
          This research is being conducted by Huda Banuqitah (huda.banuqitah@strath.ac.uk) under the supervision of Dr
          Mark Dunlop (mark.dunlop@strath.ac.uk) and Dr Sotirios Terzis (sotirios.terzis@strath.ac.uk) – all of Computer
          and Information Sciences, University of Strathclyde.
        </p>
        <p>
          I am a Ph.D. student at the University of Strathclyde (Scotland, UK), My research aims to improve the overall
          quality of crowdsourcing platforms by developing techniques that help to retain and improve workers engagement
          and performance in image labeling crowdsourcing.
          Your collaboration is highly appreciated, and your input is very important to us. Thank you for considering
          participating in our study. We have designed a collaborative task that aims to encourage worker engagement and
          performance, where you will work collaboratively anonymous (by Nickname) with a team of workers to label
          images
          of galaxies based on the number of arms in each image.
        </p>
        <p>
          Your participation will contribute significantly to our research efforts in improving task design in
          crowdsourcing platforms. The task will involve labeling up to a total of 50 images.
          For your participation in this study, you will be compensated in accordance with common US minimum wage levels
          $8.50/h.
        </p>
        <p>
          To be eligible for payment, you are required to complete a minimum of 20 labels and fill in a follow-up survey
          which will take around 20 minutes. Your payment of the minimum tasks will be based on the minimum wage levels
          $8.50/h for both the labeling and post survey tasks. However, we encourage you to label more images, as
          increasing the number of labels completed will result in higher compensation, especially if you collaborate
          live
          with your team to improve the accuracy of the labels. The more correct image labels, the higher your reward
          will
          be.
        </p>
        <p>
          The research was granted ethical approval by the University of Strathclyde Computer and Information Sciences
          Ethics Committee. The collected data may be used in academic publications, but your identity will be
          protected.
          No personal, or identifiable information will be collected except for your worker’s platform ID. An anonymous
          data of the tasks and post survey data set will be created once the study is complete by replacing worker IDs
          with randomly generated ones. Your contributions are invaluable to the success of our study, and we appreciate
          your time and effort in advance. If you have any questions or concerns, please feel free to contact us. If you
          have any questions/concerns, during or after the research, or wish to contact an independent person to whom
          any
          questions may be directed or further information may be sought from, please contact the Ethics Committee of
          the
          Department of Computer and Information Sciences, Livingstone Tower Richmond Street Glasgow G1 1XH email:
          ethics@cis.strath.ac.uk
        </p>
        <p>
          I confirm that I have read, understand and agree with the above policy and procedure for enrollment in this
          task.
        </p>
      </div>
    </BAccordionItem>
  </BAccordion>

</template>
