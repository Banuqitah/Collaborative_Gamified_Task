<template>
  Your task is to classify galaxy image by count of arms
  <ul style="column-count: 2;">
    <li>
      <img :src='"/static/galaxy_help/one.png"' style="background-color: rgb(0, 151, 157)">
      If galaxy looks like this - it has one arm
    </li>
    <li>
      <img :src='"/static/galaxy_help/two.png"' style="background-color: rgb(0, 151, 157)">
      This is two-arm galaxy
    </li>
    <li>
      <img :src='"/static/galaxy_help/three.png"' style="background-color: rgb(0, 151, 157)">
      This is three-arm galaxy
    </li>
    <li>
      <img :src='"/static/galaxy_help/four.png"' style="background-color: rgb(0, 151, 157)">
      This is four-arm galaxy
    </li>
    <li>
      <img :src='"/static/galaxy_help/many.png"' style="background-color: rgb(0, 151, 157)">
      If galaxy has mor than four arms - select "more than 4" label
    </li>
    <li>
      <img :src='"/static/galaxy_help/some.png"' style="background-color: rgb(0, 151, 157)">
      If your unsrue that galaxy has arms - check "can't tell label"
    </li>
  </ul>
</template>
