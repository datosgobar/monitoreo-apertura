var ProgressBar;

function chart(id, pct) {
    var circle = new ProgressBar.Circle(id, {
        color: '#7AF',
        strokeWidth: 2,
        duration: 1400,
        easing: 'easeInOut',
        step: function(_, circle) {
            var value = Math.round(circle.value() * 100);
            if (value === 0) {
              circle.setText('');
            } else {
              circle.setText(value + "%");
            }
        }
    });
    circle.animate(pct);
}

window.onload = function() {
    chart("#donut-catalogos", 0.5);
    chart("#donut-datasets", 0.5);
    chart("#donut-documentados", 0.5);
    chart("#donut-descargables", 0.5);
};