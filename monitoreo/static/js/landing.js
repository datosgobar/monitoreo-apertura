var Morris;
Morris.Donut({
    element: 'graph',
    data: [
        {value: 70, label: 'foo'},
        {value: 30, label: 'bar'}
    ],
    colors: [
        "#0000ff",
        "#ff0000"
    ],
    formatter: function (x) {
        return x + "%";
    }
});
