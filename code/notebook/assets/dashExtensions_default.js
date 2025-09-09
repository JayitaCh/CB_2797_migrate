window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(el) {
                var slider = document.createElement('input');
                slider.type = 'range';
                slider.min = 0;
                slider.max = 1;
                slider.step = 0.01;
                slider.value = 0.5;
                slider.style.position = 'absolute';
                slider.style.top = '10px';
                slider.style.left = '50%';
                slider.style.transform = 'translateX(-50%)';
                slider.style.zIndex = 1000;
                el.appendChild(slider);

                var topLayer = el.querySelectorAll('path')[0];
                slider.oninput = function() {
                    topLayer.style.clip = 'rect(0px, ' + (slider.value * el.offsetWidth) + 'px, ' + el.offsetHeight + 'px, 0px)';
                }
            }

            ,
        function1: function(feature) {
            return feature.properties.style;
        },
        function2: function(feature, layer) {
            layer.bindTooltip(feature.properties.tooltip);
        }
    }
});