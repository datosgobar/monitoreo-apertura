var ProgressBar;

function chart(id, pct, step_fn) {
    var settings = {
        strokeWidth: 2,
        duration: 1400,
        easing: 'easeInOut'
    };
    settings.step = step_fn ? step_fn : default_value;
    var circle = new ProgressBar.Circle(id, settings);
    circle.animate(pct);
    return circle;
}

window.onload = function() {
    chart("#donut-metadatos", $("#donut-metadatos").attr("data-pct")/100);
    chart("#donut-actualizados", $("#donut-actualizados").attr("data-pct")/100);
    var circle = chart("#donut-documentados", 0.5);
    chart("#donut-descargables", 0.5);
};

function empty() {

}

function default_value(_, circle) {
    var value = Math.round(circle.value() * 100);
    if (value === 0) {
      circle.setText('');
    } else {
      circle.setText(value + "%");
    }
}