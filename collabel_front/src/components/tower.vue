<script>
    import {fabric} from 'fabric'

    var w;
    var canvas;
    var palette = ["#5e5656", "#58668b", "#76b4bd", "#bdeaee", "#ebf4f6"]


    function arrow_pts(fromx, fromy, tox, toy) {
        var angle = Math.atan2(toy - fromy, tox - fromx);

        var headlen = 6;  // arrow head size

        tox = tox - (headlen) * Math.cos(angle);
        toy = toy - (headlen) * Math.sin(angle);

        return [
            {
                x: fromx,  // start point
                y: fromy
            }, {
                x: fromx - (headlen / 4) * Math.cos(angle - Math.PI / 2), 
                y: fromy - (headlen / 4) * Math.sin(angle - Math.PI / 2)
            },{
                x: tox - (headlen / 4) * Math.cos(angle - Math.PI / 2), 
                y: toy - (headlen / 4) * Math.sin(angle - Math.PI / 2)
            }, {
                x: tox - (headlen) * Math.cos(angle - Math.PI / 2),
                y: toy - (headlen) * Math.sin(angle - Math.PI / 2)
            },{
                x: tox + (headlen) * Math.cos(angle),  // tip
                y: toy + (headlen) * Math.sin(angle)
            }, {
                x: tox - (headlen) * Math.cos(angle + Math.PI / 2),
                y: toy - (headlen) * Math.sin(angle + Math.PI / 2)
            }, {
                x: tox - (headlen / 4) * Math.cos(angle + Math.PI / 2),
                y: toy - (headlen / 4) * Math.sin(angle + Math.PI / 2)
            }, {
                x: fromx - (headlen / 4) * Math.cos(angle + Math.PI / 2),
                y: fromy - (headlen / 4) * Math.sin(angle + Math.PI / 2)
            },{
                x: fromx,
                y: fromy
            }
        ];
    } 

    export default {
        props: ['level'],
        watch: { 
            level: function(newVal, oldVal) { // watch it
                var level = Math.min(newVal, 5);
                let h = 14;

                for (let i = Math.max(oldVal, 1); i < level  + 1; i++) { 
                    let c_w = w * ((6 - i) / 6);
                    var rect = new fabric.Rect({
                        top: 80 - h * i - 2,
                        left: w/2 - c_w * 0.5,
                        width: c_w,
                        height: h,
                        fill: palette[(i - 1) % palette.length],
                        stroke: 'black',
                        strokeWidth: 2,
                        selectable: false
                    });
                    canvas.add(rect);
                }
                
                let c_w = w * ((6 - level) / 6);
                let a_base_x = w/2 - c_w * 0.5;
                let a_base_y = 80 - h * level - 2;
                canvas.add(new fabric.Polygon(arrow_pts(a_base_x - 8, a_base_y - 24, a_base_x - 1 + 5, a_base_y - 3)));
            }
        },
        mounted() {
            canvas = new fabric.Canvas('tower');
            w = Math.min(200, document.getElementById("tower-display").clientWidth);
            canvas.setWidth(Math.min(200, document.getElementById("tower-display").clientWidth));
            for (let i = 1; i < 6; i++) { 
                let c_w = w * ((6 - i) / 6);
                let h = 14;
                var rect = new fabric.Rect({
                    top: 80 - h * i - 2,
                    left: w/2 - c_w * 0.5,
                    width: c_w,
                    height: h,
                    fill: palette[(i - 1) % palette.length],
                    stroke: 'black',
                    strokeWidth: 2,
                    selectable: false,
                    opacity: 0.1
                });
                canvas.add(rect);
            }   
        }
    }
</script>

<template>
    <canvas id="tower" width="auto" height="80"></canvas>
</template>
