<!--
// document.getElementById("redraw").onclick = redrawChart;

function redrawChart() {
    var username=document.getElementById("summ_name")
    window.alert(username)
    var chart_appearance=document.getElementById("chart_appearance");
    var chart_type=document.getElementById("chart_type");
    var chart_gwlt=document.getElementById("chart_wlt");
    var sc_content=document.getElementById("sc_content")
    var chart=document.getElementById("chart");
    var clone=chart.cloneNode(true);

    var newChart={{ redraw_chart(summoner_name=username, 
        chart_appearance=chart_appearance, chart_type=chart_type, 
        chart_wlt=chart_wlt, sc_content=sc_content) }};
    clone.setAttribute('src',(newChart|safe));
    chart.parentNode.replaceChild(clone,chart);
}
-->