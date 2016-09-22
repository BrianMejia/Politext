google.setOnLoadCallback(drawChart);
      
var options = {};
options['region'] = 'usa';
options['dataMode'] = 'regions';
options['colors'] = ["#0000ff", "#ff0000"];

function drawChart() {

  $.getJSON("test.json", function(json) {
    var json_data = json; // this will show the info it in firebug console
  });

  var data = google.visualization.arrayToDataTable([
    ['State', 	'Dem Vote (%)', 	'Rep Vote (%)'],
    ['NJ',					0.1,								0.9],
    ['CA',        	0.4,								0.6],
    ['TX',        	0.9,								0.1],
    ['MO',        	0.6,								0.4],
    ['ND',        	0.8,								0.2]
  ]);

  var chart = new google.visualization.IntensityMap(document.getElementById('chart_div'));

  chart.draw(data, options);
}