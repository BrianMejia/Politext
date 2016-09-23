google.setOnLoadCallback(drawChart);
      
var options = {};
options['region'] = 'usa';
options['dataMode'] = 'regions';
options['colors'] = ["#0000ff", "#ff0000"];

function drawChart() {

  var json_data;

  $.getJSON("test.json", function(json) {
    json_data = json; // this will show the info it in firebug console
  });

  var mapData = []
  mapData[0] = ['State', 'Yes (%)', 'No (%)']

  console.log(json_data)

  for (var i = 0; i < json_data[0]['polls'][0]['states'].length; i++) {
    
  }

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