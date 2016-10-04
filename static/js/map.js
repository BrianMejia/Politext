google.setOnLoadCallback(drawChart);

var options = {};
options['region'] = 'usa';
options['dataMode'] = 'regions';
options['colors'] = ["#0000ff", "#ff0000"];
options['title'] = 'Poll: Yes or No?';

function drawChart() {

  var js_data;

   $.ajax({
        url: "static/json/custom_polls.json",
        async: false,
        dataType: 'json',
        success: function(data) {
          js_data = data;
        }
    });

  var mapData = [];
  mapData[0] = ['State', 'Yes (%)', 'No (%)'];
  mapData[1] = ['ZZ', 0, 0];
  mapData[2] = ['FF', 100, 100];

  var json_data = js_data[0]['polls']['states'];
  var json_data_length = Object.keys(json_data).length;

  for (var i = 0; i < json_data_length; i++) {
    var state = Object.keys(json_data)[i];
    var votes = json_data[state];
    var yesPercent = votes['yes_votes'] / votes['total_votes'];
    var noPercent = votes['no_votes'] / votes['total_votes'];
    var yesRounded = Math.round(yesPercent * 100);
    var noRounded = Math.round(noPercent * 100);
    var stateData = [state, yesRounded, noRounded];
    mapData.push(stateData);
  }

  var table = $('<table></table>').addClass('states_table');
  var row = $('<tr></tr>').addClass('states_header').html('<th>State</th><th>% Yes Votes</th><th>% No Votes</th>');

  table.append(row);

  for (var i = 3; i < mapData.length; i++) {
    selectedData = mapData[i];
    var row = $('<tr></tr>').addClass('states_row').html('<td>' + selectedData[0] 
      + '</td><td>' + selectedData[1] + '%</td><td>' + selectedData[2] + '%</td>');
    table.append(row);
  }

  $('#states_table').append(table);

  var data = google.visualization.arrayToDataTable(mapData);

  var chart = new google.visualization.IntensityMap(document.getElementById('chart_div'));

  chart.draw(data, options);

}